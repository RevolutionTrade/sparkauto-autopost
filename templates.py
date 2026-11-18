"""Les 24 templates de static ads Spark Auto (format 1080x1350).
Chaque template utilise la photo du véhicule du jour (photo(0)), son nom (V('name')) et une puce véhicule (chip()).
"""
import math, random
from datetime import date
from core import photo, chip, focus, V, CTX, icon, badge, logo, header, page, BADGE_TXT



def ad01_jauge():
    W, H = 1080, 1350
    cx, cy, r = 400, 400, 300
    def pt(val, rr):
        th = math.radians(180 - val * 180)
        return cx + rr * math.cos(th), cy - rr * math.sin(th)
    ticks = ""
    for i in range(0, 21):
        v = i / 20
        x1, y1 = pt(v, r - 52)
        x2, y2 = pt(v, r - (66 if i % 5 == 0 else 60))
        ticks += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#9a9aa2" stroke-width="{4 if i%5==0 else 2}" stroke-linecap="round"/>'
    nx, ny = pt(0.9, 236)
    tx, ty = pt(0.9, -34)
    svg = f'''<svg width="800" height="470" viewBox="0 0 800 470">
      <defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="0">
        <stop offset="0" stop-color="#E0352B"/><stop offset=".45" stop-color="#F6A623"/><stop offset=".75" stop-color="#9AD13B"/><stop offset="1" stop-color="#1FB257"/></linearGradient>
        <filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-opacity=".25"/></filter></defs>
      <path d="M {cx-r} {cy} A {r} {r} 0 0 1 {cx+r} {cy}" fill="none" stroke="#d9d9de" stroke-width="74" stroke-linecap="butt"/>
      <path d="M {cx-r} {cy} A {r} {r} 0 0 1 {cx+r} {cy}" fill="none" stroke="url(#g)" stroke-width="64" stroke-linecap="butt"/>
      {ticks}
      <g filter="url(#sh)"><line x1="{tx:.1f}" y1="{ty:.1f}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="#16161a" stroke-width="16" stroke-linecap="round"/>
      <circle cx="{cx}" cy="{cy}" r="34" fill="#16161a"/><circle cx="{cx}" cy="{cy}" r="12" fill="#5b5b62"/></g>
    </svg>'''
    css = """
    .ad{background:radial-gradient(120% 80% at 50% 25%,#FAFAFB 0%,#E9E9EC 60%,#DCDCE0 100%)}
    .t{position:absolute;top:124px;width:100%;text-align:center;font-family:'Archivo Black';font-size:72px;letter-spacing:-1.5px;color:#111;line-height:1}
    .s{position:absolute;top:212px;width:100%;text-align:center;font:500 34px Inter;color:#55555c}
    .g{position:absolute;top:262px;left:140px}
    .lab{position:absolute;font:800 22px Inter;letter-spacing:1.5px;text-transform:uppercase;text-align:center;line-height:1.15}
    .mid{position:absolute;top:470px;width:100%;text-align:center;font:700 28px Inter;color:#111}
    .mid span{font-family:'Archivo Black';font-size:34px;letter-spacing:.5px}
    .card{position:absolute;left:90px;top:744px;width:900px;height:452px;border-radius:30px;overflow:hidden;box-shadow:0 30px 60px -20px rgba(0,0,0,.45),0 0 0 6px #fff}
    .card img{width:100%;height:100%;object-position:50% 38%}
    .tag{position:absolute;left:50%;transform:translateX(-50%);top:722px;white-space:nowrap;z-index:3;box-shadow:0 8px 20px rgba(31,178,87,.4);background:#1FB257;color:#fff;font:800 22px Inter;letter-spacing:1px;padding:10px 18px;border-radius:999px;text-transform:uppercase}
    .ft{position:absolute;bottom:56px;width:100%;display:flex;justify-content:center;align-items:center;gap:26px}
    """
    body = f'''{header('black', 40)}
    <div class="t">NIVEAU DE MODERNITÉ</div>
    <div class="s">de votre tableau de bord</div>
    <div class="g">{svg}</div>
    <div class="lab" style="left:92px;top:676px;width:200px;color:#C9322A">Autoradio<br>CD</div>
    <div class="lab" style="left:440px;top:460px;width:200px;color:#B9770E">Support<br>téléphone</div>
    <div class="lab" style="left:788px;top:676px;width:200px;color:#178A44">CarPlay<br>sans fil</div>
    <div class="card"><img class="shot" src="{photo(0)}" {focus(0)}>{chip()}</div>
    <div class="tag">Avec un écran Spark Auto</div>
    <div class="ft">{badge('dark', 25)}</div>
    '''
    return page(body, css, W, H)


