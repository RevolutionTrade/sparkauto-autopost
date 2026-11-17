"""Reels animés Spark Auto (1080x1920, 10 s). Même charte que les statiques : logo en haut au centre,
photo CarPlay du véhicule, badge catalogue. Zones sûres : rien d'important au-dessus de 170 px,
sous 1500 px, ni à droite de 920 px dans la moitié basse (boutons Instagram / TikTok)."""
from core import photo, focus, chip, icon, header, badge, page, V

W, H = 1080, 1920
DUR = 10.0
COVER_MS = 9500  # image de couverture : la composition finale

KF = """
@keyframes up{from{opacity:0;transform:translateY(46px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes pop{from{opacity:0;transform:scale(.9)}to{opacity:1;transform:none}}
@keyframes inl{from{opacity:0;transform:translateX(-70px)}to{opacity:1;transform:none}}
@keyframes kb{from{transform:scale(1)}to{transform:scale(1.07)}}
@keyframes on{from{opacity:0}to{opacity:1}} @keyframes off{from{opacity:1}to{opacity:0}}
@keyframes lit{to{opacity:1}} @keyframes dim{to{opacity:.25}}
@keyframes strike{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes draw{from{stroke-dashoffset:var(--len)}to{stroke-dashoffset:0}}
@keyframes print{from{clip-path:inset(0 0 100% 0)}to{clip-path:inset(0 0 0 0)}}
.ph img.shot{animation:kb 7s linear 3s both}
"""


def A(name, dur, delay, ease="cubic-bezier(.2,.8,.2,1)"):
    return f"animation:{name} {dur}s {ease} {delay}s both"


def reel_feu_rouge():
    def lens(y, color, inner, a_on, a_off=None):
        anim_g = f"{A('on', .3, a_on, 'ease')}" + (f",off .4s ease {a_off}s forwards" if a_off else "")
        anim_i = f"opacity:.25;animation:lit .3s ease {a_on}s forwards" + (f",dim .4s ease {a_off}s forwards" if a_off else "")
        return (f'<div class="lens" style="top:{y}px;--c:{color}"><div class="glow" style="{anim_g}"></div>'
                f'<div class="in" style="{anim_i}">{inner}</div></div>')
    css = KF + """
    .ad{background:radial-gradient(90% 55% at 50% 12%,#1d1d21 0%,#0a0a0b 70%)}
    .h{position:absolute;left:80px;right:60px;top:288px;font-family:Anton;font-size:104px;line-height:1.02;color:#fff;text-transform:uppercase}
    .h span{display:block}
    .s{position:absolute;left:80px;right:140px;top:630px;font:500 34px/1.35 Inter;color:#b8b8bd}
    .tl{position:absolute;left:80px;top:760px;width:220px;height:560px;border-radius:42px;background:linear-gradient(180deg,#1d1d20,#111113);
        border:3px solid #2c2c30;box-shadow:0 40px 80px rgba(0,0,0,.6)}
    .lens{position:absolute;left:32px;width:150px;height:150px;border-radius:50%;background:#262628;box-shadow:inset 0 -10px 20px rgba(0,0,0,.35)}
    .lens .in{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}
    .lens .glow{position:absolute;inset:0;border-radius:50%;background:radial-gradient(circle at 40% 35%,#fff8 0%,var(--c) 45%,var(--c) 100%);
        box-shadow:0 0 40px var(--c),0 0 90px var(--c)}
    .ph{position:absolute;left:340px;top:780px;width:580px;height:500px;border-radius:30px;overflow:hidden;box-shadow:0 0 0 4px #30D158,0 0 60px rgba(48,209,88,.45)}
    .ph img{width:100%;height:100%}
    .cap{position:absolute;left:340px;width:580px;top:1300px;text-align:center;font:600 24px Inter;color:#8d8d93}
    .cta{position:absolute;left:80px;top:1352px;font:900 54px Inter;color:#fff;letter-spacing:-.8px}
    .cta em{font-style:normal;color:#30D158}
    .bd{position:absolute;left:80px;top:1432px}
    """
    body = f'''{header('white', 180, 50)}
    <div class="h"><span style="{A('up', .45, .1)}">Votre autoradio</span><span style="{A('up', .45, .3)}">d’origine est un</span>
      <span style="{A('up', .45, .55)};color:#FF3B30">feu rouge.</span></div>
    <div class="s" style="{A('fade', .6, 1.1, 'ease')}">CD rayé, pas de GPS, téléphone dans la grille d’aération : votre tableau de bord est à l’arrêt.</div>
    <div class="tl" style="{A('inl', .6, 1.6)}">{lens(26, "#FF3B30", icon("disc-3", 80, "#fff", 2.2), 2.0, 3.6)}{lens(205, "#FFB020", "", 99)}{lens(384, "#30D158", icon("smartphone", 76, "#fff", 2.2), 3.9)}</div>
    <div class="ph" style="{A('pop', .55, 4.2, 'cubic-bezier(.2,.9,.25,1.15)')}"><img class="shot" src="{photo(0)}" {focus(0)}><div style="{A('fade', .5, 5.0, 'ease')}">{chip()}</div></div>
    <div class="cap" style="{A('fade', .5, 5.3, 'ease')}">CarPlay &amp; Android Auto sans fil</div>
    <div class="cta" style="{A('up', .5, 6.0)}">Passez <em>au vert.</em></div>
    <div class="bd" style="{A('up', .5, 6.4)}">{badge('light', 30)}</div>
    '''
    return page(body, css, W, H)


