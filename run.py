"""Agent Spark Auto : génère les pubs du jour (statiques + Reels), les auto-évalue, puis les programme
sur Instagram + TikTok via Buffer.

Usage :
  python run.py --mode normal     # génère, évalue et programme les posts du jour
  python run.py --mode test       # 1 statique + 1 Reel, envoyés en BROUILLON dans Buffer (rien n'est publié)
  python run.py --mode dry-run    # génère et évalue seulement (aucun envoi)
  python run.py --mode recap      # récapitulatif de la semaine (ouvert comme issue GitHub)
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
import evaluate
import video
from captions import build as build_caption
from reels import REELS, COVER_MS, caption_id
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


class Planner:
    """Choisit format × véhicule : formats les moins récents d'abord, pas deux fois le même couple en 90 jours,
    marques variées dans la journée, photos secondaires distinctes."""

    def __init__(self, d, vehicles, history, cfg):
        self.rng = random.Random(int(d.strftime("%Y%m%d")))
        self.promo = active_promo(cfg, d)
        excl_t = set(cfg.get("exclude_templates", []))
        pools = {
            "static": [t for t, (_, np_) in TEMPLATES.items() if t not in excl_t and (not np_ or self.promo)],
            "reel": [r for r, (_, np_) in REELS.items() if r not in excl_t and (not np_ or self.promo)],
        }
        excl_v = set(cfg.get("exclude_vehicles", []))
        vs = [v for v in vehicles if v["id"] not in excl_v]
        last_t, last_v, self.pairs = {}, {}, set()
        cutoff = (d - timedelta(days=90)).isoformat()
        for h in history:
            if h.get("status") == "rejeté":
                continue
            last_t[h["template"]] = max(last_t.get(h["template"], ""), h["date"])
            last_v[h["vehicle"]] = max(last_v.get(h["vehicle"], ""), h["date"])
            if h["date"] >= cutoff:
                self.pairs.add((h["template"], h["vehicle"]))
        self.orders = {k: sorted(p, key=lambda t: (last_t.get(t, ""), self.rng.random())) for k, p in pools.items()}
        self.v_order = sorted(vs, key=lambda v: (last_v.get(v["id"], ""), self.rng.random()))
        self.used_t, self.used_v, self.used_b = set(), set(), []

    def plan(self, kinds):
        promo_i = None
        st = [i for i, k in enumerate(kinds) if k == "static"]
        if self.promo and "promo" in self.orders["static"] and len(st) > 1:
            promo_i = self.rng.choice(st[1:])  # une pub promo par jour tant que l'offre est active
        return [self.pick(k, "promo" if i == promo_i else None) for i, k in enumerate(kinds)]

    def pick(self, kind, template=None):
        order = self.orders[kind]
        if template is None:
            free = [t for t in order if t not in self.used_t and t != "promo"] or [t for t in order if t != "promo"] or order
            template = free[0]
        self.used_t.add(template)
        pick = None
        for strict in (True, False):
            for v in self.v_order:
                if v["id"] in self.used_v or (template, v["id"]) in self.pairs:
                    continue
                if strict and self.used_b.count(v["brand"]) >= 1:
                    continue
                pick = v
                break
            if pick:
                break
        if not pick:
            pick = next((v for v in self.v_order if v["id"] not in self.used_v), self.v_order[0])
        self.used_v.add(pick["id"])
        self.used_b.append(pick["brand"])
        others = [v for v in self.v_order if v["id"] != pick["id"] and v["brand"] != pick["brand"]]
        self.rng.shuffle(others)
        alts, seen = [], {pick["brand"]}
        for o in others:  # photos secondaires : marques différentes, jamais deux fois la même photo
            if o["brand"] not in seen and o["photos"][0] not in {a["photos"][0] for a in alts}:
                alts.append(o)
                seen.add(o["brand"])
            if len(alts) == 2:
                break
        return {"template": template, "kind": kind, "vehicle": pick, "alts": alts}


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


def render_item(rd, it, d, cfg, promo, outdir, slot, attempt):
    """Rend un candidat (statique ou Reel) et lance les contrôles automatiques."""
    v = it["vehicle"]
    photos, foci = [], []
    for k, vv in enumerate([v] + it["alts"]):
        urls = vv["photos"]
        u = urls[(int(d.strftime("%j")) + slot + attempt + k) % len(urls)]
        fp = fetch_photo(u)
        photos.append("file://" + str(fp))
        foci.append(screen_focus(fp))
    core.CTX.clear()
    core.CTX.update({"v": v, "vehicles": [v] + it["alts"], "photos": photos, "focus": foci, "promo": promo,
                     "evergreen": cfg.get("evergreen_offer")})
    base = f"{d.isoformat()}_{slot:02d}_{it['template']}" + (f"_e{attempt}" if attempt else "")
    if it["kind"] == "reel":
        mp4 = outdir / f"{base}.mp4"
        cover, keys, issues = video.render_reel(rd, REELS[it["template"]][0](), mp4, cover_ms=COVER_MS, check=evaluate.auto_checks)
        return {**it, "ig": mp4, "tt": mp4, "cover": cover, "eval_images": keys, "issues": issues or []}
    png = outdir / "_html" / f"{base}.png"
    issues = rd.render(TEMPLATES[it["template"]][0](), png, check=evaluate.auto_checks)
    ig, tt = outdir / f"{base}_ig.jpg", outdir / f"{base}_tiktok.jpg"
    to_jpeg(png, ig)
    tiktok_wrap(ig, tt)
    return {**it, "ig": ig, "tt": tt, "eval_images": [ig], "issues": issues or []}


def produce(slots, planner, d, cfg, promo, history, outdir):
    """Pour chaque créneau : rendu, contrôles automatiques, notation IA, régénération si besoin (2 essais max)."""
    outdir.mkdir(parents=True, exist_ok=True)
    retries = cfg.get("evaluation", {}).get("retries", 2)
    since = (d - timedelta(days=7)).isoformat()
    recent = sorted({h["template"] for h in history if h["date"] >= since and h.get("status") != "rejeté"})
    plan = planner.plan([k for _, _, k in slots])
    rd = core.Renderer(outdir / "_html")
    accepted, rejected = [], []
    try:
        for (slot, due, kind), first in zip(slots, plan):
            cand = first
            for attempt in range(retries + 1):
                if attempt:
                    cand = planner.pick(kind)
                it = render_item(rd, cand, d, cfg, promo, outdir, slot, attempt)
                seed = int(d.strftime("%Y%m%d")) * 10 + slot
                cid = caption_id(it["template"])
                it["cap_ig"] = build_caption(cid, it["vehicle"], "instagram", promo, cfg.get("evergreen_caption"), seed)
                it["cap_tt"] = build_caption(cid, it["vehicle"], "tiktok", promo, cfg.get("evergreen_caption"), seed)
                notes = None if it["issues"] else evaluate.ai_score(it["eval_images"], it["cap_ig"], it["vehicle"]["name"],
                                                                      kind, recent, cfg)
                ok, status, reason = evaluate.verdict(it["issues"], notes, cfg)
                it.update({"slot": slot, "due": due, "notes": notes, "status": status, "reason": reason})
                mark = "✓" if ok else "✗"
                log(f"  {mark} créneau {slot} · {kind} · {it['template']} · {it['vehicle']['name']} → {status} ({reason})")
                if ok:
                    stem = it["ig"].stem.replace("_ig", "")
                    (outdir / f"{stem}_legendes.txt").write_text(
                        f"INSTAGRAM\n{it['cap_ig']}\n\nTIKTOK\n{it['cap_tt']}\n\nÉVALUATION : {status} — {reason}\n", encoding="utf-8")
                    accepted.append(it)
                    recent.append(it["template"])
                    break
                rejected.append(it)
            else:
                log(f"  créneau {slot} laissé vide : aucune pub n'a atteint le niveau requis.")
    finally:
        rd.close()
    return accepted, rejected


# ---------- hébergement des fichiers (branche git publique) ----------
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
    """Héberge les fichiers du jour sur la branche publique « media » (garde aujourd'hui et hier, un seul commit)."""
    repo = os.environ.get("GITHUB_REPOSITORY")
    token = os.environ.get("GITHUB_TOKEN")
    if not repo or not token:
        raise RuntimeError("GITHUB_REPOSITORY / GITHUB_TOKEN absents : l'envoi doit tourner dans GitHub Actions.")
    branch = cfg.get("media_branch", "media")
    url = f"https://x-access-token:{token}@github.com/{repo}.git"
    work = Path(tempfile.mkdtemp()) / "media"
    git("clone", "-q", "--depth", "1", "-b", branch, url, str(work), check=False)
    if not (work / ".git").exists():
        work.mkdir(parents=True, exist_ok=True)
        git("init", "-q", "-b", branch, cwd=work)
    keep = {d.isoformat(), (d - timedelta(days=1)).isoformat()}
    for p in work.iterdir():
        if p.is_dir() and p.name != ".git" and p.name not in keep:
            shutil.rmtree(p)
    folder = work / d.isoformat()
    folder.mkdir(exist_ok=True)
    for f in files:
        shutil.copy(f, folder / Path(f).name)
    git("checkout", "-q", "--orphan", "media-tmp", cwd=work)
    git("add", "-A", cwd=work)
    git("commit", "-q", "-m", f"media {d.isoformat()}", cwd=work)
    git("push", "-q", "-f", url, f"media-tmp:{branch}", cwd=work)
    base = f"https://raw.githubusercontent.com/{repo}/{branch}/{d.isoformat()}/"
    # attendre que les fichiers soient servis publiquement
    test = base + Path(files[-1]).name
    for _ in range(30):
        try:
            with urllib.request.urlopen(urllib.request.Request(test, method="HEAD"), timeout=20) as r:
                if r.status == 200:
                    return base
        except Exception:
            pass
        time.sleep(5)
    raise RuntimeError(f"Fichiers non accessibles publiquement ({test}). Le dépôt GitHub doit être PUBLIC.")


def save_history(history):
    p = DATA / "history.json"
    p.write_text(json.dumps(history[-3000:], ensure_ascii=False, indent=1), encoding="utf-8")
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return
    git("add", "history.json", cwd=ROOT)
    if git("status", "--porcelain", "history.json", cwd=ROOT):
        git("commit", "-q", "-m", "historique des posts [skip ci]", cwd=ROOT)
        git("pull", "-q", "--rebase", cwd=ROOT, check=False)
        git("push", "-q", cwd=ROOT)


# ---------- récapitulatif hebdomadaire ----------
def recap(d, history):
    since = (d - timedelta(days=7)).isoformat()
    week = [h for h in history if since <= h["date"] < d.isoformat() and h.get("mode") == "normal"]
    posted = [h for h in week if h.get("status") != "rejeté"]
    rej = [h for h in week if h.get("status") == "rejeté"]
    by_t = {}
    for h in week:
        s = by_t.setdefault(h["template"], {"n": 0, "notes": [], "rej": 0})
        s["n"] += 1
        if h.get("status") == "rejeté":
            s["rej"] += 1
        if (h.get("score") or {}).get("total"):
            s["notes"].append(h["score"]["total"])
    avg = {t: sum(s["notes"]) / len(s["notes"]) for t, s in by_t.items() if s["notes"]}
    best = sorted(avg, key=lambda t: -avg[t])[:3]
    worst = sorted(avg, key=lambda t: avg[t])[:3]
    remove = sorted(t for t, s in by_t.items() if s["rej"] >= 2 or (len(s["notes"]) >= 2 and avg.get(t, 20) < 15))
    lines = [f"**Semaine du {since} au {(d - timedelta(days=1)).isoformat()}**", "",
             f"- Publications programmées : {len(posted)} ({sum(h.get('kind') == 'reel' for h in posted)} Reels, "
             f"{sum(h.get('kind') != 'reel' for h in posted)} statiques)",
             f"- Non évaluées par l'IA (contrôles automatiques seulement) : {sum(h.get('status') == 'non évalué' for h in posted)}",
             f"- Pubs rejetées puis remplacées : {len(rej)}", ""]
    if best:
        lines += ["**Meilleurs formats** : " + ", ".join(f"{t} ({avg[t]:.1f}/20)" for t in best),
                  "**Formats les plus faibles** : " + ", ".join(f"{t} ({avg[t]:.1f}/20)" for t in worst), ""]
    lines += ["**Formats à retirer** : " + (", ".join(remove) if remove else "aucun"), ""]
    if rej:
        lines += ["**Pubs rejetées**"] + [f"- {h['date']} · {h['template']} · {h['vehicle']} : {h.get('reason', '')}" for h in rej[:30]]
    body = "\n".join(lines)
    log(body)
    repo, token = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN")
    if repo and token:
        req = urllib.request.Request(f"https://api.github.com/repos/{repo}/issues", method="POST",
                                     data=json.dumps({"title": f"Récap des pubs · semaine du {since}", "body": body}).encode(),
                                     headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                                              "User-Agent": "sparkauto-autopost"})
        with urllib.request.urlopen(req, timeout=60) as r:
            log(f"Récap publié : {json.loads(r.read().decode()).get('html_url')}")