def ad02_feu():
    W, H = 1080, 1350
    def lens(y, color, on, inner):
        glow = f"filter:drop-shadow(0 0 28px {color}) drop-shadow(0 0 60px {color});" if on else ""
        fill = color if on else "#262628"
        return (f'<div style="position:absolute;left:35px;top:{y}px;width:170px;height:170px;border-radius:50%;'
                f'background:radial-gradient(circle at 40% 35%,{"#fff8" if on else "#333"} 0%,{fill} 45%,{fill} 100%);{glow}'
                f'box-shadow:inset 0 -10px 20px rgba(0,0,0,.35);display:flex;align-items:center;justify-content:center">{inner}</div>')
    light = (f'<div style="position:absolute;left:96px;top:548px;width:240px;height:640px;border-radius:44px;'
             f'background:linear-gradient(180deg,#1d1d20,#111113);border:3px solid #2c2c30;box-shadow:0 40px 80px rgba(0,0,0,.6)">'
             + lens(28, "#FF3B30", True, icon("disc-3", 92, "#fff", 2.2))
             + lens(234, "#FFB020", False, "")
             + lens(440, "#30D158", True, icon("smartphone", 88, "#fff", 2.2))
             + "</div>")
    css = """
    .ad{background:radial-gradient(90% 60% at 50% 0%,#1a1a1d 0%,#0a0a0b 70%)}
    .h{position:absolute;top:130px;left:70px;right:40px;font-family:Anton;font-size:128px;line-height:1;color:#fff;letter-spacing:.5px;text-transform:uppercase}
    .h em{font-style:normal;color:#FF3B30}
    .s{position:absolute;top:436px;left:70px;right:120px;font:500 30px/1.35 Inter;color:#b8b8bd}
    .card{position:absolute;left:400px;top:588px;width:600px;height:548px;border-radius:30px;overflow:hidden;box-shadow:0 0 0 4px #30D158,0 0 60px rgba(48,209,88,.45)}
    .card img{width:100%;height:100%;object-position:50% 40%}
    .arrow{position:absolute;left:338px;top:1040px}
    .b{position:absolute;bottom:44px;left:70px;right:70px;display:flex;align-items:center;justify-content:space-between}
    .cta{font:900 36px Inter;color:#fff;letter-spacing:-.5px}
    .cta em{font-style:normal;color:#30D158}
    """
    arrow = '<svg class="arrow" width="70" height="40" viewBox="0 0 70 40"><path d="M4 20 H58 M44 6 L60 20 L44 34" fill="none" stroke="#30D158" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    body = f'''{header('white', 40)}
    <div class="h">Autoradio CD :<br><em>feu rouge.</em></div>
    <div class="s">CD rayé, pas de GPS, téléphone dans la grille d’aération : votre tableau de bord est à l’arrêt.</div>
    {light}{arrow}
    <div class="card"><img class="shot" src="{photo(0)}" {focus(0)}>{chip()}</div>
    <div class="b"><div class="cta">CarPlay sans fil : <em>feu vert.</em></div>{badge('light', 25)}</div>
    <div style="position:absolute;left:400px;top:1152px;width:600px;text-align:center;font:600 22px Inter;color:#8d8d93">CarPlay &amp; Android Auto sans fil · Spark Auto</div>
    '''
    return page(body, css, W, H)


def ad03_match():
    W, H = 1080, 1350
    ok = icon("check", 38, "#1FB257", 3.2)
    ko = icon("x", 38, "#E0352B", 3.2)
    rows = [
        ("Écran à la place de l’autoradio", ok, ko),
        ("CarPlay &amp; Android Auto sans fil", ok, ko),
        ("Commandes au volant conservées*", ok, ko),
        ("Caméra de recul compatible", ok, ko),
        ("Écran", "<b>HD tactile</b>", "<span>celui du<br>téléphone</span>"),
        ("Garantie", "<b>2 ans</b>", "<span>—</span>"),
    ]
    tr = "".join(f'<div class="r"><div class="c1">{a}</div><div class="c2">{b}</div><div class="c3">{c}</div></div>' for a, b, c in rows)
    css = """
    .ad{background:linear-gradient(165deg,#1b63d6 0%,#0d3f9a 55%,#0a2c70 100%)}
    .ad:before{content:"";position:absolute;inset:0;background:radial-gradient(60% 40% at 80% 10%,rgba(255,255,255,.18),transparent 70%)}
    .h{position:absolute;top:112px;width:100%;text-align:center;color:#fff;font-family:Anton;font-size:96px;letter-spacing:1px;line-height:1}
    .s{position:absolute;top:218px;width:100%;text-align:center;color:#d6e4ff;font:600 32px Inter}
    .tb{position:absolute;left:60px;right:60px;top:280px;background:rgba(255,255,255,.96);border-radius:30px;overflow:hidden;box-shadow:0 30px 70px rgba(0,0,0,.35)}
    .hd{display:flex;height:250px;border-bottom:2px solid #e6e8ee}
    .hd .c1{flex:1.25;display:flex;align-items:flex-end;padding:0 0 22px 32px;font:800 22px Inter;color:#8a90a0;letter-spacing:1.5px;text-transform:uppercase}
    .hd .c2{flex:1;background:#0B0B0C;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;padding:16px 16px 18px;gap:14px}
    .hd .c2 img{width:100%;height:150px;border-radius:14px;object-position:50% 40%}
    .hd .c2 div{color:#fff;font:900 24px Inter;letter-spacing:1px}
    .hd .c3{flex:.85;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;padding-bottom:18px;gap:18px;color:#6b7080}
    .hd .c3 div{font:800 22px Inter;letter-spacing:1px;text-align:center;line-height:1.15}
    .r{display:flex;height:100px;border-bottom:2px solid #eceef3;align-items:stretch}
    .r:last-child{border-bottom:0}
    .r .c1{flex:1.25;display:flex;align-items:center;padding:0 22px 0 32px;font:700 28px/1.2 Inter;color:#14161c}
    .r .c2{flex:1;display:flex;align-items:center;justify-content:center;background:#f2f6ff;font:800 30px Inter;color:#0B0B0C}
    .r .c3{flex:.85;display:flex;align-items:center;justify-content:center;font:600 22px/1.15 Inter;color:#7b8090;text-align:center}
    .r .c2 b{font-weight:900}
    .fn{position:absolute;left:60px;top:1162px;color:#bcd0ff;font:500 20px Inter}
    .ft{position:absolute;bottom:52px;left:60px;right:60px;display:flex;justify-content:flex-end;align-items:center}
    """
    body = f'''{header('white', 40)}
    <div class="h">LE VRAI MATCH</div>
    <div class="s">Écran Spark Auto vs support de téléphone</div>
    <div class="tb">
      <div class="hd"><div class="c1">Ce que vous obtenez</div>
        <div class="c2"><img class="shot" src="{photo(0)}" {focus(0)}><div>SPARK AUTO</div></div>
        <div class="c3">{icon('smartphone', 70, '#6b7080', 1.8)}<div>SUPPORT<br>TÉLÉPHONE</div></div></div>
      {tr}
    </div>
    <div class="fn">*sur les versions équipées · Photo : {V("name")}</div>
    <div class="ft">{badge('light', 25)}</div>
    '''
    return page(body, css, W, H)


def ad04_split():
    W, H = 1080, 1350
    illu = '''<svg width="420" height="520" viewBox="0 0 420 520">
      <g fill="#cfc7e3">
        <rect x="20" y="40" width="380" height="26" rx="13"/><rect x="20" y="90" width="380" height="26" rx="13"/>
        <rect x="20" y="140" width="380" height="26" rx="13"/><rect x="20" y="190" width="380" height="26" rx="13"/>
      </g>
      <rect x="196" y="120" width="28" height="70" rx="6" fill="#55506a"/>
      <g transform="rotate(-9 210 250)">
        <rect x="112" y="150" width="196" height="330" rx="34" fill="#1b1a22"/>
        <rect x="124" y="166" width="172" height="298" rx="24" fill="#eef1f6"/>
        <path d="M140 420 C 170 380, 190 360, 230 330 S 270 260, 280 210" stroke="#3B82F6" stroke-width="10" fill="none" stroke-linecap="round"/>
        <circle cx="280" cy="210" r="14" fill="#E0352B"/><circle cx="140" cy="420" r="11" fill="#3B82F6"/>
        <rect x="104" y="250" width="22" height="80" rx="6" fill="#55506a"/><rect x="294" y="250" width="22" height="80" rx="6" fill="#55506a"/>
      </g>
      <path d="M232 488 C 236 510, 200 515, 170 500 S 90 470, 60 515" stroke="#2a2836" stroke-width="9" fill="none" stroke-linecap="round"/>
    </svg>'''
    ko = lambda t: f'<div class="li">{icon("x", 30, "#E0352B", 3)}<span>{t}</span></div>'
    okk = lambda t: f'<div class="li">{icon("check", 30, "#30D158", 3.2)}<span>{t}</span></div>'
    css = """
    .ad{background:#0B0B0C}
    .L{position:absolute;left:0;top:112px;width:540px;height:1078px;background:linear-gradient(180deg,#F3EFFA,#E4DCF3)}
    .R{position:absolute;left:540px;top:112px;width:540px;height:1078px;overflow:hidden;background:#111}
    .R img{width:100%;height:100%;object-position:50% 40%}
    .R:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,0) 61%,rgba(0,0,0,.9) 67%)}
    .pill{position:absolute;top:40px;background:#fff;border-radius:26px;padding:22px 30px;font:800 34px Inter;color:#14121a;box-shadow:0 14px 30px rgba(40,20,80,.15);letter-spacing:-.5px;z-index:2}
    .il{position:absolute;left:60px;top:180px}
    .cap{position:absolute;left:52px;right:40px;top:730px;z-index:2}
    .cap h3{font:900 40px Inter;letter-spacing:-.8px;margin-bottom:22px}
    .li{display:flex;gap:14px;align-items:center;font:600 28px Inter;margin:0 0 14px}
    .vs{position:absolute;left:540px;top:600px;transform:translate(-50%,-50%);width:110px;height:110px;border-radius:50%;background:#0B0B0C;color:#fff;font:900 36px Inter;display:flex;align-items:center;justify-content:center;border:6px solid #fff;z-index:3}
    .F{position:absolute;left:0;bottom:0;width:1080px;height:160px;background:#0B0B0C;display:flex;align-items:center;justify-content:space-between;padding:0 56px}
    """
    body = f'''{header('white', 34)}
    <div class="L"><div class="pill" style="left:52px">La fausse<br>bonne idée</div><div class="il">{illu}</div>
      <div class="cap" style="color:#1d1a26"><h3>Support téléphone</h3>{ko("Tombe dans les virages")}{ko("Câble qui traîne")}{ko("Petit écran, hors de vue")}</div></div>
    <div class="R"><img class="shot" src="{photo(0)}" {focus(0, safe=(0, 0, 428, 66))}>{chip("left:52px;bottom:auto;top:200px")}<div class="pill" style="left:52px">La vraie<br>solution</div>
      <div class="cap" style="color:#fff"><h3>Écran CarPlay intégré</h3>{okk("Sans fil, connexion auto")}{okk("À la place de l’autoradio")}{okk("Écran tactile HD")}</div></div>
    <div class="vs">VS</div>
    <div class="F" style="justify-content:center">{badge('light', 25)}</div>
    '''
    return page(body, css, W, H)


def ad05_maj():
    W, H = 1080, 1350
    css = """
    .ad{background:radial-gradient(80% 50% at 50% 62%,#2a0d0c 0%,#070707 65%)}
    .ic{position:absolute;top:112px;width:100%;display:flex;justify-content:center}
    .t{position:absolute;top:222px;width:100%;text-align:center;font:900 66px Inter;color:#FF3B30;letter-spacing:.5px}
    .p1{position:absolute;top:316px;left:90px;right:90px;text-align:center;font:700 40px/1.25 Inter;color:#fff;letter-spacing:-.5px}
    .p1 em{font-style:normal;color:#FF3B30}
    .p2{position:absolute;top:434px;left:120px;right:120px;text-align:center;font:500 29px/1.4 Inter;color:#b9b9be}
    .card{position:absolute;left:90px;top:572px;width:900px;height:548px;border-radius:30px;overflow:hidden;box-shadow:0 0 0 3px rgba(255,255,255,.12),0 40px 90px rgba(0,0,0,.7)}
    .card img{width:100%;height:100%;object-position:50% 45%}
    .ft{position:absolute;bottom:58px;left:90px;right:90px;display:flex;justify-content:center;align-items:center}
    """
    body = f'''{header('white', 40)}
    <div class="ic">{icon('triangle-alert', 92, '#FF3B30', 2)}</div>
    <div class="t">MISE À JOUR IMPORTANTE</div>
    <div class="p1"><span class="fit" style="display:block;white-space:nowrap">Votre {V("name")} peut avoir CarPlay sans fil.</span><em>Sans changer de voiture.</em></div>
    <div class="p2">Écran tactile HD installé à la place de l’autoradio d’origine. Plug &amp; play, en 20 minutes environ.</div>
    <div class="card"><img class="shot" src="{photo(0)}" {focus(0)}>{chip()}</div>
    <div class="ft">{badge('light', 25)}</div>
    '''
    return page(body, css, W, H)




def ad08_officiel():
    W, H = 1080, 1350
    css = """
    .ad{background:#FAFAF7}
    .lg{position:absolute;left:64px;top:62px}
    .h{position:absolute;left:64px;right:40px;top:136px;font-family:'Archivo Black';font-size:88px;line-height:1.02;color:#0B0B0C;letter-spacing:-2px}
    .c{position:absolute;left:64px;width:478px;top:410px;font:400 32px/1.45 Inter;color:#34343a}
    .c p{margin-bottom:34px}
    .c b{font-weight:800;color:#0B0B0C}
    .ph{position:absolute;left:574px;top:400px;width:506px;height:950px;border-radius:34px 0 0 0;overflow:hidden}
    .ph img{width:100%;height:100%;object-position:52% 50%}
    .f{position:absolute;left:64px;bottom:64px}
    """
    body = f'''{header('black', 40)}
        <div class="h">C’EST OFFICIEL :<br>C’EST FINI.</div>
    <div class="c">
      <p>Le support qui tombe au premier virage. Le câble qui traîne. Le GPS qu’on ne met plus à jour.</p>
      <p>Votre voiture passe à CarPlay et Android Auto sans fil, sur un écran HD installé à la place de l’autoradio d’origine.</p>
      <p><b>Sans changer de voiture.</b></p>
    </div>
    <div class="ph"><img class="shot" src="{photo(0)}" {focus(0)}>{chip()}</div>
    <div class="f">{badge('dark', 25)}</div>
    '''
    return page(body, css, W, H)


def ad09_communique():
    W, H = 1080, 1350
    css = """
    .ad{background:#E7E1D7}
    .card{position:absolute;left:70px;right:70px;top:118px;bottom:52px;background:#fff;border-radius:16px;box-shadow:0 30px 60px rgba(60,40,20,.18);padding:46px 60px 40px;text-align:center;display:flex;flex-direction:column;justify-content:space-between;align-items:center}
    .h{font:900 43px/1.15 Inter;color:#0B0B0C;letter-spacing:.2px;text-transform:uppercase}
    .b{font:400 26px/1.5 Inter;color:#2a2a2e}
    .b p{margin-bottom:14px}
    .b b{font-weight:800;color:#0B0B0C}
    .sig{font:800 25px Inter;color:#0B0B0C;margin-top:4px}
    .ph{width:100%;height:300px;border-radius:14px;overflow:hidden;flex:none}
    .ph img{width:100%;height:100%;object-position:50% 46%}
    .f{display:flex;justify-content:center}
    """
    body = f'''{header('black', 40)}
    <div class="card">
      <div class="h">Communiqué officiel<br>à tous ceux qui roulent encore avec le téléphone dans la grille d’aération</div>
      <div class="b">
        <p><b>On aurait dû vous le dire plus tôt.</b></p>
        <p>Votre voiture n’est pas trop vieille pour CarPlay. Son autoradio, si.</p>
        <p>Nos écrans s’installent à l’emplacement exact du poste d’origine, sans découpe ni soudure. CarPlay et Android Auto sans fil, reconnexion automatique à chaque démarrage.</p>
        <p><b>Garantie 2 ans. Aide 7j/7 sur WhatsApp.</b></p>
      </div>
      <div class="sig">L’équipe Spark Auto</div>
      <div class="ph"><img class="shot" src="{photo(0)}" {focus(0)}>{chip()}</div>
      <div class="f">{badge('dark', 24)}</div>
    </div>
    '''
    return page(body, css, W, H)


def ad10_raisons():
    W, H = 1080, 1350
    items = ["Vous pensiez qu’il fallait changer de voiture.",
             "Vous pensiez que l’installation était compliquée.",
             "Vous ne saviez pas que votre modèle était compatible."]
    lis = "".join(f'<div class="it"><div class="n">{i+1}.</div><div class="tx">{t}</div></div>' for i, t in enumerate(items))
    css = """
    .ad{background:#F3F3F1}
    .h{position:absolute;top:116px;width:100%;text-align:center;font:900 104px Inter;letter-spacing:-4px;color:#0B0B0C;line-height:1}
    .s{position:absolute;top:234px;left:120px;right:120px;text-align:center;font:600 38px/1.22 Inter;color:#0B0B0C;letter-spacing:-.5px}
    .l{position:absolute;top:354px;left:110px;right:110px}
    .it{display:flex;gap:26px;align-items:center;padding:24px 0;border-bottom:2px solid #d8d8d4}
    .it:last-child{border-bottom:0}
    .n{font:900 52px Inter;color:#0B0B0C;width:54px}
    .tx{font:500 32px/1.3 Inter;color:#26262b}
    .p{position:absolute;left:0;right:0;bottom:0;height:560px;background:linear-gradient(135deg,#0d2f6b,#1c5fc4);display:flex;align-items:center;padding:0 56px;gap:44px}
    .pt{flex:1;color:#fff}
    .pt h4{font:800 38px/1.2 Inter;letter-spacing:-.5px}
    .pt p{font:500 27px/1.4 Inter;color:#cfe0ff;margin:16px 0 26px}
    .cta{display:inline-block;margin-top:22px;background:#0B0B0C;color:#fff;font:800 24px Inter;letter-spacing:1px;padding:18px 26px;border-radius:10px}
    .ph{width:420px;height:440px;border-radius:26px;overflow:hidden;flex:none;box-shadow:0 20px 50px rgba(0,0,0,.35)}
    .ph img{width:100%;height:100%;object-position:50% 45%}
    """
    body = f'''{header('black', 40)}
    <div class="h">3 raisons</div>
    <div class="s fit" data-h="100">pour lesquelles votre {V("name")} n’a toujours pas CarPlay.</div>
    <div class="l">{lis}</div>
    <div class="p"><div class="pt"><h4>Un écran CarPlay &amp; Android Auto sans fil, conçu pour votre modèle.</h4>
      <p>Plug &amp; play, en 20 minutes environ.</p>{badge('light', 23)}<br><div class="cta">VÉRIFIER MA COMPATIBILITÉ</div></div>
      <div class="ph"><img class="shot" src="{photo(0)}" {focus(0)}>{chip()}</div></div>
    '''
    return page(body, css, W, H)


def ad11_venn():
    W, H = 1080, 1350
    ink = "#3E2A86"
    svg = f'''<svg width="1080" height="1350" viewBox="0 0 1080 1350" style="position:absolute;left:0;top:0">
      <path d="M 120 690 C 118 500, 250 372, 395 370 C 560 368, 680 510, 676 700 C 672 880, 545 1020, 392 1018 C 236 1016, 122 880, 120 690 Z" fill="none" stroke="{ink}" stroke-width="7" stroke-linecap="round"/>
      <path d="M 404 700 C 400 520, 520 372, 690 372 C 850 374, 962 510, 960 692 C 958 880, 836 1020, 684 1020 C 520 1020, 408 880, 404 700 Z" fill="none" stroke="{ink}" stroke-width="7" stroke-linecap="round"/>
      <path d="M 540 260 C 545 300, 538 330, 540 372" fill="none" stroke="{ink}" stroke-width="6" stroke-linecap="round"/>
      <path d="M 522 350 L 540 378 L 560 350" fill="none" stroke="{ink}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>'''
    css = f"""
    .ad{{background:#b9bec4}}
    .wb{{position:absolute;inset:22px;border-radius:10px;background:radial-gradient(120% 90% at 30% 20%,#ffffff 0%,#f4f5f6 55%,#e8eaec 100%);box-shadow:inset 0 0 0 4px #d5d9dd,inset 0 0 40px rgba(0,0,0,.06)}}
    .hw{{position:absolute;font-family:Caveat;color:{ink};line-height:1.02}}
    .box{{position:absolute;left:50%;transform:translateX(-50%);top:120px;border:6px solid {ink};border-radius:30px;padding:10px 40px 14px;font:700 64px Caveat;color:{ink};white-space:nowrap}}
    .ph{{position:absolute;left:400px;top:548px;width:280px;height:322px;background:#fff;padding:8px 8px 44px;transform:rotate(-3deg);box-shadow:0 18px 30px rgba(0,0,0,.28)}}
    .ph img{{width:100%;height:100%;object-position:50% 40%}}
    .ph span{{position:absolute;left:6px;right:6px;bottom:6px;text-align:center;font:700 28px Caveat;color:#333;white-space:nowrap;overflow:hidden}}
    .tape{{position:absolute;width:120px;height:38px;background:rgba(240,228,190,.85);transform:rotate(-8deg);left:478px;top:540px;box-shadow:0 2px 4px rgba(0,0,0,.1)}}
    .f{{position:absolute;bottom:80px;left:0;right:0;display:flex;justify-content:center;align-items:center;gap:26px}}
    """
    body = f'''{header('black', 46)}
    <div class="wb"></div>
    <div class="box">Le meilleur des deux mondes</div>
    {svg}
    <div class="hw" style="left:160px;top:560px;width:240px;font-size:62px;font-weight:700">La voiture que vous aimez</div>
    <div class="hw" style="left:190px;top:790px;width:205px;font-size:36px;font-weight:600">celle que vous ne voulez pas changer</div>
    <div class="hw" style="left:692px;top:540px;width:230px;font-size:58px;font-weight:700">La techno d’une voiture neuve</div>
    <div class="hw" style="left:694px;top:790px;width:205px;font-size:35px;font-weight:600">CarPlay, Android Auto, GPS, écran HD</div>
    <div class="ph"><img class="shot" src="{photo(0)}" {focus(0)}><span class="fit">{V("name")}</span></div><div class="tape"></div>
    <div class="hw" style="left:0;right:0;top:1050px;text-align:center;font-size:58px;font-weight:700">= un écran Spark Auto</div>
    <div class="f">{badge('dark', 25)}</div>
    '''
    return page(body, css, W, H)


