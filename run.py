"""Agent Spark Auto : génère les static ads du jour et les programme sur Instagram + TikTok via Buffer.

Usage :
  python run.py --mode normal     # génère et programme les posts du jour
  python run.py --mode test       # 1 visuel, envoyé en BROUILLON dans Buffer (rien n'est publié)
  python run.py --mode dry-run    # génère seulement les images (aucun envoi)
"""
import argparse
import hashlib
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFilter

import core
from captions import build as build_caption
from templates import TEMPLATES

ROOT = core.ROOT
DATA = ROOT
OUT = ROOT / "out"
CACHE = ROOT / ".cache" / "photos"


def log(*a):
    print(*a, flush=True)


def load_json(p, default):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


# ---------- photos produits ----------
def fetch_photo(url):
    CACHE.mkdir(parents=True, exist_ok=True)
    key = hashlib.md5(url.encode()).hexdigest()[:16]
    dst = CACHE / f"{key}.jpg"
    if dst.exists():
        return dst
    sep = "&" if "?" in url else "?"
    req = urllib.request.Request(url + sep + "width=1400", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    tmp = dst.with_suffix(".tmp")
    tmp.write_bytes(raw)
    Image.open(tmp).convert("RGB").save(dst, "JPEG", quality=92)
    tmp.unlink()
    return dst


def screen_focus(path):
    """Centre approximatif de l'écran CarPlay (zone la plus saturée et lumineuse), en % de l'image."""
    import numpy as np
    im = Image.open(path).convert("RGB").resize((160, 160))
    hsv = np.asarray(im.convert("HSV")).astype(float) / 255
    S, Vv = hsv[..., 1], hsv[..., 2]
    w = ((S > 0.5) & (Vv > 0.55)) * (S * Vv) ** 2
    if w.sum() < 1:
        return (50, 40)
    ys, xs = np.mgrid[0:160, 0:160]
    return (round((w * xs).sum() / w.sum() / 159 * 100), round((w * ys).sum() / w.sum() / 159 * 100))


# ---------- planification ----------
def active_promo(cfg, d):
    for p in cfg.get("promos", []):
        if p.get("from", "2000-01-01") <= d.isoformat() <= p.get("until", "1999-01-01"):
            return p
    return None


def plan_day(d, n, vehicles, history, cfg):
    rng = random.Random(int(d.strftime("%Y%m%d")))
    promo = active_promo(cfg, d)
    excl_t = set(cfg.get("exclude_templates", []))
    tids = [t for t, (_, needs_promo) in TEMPLATES.items() if t not in excl_t and (not needs_promo or promo)]
    excl_v = set(cfg.get("exclude_vehicles", []))
    vs = [v for v in vehicles if v["id"] not in excl_v]

    last_t, last_v, pairs = {}, {}, set()
    cutoff = (d - timedelta(days=90)).isoformat()
    for h in history:
        last_t[h["template"]] = max(last_t.get(h["template"], ""), h["date"])
        last_v[h["vehicle"]] = max(last_v.get(h["vehicle"], ""), h["date"])
        if h["date"] >= cutoff:
            pairs.add((h["template"], h["vehicle"]))

    t_order = sorted(tids, key=lambda t: (last_t.get(t, ""), rng.random()))
    if n > 1 and promo and "promo" in tids and "promo" not in t_order[:n]:
        # une ad promo par jour tant que l'offre est active
        t_order.remove("promo")
        t_order.insert(rng.randrange(1, n), "promo")
    chosen_t = t_order[:n]

    v_order = sorted(vs, key=lambda v: (last_v.get(v["id"], ""), rng.random()))
    plan, used_v, used_b = [], set(), []
    for t in chosen_t:
        pick = None
        for strict in (True, False):
            for v in v_order:
                if v["id"] in used_v or (t, v["id"]) in pairs:
                    continue
                if strict and used_b.count(v["brand"]) >= 1:
                    continue
                pick = v
                break
            if pick:
                break
        if not pick:
            pick = next(v for v in v_order if v["id"] not in used_v)
        used_v.add(pick["id"])
        used_b.append(pick["brand"])
        others = [v for v in v_order if v["id"] != pick["id"] and v["brand"] != pick["brand"]]
        rng.shuffle(others)
        alts, seen = [], {pick["brand"]}
        for o in others:  # photos secondaires : marques différentes, jamais deux fois la même photo
            if o["brand"] not in seen and o["photos"][0] not in {a["photos"][0] for a in alts}:
                alts.append(o)
                seen.add(o["brand"])
            if len(alts) == 2:
                break
        plan.append({"template": t, "vehicle": pick, "alts": alts})
    return plan, promo


# ---------- rendu ----------
def to_jpeg(png, jpg, q=90):
    Image.open(png).convert("RGB").save(jpg, "JPEG", quality=q, optimize=True, progressive=False)


def tiktok_wrap(ig_jpg, out_jpg):
    """Met le visuel 4:5 au format TikTok 9:16 avec un fond flouté."""
    W, H = 1080, 1920
    src = Image.open(ig_jpg).convert("RGB")
    s = H / src.height
    bg = src.resize((int(src.width * s), H), Image.LANCZOS)
    x0 = (bg.width - W) // 2
    bg = bg.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(42))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (8, 8, 10)), 0.55)
    sc = 0.9
    fg = src.resize((int(1080 * sc), int(1350 * sc)), Image.LANCZOS)
    mask = Image.new("L", fg.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, fg.width, fg.height], radius=34, fill=255)
    shadow = Image.new("L", (W, H), 0)
    px, py = (W - fg.width) // 2, 250
    ImageDraw.Draw(shadow).rounded_rectangle([px, py + 18, px + fg.width, py + fg.height + 18], radius=34, fill=160)
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    bg.paste(Image.new("RGB", (W, H), (0, 0, 0)), (0, 0), shadow)
    bg.paste(fg, (px, py), mask)
    bg.save(out_jpg, "JPEG", quality=90, optimize=True)


