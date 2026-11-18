"""Auto-évaluation des ads avant programmation.

1. Contrôles automatiques (gratuits), faits dans la page rendue : textes coupés ou qui débordent, textes qui se
   chevauchent, logo en haut au centre, badge « +300 modèles / 40 marques », couleurs du logo, prix affiché.
2. Notation par une IA qui regarde l'image (Claude, si le secret ANTHROPIC_API_KEY existe) avec la grille sur 20.
"""
import base64
import io
import json
import os
import re
import time
import urllib.error
import urllib.request

from PIL import Image

import core

CHECK_JS = r"""
([W, H, badgeTxt]) => {
  const issues = [];
  const vis = e => { const s = getComputedStyle(e); return s.display !== 'none' && s.visibility !== 'hidden' && parseFloat(s.opacity) > 0.05; };
  // éléments porteurs de texte (texte direct)
  const texts = [...document.querySelectorAll('.ad *')].filter(e => vis(e) && !e.closest('svg') &&
      [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1));
  const R = e => e.getBoundingClientRect();
  for (const e of texts) {
    const r = R(e);
    if (r.width < 2 || r.height < 2) continue;
    if (r.left < -2 || r.top < -2 || r.right > W + 2 || r.bottom > H + 2)
      issues.push('texte hors cadre : « ' + e.textContent.trim().slice(0, 40) + ' »');
    const s = getComputedStyle(e);
    if ((s.overflowX === 'hidden' || s.overflowX === 'clip') && (e.scrollWidth > e.clientWidth + 6))
      issues.push('texte coupé : « ' + e.textContent.trim().slice(0, 40) + ' »');
  }
  // chevauchements texte / texte (hors éléments imbriqués), mesurés sans les rotations décoratives
  for (const e of document.querySelectorAll('.ad *')) {
    const t = getComputedStyle(e).transform;
    const m = t && t.startsWith('matrix(') ? t.slice(7, -1).split(',').map(Number) : null;
    if (m && (Math.abs(m[1]) > 1e-3 || Math.abs(m[2]) > 1e-3)) e.style.setProperty('transform', `matrix(1,0,0,1,${m[4]},${m[5]})`, 'important');
  }
  for (let i = 0; i < texts.length; i++) for (let j = i + 1; j < texts.length; j++) {
    const a = texts[i], b = texts[j];
    if (a.contains(b) || b.contains(a)) continue;
    const r1 = R(a), r2 = R(b);
    const w = Math.min(r1.right, r2.right) - Math.max(r1.left, r2.left), h = Math.min(r1.bottom, r2.bottom) - Math.max(r1.top, r2.top);
    if (w > 4 && h > 4) {
      const small = Math.min(r1.width * r1.height, r2.width * r2.height);
      if (w * h > 0.25 * small) issues.push('textes qui se chevauchent : « ' + a.textContent.trim().slice(0, 25) + ' » / « ' + b.textContent.trim().slice(0, 25) + ' »');
    }
  }
  // cadrage : l'écran CarPlay de chaque photo doit être entièrement visible dans son cadre
  for (const im of document.querySelectorAll('img.shot')) {
    if (!vis(im) || !im.dataset.vis) continue;
    const v = parseFloat(im.dataset.vis);
    if (v < 0.985) issues.push('écran CarPlay coupé (' + Math.round(v * 100) + ' % visible)');
  }
  // occultation : aucun texte, carte ou pastille ne doit recouvrir l'écran CarPlay (tolérance 3 %)
  const opaque = el => {
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || parseFloat(cs.opacity) < 0.3) return false;
    const m = cs.backgroundColor.match(/rgba?\(([^)]+)\)/);
    if (m) { const p = m[1].split(',').map(parseFloat); if ((p.length < 4 ? 1 : p[3]) >= 0.5) return true; }
    if (['IMG', 'CANVAS', 'VIDEO'].includes(el.tagName)) return true;
    if (el instanceof SVGElement && el.tagName.toLowerCase() !== 'svg') return true;
    return false;
  };
  const onText = (el, x, y) => {
    for (const n of el.childNodes) {
      if (n.nodeType !== 3 || !n.textContent.trim()) continue;
      const rg = document.createRange(); rg.selectNodeContents(n);
      for (const r of rg.getClientRects()) if (x >= r.left && x <= r.right && y >= r.top && y <= r.bottom) return true;
    }
    return false;
  };
  for (const im of document.querySelectorAll('img.shot')) {
    if (!vis(im) || !im.dataset.scr) continue;
    const fr = (im.dataset.mode === 'fit' ? im.parentElement : im).getBoundingClientRect();
    const [a0, b0, a1, b1] = im.dataset.scr.split(',').map(parseFloat);
    const L = Math.max(fr.left + a0, 0), T = Math.max(fr.top + b0, 0), Rr = Math.min(fr.left + a1, W), B = Math.min(fr.top + b1, H);
    if (Rr - L < 20 || B - T < 20) continue;
    let tot = 0, hid = 0; const who = {};
    for (let i = 0; i < 16; i++) for (let j = 0; j < 10; j++) {
      const x = L + (Rr - L) * (0.03 + 0.94 * i / 15), y = T + (B - T) * (0.03 + 0.94 * j / 9);
      tot++;
      for (const el of document.elementsFromPoint(x, y)) {
        if (el === im) break;
        if (el.contains(im) || el.classList.contains('shotbg')) continue;
        if (opaque(el) || onText(el, x, y)) { hid++; const k = (el.className && el.className.baseVal === undefined ? el.className : el.tagName) || el.tagName; who[k] = (who[k] || 0) + 1; break; }
      }
    }
    if (hid / tot > 0.03) issues.push('écran CarPlay masqué à ' + Math.round(100 * hid / tot) + ' % (' + Object.keys(who).join(', ') + ')');
  }
  // logo Spark Auto en haut, centré, blanc / noir / gris
  const logos = [...document.querySelectorAll('img')].filter(i => /logo_(white|black|gray)\.png/.test(i.src) && vis(i));
  const top = logos.filter(i => { const r = R(i); return Math.abs((r.left + r.right) / 2 - W / 2) < 40 && r.top < H * 0.2; });
  if (!top.length) issues.push('logo absent en haut au centre');
  if ([...document.querySelectorAll('img')].some(i => /logo_/.test(i.src) && !/logo_(white|black|gray)\.png/.test(i.src)))
    issues.push('logo d’une couleur non autorisée');
  // badge catalogue
  const b = [...document.querySelectorAll('.b250')].filter(vis);
  if (!b.length || !b.some(x => x.textContent.includes(badgeTxt))) issues.push('badge « ' + badgeTxt + ' » absent');
  else for (const x of b) { const r = R(x); if (r.left < 0 || r.right > W || r.top < 0 || r.bottom > H) issues.push('badge hors cadre'); }
  // prix (une remise « −10 € » n'est pas un prix)
  const txt = document.querySelector('.ad').innerText;
  const m = txt.match(/(^|[^−\-\d])\d[\d\s.,]*\s?€/m);
  if (m) issues.push('prix affiché : « ' + m[0].trim() + ' »');
  return [...new Set(issues)];
}
"""

