import math, random
from pathlib import Path

OUT = Path(__file__).parent
OUT.mkdir(exist_ok=True)
FONT = "font-family=\"'Segoe UI',-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif\""

GROUPS = [
    ("Direction &amp; finance", "#A78BFA", [("CEO", "CEO"), ("DAF", "DAF"), ("CG", "Contrôleur de gestion"), ("CPT", "Comptable")]),
    ("Achats &amp; logistique", "#38BDF8", [("DA", "Directeur achats"), ("ACH", "Acheteur"), ("LOG", "Logistique / magasin")]),
    ("Projet &amp; chantier", "#F59E0B", [("CP", "Chef de projet"), ("CC", "Chef de chantier"), ("CT", "Conducteur de travaux"), ("ECO", "Économiste")]),
    ("Commercial &amp; SAV", "#F472B6", [("CA", "Chargé d'affaires"), ("SAV", "Responsable SAV")]),
    ("Externes · portail", "#34D399", [("FRN", "Fournisseur"), ("ST", "Sous-traitant"), ("MOA", "Maître d'ouvrage")]),
    ("Contrôle &amp; support", "#94A3B8", [("QHSE", "Responsable QHSE"), ("RH", "Responsable RH"), ("JUR", "Juriste contrats"), ("ADM", "Admin Salesforce")]),
]
PERSONAS = [(a, l, c) for _, c, ps in GROUPS for a, l in ps]

DEFS = """<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#070B16"/><stop offset="1" stop-color="#101B33"/></linearGradient>
<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#38BDF8" stop-opacity="0.55"/><stop offset="1" stop-color="#38BDF8" stop-opacity="0"/></radialGradient>
<linearGradient id="core" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#38BDF8"/><stop offset="1" stop-color="#6366F1"/></linearGradient>
<linearGradient id="sf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1FB6F0"/><stop offset="1" stop-color="#0176D3"/></linearGradient>
<linearGradient id="go" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#22C55E"/><stop offset="1" stop-color="#10B981"/></linearGradient>
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#1E293B" stroke-width="1" opacity="0.6"/></pattern>
<filter id="sh" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000" flood-opacity="0.45"/></filter>
</defs>"""


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" {FONT}>'
            f'{DEFS}<rect width="{w}" height="{h}" rx="24" fill="url(#bg)"/>'
            f'<rect width="{w}" height="{h}" rx="24" fill="url(#grid)" opacity="0.5"/>{body}</svg>')


# ------------------------------------------------------------------ HERO
def cloud(cx, cy, k, fill, extra=""):
    parts = [(-1.05, 0.25, 0.62), (-0.45, -0.25, 0.78), (0.35, -0.35, 0.9), (1.05, 0.15, 0.68), (0.0, 0.35, 0.75)]
    out = "".join(f'<circle cx="{cx+dx*k:.1f}" cy="{cy+dy*k:.1f}" r="{r*k:.1f}" fill="{fill}"/>' for dx, dy, r in parts)
    out += f'<rect x="{cx-1.05*k:.1f}" y="{cy+0.1*k:.1f}" width="{2.1*k:.1f}" height="{0.85*k:.1f}" rx="{0.42*k:.1f}" fill="{fill}"/>'
    return f'<g {extra}>{out}</g>'