def reel_jauge():
    import math
    cx, cy, r = 400, 400, 300

    def pt(val, rr):
        th = math.radians(180 - val * 180)
        return cx + rr * math.cos(th), cy - rr * math.sin(th)
    ticks = ""
    for i in range(21):
        x1, y1 = pt(i / 20, r - 52)
        x2, y2 = pt(i / 20, r - (66 if i % 5 == 0 else 60))
        ticks += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#9a9aa2" stroke-width="{4 if i % 5 == 0 else 2}" stroke-linecap="round"/>'
    svg = f'''<svg width="760" height="446" viewBox="0 0 800 470">
      <defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#E0352B"/><stop offset=".45" stop-color="#F6A623"/>
        <stop offset=".75" stop-color="#9AD13B"/><stop offset="1" stop-color="#1FB257"/></linearGradient></defs>
      <path d="M {cx-r} {cy} A {r} {r} 0 0 1 {cx+r} {cy}" fill="none" stroke="#d9d9de" stroke-width="74"/>
      <path d="M {cx-r} {cy} A {r} {r} 0 0 1 {cx+r} {cy}" fill="none" stroke="url(#g)" stroke-width="64"/>
      {ticks}
      <g class="needle"><line x1="{cx+34}" y1="{cy}" x2="{cx-236}" y2="{cy}" stroke="#16161a" stroke-width="16" stroke-linecap="round"/></g>
      <circle cx="{cx}" cy="{cy}" r="34" fill="#16161a"/><circle cx="{cx}" cy="{cy}" r="12" fill="#5b5b62"/>
    </svg>'''
    css = KF + """
    .ad{background:radial-gradient(120% 70% at 50% 25%,#FAFAFB 0%,#E9E9EC 60%,#DCDCE0 100%)}
    .t{position:absolute;top:290px;width:100%;text-align:center;font-family:'Archivo Black';font-size:92px;line-height:1.02;letter-spacing:-2px;color:#111}
    .s{position:absolute;top:500px;width:100%;text-align:center;font:500 36px Inter;color:#55555c}
    .g{position:absolute;left:160px;top:575px}
    .needle{transform-box:view-box;transform-origin:400px 400px;animation:needle 2.2s cubic-bezier(.55,0,.2,1) 1.4s both}
    @keyframes needle{from{transform:rotate(14deg)}to{transform:rotate(162deg)}}
    .lab{position:absolute;font:800 24px Inter;letter-spacing:1.5px;text-transform:uppercase;text-align:center;line-height:1.15}
    .ph{position:absolute;left:120px;top:1066px;width:760px;height:340px;border-radius:30px;overflow:hidden;box-shadow:0 30px 60px -20px rgba(0,0,0,.45),0 0 0 6px #fff}
    .ph img{width:100%;height:100%}
    .tag{position:absolute;left:50%;top:1042px;margin-left:-190px;width:380px;text-align:center;z-index:3;background:#1FB257;color:#fff;font:800 22px Inter;
         letter-spacing:1px;padding:10px 0;border-radius:999px;text-transform:uppercase;box-shadow:0 8px 20px rgba(31,178,87,.4)}
    .bd{position:absolute;top:1432px;width:100%;display:flex;justify-content:center}
    """
    body = f'''{header('black', 180, 50)}
    <div class="t"><div style="{A('up', .45, .1)}">NIVEAU DE</div><div style="{A('up', .45, .3)}">MODERNITÉ</div></div>
    <div class="s" style="{A('fade', .5, .7, 'ease')}">de votre tableau de bord</div>
    <div class="g" style="{A('fade', .5, .9, 'ease')}">{svg}</div>
    <div class="lab" style="left:110px;top:950px;width:200px;color:#C9322A;{A('up', .4, 1.5)}">Autoradio<br>CD</div>
    <div class="lab" style="left:440px;top:752px;width:200px;color:#B9770E;{A('up', .4, 2.4)}">Support<br>téléphone</div>
    <div class="lab" style="left:770px;top:950px;width:200px;color:#178A44;{A('up', .4, 3.4)}">CarPlay<br>sans fil</div>
    <div class="ph" style="{A('pop', .55, 4.2, 'cubic-bezier(.2,.9,.25,1.15)')}"><img class="shot" src="{photo(0)}" {focus(0)}><div style="{A('fade', .5, 5.0, 'ease')}">{chip()}</div></div>
    <div class="tag" style="{A('pop', .45, 4.8)}">Avec un écran Spark Auto</div>
    <div class="bd" style="{A('up', .5, 5.6)}">{badge('dark', 30)}</div>
    '''
    return page(body, css, W, H)