GRID = """Tu es directeur artistique et responsable acquisition de Spark Auto (sparkauto.fr), boutique française d'écrans CarPlay / Android Auto sans fil installés à la place de l'autoradio d'origine.
Évalue cette publicité {kind} pour Instagram et TikTok (organique), destinée à un conducteur français sur mobile.

Note chaque critère de 1 à 5 (5 = excellent) :
- esthetisme : composition, hiérarchie, lisibilité, aucun texte coupé ni chevauchement, photo nette ; l'écran CarPlay est entièrement visible, idéalement avec une partie du tableau de bord.
- comprehension : en 2 secondes sur mobile, on comprend le produit et pour quelle voiture ; chaque phrase se lit naturellement, sans formulation bizarre ou ambiguë.
- interet : l'accroche arrête le scroll{recent}.
- conversion : bénéfice clair, appel à l'action, cohérence entre le visuel et la légende.

Critères éliminatoires (liste ceux qui s'appliquent, sinon liste vide) :
"pas d'écran CarPlay visible", "écran CarPlay pas en français", "badge +300 modèles / 40 marques absent", "logo Spark Auto absent en haut au centre",
"prix affiché", "faute d'orthographe ou de typographie française", "photo incohérente avec le véhicule annoncé ({vehicle})",
"écran CarPlay coupé ou photo mal cadrée", "formulation bizarre, peu naturelle ou ambiguë (dans le visuel ou la légende)",
"information invraisemblable ou non vérifiable".
Informations autorisées (présentes sur le site) : CarPlay et Android Auto sans fil, écran tactile HD, installation à la place de l'autoradio d'origine sans découpe ni soudure, plug & play en 20 minutes environ, commandes au volant conservées sur les versions équipées, caméra de recul compatible, cadre / faisceau / outils fournis, garantie 2 ans, aide 7j/7 sur WhatsApp, +300 modèles / 40 marques, codes promo indiqués.

Légende qui accompagnera la publication :
---
{caption}
---
Réponds UNIQUEMENT avec un objet JSON : {{"esthetisme":n,"comprehension":n,"interet":n,"conversion":n,"eliminatoire":[...],"justification":"une phrase en français"}}"""