def hero():
    W, H = 1280, 440
    cx, cy, R = 955, 225, 168
    b = []
    b.append(f'<circle cx="{cx}" cy="{cy}" r="250" fill="url(#glow)"/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#1E3A5F" stroke-width="1.5" stroke-dasharray="3 6"/>')
    for i, (a, l, c) in enumerate(PERSONAS):
        ang = -math.pi / 2 + i * 2 * math.pi / 20
        x, y = cx + R * math.cos(ang), cy + R * math.sin(ang)
        b.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#00A1E0" stroke-opacity="0.35" stroke-width="1.5">'
                 f'<animate attributeName="stroke-opacity" values="0.1;0.7;0.1" dur="3s" begin="{i*0.15:.2f}s" repeatCount="indefinite"/></line>')
    for i, (a, l, c) in enumerate(PERSONAS):
        ang = -math.pi / 2 + i * 2 * math.pi / 20
        x, y = cx + R * math.cos(ang), cy + R * math.sin(ang)
        if i == 0:
            b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="23" fill="#FBBF24" stroke="#FDE68A" stroke-width="2.5"/>'
                     f'<text x="{x:.1f}" y="{y+4.2:.1f}" text-anchor="middle" font-size="11.5" font-weight="800" fill="#422006">CEO</text>')
        else:
            b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="19" fill="#0B1220" stroke="{c}" stroke-width="2.5"/>'
                     f'<circle cx="{x:.1f}" cy="{y-4:.1f}" r="4.2" fill="{c}"/>'
                     f'<path d="M{x-7.5:.1f} {y+9:.1f}a7.5 6.5 0 0 1 15 0z" fill="{c}"/>')
    b.append(cloud(cx, cy - 8, 58, "url(#sf)", 'filter="url(#sh)"'))
    b.append(f'<text x="{cx}" y="{cy+6}" text-anchor="middle" font-size="20" font-weight="800" fill="#fff">Ton org</text>'
             f'<text x="{cx}" y="{cy+26}" text-anchor="middle" font-size="12.5" font-weight="700" fill="#E0F2FE" letter-spacing="1">Salesforce</text>')
    b.append(f'<rect x="{cx-70}" y="{cy+62}" width="140" height="24" rx="12" fill="#0B1220" stroke="#A78BFA"/>'
             f'<text x="{cx}" y="{cy+78}" text-anchor="middle" font-size="11.5" font-weight="700" fill="#C4B5FD">orchestré par Claude</text>')
    b.append('<rect x="64" y="64" width="250" height="32" rx="16" fill="#00A1E0" fill-opacity="0.16" stroke="#00A1E0" stroke-opacity="0.7"/>'
             + cloud(88, 79, 9, "#00A1E0") +
             '<text x="106" y="85" font-size="13" font-weight="800" fill="#7DD3FC" letter-spacing="2">SALESFORCE · RECETTE</text>')
    b.append('<text x="64" y="160" font-size="52" font-weight="800" fill="#F8FAFC">Recette <tspan fill="#00A1E0">Salesforce</tspan></text>'
             '<text x="64" y="218" font-size="52" font-weight="800" fill="url(#core)">par agents IA</text>')
    b.append('<text x="64" y="262" font-size="20" fill="#94A3B8">3 à 20 rôles métier testent ton app Salesforce en parallèle.</text>'
             '<text x="64" y="290" font-size="20" fill="#94A3B8">Un rapport. Ton GO. Les corrections.</text>')
    b.append('<rect x="64" y="326" width="330" height="54" rx="14" fill="#0B1220" stroke="#00A1E0" stroke-width="2"/>'
             '<text x="86" y="361" font-size="22" font-weight="700" fill="#E0F2FE" font-family="ui-monospace,Menlo,Consolas,monospace">'
             '<tspan fill="#00A1E0">&gt;</tspan> /review-multi-agent</text>')
    return svg(W, H, "".join(b))


