"""video.html + voice.mp3 -> video.mp4, cover.html -> cover.jpg

Usage: python tools/render.py content/2026-11/<slug> [--preview 3.5,12,30]
"""
import sys, os, asyncio, subprocess, pathlib, json
from playwright.async_api import async_playwright
sys.path.insert(0, str(pathlib.Path(__file__).parent))

FPS = 30


async def run(folder, preview=None):
    folder = pathlib.Path(folder).resolve()
    total = json.loads((folder / "timing.json").read_text())["duration"]
    exe = os.environ.get("CHROME_PATH")
    async with async_playwright() as p:
        b = await p.chromium.launch(**({"executable_path": exe} if exe else {}), args=["--disable-gpu"])
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        # cover
        await pg.goto((folder / "cover.html").as_uri()); await pg.wait_for_function("window.READY===true")
        await pg.evaluate("document.fonts.ready"); await pg.evaluate("render(5)")
        await pg.screenshot(path=str(folder / "cover.jpg"), type="jpeg", quality=90)
        await pg.goto((folder / "video.html").as_uri()); await pg.wait_for_function("window.READY===true")
        await pg.evaluate("document.fonts.ready")
        if preview:
            for t in preview:
                await pg.evaluate(f"render({t})")
                await pg.screenshot(path=str(folder / f"preview_{t}.jpg"), type="jpeg", quality=80)
            await b.close(); return
        tmp = folder / "video.part.mp4"
        ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                               "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
                               str(tmp)], stdin=subprocess.PIPE)
        n = int(total * FPS)
        for i in range(n):
            await pg.evaluate(f"render({i / FPS:.4f})")
            ff.stdin.write(await pg.screenshot(type="jpeg", quality=92))
            if i % 300 == 0:
                print(f"{folder.name}: frame {i}/{n}", flush=True)
        await b.close()
    ff.stdin.close()
    if ff.wait() != 0:
        sys.exit("ffmpeg failed")
    mix_audio(folder, total, tmp)
    print("rendered", folder / "video.mp4")


def mix_audio(folder, total, video):
    """voice + generated music bed (ducked under the voice) + whoosh/impact/pop effects -> video.mp4"""
    import music
    fx = json.loads((folder / "fx.json").read_text()) if (folder / "fx.json").exists() else {}
    music.write_wav(str(folder / "bed.wav"), music.make_bed(fx.get("music", "tech"), total))
    music.write_wav(str(folder / "sfx.wav"), music.make_fx(fx, total))
    out = folder / "video.part2.mp4"
    flt = ("[1:a]aresample=44100,aformat=channel_layouts=stereo,asplit=2[v1][vsc];[2:a]volume=0.085[m];"
           "[m][vsc]sidechaincompress=threshold=0.02:ratio=4:attack=15:release=500[md];[3:a]volume=0.28[f];"
           "[v1][md][f]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-i", str(folder / "voice.mp3"), "-i", str(folder / "bed.wav"),
                        "-i", str(folder / "sfx.wav"), "-filter_complex", flt, "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", "-movflags", "+faststart", str(out)])
    if r.returncode != 0:
        sys.exit("audio mix failed")
    os.replace(out, folder / "video.mp4"); os.remove(video)


if __name__ == "__main__":
    prev = None
    if "--preview" in sys.argv:
        prev = [float(x) for x in sys.argv[sys.argv.index("--preview") + 1].split(",")]
    asyncio.run(run(sys.argv[1], prev))
