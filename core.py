"""Moteur de rendu : HTML/CSS -> PNG via Chromium (Playwright)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NPM = ROOT / ".deps" / "node_modules"          # installé par le workflow (npm)
BRAND = ROOT / ".cache" / "brand"
LOGO_URL = "https://cdn.shopify.com/s/files/1/0693/2968/2543/files/IMG_8380_e0d764f2-b8ca-46e2-a524-0c5b31c02f15.jpg"


def font_path(file):
    pkg = file.split("-latin-")[0]
    return NPM / "@fontsource" / pkg / "files" / file


def icon_path(name):
    return NPM / "lucide-static" / "icons" / f"{name}.svg"


def ensure_logos():
    """Logo Spark Auto (fond transparent, noir et blanc) généré depuis le logo de la boutique."""
    if (BRAND / "logo_white.png").exists():
        return
    import io, urllib.request
    import numpy as np
    from PIL import Image
    BRAND.mkdir(parents=True, exist_ok=True)
    raw = urllib.request.urlopen(urllib.request.Request(LOGO_URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
    a = np.asarray(Image.open(io.BytesIO(raw)).convert("L")).astype(float)
    alpha = (np.clip((225 - a) / 185, 0, 1) * 255).astype("uint8")
    for col, name in [((0, 0, 0), "logo_black.png"), ((255, 255, 255), "logo_white.png")]:
        out = np.zeros(alpha.shape + (4,), dtype="uint8")
        out[..., 0], out[..., 1], out[..., 2], out[..., 3] = col[0], col[1], col[2], alpha
        img = Image.fromarray(out, "RGBA")
        img.crop(img.getbbox()).save(BRAND / name)

BADGE_TXT = "+300 modèles / 40 marques"

# Contexte de l'ad en cours (véhicule + photos), fixé par run.py avant chaque rendu
CTX = {"v": None, "photos": [], "promo": None}


def _ff(family, file, weight, style="normal"):
    return (f"@font-face{{font-family:'{family}';src:url('file://{font_path(file)}') format('woff2');"
            f"font-weight:{weight};font-style:{style};font-display:block}}")


FONT_CSS = "\n".join(
    [_ff("Inter", f"inter-latin-{w}-normal.woff2", w) for w in (400, 500, 600, 700, 800, 900)]
    + [_ff("Inter", f"inter-latin-{w}-italic.woff2", w, "italic") for w in (400, 700, 800, 900)]
    + [_ff("Anton", "anton-latin-400-normal.woff2", 400),
       _ff("Archivo Black", "archivo-black-latin-400-normal.woff2", 400),
       _ff("Permanent Marker", "permanent-marker-latin-400-normal.woff2", 400)]
    + [_ff("Caveat", f"caveat-latin-{w}-normal.woff2", w) for w in (500, 600, 700)]
    + [_ff("Kalam", f"kalam-latin-{w}-normal.woff2", w) for w in (400, 700)]
    + [_ff("Playfair Display", f"playfair-display-latin-{w}-normal.woff2", w) for w in (500, 600, 700, 800, 900)]
    + [_ff("Playfair Display", f"playfair-display-latin-{w}-italic.woff2", w, "italic") for w in (500, 700)]
    + [_ff("JetBrains Mono", f"jetbrains-mono-latin-{w}-normal.woff2", w) for w in (400, 500, 700, 800)]
    + [_ff("Oswald", f"oswald-latin-{w}-normal.woff2", w) for w in (500, 600, 700)]
)

BASE_CSS = FONT_CSS + """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:var(--w);height:var(--h);overflow:hidden}
body{font-family:'Inter',sans-serif;-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}
.ad{position:relative;width:var(--w);height:var(--h);overflow:hidden}
.shot{display:block;object-fit:cover}
.ph,.card,.c,.R,.so,.bx{position:relative}
.b250{display:inline-flex;align-items:center;gap:12px;font-family:'Inter';font-weight:800;letter-spacing:-.2px;white-space:nowrap}
.b250 svg{flex:none}
.hdr{position:absolute;left:0;right:0;z-index:30;display:flex;justify-content:center;pointer-events:none}
.vchip{position:absolute;left:16px;bottom:16px;z-index:5;display:inline-flex;align-items:center;gap:8px;background:rgba(10,10,12,.78);color:#fff;
  font:700 21px Inter;letter-spacing:-.1px;padding:9px 15px;border-radius:999px;white-space:nowrap;-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px)}