# ------------------------------------------------------------------ WORKFLOW
def icon(kind, x, y, c):
    s = f'stroke="{c}" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "ask":
        return f'<g transform="translate({x},{y})"><path d="M-15 -11H15V8H-3L-10 15V8H-15Z" {s}/><text x="0" y="3" text-anchor="middle" font-size="13" font-weight="800" fill="{c}" stroke="none">?</text></g>'
    if kind == "people":
        return (f'<g transform="translate({x},{y})"><circle cx="0" cy="-7" r="6" fill="#FBBF24"/><path d="M-10 13a10 9 0 0 1 20 0z" fill="#FBBF24"/>'
                f'<circle cx="-14" cy="-3" r="4" fill="{c}"/><path d="M-21 12a7 6 0 0 1 14 0z" fill="{c}"/>'
                f'<circle cx="14" cy="-3" r="4" fill="{c}"/><path d="M7 12a7 6 0 0 1 14 0z" fill="{c}"/></g>')
    if kind == "check":   # radar / preflight
        return f'<g transform="translate({x},{y})"><circle r="14" {s}/><circle r="6" {s}/><path d="M0 0L11 -9" {s}/></g>'
    if kind == "agents":
        out = []
        for i in range(20):
            a = i * 2 * math.pi / 20
            out.append(f'<circle cx="{x+16*math.cos(a):.1f}" cy="{y+16*math.sin(a):.1f}" r="2.6" fill="{PERSONAS[i][2]}"/>')
        out.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{c}"/>')
        return "".join(out)
    if kind == "merge":
        return f'<g transform="translate({x},{y})"><path d="M-14 -12L0 0L-14 12M0 0H14" {s}/><circle cx="-14" cy="-12" r="3" fill="{c}"/><circle cx="-14" cy="12" r="3" fill="{c}"/><circle cx="14" cy="0" r="3" fill="{c}"/></g>'
    if kind == "go":
        return f'<g transform="translate({x},{y})"><path d="M0 -16L14 -10V2C14 10 7 15 0 17C-7 15 -14 10 -14 2V-10Z" {s}/><path d="M-6 1L-1 6L7 -4" {s}/></g>'
    if kind == "build":
        return f'<g transform="translate({x},{y})"><path d="M-12 -12H12M-12 0H6M-12 12H12" {s}/><circle cx="12" cy="0" r="3" fill="{c}"/></g>'
    if kind == "retest":
        return f'<g transform="translate({x},{y})"><path d="M12 -4A12 12 0 1 0 8 9" {s}/><path d="M13 -13V-3H3" {s}/></g>'


def workflow():
    W, H = 1280, 470
    steps = [
        ("ask", "#FBBF24", "3 questions", ["Domaine ?", "Nb agents 3–20", "Consigne libre"]),
        ("check", "#00A1E0", "Salesforce", ["MCP connecté", "1 seul user", "Carte de l'app"]),
        ("people", "#FB923C", "Rôles métier", ["CEO toujours", "Choisis par l'IA", "Selon périmètre"]),
        ("agents", "#A78BFA", "N agents", ["Tous en parallèle", "Vrais parcours", "Données jetables"]),
        ("merge", "#F59E0B", "Rapport", ["Bugs &amp; manques", "P0 → P3", "Données nettoyées"]),
        ("go", "#22C55E", "TON GO", ["GO · GO L1,L3", "GO P0 · NO GO", "Rien avant"]),
        ("build", "#F472B6", "Corrections", ["1 agent / lot", "Sandbox seule", "Re-test parallèle"]),
    ]
    b = ['<text x="640" y="58" text-anchor="middle" font-size="28" font-weight="800" fill="#F8FAFC">Le cycle complet</text>',
         '<text x="640" y="86" text-anchor="middle" font-size="16" fill="#64748B">une commande · trois questions · aucune modification de ton org sans ton GO</text>']
    cw, ch, gap, x0, y0 = 160, 290, 14, 31, 130
    # connecting rail
    b.append(f'<line x1="{x0+cw/2}" y1="{y0+62}" x2="{x0+6*(cw+gap)+cw/2}" y2="{y0+62}" stroke="#1E293B" stroke-width="4"/>')
    b.append(f'<line x1="{x0+cw/2}" y1="{y0+62}" x2="{x0+6*(cw+gap)+cw/2}" y2="{y0+62}" stroke="#38BDF8" stroke-width="4" stroke-dasharray="10 14" stroke-opacity="0.7">'
             f'<animate attributeName="stroke-dashoffset" from="48" to="0" dur="1.2s" repeatCount="indefinite"/></line>')
    for i, (ic, c, title, lines) in enumerate(steps):
        x = x0 + i * (cw + gap)
        gate = ic == "go"
        b.append(f'<rect x="{x}" y="{y0}" width="{cw}" height="{ch}" rx="18" fill="#0F172A" stroke="{c}" '
                 f'stroke-opacity="{1 if gate else 0.35}" stroke-width="{3 if gate else 1.5}" filter="url(#sh)"/>')
        if gate:
            b.append(f'<rect x="{x}" y="{y0}" width="{cw}" height="{ch}" rx="18" fill="#22C55E" fill-opacity="0.07"/>'
                     f'<rect x="{x+cw/2-46}" y="{y0-14}" width="92" height="28" rx="14" fill="url(#go)"/>'
                     f'<text x="{x+cw/2}" y="{y0+5}" text-anchor="middle" font-size="12" font-weight="800" fill="#052e16" letter-spacing="1.5">STOP</text>')
        b.append(f'<circle cx="{x+cw/2}" cy="{y0+62}" r="34" fill="#0B1220" stroke="{c}" stroke-width="2.5"/>')
        b.append(icon(ic, x + cw / 2, y0 + 62, c))
        b.append(f'<text x="{x+18}" y="{y0+130}" font-size="13" font-weight="700" fill="{c}" letter-spacing="2">0{i+1}</text>')
        b.append(f'<text x="{x+18}" y="{y0+160}" font-size="21" font-weight="800" fill="#F8FAFC">{title}</text>')
        for j, t in enumerate(lines):
            yy = y0 + 196 + j * 28
            b.append(f'<circle cx="{x+22}" cy="{yy-5}" r="3.5" fill="{c}"/><text x="{x+33}" y="{yy}" font-size="13.5" fill="#CBD5E1">{t}</text>')
    return svg(W, H, "".join(b))


