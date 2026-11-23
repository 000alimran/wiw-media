"""Make voice.mp3 for a video.

  python tools/voice.py content/2026-11/<slug>        -> writes script.txt (paste into ElevenLabs)
  ELEVENLABS_API_KEY=... python tools/voice.py ... --tts  -> also generates voice.mp3 with spec `voice_id`
"""
import os, re, sys, pathlib, requests, yaml


def lines(spec):
    out = []
    for sc in spec["scenes"]:
        for l in sc["lines"]:
            out.append(l if isinstance(l, dict) else {"show": l, "say": re.sub(r"[*~]", "", l)})
    return out


def main(folder, tts=False):
    fp = pathlib.Path(folder)
    spec = yaml.safe_load((fp / "spec.yaml").read_text())
    script = "\n\n".join(l["say"] for l in lines(spec))
    (fp / "script.txt").write_text(script + "\n")
    print("script.txt written")
    if tts and not (fp / "voice.mp3").exists():
        cfg = yaml.safe_load(pathlib.Path(__file__).resolve().parent.parent.joinpath("config.yaml").read_text()) or {}
        vid = spec.get("voice_id") or os.environ.get("ELEVENLABS_VOICE_ID") or cfg.get("voice_id")
        if not vid:
            print("no voice_id (spec, config.yaml or ELEVENLABS_VOICE_ID) - skipped"); sys.exit(3)
        r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_128",
                          headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]},
                          json={"text": script, "model_id": spec.get("voice_model") or cfg.get("voice_model", "eleven_multilingual_v2")}, timeout=300)
        r.raise_for_status()
        (fp / "voice.mp3").write_bytes(r.content)
        print("voice.mp3 generated")


if __name__ == "__main__":
    main(sys.argv[1], "--tts" in sys.argv)