.vchip i{font-style:normal;font-weight:500;opacity:.75}
"""

# Ajuste automatiquement la taille des textes marqués .fit pour qu'ils tiennent dans leur boîte
FIT_JS = """
<script>
// Cadrage des photos : l'écran CarPlay (rectangle data-sb, en fractions de la photo) est toujours entier et
// centré, avec le plus de recul possible (on voit le tableau de bord). Si le cadre est trop étroit pour
// montrer l'écran entier, la photo dézoome et le fond est rempli par la même photo floutée.
const imgs=[...document.querySelectorAll('img.shot[data-fx]')];
// bords de la photo adoucis sur 3 % seulement : l'écran (parfois proche du bord de la photo) reste net
const FEATHER='linear-gradient(90deg,transparent,#000 3%,#000 97%,transparent),linear-gradient(180deg,transparent,#000 3%,#000 97%,transparent)';
Promise.all([document.fonts.ready, ...imgs.map(i=>i.decode().catch(()=>{}))]).then(()=>{
  imgs.forEach(img=>{
    const cw=img.clientWidth, ch=img.clientHeight, nw=img.naturalWidth, nh=img.naturalHeight;
    if(!cw||!ch||!nw||!nh) return;
    const sb=(img.dataset.sb||'').split(',').map(Number);
    const has=sb.length===4 && sb.every(x=>!isNaN(x));
    const [x0,y0,x1,y1]=has?sb:[+img.dataset.fx/100,+img.dataset.fy/100,+img.dataset.fx/100,+img.dataset.fy/100];
    const bw=(x1-x0)*nw, bh=(y1-y0)*nh, m=0.06;
    // zone où l'écran doit tenir : marge de 6 % + zones réservées (data-safe = haut,droite,bas,gauche en px)
    const sf=(img.dataset.safe||'0,0,0,0').split(',').map(Number);
    let mt=Math.max(m*ch,sf[0]), mr=Math.max(m*cw,sf[1]), mb=Math.max(m*ch,sf[2]), ml=Math.max(m*cw,sf[3]);
    // la pastille véhicule du même cadre ne doit pas recouvrir l'écran : on réserve sa bande
    const fr=img.parentElement;
    if(fr.querySelectorAll('img.shot').length===1){
      const chip=fr.querySelector('.vchip');
      if(chip && chip.offsetHeight){
        let y=0, el=chip; while(el && el!==fr){ y+=el.offsetTop; el=el.offsetParent; }
        if(el===fr){ if(y+chip.offsetHeight/2>ch/2) mb=Math.max(mb,ch-y+8); else mt=Math.max(mt,y+chip.offsetHeight+8); }
      }
    }
    if(cw-ml-mr<cw*0.4){ ml=mr=m*cw; } if(ch-mt-mb<ch*0.3){ mt=mb=m*ch; }
    const sCover=Math.max(cw/nw, ch/nh);
    const sFit=has?Math.min((cw-ml-mr)/bw, (ch-mt-mb)/bh):Infinity;
    const s=Math.min(sCover, sFit), w=nw*s, h=nh*s;
    const cx=(x0+x1)/2*w, cy=(y0+y1)/2*h;
    // point visé : (tx,ty) s'il est imposé, sinon le centre de la zone libre
    const gx=img.dataset.tx?cw*parseFloat(img.dataset.tx):ml+(cw-ml-mr)/2;
    const gy=img.dataset.ty?ch*parseFloat(img.dataset.ty):mt+(ch-mt-mb)/2;
    // position : l'écran dans sa zone (priorité absolue), et si possible la photo sans vide autour
    const place=(o,lo,hi,len,full)=>{
      if(lo>hi){ lo=hi=(lo+hi)/2; }
      const A=full>=len?len-full:0, B=full>=len?0:len-full, L=Math.max(lo,A), H=Math.min(hi,B);
      return L<=H ? Math.max(L,Math.min(H,o)) : Math.max(lo,Math.min(hi,o));
    };
    const ox=place(gx-cx, ml-x0*w, cw-mr-x1*w, cw, w);
    const oy=place(gy-cy, mt-y0*h, ch-mb-y1*h, ch, h);
    const covers=s>=sCover-1e-6 && ox<=0.5 && oy<=0.5 && ox+w>=cw-0.5 && oy+h>=ch-0.5;
    if(covers){
      img.style.objectPosition=ox+'px '+oy+'px';
      img.dataset.mode='cover';
    } else {
      // l'image ne couvre plus le cadre : on garde l'écran entier et on comble avec un fond flou
      const bg=document.createElement('div');
      bg.className='shotbg';
      bg.style.cssText=`position:absolute;inset:-40px;background:url("${img.src}") center/cover;filter:blur(28px) brightness(.55)`;
      img.parentNode.insertBefore(bg,img);
      const pcs=getComputedStyle(img.parentNode);
      if(pcs.position==='static') img.parentNode.style.position='relative';
      if(pcs.overflow==='visible') img.parentNode.style.overflow='hidden';
      for(const [k,v] of Object.entries({position:'absolute',left:ox+'px',top:oy+'px',width:w+'px',height:h+'px',
          'max-width':'none','object-fit':'fill',
          '-webkit-mask-image':FEATHER,'mask-image':FEATHER,'-webkit-mask-composite':'source-in','mask-composite':'intersect'}))
        img.style.setProperty(k,v,'important');
      img.dataset.mode='fit';
    }
    img.style.transformOrigin=(ox+cx)+'px '+(oy+cy)+'px';
    // part de l'écran visible dans le cadre (contrôle qualité)
    const L=Math.max(0,ox+x0*w), T=Math.max(0,oy+y0*h), R=Math.min(cw,ox+x1*w), B=Math.min(ch,oy+y1*h);
    img.dataset.vis=has?(Math.max(0,R-L)*Math.max(0,B-T)/((x1-x0)*w*(y1-y0)*h)).toFixed(3):'';
    // rectangle de l'écran, relatif au cadre (pour le contrôle d'occultation)
    if(has) img.dataset.scr=[ox+x0*w,oy+y0*h,ox+x1*w,oy+y1*h].map(v=>v.toFixed(1)).join(',');
  });
  document.querySelectorAll('.fit').forEach(el=>{
    let fs=parseFloat(getComputedStyle(el).fontSize), min=fs*0.55;
    const maxH=parseFloat(el.dataset.h||0);
    const over=()=> el.scrollWidth>el.clientWidth+1 || (maxH && el.scrollHeight>maxH+1);
    while(over() && fs>min){ fs-=1; el.style.fontSize=fs+'px'; }
  });
  document.body.dataset.ready='1';
});
</script>
"""


def photo(i=0):
    ph = CTX["photos"]
    return ph[i % len(ph)]


def focus(i=0, tx=None, ty=None, safe=None):
    """Attributs data-* : le JS centre automatiquement l'écran CarPlay de la photo dans son cadre."""
    fs = CTX.get("focus") or []
    fx, fy = fs[i % len(fs)] if fs else (50, 40)
    sbs = CTX.get("screens") or []
    sb = sbs[i % len(sbs)] if sbs else None
    if sb:  # rectangle de l'écran connu : on vise son centre
        fx, fy = round((sb[0] + sb[2]) * 50), round((sb[1] + sb[3]) * 50)
    extra = (f' data-tx="{tx}"' if tx is not None else "") + (f' data-ty="{ty}"' if ty is not None else "")
    extra += f' data-sb="{",".join(str(x) for x in sb)}"' if sb else ""
    extra += f' data-safe="{",".join(str(x) for x in safe)}"' if safe else ""  # zones réservées (px) : haut, droite, bas, gauche
    return f'data-fx="{fx}" data-fy="{fy}"{extra}'