def render_plan(plan, d, promo, cfg, outdir):
    T = TEMPLATES
    outdir.mkdir(parents=True, exist_ok=True)
    rd = core.Renderer(outdir / "_html")
    items = []
    try:
        for i, p in enumerate(plan, 1):
            v = p["vehicle"]
            vlist = [v] + p["alts"]
            photos, foci = [], []
            for vv in vlist:
                urls = vv["photos"]
                u = urls[(int(d.strftime("%j")) + i) % len(urls)]
                fp = fetch_photo(u)
                photos.append("file://" + str(fp))
                foci.append(screen_focus(fp))
            core.CTX.clear()
            core.CTX.update({"v": v, "vehicles": vlist, "photos": photos, "focus": foci, "promo": promo,
                             "evergreen": cfg.get("evergreen_offer")})
            fn = T[p["template"]][0]
            base = f"{d.isoformat()}_{i:02d}_{p['template']}"
            png = outdir / "_html" / f"{base}.png"
            rd.render(fn(), png)
            ig = outdir / f"{base}_ig.jpg"
            tt = outdir / f"{base}_tiktok.jpg"
            to_jpeg(png, ig)
            tiktok_wrap(ig, tt)
            items.append({**p, "slot": i, "ig": ig, "tt": tt})
            log(f"  rendu {i}/{len(plan)} : {p['template']} · {v['name']}")
    finally:
        rd.close()
    return items


# ---------- hébergement des images (branche git publique) ----------
def git_env():
    """Identité des commits automatiques : le compte GitHub qui lance le workflow (adresse noreply)."""
    actor = os.environ.get("GITHUB_ACTOR", "github-actions")
    ident = actor + "@users.noreply.github.com"
    return {**os.environ, "GIT_AUTHOR_NAME": actor, "GIT_COMMITTER_NAME": actor,
            "GIT_AUTHOR_EMAIL": ident, "GIT_COMMITTER_EMAIL": ident}


def git(*args, cwd=None, check=True):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=git_env())
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} : {r.stderr.strip()}")
    return r.stdout.strip()


def publish_media(files, d, cfg):
    repo = os.environ.get("GITHUB_REPOSITORY")
    token = os.environ.get("GITHUB_TOKEN")
    if not repo or not token:
        raise RuntimeError("GITHUB_REPOSITORY / GITHUB_TOKEN absents : l'envoi doit tourner dans GitHub Actions.")
    branch = cfg.get("media_branch", "media")
    tmp = Path(tempfile.mkdtemp())
    folder = tmp / d.isoformat()
    folder.mkdir()
    for f in files:
        shutil.copy(f, folder / Path(f).name)
    git("init", "-q", "-b", branch, cwd=tmp)
    git("add", ".", cwd=tmp)
    git("commit", "-q", "-m", f"media {d.isoformat()}", cwd=tmp)
    git("push", "-q", "-f", f"https://x-access-token:{token}@github.com/{repo}.git", f"{branch}:{branch}", cwd=tmp)
    base = f"https://raw.githubusercontent.com/{repo}/{branch}/{d.isoformat()}/"
    # attendre que les fichiers soient servis publiquement
    test = base + Path(files[0]).name
    for _ in range(30):
        try:
            with urllib.request.urlopen(urllib.request.Request(test, method="HEAD"), timeout=20) as r:
                if r.status == 200:
                    return base
        except Exception:
            pass
        time.sleep(5)
    raise RuntimeError(f"Images non accessibles publiquement ({test}). Le dépôt GitHub doit être PUBLIC.")


def save_history(history):
    p = DATA / "history.json"
    p.write_text(json.dumps(history[-2000:], ensure_ascii=False, indent=1), encoding="utf-8")
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return
    git("add", "history.json", cwd=ROOT)
    if git("status", "--porcelain", "history.json", cwd=ROOT):
        git("commit", "-q", "-m", "historique des posts [skip ci]", cwd=ROOT)
        git("pull", "-q", "--rebase", cwd=ROOT, check=False)
        git("push", "-q", cwd=ROOT)