def reel_liste_barree():
    items = ["Le support qui tombe au premier virage", "Le câble qui traîne sur le levier de vitesse",
             "Le lecteur CD qui ne sert plus", "Le GPS jamais mis à jour"]
    lis = ""
    for i, t in enumerate(items):
        t0 = .15 + i * .75
        lis += (f'<div class="it" style="{A("up", .4, t0)}"><span>{t}<i class="st" style="{A("strike", .35, t0 + .45, "ease-in")}"></i></span></div>')
    css = KF + """
    .ad{background:#F1E6D3}
    .cd{position:absolute;inset:40px;background:#FBF4E8;border-radius:44px;box-shadow:inset 0 0 0 2px #ead9bd}
    .l{position:absolute;left:100px;right:60px;top:300px}
    .it{font:500 44px/1.25 'Playfair Display';color:#3b2b20;margin-bottom:30px;white-space:nowrap}
    .it span{position:relative;display:inline-block}
    .st{position:absolute;left:-4px;right:-4px;top:54%;height:4px;background:#C8102E;transform-origin:left center;border-radius:2px}
    .ph{position:absolute;left:100px;width:820px;top:690px;height:500px;border-radius:28px;overflow:hidden;box-shadow:0 24px 50px -16px rgba(80,50,20,.45)}
    .ph img{width:100%;height:100%}
    .t1{position:absolute;left:100px;top:1226px;font:700 66px 'Playfair Display';color:#C8102E;letter-spacing:-.5px}
    .t2{position:absolute;left:100px;top:1310px;font:500 54px 'Playfair Display';color:#2a1f18}
    .bd{position:absolute;left:100px;top:1420px}
    """
    body = f'''<div class="cd"></div>{header('black', 180, 50)}
    <div class="l">{lis}</div>
    <div class="ph" style="{A('pop', .55, 3.3, 'cubic-bezier(.2,.9,.25,1.15)')}"><img class="shot" src="{photo(0)}" {focus(0)}><div style="{A('fade', .5, 4.0, 'ease')}">{chip()}</div></div>
    <div class="t1" style="{A('up', .5, 4.3)}">CarPlay sans fil,</div>
    <div class="t2" style="{A('up', .5, 4.7)}">sans changer de voiture.</div>
    <div class="bd" style="{A('up', .5, 5.4)}">{badge('dark', 30)}</div>
    '''
    return page(body, css, W, H)