# ------------------------------------------------------------------ PERSONAS
def personas():
    W, H = 1280, 700
    b = ['<text x="640" y="58" text-anchor="middle" font-size="28" font-weight="800" fill="#F8FAFC">Exemple : domaine BTP</text>',
         '<text x="640" y="86" text-anchor="middle" font-size="16" fill="#64748B">rôles métier choisis par l\'orchestrateur selon ton domaine et ton périmètre · le CEO est toujours là</text>']
    colw, x0, y0 = 196, 27, 124
    for gi, (gname, c, ps) in enumerate(GROUPS):
        x = x0 + gi * (colw + 10)
        b.append(f'<rect x="{x}" y="{y0}" width="{colw}" height="440" rx="18" fill="{c}" fill-opacity="0.06" stroke="{c}" stroke-opacity="0.3"/>')
        b.append(f'<rect x="{x}" y="{y0}" width="{colw}" height="6" rx="3" fill="{c}"/>')
        b.append(f'<text x="{x+colw/2}" y="{y0+40}" text-anchor="middle" font-size="14" font-weight="800" fill="{c}" letter-spacing="0.5">{gname}</text>')
        for pi, (a, l) in enumerate(ps):
            yy = y0 + 66 + pi * 92
            b.append(f'<rect x="{x+14}" y="{yy}" width="{colw-28}" height="78" rx="14" fill="#0F172A" stroke="#1E293B"/>')
            b.append(f'<circle cx="{x+44}" cy="{yy+39}" r="20" fill="{c}" fill-opacity="0.15" stroke="{c}" stroke-width="2"/>')
            fs = 9.5 if len(a) >= 4 else 11.5
            b.append(f'<text x="{x+44}" y="{yy+43.5}" text-anchor="middle" font-size="{fs}" font-weight="800" fill="{c}">{a}</text>')
            words = l.split(" ")
            if len(l) > 13 and len(words) > 1:
                cut = len(words) // 2 if len(words) > 2 else 1
                l1, l2 = " ".join(words[:cut]), " ".join(words[cut:])
                b.append(f'<text x="{x+74}" y="{yy+36}" font-size="13.5" font-weight="600" fill="#E2E8F0">{l1}</text>'
                         f'<text x="{x+74}" y="{yy+54}" font-size="13.5" font-weight="600" fill="#E2E8F0">{l2}</text>')
            else:
                b.append(f'<text x="{x+74}" y="{yy+44}" font-size="13.5" font-weight="600" fill="#E2E8F0">{l}</text>')
    # axes
    axes = [("Couverture", "#38BDF8"), ("Fluidité", "#A78BFA"), ("Facilité", "#F59E0B"), ("Accessibilité", "#F472B6"), ("Fiabilité", "#34D399")]
    b.append('<text x="640" y="610" text-anchor="middle" font-size="14" font-weight="700" fill="#64748B" letter-spacing="3">CHAQUE AGENT NOTE 5 AXES /5 · + BUGS · + AMÉLIORATIONS</text>')
    tw = sum(40 + len(n) * 9 for n, _ in axes) + 14 * 4
    x = 640 - tw / 2
    for n, c in axes:
        w = 40 + len(n) * 9
        b.append(f'<rect x="{x}" y="630" width="{w}" height="38" rx="19" fill="{c}" fill-opacity="0.14" stroke="{c}" stroke-opacity="0.6"/>'
                 f'<text x="{x+w/2}" y="654" text-anchor="middle" font-size="15" font-weight="700" fill="{c}">{n}</text>')
        x += w + 14
    return svg(W, H, "".join(b))


