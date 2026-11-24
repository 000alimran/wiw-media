"""Publish rendered videos to HighLevel Social Planner, then clean Media Storage.

  python tools/ghl.py publish content/2026-11/<slug>   upload video+cover to WIW/<Month>, create posts
  python tools/ghl.py cleanup                          delete media of videos whose posts are all live

Needs env GHL_TOKEN (HighLevel Private Integration token for the YOLO sub-account).
"""
import os, sys, json, time, pathlib, datetime as dt, requests, yaml
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
LOC = CFG["location_id"]
API = "https://services.leadconnectorhq.com"
S = requests.Session()
S.headers.update({"Authorization": f"Bearer {os.environ.get('GHL_TOKEN', '')}", "Version": "2021-07-28", "Accept": "application/json"})


def req(method, path, **kw):
    for attempt in range(4):
        r = S.request(method, API + path, timeout=120, **kw)
        if r.status_code in (429, 502, 503, 504):
            time.sleep(5 * (attempt + 1)); continue
        if r.status_code >= 400:
            sys.exit(f"{method} {path} -> {r.status_code}: {r.text[:500]}")
        return r.json() if r.text else {}
    sys.exit(f"{method} {path} kept failing")


def files(**q):
    q = {"altId": LOC, "altType": "location", "limit": 50, **q}
    return req("GET", "/medias/files", params=q).get("files", [])


def folder(name, parent=None):
    for f in files(type="folder", query=name, **({"parentId": parent} if parent else {})):
        if f.get("name") == name and (parent is None or f.get("parentId") == parent):
            return f["_id"]
    body = {"altId": LOC, "altType": "location", "name": name, **({"parentId": parent} if parent else {})}
    r = req("POST", "/medias/folder", json=body)
    return r.get("_id") or r.get("id") or r.get("folder", {}).get("_id")


def upload(path, name, parent):
    with open(path, "rb") as fh:
        r = req("POST", "/medias/upload-file", files={"file": (name, fh, "video/mp4" if name.endswith(".mp4") else "image/jpeg")}, data={"name": name, "parentId": parent})
    fid = r.get("fileId") or r.get("_id")
    for _ in range(60):  # wait for HighLevel to finish encoding the video
        hit = [f for f in files(type="file", query=name.rsplit(".", 1)[0]) if f.get("_id") == fid]  # GHL may rename to "name (2).mp4"
        if hit and not hit[0].get("encodingInProgress") and hit[0].get("url"):
            return hit[0]
        time.sleep(10)
    sys.exit(f"{name}: still encoding after 10 minutes")


def when(spec):
    p = str(spec.get("publish", "now")).strip()
    if p == "now":
        return None
    d, t, tz = p.split()  # "2026-11-24 11:00 America/New_York"
    local = dt.datetime.fromisoformat(f"{d}T{t}").replace(tzinfo=ZoneInfo(tz))
    return local.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def post_body(platform, spec, media, sched):
    cap = spec["caption"]; tags = " ".join("#" + h for h in spec.get("hashtags", []))
    cta = CFG["cta"].get(platform, "")
    long_ = f"{cap['long'].strip()}\n\n{cta}\n\n{tags}".strip()
    short = f"{cap.get('short', cap['long']).strip()}\n\n{' '.join('#' + h for h in spec.get('hashtags', [])[:4])}".strip()
    b = {"accountIds": [CFG["accounts"][platform]], "userId": CFG["user_id"], "media": [media],
         "status": "scheduled" if sched else "published", **({"scheduleDate": sched} if sched else {})}
    if platform == "youtube":
        b.update(type="post", summary=long_ + " #Shorts", youtubePostDetails={"type": "short", "title": spec["title"][:100], "privacyLevel": "public"})
    elif platform == "instagram":
        b.update(type="reel", summary=long_, instagramPostDetails={"type": "reel", "showOnFeed": True})
    elif platform == "facebook":
        b.update(type="reel", summary=short, facebookPostDetails={"type": "reel"})
    elif platform == "tiktok":
        b.update(type="post", summary=short, tiktokPostDetails={"privacyLevel": "PUBLIC_TO_EVERYONE", "enableComment": True, "enableDuet": True,
                 "enableStitch": True, "promoteOtherBrand": False, "promoteYourBrand": False, "videoDisclosure": False})
    elif platform == "linkedin":
        b.update(type="post", summary=long_)
    return b


def publish(folder_path):
    fp = (ROOT / folder_path).resolve()
    state_f = fp / "state.json"
    if state_f.exists():
        print("already published:", fp.name); return
    spec = yaml.safe_load((fp / "spec.yaml").read_text())
    month = dt.date.fromisoformat(fp.parent.name + "-01").strftime("%B %Y")
    parent = folder(month, folder(CFG["media_root_folder"]))
    slug = spec.get("slug", fp.name)
    vid = upload(fp / "video.mp4", f"{slug}.mp4", parent)
    cov = upload(fp / "cover.jpg", f"{slug}-cover.jpg", parent)
    media = {"url": vid["url"], "type": "video/mp4", "thumbnail": cov["url"]}
    sched = when(spec)
    posts = {}
    for pl in spec.get("platforms", CFG["default_platforms"]):
        r = req("POST", f"/social-media-posting/{LOC}/posts", json=post_body(pl, spec, media, sched))
        p = (r.get("results") or {}).get("post") or {}
        posts[pl] = p.get("parentPostId") or p.get("_id")
        print(f"  {pl}: {'scheduled ' + sched if sched else 'publishing now'}")
    state = {"slug": slug, "created": dt.datetime.utcnow().isoformat() + "Z", "schedule": sched,
             "media": [vid["_id"], cov["_id"]], "posts": posts, "cleaned": False}
    state_f.write_text(json.dumps(state, indent=1))
    print("published", slug)


def cleanup():
    accts = ",".join(CFG["accounts"].values())
    for sf in sorted(ROOT.glob("content/*/*/state.json")):
        st = json.loads(sf.read_text())
        if st.get("cleaned"):
            continue
        start = dt.datetime.fromisoformat(st["created"].rstrip("Z")) - dt.timedelta(hours=1)
        end = (dt.datetime.fromisoformat(st["schedule"].rstrip("Z")) if st.get("schedule") else start) + dt.timedelta(days=2)
        if st.get("schedule") and dt.datetime.utcnow() < dt.datetime.fromisoformat(st["schedule"].rstrip("Z")):
            continue
        body = {"type": "all", "accounts": accts, "limit": "100", "skip": "0", "includeUsers": "false",
                "fromDate": start.isoformat() + "Z", "toDate": end.isoformat() + "Z"}
        found = req("POST", f"/social-media-posting/{LOC}/posts/list", json=body).get("results", {}).get("posts", [])
        mine = [p for p in found if p.get("parentPostId") in st["posts"].values() or p.get("_id") in st["posts"].values()]
        status = {p.get("platform"): p.get("status") for p in mine}
        st["post_status"] = status
        if mine and all(s == "published" for s in status.values()) and len(mine) >= len(st["posts"]):
            for mid in st["media"]:
                req("DELETE", f"/medias/{mid}", params={"altId": LOC, "altType": "location"})
            st["cleaned"] = True
            print("cleaned", st["slug"])
        else:
            print("waiting", st["slug"], status)
        sf.write_text(json.dumps(st, indent=1))


if __name__ == "__main__":
    {"publish": lambda: publish(sys.argv[2]), "cleanup": cleanup}[sys.argv[1]]()