CRITERIA = ("esthetisme", "comprehension", "interet", "conversion")


def auto_checks(page, w, h):
    try:
        return page.evaluate(CHECK_JS, [w, h, core.BADGE_TXT])
    except Exception as e:  # un contrôle qui plante ne doit pas bloquer la journée
        return [f"contrôle automatique impossible : {e}"]


def _b64(path, max_side):
    im = Image.open(path).convert("RGB")
    im.thumbnail((max_side, max_side), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def ai_score(images, caption, vehicle_name, kind, recent_formats, cfg):
    """Retourne un dict de notes, ou None si l'évaluateur est indisponible (pas de clé, erreur réseau…)."""
    key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    if not key:
        return None
    ev = cfg.get("evaluation", {})
    model = ev.get("model", "claude-haiku-5-5")
    recent = f" et ne ressemble pas aux publications des 7 derniers jours (formats : {', '.join(recent_formats)})" if recent_formats else ""
    text = GRID.format(kind="vidéo (images clés dans l'ordre)" if kind == "reel" else "statique",
                       recent=recent, vehicle=vehicle_name, caption=caption)
    content = [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                             "data": _b64(p, 1000 if kind != "reel" else 900)}} for p in images]
    content.append({"type": "text", "text": text})
    body = json.dumps({"model": model, "max_tokens": 400, "messages": [{"role": "user", "content": content}]}).encode()
    for attempt in range(3):
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, method="POST", headers={
            "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                data = json.loads(r.read().decode())
            out = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
            m = re.search(r"\{.*\}", out, re.S)
            s = json.loads(m.group(0))
            notes = {c: max(1, min(5, int(round(float(s[c]))))) for c in CRITERIA}
            notes["eliminatoire"] = [str(x) for x in (s.get("eliminatoire") or [])]
            notes["justification"] = str(s.get("justification", ""))[:300]
            notes["total"] = sum(notes[c] for c in CRITERIA)
            notes["modele"] = model
            return notes
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="ignore")[:200]
            if e.code in (400, 401, 403, 404):
                print(f"  évaluateur IA indisponible (HTTP {e.code}) : {msg}", flush=True)
                return None
        except Exception as e:
            msg = str(e)
        time.sleep(5 * (attempt + 1))
    print(f"  évaluateur IA indisponible : {msg}", flush=True)
    return None


def verdict(auto_issues, notes, cfg):
    """(accepté ?, statut, raison)."""
    ev = cfg.get("evaluation", {})
    if auto_issues:
        return False, "rejeté", "contrôles automatiques : " + " ; ".join(auto_issues)
    if notes is None:
        if ev.get("publish_if_unavailable", True):
            return True, "non évalué", "évaluateur IA indisponible : contrôles automatiques seulement"
        return False, "rejeté", "évaluateur IA indisponible"
    if notes["eliminatoire"]:
        return False, "rejeté", "éliminatoire : " + " ; ".join(notes["eliminatoire"])
    mn, tot = min(notes[c] for c in CRITERIA), notes["total"]
    if tot < ev.get("min_total", 16) or mn < ev.get("min_each", 3):
        return False, "rejeté", f"note {tot}/20 (minimum {mn}/5) : {notes['justification']}"
    return True, "validé", f"note {tot}/20 : {notes['justification']}"