def V(key="name"):
    v = CTX["v"] or {}
    return v.get(key) or ""


def chip(extra_style="", years=True, which=0):
    vs = CTX.get("vehicles") or [CTX["v"]]
    v = vs[which % len(vs)] if vs else None
    if not v:
        return ""
    yrs = f" <i>· {v['years']}</i>" if (years and v.get("years")) else ""
    return f'<div class="vchip" style="{extra_style}">{v["name"]}{yrs}</div>'


def logo_src(color):
    return f"file://{BRAND / ('logo_' + color + '.png')}"


def icon(name, size=40, color="currentColor", stroke=2):
    s = icon_path(name).read_text()
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S).strip()
    s = re.sub(r'width="\d+"', f'width="{size}"', s, count=1)
    s = re.sub(r'height="\d+"', f'height="{size}"', s, count=1)
    s = s.replace('stroke="currentColor"', f'stroke="{color}"')
    s = re.sub(r'stroke-width="[\d.]+"', f'stroke-width="{stroke}"', s, count=1)
    return s


def badge(theme="dark", size=26, pad="14px 24px", bg=None, fg=None):
    """Badge catalogue obligatoire sur chaque visuel."""
    bg = bg or ("#0B0B0C" if theme == "dark" else "#FFFFFF")
    fg = fg or ("#FFFFFF" if theme == "dark" else "#0B0B0C")
    return (f'<div class="b250" style="background:{bg};color:{fg};font-size:{size}px;padding:{pad};border-radius:999px">'
            f'{icon("car", int(size * 1.25), fg, 2.2)}<span>{BADGE_TXT}</span></div>')