# ---------- programme principal ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="normal", choices=["normal", "test", "dry-run", "recap"])
    ap.add_argument("--date", default=None, help="AAAA-MM-JJ (défaut : aujourd'hui, heure de Paris)")
    ap.add_argument("--count", type=int, default=None)
    a = ap.parse_args()

    cfg = load_json(ROOT / "config.json", {})
    tz = ZoneInfo(cfg.get("timezone", "Europe/Paris"))
    now = datetime.now(tz)
    d = date.fromisoformat(a.date) if a.date else now.date()
    vehicles = load_json(DATA / "vehicles.json", [])
    history = load_json(DATA / "history.json", [])
    if a.mode == "recap":
        return recap(d, history)

    video_slots = set(cfg.get("video_slots", [2, 5]))
    slots = []
    for i, t in enumerate(cfg.get("times", []), 1):
        hh, mm = map(int, t.split(":"))
        slots.append((i, datetime(d.year, d.month, d.day, hh, mm, tzinfo=tz), "reel" if i in video_slots else "static"))
    done = {h["slot"] for h in history if h["date"] == d.isoformat() and h.get("mode") == "normal" and h.get("status") != "rejeté"}

    if a.mode == "test":
        slots = [(98, now + timedelta(days=1), "static"), (99, now + timedelta(days=1, minutes=5), "reel")]
    elif a.mode == "normal":
        slots = [s for s in slots if s[0] not in done and s[1] > now + timedelta(minutes=10)]
        if not slots:
            log("Rien à programmer : tous les créneaux du jour sont passés ou déjà programmés.")
            return
    slots = slots[:a.count or len(slots)]

    log(f"== Spark Auto · {d.isoformat()} · mode {a.mode} · {len(slots)} créneau(x) "
        f"({sum(k == 'reel' for *_, k in slots)} Reel(s)) ==")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        log("Évaluation IA désactivée (secret ANTHROPIC_API_KEY absent) : contrôles automatiques seulement.")
    planner = Planner(d, vehicles, history, cfg)
    outdir = OUT / d.isoformat()
    items, rejected = produce(slots, planner, d, cfg, planner.promo, history, outdir)

    def rec(it):
        n = it.get("notes")
        return {"date": d.isoformat(), "slot": it["slot"], "time": it["due"].strftime("%H:%M"), "mode": a.mode,
                "kind": it["kind"], "template": it["template"], "vehicle": it["vehicle"]["id"], "status": it["status"],
                "reason": it["reason"], "score": {k: n[k] for k in ("esthetisme", "comprehension", "interet", "conversion", "total")} if n else None,
                "posts": {}}

    if a.mode == "dry-run":
        log(f"Fichiers générés dans {outdir} (aucun envoi).")
        return
    if a.mode == "normal":
        history += [rec(it) for it in rejected]
    if not items:
        if a.mode == "normal":
            save_history(history)
        raise SystemExit("Aucune pub n'a passé l'évaluation aujourd'hui : rien n'a été programmé.")

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
        if c:
            targets.append(("instagram", c))
        else:
            log("ATTENTION : aucun compte Instagram connecté dans Buffer.")
    if cfg.get("platforms", {}).get("tiktok", True):
        c = pick("tiktok", "tiktok_channel_id")
        if c:
            targets.append(("tiktok", c))
        else:
            log("ATTENTION : aucun compte TikTok connecté dans Buffer.")
    if not targets:
        raise SystemExit("Aucun canal Buffer utilisable. Connectez Instagram et TikTok dans Buffer.")
    log("Canaux : " + ", ".join(f"{s} ({c.get('displayName') or c.get('name')})" for s, c in targets))

    files = sorted({str(it["ig"]) for it in items} | {str(it["tt"]) for it in items})
    base = publish_media(files, d, cfg)
    errors = 0
    for it in items:
        r = rec(it)
        for service, c in targets:
            url = base + (it["ig"].name if service == "instagram" else it["tt"].name)
            text = it["cap_ig"] if service == "instagram" else it["cap_tt"]
            due = it["due"].astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            try:
                post = buf.create_post(c["id"], service, text, url, due, draft=(a.mode == "test"),
                                       kind=it["kind"], thumb_ms=COVER_MS if it["kind"] == "reel" else None)
                r["posts"][service] = post.get("id")
                log(f"  ✓ {service} · {it['due'].strftime('%H:%M')} · {it['kind']} · {it['template']} · {it['vehicle']['name']}")
            except Exception as e:
                errors += 1
                r["posts"][service] = f"ERREUR : {e}"
                log(f"  ✗ {service} · {it['template']} : {e}")
        if a.mode == "normal":
            history.append(r)
    if a.mode == "normal":
        save_history(history)
    if errors:
        raise SystemExit(f"{errors} envoi(s) en erreur : voir le journal ci-dessus.")
    log("Terminé." + (" Brouillons créés dans Buffer : vérifiez-les." if a.mode == "test" else ""))


if __name__ == "__main__":
    main()