def reel_ticket():
    start = V("start") or "2009"
    lines = [("Autoradio CD", "OK"), ("Radio FM", "OK"), ("GPS", "—"), ("Apple CarPlay", "—"),
             ("Android Auto", "—"), ("Écran tactile", "—"), ("Waze / Google Maps", "—")]
    li = "".join(f'<div class="ln"><span>{a}</span><i></i><span class="{"ko" if b == "—" else ""}">{b}</span></div>' for a, b in lines)
    css = KF + """
    .ad{background:radial-gradient(90% 60% at 50% 20%,#24242a 0%,#0c0c0e 75%)}
    .rc{position:absolute;left:150px;top:286px;width:780px;background:#fbfbf8;transform:rotate(-2deg);box-shadow:0 30px 50px rgba(0,0,0,.5);
        padding:42px 44px 36px;font-family:'JetBrains Mono';color:#1b1b1b}
    .rc h5{font:800 36px 'JetBrains Mono';text-align:center;letter-spacing:1px;white-space:nowrap}
    .rc .sub{font:500 24px 'JetBrains Mono';text-align:center;color:#555;margin-top:6px}
    .hr{border-top:2px dashed #999;margin:18px 0}
    .ln{display:flex;align-items:baseline;gap:10px;font:500 29px 'JetBrains Mono';margin:10px 0}
    .ln i{flex:1;border-bottom:2px dotted #999;transform:translateY(-6px)}
    .ln .ko{color:#C8102E;font-weight:800}
    .tt{display:flex;justify-content:space-between;font:800 30px 'JetBrains Mono'}
    .t1{position:absolute;left:80px;right:80px;top:1004px;text-align:center;font:900 40px Inter;color:#fff;letter-spacing:.5px}
    .t2{position:absolute;left:80px;right:80px;top:1056px;text-align:center;font:800 40px Inter;color:#FFB020;letter-spacing:-.5px}
    .ph{position:absolute;left:120px;width:760px;top:1126px;height:284px;border-radius:26px;overflow:hidden;box-shadow:0 0 0 3px rgba(255,255,255,.14),0 30px 60px rgba(0,0,0,.6)}
    .ph img{width:100%;height:100%}
    .bd{position:absolute;top:1436px;width:100%;display:flex;justify-content:center}
    """
    body = f'''{header('white', 180, 50)}
    <div class="rc" style="animation:print 2.4s steps(24) .1s both"><h5 class="fit">VOTRE {V("name").upper()}</h5><div class="sub">Équipement d’origine</div>
      <div class="hr"></div>{li}<div class="hr"></div>
      <div class="tt"><span>TOTAL</span><span>BLOQUÉ EN {start}</span></div></div>
    <div class="t1" style="{A('up', .5, 3.0)}">CE QUI MANQUE SUR CE TICKET :</div>
    <div class="t2 fit" style="white-space:nowrap;{A('up', .5, 3.4)}">CarPlay, Android Auto, GPS, écran HD</div>
    <div class="ph" style="{A('pop', .55, 4.1, 'cubic-bezier(.2,.9,.25,1.15)')}"><img class="shot" src="{photo(0)}" {focus(0)}><div style="{A('fade', .5, 4.8, 'ease')}">{chip()}</div></div>
    <div class="bd" style="{A('up', .5, 5.4)}">{badge('light', 30)}</div>
    '''
    return page(body, css, W, H)