def header(color="black", top=40, h=44):
    """En-tête de la charte : logo Spark Auto seul, en haut au centre (blanc, noir ou gris)."""
    return f'<div class="hdr" style="top:{top}px">{logo(color, h)}</div>'


def logo(color="black", h=46, style=""):
    return f'<img src="{logo_src(color)}" style="height:{h}px;width:auto;display:block;{style}">'


def page(body, css, w=1080, h=1350):
    # espaces insécables avant ? : ! ; (typographie française)
    body = re.sub(r" ([?:!;])", r"&nbsp;\1", body)
    return (f"<!doctype html><html lang='fr'><head><meta charset='utf-8'><style>:root{{--w:{w}px;--h:{h}px}}"
            f"{BASE_CSS}{css}</style></head><body><div class='ad'>{body}</div>{FIT_JS}</body></html>")


class Renderer:
    def __init__(self, workdir):
        from playwright.sync_api import sync_playwright
        self.workdir = Path(workdir).resolve()
        self.workdir.mkdir(parents=True, exist_ok=True)
        ensure_logos()
        self._pw = sync_playwright().start()
        import os
        exe = os.environ.get("CHROME_PATH") or None
        self.browser = self._pw.chromium.launch(executable_path=exe, args=["--allow-file-access-from-files"])

    def render(self, html, out_png, w=1080, h=1350, check=None):
        """Rend la page en PNG. Si check est fourni, check(page, w, h) est appelé et son résultat renvoyé."""
        f = self.workdir / (Path(out_png).stem + ".html")
        f.write_text(html, encoding="utf-8")
        pg = self.browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        try:
            pg.goto(f"file://{f}")
            pg.wait_for_load_state("networkidle")
            pg.wait_for_function("document.body.dataset.ready==='1'", timeout=20000)
            pg.wait_for_timeout(200)
            pg.screenshot(path=str(out_png), clip={"x": 0, "y": 0, "width": w, "height": h})
            return check(pg, w, h) if check else None
        finally:
            pg.close()

    def close(self):
        self.browser.close()
        self._pw.stop()
