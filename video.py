"""Rendu des Reels : capture image par image (animations pilotées) puis encodage MP4 H.264 avec ffmpeg."""
import os
import shutil
import subprocess
from pathlib import Path


def ffmpeg_exe():
    """ffmpeg du système, sinon celui fourni par le paquet Python imageio-ffmpeg."""
    exe = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if exe:
        return exe
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def render_reel(renderer, html, mp4, dur=10.0, fps=30, cover_ms=9500, key_ms=(1000, 3500, 6000, 9500), w=1080, h=1920, check=None):
    """Écrit mp4, une image de couverture (.jpg) et des images clés (pour l'auto-évaluation).
    Retourne (cover_path, [keyframe_paths], résultat de check(page, w, h) sur l'image finale)."""
    mp4 = Path(mp4)
    work = renderer.workdir
    f = work / (mp4.stem + ".html")
    f.write_text(html, encoding="utf-8")
    pg = renderer.browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
    try:
        pg.goto(f"file://{f}")
        pg.wait_for_load_state("networkidle")
        pg.wait_for_function("document.body.dataset.ready==='1'", timeout=20000)
        pg.evaluate("document.getAnimations().forEach(a=>a.pause())")
        cmd = [ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
               "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100", "-shortest",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(fps),
               "-c:a", "aac", "-b:a", "64k", "-movflags", "+faststart", str(mp4)]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        keys = {int(round(k / 1000 * fps)): k for k in key_ms}
        key_paths = []
        n = int(round(dur * fps))
        for i in range(n):
            t = i * 1000 / fps
            pg.evaluate("t=>document.getAnimations().forEach(a=>{a.currentTime=t})", t)
            jpg = pg.screenshot(type="jpeg", quality=92)
            ff.stdin.write(jpg)
            if i in keys:
                kp = mp4.with_name(f"{mp4.stem}_k{keys[i]:05d}.jpg")
                kp.write_bytes(jpg)
                key_paths.append(kp)
        ff.stdin.close()
        if ff.wait() != 0:
            raise RuntimeError("ffmpeg a échoué")
        pg.evaluate("t=>document.getAnimations().forEach(a=>{a.currentTime=t})", cover_ms)
        cover = mp4.with_suffix(".jpg")
        pg.screenshot(path=str(cover), type="jpeg", quality=92)
        issues = check(pg, w, h) if check else None
    finally:
        pg.close()
    return cover, key_paths, issues