def ad12_checklist():
    W, H = 1080, 1350
    ink = "#1B2A4A"
    box = f'<svg width="46" height="46" viewBox="0 0 46 46"><rect x="4" y="5" width="36" height="36" rx="4" fill="none" stroke="{ink}" stroke-width="3.5"/><path d="M11 23 L20 33 L42 4" fill="none" stroke="#1F7A3A" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    items = ["Fait pour votre modèle exact", "Installation sans découpe ni soudure", "Commandes au volant conservées*",
             "CarPlay <u>et</u> Android Auto sans fil", "Caméra de recul compatible", "Garantie 2 ans"]
    lis = "".join(f'<div class="it">{box}<span>{t}</span></div>' for t in items)
    css = f"""
    .ad{{background:linear-gradient(180deg,#d9d3c8,#cfc8bb)}}
    .wb{{position:absolute;left:60px;right:60px;top:56px;bottom:56px;background:linear-gradient(160deg,#fdfdfd,#f1f2f3);border:16px solid #c8ccd1;border-radius:8px;box-shadow:0 30px 60px rgba(0,0,0,.25)}}
    .t{{position:absolute;left:120px;right:110px;top:158px;font:700 56px/1.1 Kalam;color:{ink};text-transform:uppercase;letter-spacing:.5px}}
    .l{{position:absolute;left:120px;right:100px;top:318px}}
    .it{{display:flex;align-items:center;gap:22px;font:400 39px Kalam;color:{ink};margin-bottom:26px}}
    .it svg{{flex:none}}
    .ok{{position:absolute;left:120px;top:868px;width:420px;font:700 44px/1.1 Kalam;color:#1F7A3A}}
    .ph{{position:absolute;right:100px;top:820px;width:430px;height:330px;background:#fff;padding:14px 14px 50px;transform:rotate(3.5deg);box-shadow:0 18px 34px rgba(0,0,0,.28)}}
    .ph img{{width:100%;height:100%;object-position:50% 40%}}
    .ph span{{position:absolute;bottom:10px;left:10px;right:10px;text-align:center;font:700 28px Caveat;color:#333;white-space:nowrap;overflow:hidden}}
    .ar{{position:absolute;left:390px;top:992px}}
    .fn{{position:absolute;left:120px;top:1100px;font:400 24px Kalam;color:#55627d}}
    .f{{position:absolute;left:120px;bottom:110px;display:flex;align-items:center;gap:22px}}
    """
    arrow = f'<svg class="ar" width="150" height="80" viewBox="0 0 150 80"><path d="M6 40 C 40 70, 90 70, 132 34" fill="none" stroke="#1F7A3A" stroke-width="5" stroke-linecap="round"/><path d="M110 28 L134 32 L128 56" fill="none" stroke="#1F7A3A" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    body = f'''{header('black', 92)}
    <div class="wb"></div>
    <div class="t">Avant d’acheter un écran CarPlay, vérifiez :</div>
    <div class="l">{lis}</div>
    <div class="ok">Spark Auto coche toutes les cases.</div>{arrow}
    <div class="ph"><img class="shot" src="{photo(0)}" {focus(0)}><span class="fit">{V("name")}</span></div>
    <div class="fn">*sur les versions équipées</div>
    <div class="f">{badge('dark', 24)}</div>
    '''
    return page(body, css, W, H)


def ad13_etapes():
    W, H = 1080, 1350
    k = "#2a2a2a"
    s1 = f'''<svg width="260" height="300" viewBox="0 0 260 300" fill="none" stroke="{k}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
      <rect x="30" y="150" width="200" height="90" rx="10"/><rect x="60" y="168" width="140" height="10" rx="5"/>
      <circle cx="65" cy="212" r="14"/><circle cx="195" cy="212" r="14"/><rect x="100" y="200" width="60" height="22" rx="4"/>
      <path d="M130 130 V40"/><path d="M104 66 L130 38 L156 66"/>
      <path d="M40 275 h180" stroke-dasharray="6 10"/></svg>'''
    s2 = f'''<svg width="260" height="300" viewBox="0 0 260 300" fill="none" stroke="{k}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
      <rect x="22" y="120" width="86" height="64" rx="8"/><path d="M108 136 h20 M108 168 h20"/>
      <rect x="152" y="120" width="86" height="64" rx="8"/><path d="M152 136 h-14 M152 168 h-14"/>
      <path d="M65 184 C 65 240, 20 250, 20 290"/><path d="M195 184 C 195 240, 240 250, 240 290"/>
      <path d="M118 80 l12 -22 l12 22"/><path d="M130 58 V98" stroke-dasharray="4 8"/>
      <path d="M96 210 l14 14 l26 -30" stroke="#1F7A3A" stroke-width="5"/></svg>'''
    css = """
    .ad{background:#F7F2E8}
    .t{position:absolute;top:104px;width:100%;text-align:center;font:700 84px Caveat;color:#1d1d1d}
    .s{position:absolute;top:206px;width:100%;text-align:center;font:600 28px Inter;color:#6a6258;letter-spacing:.3px}
    .cards{position:absolute;top:276px;left:50px;right:50px;display:flex;gap:25px}
    .cd{flex:1;display:flex;flex-direction:column;align-items:center}
    .bx{width:100%;height:540px;background:#fff;border:2px solid #e5ddcf;border-radius:18px;display:flex;align-items:center;justify-content:center;overflow:hidden}
    .bx img{width:100%;height:100%;object-position:50% 40%}
    .cap{margin-top:22px;font:600 40px/1.05 Caveat;color:#222;text-align:center}
    .no{position:absolute;top:1000px;width:100%;text-align:center;font:700 52px Caveat;color:#1d1d1d}
    .sm{position:absolute;top:1078px;width:100%;text-align:center;font:500 25px Inter;color:#6a6258}
    .f{position:absolute;bottom:62px;left:0;right:0;display:flex;justify-content:center;align-items:center;gap:26px}
    """
    body = f'''{header('black', 40)}
    <div class="t">CarPlay en 3 étapes.</div>
    <div class="s">Plug &amp; play · 20 minutes environ</div>
    <div class="cards">
      <div class="cd"><div class="bx">{s1}</div><div class="cap">étape 1 :<br>on retire l’autoradio</div></div>
      <div class="cd"><div class="bx">{s2}</div><div class="cap">étape 2 :<br>on branche le faisceau</div></div>
      <div class="cd"><div class="bx" style="position:relative"><img class="shot" src="{photo(0)}" {focus(0)}>{chip("font-size:16px;left:10px;bottom:10px;padding:7px 11px", years=False)}</div><div class="cap">étape 3 :<br>CarPlay.</div></div>
    </div>
    <div class="no">pas de découpe. pas de soudure. réversible.</div>
    <div class="sm">Cadre, faisceau et outils de démontage fournis</div>
    <div class="f">{badge('dark', 25)}</div>
    '''
    return page(body, css, W, H)


def ad14_julien():
    W, H = 1080, 1350
    k = "#111"
    fig = f'''<svg width="360" height="560" viewBox="0 0 360 560" fill="none" stroke="{k}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="170" cy="90" r="46"/>
      <path d="M152 86 q6 -6 12 0 M186 86 q6 -6 12 0"/><path d="M158 118 q14 -10 28 0"/>
      <path d="M182 136 C 196 200, 200 250, 196 330"/>
      <path d="M190 190 C 150 220, 140 250, 168 268"/><path d="M192 196 C 230 228, 236 252, 204 270"/>
      <rect x="162" y="246" width="40" height="64" rx="8" fill="#fff"/><path d="M174 258 h16" />
      <path d="M196 330 C 180 400, 160 440, 130 500 l-30 6"/><path d="M196 330 C 220 400, 236 450, 250 500 l30 0"/>
      <path d="M70 40 q-14 -16 0 -30 q16 -12 26 6 q4 14 -10 20 q-8 4 -8 16" stroke-width="4"/><circle cx="78" cy="68" r="3" fill="{k}"/>
      <path d="M40 540 h300" stroke-dasharray="4 12" stroke-width="3"/></svg>'''
    css = """
    .ad{background:#fff}
    .fg{position:absolute;left:30px;top:112px}
    .tx{position:absolute;left:430px;right:56px;top:116px}
    .tx h2{font:900 56px Inter;letter-spacing:-1.5px;color:#0B0B0C;margin-bottom:22px}
    .tx p{font:400 32px/1.36 Inter;color:#1a1a1e;margin-bottom:24px}
    .tx p i{font-style:italic}
    .dl{position:absolute;left:470px;right:50px;top:850px;font:900 italic 60px/1.08 Inter;letter-spacing:-2px;color:#0B0B0C}
    .ph{position:absolute;left:44px;top:706px;width:380px;height:400px;border-radius:24px;overflow:hidden;transform:rotate(-2deg);box-shadow:0 20px 40px rgba(0,0,0,.25)}
    .ph img{width:100%;height:100%;object-position:50% 40%}
    .bar{position:absolute;left:0;right:0;bottom:0;height:150px;background:#FF5B1F;display:flex;align-items:center;justify-content:space-between;padding:0 48px}
    .bar > span{font:800 31px/1.2 Inter;color:#fff;letter-spacing:-.3px}
    """
    body = f'''{header('black', 40)}
    <div class="fg">{fig}</div>
    <div class="tx"><h2>Voici Julien.</h2>
      <p>Julien adore sa {V("name")}. <i>Vraiment.</i></p>
      <p>Mais son téléphone, coincé dans la grille d’aération, tombe à chaque rond-point.</p>
      <p>Julien pense qu’il faut changer de voiture pour avoir CarPlay.</p>
      <p>Pourtant, un écran sur mesure s’installe en 20 minutes environ, à la place de l’autoradio.</p></div>
    <div class="ph"><img class="shot" src="{photo(0)}" {focus(0)}>{chip()}</div>
    <div class="dl">Ne soyez pas<br>comme Julien.</div>
    <div class="bar"><span>Vérifiez votre modèle<br>sur sparkauto.fr</span>{badge('light', 25)}</div>
    '''
    return page(body, css, W, H)




def ad15_age():
    W, H = 1080, 1350
    stamp = '''<svg width="230" height="230" viewBox="0 0 230 230">
      <defs><path id="cp" d="M115,115 m-86,0 a86,86 0 1,1 172,0 a86,86 0 1,1 -172,0"/></defs>
      <circle cx="115" cy="115" r="110" fill="#FBE3E3" stroke="#D94848" stroke-width="5" stroke-dasharray="2 7" stroke-linecap="round"/>
      <circle cx="115" cy="115" r="62" fill="none" stroke="#D94848" stroke-width="3"/>
      <text font-family="Inter" font-weight="800" font-size="20" fill="#D94848"><textPath href="#cp" textLength="532" lengthAdjust="spacing">GARANTIE 2 ANS • AIDE 7J/7 • GARANTIE 2 ANS • AIDE 7J/7 •</textPath></text>
      <text x="115" y="132" text-anchor="middle" font-family="Archivo Black" font-size="48" fill="#D94848">2 ANS</text>
    </svg>'''
    css = """
    .ad{background:#ECECEE}
    .fr{position:absolute;inset:24px;border:2px solid #d4d4d8}
    .h{position:absolute;top:118px;left:70px;right:60px;font:600 76px/1.04 Inter;letter-spacing:-2.5px;color:#0B0B0C}
    .a{position:absolute;top:316px;left:70px;font:400 40px Inter;color:#3a3a40}
    .b{position:absolute;top:400px;left:70px;font:800 52px Inter;letter-spacing:-1.2px;color:#0B0B0C}
    .ph{position:absolute;left:70px;right:70px;top:510px;height:610px;border-radius:30px;overflow:hidden;box-shadow:0 30px 60px -20px rgba(0,0,0,.35)}
    .ph img{width:100%;height:100%;object-position:50% 45%}
    .st{position:absolute;right:30px;top:990px;transform:rotate(-12deg);filter:drop-shadow(0 8px 14px rgba(0,0,0,.18))}
    .f{position:absolute;left:70px;bottom:62px;display:flex;align-items:center;gap:26px}
    """
    body = f'''{header('black', 44)}
    <div class="fr"></div>
    <div class="h fit" data-h="170">{age_line()}</div>
    <div class="a">Avant : un autoradio CD.</div>
    <div class="b">Après : CarPlay sans fil.</div>
    <div class="ph"><img class="shot" src="{photo(0)}" {focus(0)}>{chip()}</div>
    <div class="st">{stamp}</div>
    <div class="f">{badge('dark', 25)}</div>
    '''
    return page(body, css, W, H)


def ad16_barre():
    W, H = 1080, 1350
    items = ["Le support qui tombe au premier virage", "Le câble qui traîne sur le levier de vitesse",
             "Le lecteur CD qui ne sert plus", "Le GPS jamais mis à jour"]
    lis = "".join(f'<div class="it">{t}</div>' for t in items)
    css = """
    .ad{background:#F1E6D3}
    .cd{position:absolute;inset:44px;background:#FBF4E8;border-radius:44px;box-shadow:inset 0 0 0 2px #ead9bd}
    .l{position:absolute;left:100px;right:90px;top:150px}
    .it{font:500 39px/1.25 'Playfair Display';color:#3b2b20;margin-bottom:22px;text-decoration:line-through;text-decoration-color:#C8102E;text-decoration-thickness:3px}
    .ph{position:absolute;left:150px;right:150px;top:486px;height:484px;border-radius:26px;overflow:hidden;box-shadow:0 24px 50px -16px rgba(80,50,20,.45)}
    .ph img{width:100%;height:100%;object-position:50% 40%}
    .t1{position:absolute;left:100px;top:1012px;font:700 62px 'Playfair Display';color:#C8102E;letter-spacing:-.5px}
    .t2{position:absolute;left:100px;top:1088px;font:500 52px 'Playfair Display';color:#2a1f18}
    .f{position:absolute;left:100px;right:100px;bottom:92px;display:flex;justify-content:flex-start;align-items:center}
    """
    body = f'''{header('black', 76)}
    <div class="cd"></div>
    <div class="l">{lis}</div>
    <div class="ph"><img class="shot" src="{photo(0)}" {focus(0)}>{chip()}</div>
    <div class="t1">CarPlay sans fil,</div>
    <div class="t2">sans changer de voiture.</div>
    <div class="f">{badge('dark', 24)}</div>
    '''
    return page(body, css, W, H)


def ad17_nachetez():
    W, H = 1080, 1350
    def arr(x, y, w, h, d, head):
        return (f'<svg style="position:absolute;left:{x}px;top:{y}px" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
                f'<path d="{d}" fill="none" stroke="#111" stroke-width="5" stroke-linecap="round"/>'
                f'<path d="{head}" fill="none" stroke="#111" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    css = """
    .ad{background:#FFD60A}
    .h{position:absolute;top:112px;width:100%;text-align:center;font-family:'Archivo Black';font-size:78px;line-height:1.02;color:#111;letter-spacing:-2px}
    .s{position:absolute;top:288px;width:100%;text-align:center;font:600 36px Oswald;letter-spacing:3px;color:#111}
    .ph{position:absolute;left:250px;top:532px;width:580px;height:420px;border-radius:28px;overflow:hidden;box-shadow:0 26px 50px -14px rgba(0,0,0,.45);border:6px solid #111}
    .ph img{width:100%;height:100%;object-position:50% 50%}
    .c{position:absolute;font:400 40px/1.05 'Permanent Marker';color:#111;text-align:center}
    .f{position:absolute;bottom:58px;left:0;right:0;display:flex;justify-content:center;align-items:center;gap:26px}
    """
    body = f'''{header('black', 40)}
    <div class="h">N’achetez pas<br>cet écran si…</div>
    <div class="s">VOUS NE VOULEZ PAS CES EFFETS SECONDAIRES</div>
    <div class="c" style="left:40px;top:372px;width:380px">Plus jamais<br>perdu</div>
    {arr(150, 468, 140, 110, "M30 6 C 30 50, 60 80, 120 96", "M96 78 L122 97 L96 108")}
    <div class="c" style="left:640px;top:372px;width:400px">Vos playlists<br>sur grand écran</div>
    {arr(760, 468, 140, 110, "M100 6 C 100 50, 70 80, 18 96", "M42 78 L16 97 L42 108")}
    <div class="ph"><img class="shot" src="{photo(0)}" {focus(0)}>{chip()}</div>
    {arr(150, 942, 140, 110, "M30 104 C 30 60, 60 30, 120 14", "M96 2 L122 14 L98 34")}
    <div class="c" style="left:30px;top:1058px;width:420px">Le téléphone<br>reste dans la poche</div>
    {arr(770, 942, 140, 110, "M100 104 C 100 60, 70 30, 18 14", "M42 2 L16 14 L40 34")}
    <div class="c" style="left:640px;top:1058px;width:400px">Un tableau de bord<br>comme neuf</div>
    <div class="f">{badge('dark', 25)}</div>
    '''
    return page(body, css, W, H)


def ad18_doigt():
    W, H = 1080, 1350
    items = [("smartphone", "Téléphone dans la grille d’aération", 1), ("cable", "Câble qui traîne", 1),
             ("map-pin", "Pas de GPS intégré", 0), ("disc-3", "Lecteur CD inutilisé", 1),
             ("bluetooth", "Pas de Bluetooth", 0), ("camera", "Pas de caméra de recul", 1),
             ("radio", "Écran d’autoradio minuscule", 0), ("music", "Pas de Spotify à l’écran", 0),
             ("navigation", "Pas de Waze à l’écran", 0)]
    cards = ""
    for ic, t, on in items:
        chk = f'<div class="ck">{icon("check", 22, "#fff", 3.4)}</div>' if on else ""
        cards += f'<div class="g {"on" if on else ""}">{icon(ic, 40, "#B0185C" if on else "#55555c", 1.9)}<span>{t}</span>{chk}</div>'
    css = """
    .ad{background:#fff}
    .h{position:absolute;left:66px;top:108px;font:700 74px 'Playfair Display';color:#111;letter-spacing:-1px}
    .s{position:absolute;left:68px;top:198px;font:500 italic 32px 'Playfair Display';color:#444}
    .gr{position:absolute;left:66px;right:66px;top:262px;display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
    .g{position:relative;height:168px;border:2px solid #e3e3e6;border-radius:18px;padding:20px 20px 18px;display:flex;flex-direction:column;justify-content:space-between;background:#fafafa}
    .g span{font:600 24px/1.2 Inter;color:#2a2a2e}
    .g.on{border:3px solid #B0185C;background:#FDF2F7}
    .ck{position:absolute;right:14px;top:14px;width:38px;height:38px;border-radius:50%;background:#B0185C;display:flex;align-items:center;justify-content:center}
    .q{position:absolute;left:66px;top:852px;width:520px;font:600 36px/1.2 'Playfair Display';color:#222}
    .q b{display:block;margin-top:14px;font:700 46px/1.1 'Playfair Display';color:#B0185C}
    .p2{position:absolute;left:606px;top:836px;width:410px;height:330px;border-radius:22px;overflow:hidden;box-shadow:0 20px 40px -10px rgba(0,0,0,.4);border:5px solid #fff;transform:rotate(3deg)}
    .p2 img{width:100%;height:100%}
    .f{position:absolute;left:66px;bottom:60px;display:flex;align-items:center;gap:24px}
    """
    body = f'''{header('black', 40)}
    <div class="h">Baissez un doigt</div>
    <div class="s">si votre voiture a plus de 10 ans</div>
    <div class="gr">{cards}</div>
    <div class="q">Vous avez baissé 3 doigts ou plus ?<b>C’est l’autoradio qu’il faut changer.</b></div>
    <div class="p2"><img class="shot" src="{photo(0)}" {focus(0)}>{chip("font-size:17px;padding:7px 12px;left:10px;bottom:10px", years=False)}</div>
    <div class="f">{badge('dark', 24)}</div>
    '''
    return page(body, css, W, H)


def ad19_affiche():
    W, H = 1080, 1350
    g = "#1F4D3A"
    sig = [("map-pin", "PAS DE GPS"), ("disc-3", "CD RAYÉ"), ("cable", "CÂBLE QUI<br>TRAÎNE"), ("smartphone", "TÉLÉPHONE<br>QUI TOMBE")]
    ics = "".join(f'<div class="i">{icon(a, 78, g, 1.8)}<span>{b}</span></div>' for a, b in sig)
    noise = '''<svg width="0" height="0" style="position:absolute"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="4" seed="7"/><feColorMatrix values="0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 .55 0"/></filter>
      <filter id="n2"><feTurbulence type="fractalNoise" baseFrequency=".012" numOctaves="3" seed="3"/><feColorMatrix values="0 0 0 0 .3  0 0 0 0 .3  0 0 0 0 .3  0 0 0 .35 0"/></filter></svg>'''
    css = f"""
    .ad{{background:#8e8f8c}}
    .cn,.cn2{{position:absolute;inset:0}}
    .tp{{position:absolute;width:150px;height:46px;background:rgba(236,230,214,.78);box-shadow:0 2px 3px rgba(0,0,0,.15)}}
    .po{{position:absolute;left:110px;top:90px;width:860px;height:1170px;background:linear-gradient(175deg,#fbfbf9,#efefeb);transform:rotate(-.7deg);box-shadow:0 26px 40px rgba(0,0,0,.35);padding:56px 56px 40px;text-align:center}}
    .plg{{display:flex;justify-content:center;margin:-12px 0 22px}}
    .t1{{font:700 74px/1 Oswald;color:{g};letter-spacing:.5px}}
    .t2{{font:700 50px/1.05 Oswald;color:{g};margin-top:14px}}
    .ic{{display:flex;justify-content:space-between;margin:30px 10px 0}}
    .i{{display:flex;flex-direction:column;align-items:center;gap:12px;width:170px}}
    .i span{{font:600 22px/1.1 Oswald;color:{g};letter-spacing:1px}}
    .ph{{margin:28px auto 0;width:700px;height:270px;border-radius:12px;overflow:hidden}}
    .ph img{{width:100%;height:100%;object-position:50% 42%}}
    .m{{font:600 33px/1.15 Oswald;color:{g};margin-top:30px;letter-spacing:.5px}}
    .bt{{display:inline-block;margin-top:24px;background:{g};color:#fff;font:600 30px Oswald;letter-spacing:1.5px;padding:16px 40px;border-radius:8px}}
    .f{{margin-top:26px;display:flex;justify-content:center}}
    """
    body = f'''{noise}
    <svg class="cn" width="1080" height="1350"><rect width="1080" height="1350" filter="url(#n2)"/></svg>
    <svg class="cn2" width="1080" height="1350"><rect width="1080" height="1350" filter="url(#n)"/></svg>
    <div class="po">
      <div class="plg">{logo('black', 40)}</div>
      <div class="t1">VOITURE DE PLUS<br>DE 10 ANS ?</div>
      <div class="t2">VOUS RECONNAISSEZ CES SIGNES ?</div>
      <div class="ic">{ics}</div>
      <div class="ph"><img class="shot" src="{photo(0)}" {focus(0)}>{chip()}</div>
      <div class="m">CE N’EST PAS VOTRE VOITURE QUI A VIEILLI.<br>C’EST SON AUTORADIO.</div>
      <div class="bt">VÉRIFIER MA COMPATIBILITÉ</div>
      <div class="f">{badge('dark', 23, bg=g)}</div>
    </div>
    <div class="tp" style="left:70px;top:76px;transform:rotate(-38deg)"></div>
    <div class="tp" style="left:870px;top:62px;transform:rotate(36deg)"></div>
    <div class="tp" style="left:76px;top:1226px;transform:rotate(36deg)"></div>
    <div class="tp" style="left:866px;top:1238px;transform:rotate(-38deg)"></div>
    '''
    return page(body, css, W, H)


def ad20_signes():
    W, H = 1080, 1350
    cx, cy, r = 540, 740, 262
    labels = [("smartphone", "TÉLÉPHONE DANS<br>LA GRILLE", -150, "L"), ("map-pin", "PAS DE GPS<br>INTÉGRÉ", -30, "R"),
              ("disc-3", "LECTEUR CD<br>INUTILE", 180, "L"), ("cable", "CÂBLE QUI<br>TRAÎNE", 0, "R"),
              ("bluetooth", "PAS DE<br>BLUETOOTH", 150, "L"), ("camera", "PAS DE CAMÉRA<br>DE RECUL", 30, "R")]
    dots, labs = "", ""
    for ic, t, ang, side in labels:
        a = math.radians(ang)
        px, py = cx + (r + 10) * math.cos(a), cy + (r + 10) * math.sin(a)
        lx = 60 if side == "L" else 800
        ly = py - 50
        ex = 270 if side == "L" else 810
        dots += f'<circle cx="{px:.0f}" cy="{py:.0f}" r="9" fill="#FF3B30"/><line x1="{px:.0f}" y1="{py:.0f}" x2="{ex}" y2="{py:.0f}" stroke="#FF3B30" stroke-width="2.5" stroke-dasharray="3 6"/>'
        al = "left" if side == "L" else "right"
        labs += (f'<div class="lb" style="left:{lx}px;top:{ly:.0f}px;text-align:{al};align-items:{"flex-start" if side=="L" else "flex-end"}">'
                 f'{icon(ic, 38, "#fff", 2)}<span>{t}</span></div>')
    css = f"""
    .ad{{background:radial-gradient(80% 60% at 50% 55%,#2e2e33 0%,#1a1a1d 70%)}}
    .h{{position:absolute;top:108px;width:100%;text-align:center;font:400 136px/1 Anton;color:#FF3B30;letter-spacing:2px}}
    .s{{position:absolute;top:252px;width:100%;text-align:center;font:400 46px/1.1 Anton;color:#fff;letter-spacing:1px}}
    .c{{position:absolute;left:{cx-r}px;top:{cy-r}px;width:{2*r}px;height:{2*r}px;border-radius:50%;overflow:hidden;box-shadow:0 0 0 8px #2b2b30,0 0 0 11px #FF3B30,0 30px 60px rgba(0,0,0,.6)}}
    .c img{{width:100%;height:100%;object-position:50% 40%}}
    .vl{{position:absolute;left:290px;right:290px;top:1018px;text-align:center;font:600 24px Oswald;color:#FF3B30;letter-spacing:1.5px;text-transform:uppercase;white-space:nowrap}}
    .lb{{position:absolute;width:220px;display:flex;flex-direction:column;gap:10px}}
    .lb span{{font:600 25px/1.12 Oswald;color:#fff;letter-spacing:1px}}
    .bt{{position:absolute;top:1090px;width:100%;text-align:center;font:600 30px/1.3 Inter;color:#d0d0d5}}
    .bt b{{color:#fff;font-weight:800}}
    .f{{position:absolute;bottom:56px;left:0;right:0;display:flex;justify-content:center;align-items:center;gap:26px}}
    """
    body = f'''{header('white', 40)}
    <div class="h">6 SIGNES</div>
    <div class="s">QUE VOTRE AUTORADIO A FAIT SON TEMPS</div>
    <svg width="1080" height="1350" style="position:absolute;left:0;top:0">{dots}</svg>
    <div class="c"><img class="shot" src="{photo(0)}" {focus(0)}></div><div class="vl fit">{V("name")}</div>
    {labs}
    <div class="bt">La solution : <b>un écran CarPlay &amp; Android Auto sans fil,<br>sur mesure pour votre voiture.</b></div>
    <div class="f">{badge('light', 25)}</div>
    '''
    return page(body, css, W, H)


def ad21_callouts():
    W, H = 1080, 1350
    def co(x, y, w, t):
        return f'<div class="co" style="left:{x}px;top:{y}px;width:{w}px">{t}</div>'
    css = """
    .bgimg{position:absolute;left:0;top:0;width:100%;height:100%}
    .ov{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,0) 18%,rgba(0,0,0,0) 58%,rgba(0,0,0,.8) 63%,rgba(0,0,0,.92) 100%)}
    .hd{position:absolute;left:50%;transform:translateX(-50%);top:112px;background:#fff;border-radius:22px;padding:18px 30px;text-align:center;box-shadow:0 14px 30px rgba(0,0,0,.3);width:900px}
    .hd b{display:block;font:800 40px/1.15 Inter;color:#111;letter-spacing:-.6px}
    .hd span{display:block;font:600 30px Inter;color:#444;margin-top:6px}
    .co{position:absolute;background:#fff;border-radius:16px;padding:16px 20px;font:700 25px/1.25 Inter;color:#111;box-shadow:0 10px 24px rgba(0,0,0,.3)}
    .co small{display:block;font:500 21px/1.25 Inter;color:#555;margin-top:2px}
    .pr{position:absolute;left:50%;transform:translateX(-50%);top:1132px;background:#FFD60A;border-radius:999px;padding:18px 42px;font:900 36px Inter;color:#111;white-space:nowrap;letter-spacing:-.5px}
    .fn{position:absolute;left:40px;top:1218px;font:500 19px Inter;color:#bbb}
    .f{position:absolute;bottom:40px;left:40px;right:40px;display:flex;justify-content:flex-end;align-items:center}
    """
    body = f'''{header('white', 40)}
    <img class="shot bgimg" src="{photo(0)}" {focus(0, safe=(300, 0, 520, 0))}><div class="ov"></div>{chip("left:auto;right:40px;bottom:auto;top:780px")}
    <div class="hd"><b>Encore le téléphone dans la grille d’aération ?</b><span>Voici ce que vous ratez :</span></div>
    {co(40, 840, 470, "CarPlay &amp; Android Auto sans fil<small>Reconnexion auto à chaque démarrage</small>")}
    {co(570, 840, 470, "Écran tactile HD<small>À la place de l’autoradio, sans découpe</small>")}
    {co(40, 990, 470, "Waze, Google Maps, Spotify<small>Sur grand écran</small>")}
    {co(570, 990, 470, "Commandes au volant conservées*<small>Haut-parleurs et micro d’origine aussi</small>")}
    <div class="pr">{evergreen_offer()}</div>
    <div class="fn">*sur les versions équipées</div>
    <div class="f">{badge('light', 24)}</div>
    '''
    return page(body, css, W, H)


def ad22_probleme():
    W, H = 1080, 1350
    lime = "#C6F432"
    rows = [("map-pin", "Pas de GPS dans la voiture", "Waze et Google Maps à l’écran"),
            ("smartphone", "Le téléphone coincé dans la grille d’aération", "Le téléphone reste dans la poche"),
            ("disc-3", "La musique encore sur CD", "Spotify et vos playlists à l’écran")]
    ok = icon("check", 22, "#0F2D27", 3.4)
    arrow = f'<svg width="54" height="30" viewBox="0 0 76 40"><path d="M4 20 H60 M46 6 L62 20 L46 34" fill="none" stroke="#0F2D27" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    tr = "".join(f'<div class="r"><div class="av"><div class="ic">{icon(i, 34, "#0F2D27", 2)}</div><span>{a}</span></div>{arrow}'
                 f'<div class="ap"><div class="ck">{ok}</div><span>{b}</span></div></div>' for i, a, b in rows)
    css = f"""
    .ad{{background:#0F2D27}}
    .h{{position:absolute;top:118px;width:100%;text-align:center;font:900 68px/1 Inter;color:#fff;letter-spacing:-1.5px}}
    .s{{position:absolute;top:200px;width:100%;text-align:center;font:500 30px Inter;color:#cfe7d9}}
    .tb{{position:absolute;left:70px;right:70px;top:262px;background:#fff;border-radius:30px;padding:6px 28px 8px}}
    .hd{{display:flex;justify-content:space-between;padding:16px 0 12px;border-bottom:2px solid #e6ece9;font:800 22px Inter;letter-spacing:2px;color:#5d7a70}}
    .hd span{{width:390px}} .hd span:last-child{{color:#3f7a14}}
    .r{{display:flex;align-items:center;justify-content:space-between;height:98px;border-bottom:2px solid #eef2f0}}
    .r:last-child{{border-bottom:0}}
    .av,.ap{{display:flex;align-items:center;gap:14px;width:390px}}
    .av span{{font:600 25px/1.2 Inter;color:#5d6b66}}
    .ap span{{font:800 25px/1.2 Inter;color:#0F2D27}}
    .ic{{width:58px;height:58px;border-radius:50%;background:#EEF2F0;display:flex;align-items:center;justify-content:center;flex:none}}
    .ck{{width:46px;height:46px;border-radius:50%;background:{lime};display:flex;align-items:center;justify-content:center;flex:none}}
    .ph{{position:absolute;left:70px;right:70px;top:648px;height:420px;border-radius:26px;overflow:hidden;box-shadow:0 20px 40px rgba(0,0,0,.35)}}
    .ph img{{width:100%;height:100%}}
    .cta{{position:absolute;left:50%;transform:translateX(-50%);top:1094px;background:{lime};border-radius:999px;padding:20px 46px;font:900 30px Inter;color:#0F2D27;white-space:nowrap;box-shadow:0 0 0 6px rgba(198,244,50,.25)}}
    .f{{position:absolute;bottom:52px;width:100%;display:flex;justify-content:center}}
    """
    body = f'''{header('white', 40)}
    <div class="h">Avant / Après</div>
    <div class="s">avec un écran CarPlay &amp; Android Auto sans fil</div>
    <div class="tb"><div class="hd"><span>AVANT</span><span>APRÈS</span></div>{tr}</div>
    <div class="ph"><img class="shot" src="{photo(0)}" {focus(0)}>{chip()}</div>
    <div class="cta">VÉRIFIER MA COMPATIBILITÉ</div>
    <div class="f">{badge('light', 25)}</div>
    '''
    return page(body, css, W, H)


def barcode(w, h, seed=3, color="#111"):
    random.seed(seed)
    x, bars = 0, ""
    while x < w:
        bw = random.choice([2, 3, 4, 6, 2, 3])
        if random.random() > .35:
            bars += f'<rect x="{x}" y="0" width="{bw}" height="{h}" fill="{color}"/>'
        x += bw + random.choice([2, 3, 4])
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">{bars}</svg>'


def ad23_colis():
    W, H = 1080, 1350
    noise = '''<svg width="1080" height="1350" style="position:absolute;left:0;top:0"><filter id="k"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="3" seed="11"/>
      <feColorMatrix values="0 0 0 0 .35  0 0 0 0 .22  0 0 0 0 .1  0 0 0 .45 0"/></filter><rect width="1080" height="1350" filter="url(#k)"/></svg>'''
    css = """
    .ad{background:linear-gradient(160deg,#c9a074,#b98c5f)}
    .lb{position:absolute;left:120px;top:112px;width:840px;height:1080px;background:#fff;transform:rotate(1.6deg);box-shadow:0 24px 40px rgba(60,30,0,.35);padding:30px;border-radius:6px}
    .in{border:3px solid #111;height:100%;display:flex;flex-direction:column}
    .row{border-bottom:3px solid #111;padding:16px 22px}
    .k{font:700 20px 'JetBrains Mono';color:#111}
    .v{font:800 30px Inter;color:#111;letter-spacing:-.3px}
    .big{font:900 92px/1 'Playfair Display';color:#D7263D;letter-spacing:-1px;text-align:center}
    .mid{font:700 34px 'Playfair Display';color:#D7263D;text-align:center;margin-top:6px}
    .sm{font:600 19px 'JetBrains Mono';color:#111;text-align:center;margin-top:10px;letter-spacing:.5px}
    .ph{height:330px;border-radius:10px;overflow:hidden;margin-top:18px}
    .ph img{width:100%;height:100%;object-position:50% 42%}
    .st{position:absolute;left:30px;top:870px;transform:rotate(-14deg);background:#E8417A;color:#fff;border-radius:999px;padding:16px 34px;font:900 34px/1 Inter;letter-spacing:1px;box-shadow:0 10px 20px rgba(0,0,0,.25);text-align:center}
    .st small{display:block;font:800 20px Inter;letter-spacing:2px;margin-top:4px}
    .f{position:absolute;bottom:50px;width:100%;display:flex;justify-content:center;align-items:center;gap:24px}
    """
    body = f'''{header('black', 40)}{noise}
    <div class="lb"><div class="in">
      <div class="row" style="display:flex;justify-content:space-between;align-items:center"><div><div class="k">DE :</div><div class="v">SPARK AUTO — FRANCE</div></div>{barcode(260, 60, 4)}</div>
      <div class="row" style="flex:1;padding:22px 26px">
        <div class="k">À :</div><div class="v fit" style="font-size:36px;white-space:nowrap">VOTRE {V("name").upper()}</div>
        <div class="big" style="margin-top:22px">CARPLAY</div>
        <div class="mid">+ Android Auto sans fil</div>
        <div class="sm">ÉCRAN HD · CADRE, FAISCEAU ET OUTILS FOURNIS</div>
        <div class="ph"><img class="shot" src="{photo(0)}" {focus(0)}>{chip()}</div>
        <div style="display:flex;justify-content:center;margin-top:22px">{barcode(560, 90, 9)}</div>
        <div class="sm" style="margin-top:6px">SUIVI</div>
      </div>
      <div class="row" style="border-bottom:0;text-align:center"><div class="v">LIVRAISON SUIVIE</div><div class="k" style="margin-top:4px;font-weight:500">Installation plug &amp; play · 20 minutes environ</div></div>
    </div></div>
    <div class="st">GARANTIE<small>2 ANS</small></div>
    <div class="f">{badge('dark', 25)}</div>
    '''
    return page(body, css, W, H)


def ad24_ticket():
    W, H = 1080, 1350
    lines = [("Autoradio CD", "OK"), ("Radio FM", "OK"), ("GPS", "—"), ("Apple CarPlay", "—"),
             ("Android Auto", "—"), ("Écran tactile", "—"), ("Waze / Google Maps", "—")]
    li = "".join(f'<div class="ln"><span>{a}</span><i></i><span>{b}</span></div>' for a, b in lines)
    edge = "".join(f"{i*20},0 {i*20+10},12 " for i in range(30))
    css = """
    .ad{background:#0B0B0C}
    .bk{position:absolute;inset:-60px;width:calc(100% + 120px);height:calc(100% + 120px);filter:blur(34px) brightness(.32);object-fit:cover}
    .rc{position:absolute;left:300px;top:118px;width:480px;background:#fbfbf8;transform:rotate(-3deg);box-shadow:0 26px 40px rgba(0,0,0,.45);padding:30px 34px 26px;font-family:'JetBrains Mono';color:#1b1b1b}
    .rc:after{content:"";position:absolute;left:0;right:0;bottom:-11px;height:12px;background:linear-gradient(-45deg,transparent 8px,#fbfbf8 0) 0 0/16px 12px,linear-gradient(45deg,transparent 8px,#fbfbf8 0) 0 0/16px 12px}
    .rc h5{font:800 26px 'JetBrains Mono';text-align:center;letter-spacing:1px}
    .rc .sub{font:500 18px 'JetBrains Mono';text-align:center;color:#555;margin-top:4px}
    .hr{border-top:2px dashed #999;margin:14px 0}
    .ln{display:flex;align-items:baseline;gap:8px;font:500 21px 'JetBrains Mono';margin:7px 0}
    .ln i{flex:1;border-bottom:2px dotted #999;transform:translateY(-5px)}
    .tt{display:flex;justify-content:space-between;font:800 23px 'JetBrains Mono'}
    .ph{position:absolute;left:64px;right:64px;top:640px;height:420px;border-radius:26px;overflow:hidden;box-shadow:0 24px 50px rgba(0,0,0,.55)}
    .ph img{width:100%;height:100%}
    .t1{position:absolute;left:60px;right:60px;top:1084px;text-align:center;font:900 36px Inter;color:#fff;letter-spacing:.5px}
    .t2{position:absolute;left:60px;right:60px;top:1134px;text-align:center;font:800 40px Inter;color:#FFB020;letter-spacing:-.5px}
    .t3{position:absolute;left:60px;right:60px;top:1192px;text-align:center;font:500 26px Inter;color:#ddd}
    .f{position:absolute;bottom:40px;left:60px;right:60px;display:flex;justify-content:center;align-items:center}
    """
    body = f'''<img class="bk" src="{photo(0)}">{header('white', 40)}
    <div class="rc"><h5 class="fit" style="white-space:nowrap">VOTRE {V("name").upper()}</h5><div class="sub">Équipement d’origine</div>
      <div class="hr"></div>{li}<div class="hr"></div>
      <div class="tt"><span>TOTAL</span><span>BLOQUÉ EN {V("start") or 2009}</span></div></div>
    <div class="ph"><img class="shot" src="{photo(0)}" {focus(0)}>{chip()}</div>
    <div class="t1">CE QUI MANQUE SUR CE TICKET :</div>
    <div class="t2">CarPlay, Android Auto, GPS, écran HD</div>
    <div class="t3">Spark Auto ajoute tout ça, à la place de l’autoradio d’origine.</div>
    <div class="f">{badge('light', 24)}</div>
    '''
    return page(body, css, W, H)


def ad25_promo():
    W, H = 1080, 1350
    def tag(x, y, t, dx, dy):
        return (f'<svg style="position:absolute;left:0;top:0" width="1080" height="1350"><line x1="{x}" y1="{y}" x2="{dx}" y2="{dy}" stroke="#fff" stroke-width="3"/>'
                f'<circle cx="{dx}" cy="{dy}" r="8" fill="#FF5B1F" stroke="#fff" stroke-width="3"/></svg>')
    css = """
    .ad{background:#0B0B0C}
    .b1{position:absolute;left:50%;transform:translateX(-50%);top:108px;background:#0B0B0C;color:#fff;font:400 100px/1 Anton;letter-spacing:2px;padding:6px 26px;white-space:nowrap;border:4px solid #fff}
    .b2{position:absolute;left:50%;transform:translateX(-50%) rotate(-1.5deg);top:236px;background:#FF5B1F;color:#fff;font:400 82px/1 Anton;letter-spacing:1px;padding:10px 30px;white-space:nowrap}
    .ph{position:absolute;left:0;right:0;top:362px;height:628px;overflow:hidden}
    .ph img{width:100%;height:100%;object-position:50% 46%}
    .ph:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55),rgba(0,0,0,0) 20%,rgba(0,0,0,0) 85%,rgba(0,0,0,.75))}
    .c{position:absolute;font:800 32px Inter;color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.8);letter-spacing:-.3px}
    .code{position:absolute;top:1018px;width:100%;text-align:center;font:400 104px/1 Anton;color:#FF5B1F;letter-spacing:2px}
    .sub{position:absolute;top:1132px;width:100%;text-align:center;font:600 30px Inter;color:#fff}
    .f{position:absolute;bottom:46px;left:60px;right:60px;display:flex;justify-content:flex-end;align-items:center}
    """
    body = f'''{header('white', 40)}
    <div class="ph"><img class="shot" src="{photo(0)}" {focus(0, safe=(124, 0, 80, 0))}>{chip("left:auto;right:50px;bottom:auto;top:76px")}</div>
    <div class="b1 fit" style="max-width:1000px">{P("title")}</div>
    <div class="b2 fit" style="max-width:1020px">{P("headline")}</div>
    <div class="c" style="left:50px;top:382px">CarPlay sans fil</div>
        <div class="c" style="right:50px;top:382px;text-align:right">Écran tactile HD</div>
    <div class="c" style="left:50px;top:920px">Commandes au volant conservées*</div>
    <div class="c" style="right:50px;top:920px;text-align:right">Garantie 2 ans</div>
    <div class="code fit" style="white-space:nowrap">CODE {P("code")}</div>
    <div class="sub">{P("until_label")} · *sur les versions équipées</div>
    <div class="f">{badge('light', 24)}</div>
    '''
    return page(body, css, W, H)


def ad26_commande():
    W, H = 1080, 1350
    lime = "#C6F432"
    items = ["CarPlay &amp; Android Auto sans fil", "Waze, Google Maps et Plans en grand", "Spotify, Deezer, YouTube à l’écran",
             "Appels Bluetooth mains libres", "Commandes au volant conservées*", "Caméra de recul compatible",
             "Fini le téléphone dans la grille d’aération"]
    li = "".join(f'<div class="it"><div class="ck">{icon("check", 24, lime, 3.4)}</div><span>{t}</span></div>' for t in items)
    curve = '<svg style="position:absolute;left:336px;top:206px" width="150" height="110" viewBox="0 0 150 110"><path d="M10 10 C 70 10, 110 40, 120 92" fill="none" stroke="#0B0B0C" stroke-width="4" stroke-linecap="round"/><path d="M104 80 L121 96 L134 76" fill="none" stroke="#0B0B0C" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    css = f"""
    .L{{position:absolute;left:0;top:0;width:500px;height:1350px;background:#fff}}
    .R{{position:absolute;left:500px;top:0;width:580px;height:1350px;background:{lime}}}
    .lt{{position:absolute;left:56px;top:122px;font:900 46px/1.02 Inter;color:#0B0B0C;letter-spacing:-1px}}
    .ph{{position:absolute;left:56px;top:330px;width:400px;height:540px;border-radius:24px;overflow:hidden;box-shadow:0 24px 40px -14px rgba(0,0,0,.4)}}
    .ph img{{width:100%;height:100%;object-position:50% 42%}}
    .lc{{position:absolute;left:56px;top:900px;width:400px;font:500 27px/1.35 Inter;color:#444}}
    .lc b{{color:#0B0B0C;font-weight:800}}
    .rt{{position:absolute;left:556px;top:122px;font:900 46px/1.02 Inter;color:#0B0B0C;letter-spacing:-1px}}
    .l{{position:absolute;left:556px;right:44px;top:270px}}
    .it{{display:flex;align-items:center;gap:18px;margin-bottom:26px;font:700 28px/1.22 Inter;color:#0B0B0C}}
    .ck{{width:46px;height:46px;border-radius:50%;background:#0B0B0C;display:flex;align-items:center;justify-content:center;flex:none}}
    .fn{{position:absolute;left:556px;top:1000px;font:500 20px Inter;color:#3a4a10}}
    .f{{position:absolute;left:56px;right:56px;bottom:60px;display:flex;justify-content:flex-end;align-items:center}}
    """
    body = f'''{header('black', 40)}
    <div class="L"></div><div class="R"></div>
    <div class="lt">CE QUE VOUS<br>COMMANDEZ</div>{curve}
    <div class="ph"><img class="shot" src="{photo(0)}" {focus(0)}>{chip()}</div>
    <div class="lc"><b>Un écran CarPlay conçu pour votre {V("name")}.</b><br>Garantie 2 ans · aide 7j/7 sur WhatsApp</div>
    <div class="rt">CE QUE VOUS<br>OBTENEZ</div>
    <div class="l">{li}</div>
    <div class="fn">*sur les versions équipées</div>
    <div class="f">{badge('dark', 25)}</div>
    '''
    return page(body, css, W, H)



def age_line():
    st = V("start")
    if st:
        return f"Votre {V('short')}<br>date de {st} ?"
    return "Votre voiture a<br>plus de 10 ans ?"


def evergreen_offer():
    return CTX.get("evergreen") or "−10 € avec le code CARPLAY10"


def P(key):
    return (CTX.get("promo") or {}).get(key, "")


# id -> (fonction, a besoin d'une promo active)
TEMPLATES = {
    "jauge": (ad01_jauge, False), "feu_rouge": (ad02_feu, False), "vrai_match": (ad03_match, False),
    "fausse_vs_vraie": (ad04_split, False), "mise_a_jour": (ad05_maj, False), "c_est_officiel": (ad08_officiel, False),
    "communique": (ad09_communique, False), "3_raisons": (ad10_raisons, False), "venn": (ad11_venn, False),
    "checklist": (ad12_checklist, False), "3_etapes": (ad13_etapes, False), "voici_julien": (ad14_julien, False),
    "voitures_de": (ad15_age, False), "liste_barree": (ad16_barre, False), "n_achetez_pas": (ad17_nachetez, False),
    "baissez_un_doigt": (ad18_doigt, False), "affiche": (ad19_affiche, False), "6_signes": (ad20_signes, False),
    "ce_que_vous_ratez": (ad21_callouts, False), "probleme_solution": (ad22_probleme, False), "colis": (ad23_colis, False),
    "ticket": (ad24_ticket, False), "promo": (ad25_promo, True), "commandez_obtenez": (ad26_commande, False),
}