# ------------------------------------------------------------------ REPORT
def report():
    W, H = 1280, 710
    random.seed(7)
    b = ['<text x="640" y="58" text-anchor="middle" font-size="28" font-weight="800" fill="#F8FAFC">Ce que tu reçois</text>',
         '<text x="640" y="86" text-anchor="middle" font-size="16" fill="#64748B">rapport consolidé HTML + Markdown · aperçu illustratif</text>']
    X, Y, WW, HH = 70, 116, 1140, 560
    b.append(f'<rect x="{X}" y="{Y}" width="{WW}" height="{HH}" rx="16" fill="#F8FAFC" filter="url(#sh)"/>')
    b.append(f'<path d="M{X} {Y+16}a16 16 0 0 1 16 -16h{WW-32}a16 16 0 0 1 16 16v20h-{WW}z" fill="#E2E8F0"/>')
    for i, c in enumerate(["#EF4444", "#F59E0B", "#22C55E"]):
        b.append(f'<circle cx="{X+22+i*18}" cy="{Y+18}" r="5.5" fill="{c}"/>')
    b.append(f'<rect x="{X+400}" y="{Y+8}" width="340" height="20" rx="10" fill="#fff"/><text x="{X+570}" y="{Y+22}" text-anchor="middle" font-size="11" fill="#64748B">recette-runs/20261118-2000/rapport.html</text>')
    b.append(f'<rect x="{X}" y="{Y+36}" width="{WW}" height="34" fill="#0176D3"/>' + cloud(X + 30, Y + 51, 9, "#fff") +
             f'<text x="{X+50}" y="{Y+58}" font-size="14" font-weight="800" fill="#fff">Recette Salesforce — rapport consolidé</text>'
             f'<text x="{X+WW-20}" y="{Y+58}" text-anchor="end" font-size="12" fill="#BAE6FD">domaine BTP · 20 agents · toute l\'org</text>')
    kp = [("Verdict", "RÉSERVES", "#EA580C"), ("Personas", "20/20", "#0F172A"), ("Constats", "37", "#0F172A"),
          ("Bloquants", "3", "#DC2626"), ("Majeurs", "11", "#EA580C"), ("Données test", "0 reste", "#16A34A")]
    for i, (k, v, c) in enumerate(kp):
        x = X + 24 + i * 182
        b.append(f'<rect x="{x}" y="{Y+86}" width="168" height="62" rx="10" fill="#fff" stroke="#E2E8F0"/>'
                 f'<text x="{x+14}" y="{Y+104}" font-size="12" fill="#64748B">{k}</text>'
                 f'<text x="{x+14}" y="{Y+136}" font-size="{22 if len(v) > 5 else 28}" font-weight="800" fill="{c}">{v}</text>')
    # heatmap
    hx, hy = X + 24, Y + 178
    b.append(f'<text x="{hx}" y="{hy}" font-size="14" font-weight="800" fill="#0F172A">Scores par persona</text>')
    heat = ["#FCA5A5", "#FDBA74", "#FDE047", "#86EFAC", "#4ADE80"]
    cols = ["Couv.", "Flui.", "Faci.", "Acce.", "Fiab."]
    for j, cn in enumerate(cols):
        b.append(f'<text x="{hx+64+j*30+13}" y="{hy+22}" text-anchor="middle" font-size="9.5" fill="#64748B">{cn}</text>')
    for i in range(20):
        col = i // 10
        r = i % 10
        a, l, c = PERSONAS[i]
        bx = hx + col * 250
        by = hy + 32 + r * 28
        if col == 1 and r == 0:
            for j, cn in enumerate(cols):
                b.append(f'<text x="{bx+64+j*30+13}" y="{hy+22}" text-anchor="middle" font-size="9.5" fill="#64748B">{cn}</text>')
        b.append(f'<circle cx="{bx+12}" cy="{by+12}" r="9" fill="{c}"/><text x="{bx+26}" y="{by+16}" font-size="10.5" font-weight="700" fill="#334155">{a}</text>')
        for j in range(5):
            v = max(0, min(4, int(random.gauss(2.8, 1))))
            b.append(f'<rect x="{bx+64+j*30}" y="{by+1}" width="26" height="22" rx="4" fill="{heat[v]}"/>'
                     f'<text x="{bx+64+j*30+13}" y="{by+16}" text-anchor="middle" font-size="11" font-weight="700" fill="#1F2937">{v+1}</text>')
    # lots
    lx, ly = X + 560, Y + 178
    b.append(f'<text x="{lx}" y="{ly}" font-size="14" font-weight="800" fill="#0F172A">Lots proposés · en attente de ton GO</text>')
    lots = [("L1", "P0", "Flow DA → Commande", "acheteur · chef de chantier · conducteur", "#DC2626", "#FEE2E2"),
            ("L2", "P0", "Partage Commandes portail", "fournisseur · sous-traitant", "#DC2626", "#FEE2E2"),
            ("L3", "P0", "Situation de travaux — calcul TVA", "comptable · DAF · maître d'ouvrage", "#DC2626", "#FEE2E2"),
            ("L4", "P1", "Page Chantier (mobile)", "chef de chantier · QHSE", "#EA580C", "#FFEDD5"),
            ("L5", "P1", "Rapport marge par lot", "CEO · contrôleur de gestion", "#EA580C", "#FFEDD5"),
            ("L6", "P2", "Libellés &amp; aide en ligne Achats", "acheteur · directeur achats", "#A16207", "#FEF9C3")]
    for i, (lid, p, t, who, c, bg) in enumerate(lots):
        y = ly + 18 + i * 50
        b.append(f'<rect x="{lx}" y="{y}" width="556" height="42" rx="9" fill="#fff" stroke="#E2E8F0"/>'
                 f'<text x="{lx+14}" y="{y+26}" font-size="14" font-weight="800" fill="#0F172A">{lid}</text>'
                 f'<rect x="{lx+44}" y="{y+11}" width="34" height="20" rx="10" fill="{bg}"/><text x="{lx+61}" y="{y+25}" text-anchor="middle" font-size="11" font-weight="800" fill="{c}">{p}</text>'
                 f'<text x="{lx+90}" y="{y+19}" font-size="13" font-weight="700" fill="#1E293B">{t}</text>'
                 f'<text x="{lx+90}" y="{y+34}" font-size="10.5" fill="#64748B">{who}</text>')
    gy = ly + 352
    for i, (t, c) in enumerate([("GO", "#16A34A"), ("GO L1,L3", "#16A34A"), ("GO P0", "#16A34A"), ("NO GO", "#64748B")]):
        x = lx + i * 140
        b.append(f'<rect x="{x}" y="{gy-22}" width="128" height="34" rx="17" fill="{c}" fill-opacity="0.12" stroke="{c}"/>'
                 f'<text x="{x+64}" y="{gy}" text-anchor="middle" font-size="14" font-weight="800" fill="{c}" font-family="ui-monospace,Menlo,Consolas,monospace">{t}</text>')
    return svg(W, H, "".join(b))


for name, fn in [("hero", hero), ("workflow", workflow), ("personas", personas), ("report", report)]:
    (OUT / f"{name}.svg").write_text(fn(), encoding="utf-8")
print("ok")
