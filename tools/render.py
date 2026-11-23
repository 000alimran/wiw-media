"""video.html + voice.mp3 -> video.mp4, cover.html -> cover.jpg

Usage: python tools/render.py content/2026-11/<slug> [--preview 3.5,12,30]
"""
import sys, os, asyncio, subprocess, pathlib, json
from playwright.async_api import async_playwright

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
                               "-i", str(folder / "voice.mp3"), "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast",
                               "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-shortest",
                               "-movflags", "+faststart", str(tmp)], stdin=subprocess.PIPE)
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
    os.replace(tmp, folder / "video.mp4")
    print("rendered", folder / "video.mp4")


if __name__ == "__main__":
    prev = None
    if "--preview" in sys.argv:
        prev = [float(x) for x in sys.argv[sys.argv.index("--preview") + 1].split(",")]
    asyncio.run(run(sys.argv[1], prev))