def reel_3_etapes():
    k = "#2a2a2a"
    s1 = f'''<svg width="190" height="190" viewBox="0 0 260 300" fill="none" stroke="{k}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
      <rect x="30" y="150" width="200" height="90" rx="10"/><rect x="60" y="168" width="140" height="10" rx="5"/>
      <circle cx="65" cy="212" r="14"/><circle cx="195" cy="212" r="14"/><rect x="100" y="200" width="60" height="22" rx="4"/>
      <path d="M130 130 V40"/><path d="M104 66 L130 38 L156 66"/></svg>'''
    s2 = f'''<svg width="190" height="190" viewBox="0 0 260 300" fill="none" stroke="{k}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
      <rect x="22" y="120" width="86" height="64" rx="8"/><path d="M108 136 h20 M108 168 h20"/>
      <rect x="152" y="120" width="86" height="64" rx="8"/><path d="M152 136 h-14 M152 168 h-14"/>
      <path d="M65 184 C 65 240, 20 250, 20 290"/><path d="M195 184 C 195 240, 240 250, 240 290"/>
      <path d="M96 210 l14 14 l26 -30" stroke="#1F7A3A" stroke-width="6"/></svg>'''
    css = KF + """
    .ad{background:#F7F2E8}
    .t{position:absolute;top:286px;width:100%;text-align:center;font:700 96px Caveat;color:#1d1d1d}
    .s{position:absolute;top:404px;width:100%;text-align:center;font:600 30px Inter;color:#6a6258;letter-spacing:.3px}
    .row{position:absolute;left:100px;right:160px;display:flex;align-items:center;gap:36px}
    .bx{width:220px;height:210px;flex:none;background:#fff;border:2px solid #e5ddcf;border-radius:22px;display:flex;align-items:center;justify-content:center}
    .cap{font:600 50px/1.02 Caveat;color:#222}
    .cap b{display:block;font-weight:700;color:#8a7d6c;font-size:40px}
    .s3{position:absolute;left:100px;top:946px;font:600 50px Caveat;color:#222}
    .s3 b{font-weight:700;color:#8a7d6c;font-size:40px;margin-right:12px}
    .ph{position:absolute;left:100px;width:820px;top:1012px;height:320px;border-radius:26px;overflow:hidden;box-shadow:0 20px 40px -12px rgba(0,0,0,.35)}
    .ph img{width:100%;height:100%}
    .no{position:absolute;top:1350px;width:100%;text-align:center;font:700 46px Caveat;color:#1d1d1d}
    .bd{position:absolute;top:1424px;width:100%;display:flex;justify-content:center}
    """
    body = f'''{header('black', 180, 50)}
    <div class="t" style="{A('up', .5, .1)}">Installer CarPlay, réglé.</div>
    <div class="s" style="{A('fade', .5, .6, 'ease')}">Plug &amp; play · 20 minutes environ</div>
    <div class="row" style="top:476px;{A('inl', .5, 1.1)}"><div class="bx">{s1}</div><div class="cap"><b>étape 1 :</b>on retire l’autoradio</div></div>
    <div class="row" style="top:712px;{A('inl', .5, 2.1)}"><div class="bx">{s2}</div><div class="cap"><b>étape 2 :</b>on branche le faisceau</div></div>
    <div class="s3" style="{A('inl', .5, 3.1)}"><b>étape 3 :</b>CarPlay.</div>
    <div class="ph" style="{A('pop', .55, 3.4, 'cubic-bezier(.2,.9,.25,1.15)')}"><img class="shot" src="{photo(0)}" {focus(0)}><div style="{A('fade', .5, 4.1, 'ease')}">{chip()}</div></div>
    <div class="no" style="{A('up', .5, 4.8)}">pas de découpe. pas de soudure. réversible.</div>
    <div class="bd" style="{A('up', .5, 5.5)}">{badge('dark', 30)}</div>
    '''
    return page(body, css, W, H)