# ---------- programme principal ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="normal", choices=["normal", "test", "dry-run"])
    ap.add_argument("--date", default=None, help="AAAA-MM-JJ (défaut : aujourd'hui, heure de Paris)")
    ap.add_argument("--count", type=int, default=None)
    a = ap.parse_args()

    cfg = load_json(ROOT / "config.json", {})
    tz = ZoneInfo(cfg.get("timezone", "Europe/Paris"))
    now = datetime.now(tz)
    d = date.fromisoformat(a.date) if a.date else now.date()
    vehicles = load_json(DATA / "vehicles.json", [])
    history = load_json(DATA / "history.json", [])

    times = cfg.get("times", [])
    slots = []
    for i, t in enumerate(times, 1):
        hh, mm = map(int, t.split(":"))
        due = datetime(d.year, d.month, d.day, hh, mm, tzinfo=tz)
        slots.append((i, due))
    done = {h["slot"] for h in history if h["date"] == d.isoformat() and h.get("mode") == "normal"}

    if a.mode == "test":
        slots = [(99, now + timedelta(days=1))]
    elif a.mode == "normal":
        slots = [(i, due) for i, due in slots if i not in done and due > now + timedelta(minutes=10)]
        if not slots:
            log("Rien à programmer : tous les créneaux du jour sont passés ou déjà programmés.")
            return
    n = a.count or len(slots)
    slots = slots[:n]

    log(f"== Spark Auto · {d.isoformat()} · mode {a.mode} · {len(slots)} visuel(s) ==")
    plan, promo = plan_day(d, len(slots), vehicles, history, cfg)
    outdir = OUT / d.isoformat()
    items = render_plan(plan, d, promo, cfg, outdir)
    for it, (slot, due) in zip(items, slots):
        it["slot"], it["due"] = slot, due
        seed = int(d.strftime("%Y%m%d")) * 10 + slot
        it["cap_ig"] = build_caption(it["template"], it["vehicle"], "instagram", promo, cfg.get("evergreen_caption"), seed)
        it["cap_tt"] = build_caption(it["template"], it["vehicle"], "tiktok", promo, cfg.get("evergreen_caption"), seed)
        (outdir / f"{it['ig'].stem.replace('_ig', '')}_legendes.txt").write_text(
            f"INSTAGRAM\n{it['cap_ig']}\n\nTIKTOK\n{it['cap_tt']}\n", encoding="utf-8")

    if a.mode == "dry-run":
        log(f"Images générées dans {outdir} (aucun envoi).")
        return

    from buffer import Buffer, BufferError
    buf = Buffer(os.environ.get("BUFFER_API_KEY", ""))
    try:
        chans = buf.channels()
    except BufferError as e:
        raise SystemExit(f"Connexion à Buffer impossible (clé refusée ou API indisponible) : {e}")
    ids = cfg.get("buffer", {})
    def pick(service, key):
        if ids.get(key):
            return next((c for c in chans if c["id"] == ids[key]), None)
        return next((c for c in chans if (c.get("service") or "").lower() == service), None)
    targets = []
    if cfg.get("platforms", {}).get("instagram", True):
        c = pick("instagram", "instagram_channel_id")
        if c: targets.append(("instagram", c))
        else: log("ATTENTION : aucun compte Instagram connecté dans Buffer.")
    if cfg.get("platforms", {}).get("tiktok", True):
        c = pick("tiktok", "tiktok_channel_id")
        if c: targets.append(("tiktok", c))
        else: log("ATTENTION : aucun compte TikTok connecté dans Buffer.")
    if not targets:
        raise SystemExit("Aucun canal Buffer utilisable. Connectez Instagram et TikTok dans Buffer.")
    log("Canaux : " + ", ".join(f"{s} ({c.get('displayName') or c.get('name')})" for s, c in targets))

    files = [str(it["ig"]) for it in items] + [str(it["tt"]) for it in items]
    base = publish_media(files, d, cfg)
    errors = 0
    for it in items:
        rec = {"date": d.isoformat(), "slot": it["slot"], "time": it["due"].strftime("%H:%M"), "mode": a.mode,
               "template": it["template"], "vehicle": it["vehicle"]["id"], "posts": {}}
        for service, c in targets:
            url = base + (it["ig"].name if service == "instagram" else it["tt"].name)
            text = it["cap_ig"] if service == "instagram" else it["cap_tt"]
            due = it["due"].astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            try:
                post = buf.create_post(c["id"], service, text, url, due, draft=(a.mode == "test"))
                rec["posts"][service] = post.get("id")
                log(f"  ✓ {service} · {it['due'].strftime('%H:%M')} · {it['template']} · {it['vehicle']['name']}")
            except Exception as e:
                errors += 1
                rec["posts"][service] = f"ERREUR : {e}"
                log(f"  ✗ {service} · {it['template']} : {e}")
        if a.mode == "normal":
            history.append(rec)
    if a.mode == "normal":
        save_history(history)
    if errors:
        raise SystemExit(f"{errors} envoi(s) en erreur : voir le journal ci-dessus.")
    log("Terminé." + (" Brouillons créés dans Buffer : vérifiez-les." if a.mode == "test" else ""))


if __name__ == "__main__":
    main()