def reel_probleme_solution():
    lime = "#C6F432"
    rows = [("map-pin", "Pas de GPS", 0), ("smartphone", "Téléphone dans la grille d’aération", 1), ("disc-3", "Musique sur CD", 2)]
    tr = ""
    for k, (ic, t, p) in enumerate(rows):
        t0 = .9 + k * 1.3
        tr += (f'<div class="r" style="top:{560 + k * 262}px;{A("inl", .45, t0)}">'
               f'<div class="pb"><div class="ic">{icon(ic, 46, "#0F2D27", 2)}</div><span>{t}</span></div>'
               f'<svg class="ar" width="70" height="40" viewBox="0 0 76 40" style="{A("fade", .3, t0 + .4, "ease")}"><path d="M4 20 H60 M46 6 L62 20 L46 34" fill="none" stroke="{lime}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></svg>'
               f'<div class="so" style="{A("pop", .45, t0 + .65, "cubic-bezier(.2,.9,.25,1.15)")}"><img class="shot" src="{photo(p)}" {focus(p)}>'
               f'{chip("font-size:16px;padding:6px 10px;left:8px;bottom:8px", years=False, which=p)}</div></div>')
    css = KF + f"""
    .ad{{background:#0F2D27}}
    .h{{position:absolute;top:290px;width:100%;text-align:center;font:800 64px/1.1 Inter;color:#fff;letter-spacing:-1.4px}}
    .lbl{{position:absolute;top:478px;left:80px;right:160px;display:flex;justify-content:space-between;font:800 24px Inter;letter-spacing:2px;color:{lime}}}
    .r{{position:absolute;left:80px;right:160px;height:230px;display:flex;align-items:center;justify-content:space-between;
        background:#fff;border-radius:26px;padding:0 20px 0 22px}}
    .pb{{display:flex;align-items:center;gap:16px;width:330px}}
    .pb span{{font:700 30px/1.2 Inter;color:#0F2D27}}
    .ic{{width:76px;height:76px;border-radius:50%;background:#EAF5D5;display:flex;align-items:center;justify-content:center;flex:none}}
    .ar{{flex:none}}
    .so{{position:relative;width:330px;height:190px;border-radius:16px;overflow:hidden;box-shadow:0 10px 20px rgba(0,0,0,.18)}}
    .so img{{width:100%;height:100%}}
    .cta{{position:absolute;left:50%;top:1354px;width:640px;margin-left:-320px;text-align:center;background:{lime};border-radius:999px;padding:22px 0;
        font:900 32px Inter;color:#0F2D27;box-shadow:0 0 0 6px rgba(198,244,50,.25)}}
    .bd{{position:absolute;top:1448px;width:100%;display:flex;justify-content:center}}
    """
    body = f'''{header('white', 180, 50)}
    <div class="h"><div style="{A('up', .45, .1)}">Besoin d’un tableau</div><div style="{A('up', .45, .3)}">de bord moderne ?</div></div>
    <div class="lbl" style="{A('fade', .4, .6, 'ease')}"><span>PROBLÈME</span><span style="width:330px;text-align:center">SOLUTION</span></div>
    {tr}
    <div class="cta" style="{A('pop', .45, 5.2)}">VÉRIFIER MA COMPATIBILITÉ</div>
    <div class="bd" style="{A('up', .5, 5.7)}">{badge('light', 28)}</div>
    '''
    return page(body, css, W, H)


# id -> (fonction, a besoin d'une promo active). L'id sans « reel_ » sert pour les légendes.
REELS = {
    "reel_feu_rouge": (reel_feu_rouge, False),
    "reel_jauge": (reel_jauge, False),
    "reel_liste_barree": (reel_liste_barree, False),
    "reel_ticket": (reel_ticket, False),
    "reel_3_etapes": (reel_3_etapes, False),
    "reel_probleme_solution": (reel_probleme_solution, False),
}


def caption_id(rid):
    return rid[5:] if rid.startswith("reel_") else rid
