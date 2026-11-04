"""Generates every image in assets/ for README.md (English) and README.es.md (Spanish).

Each image comes in light and dark, and in a wide (desktop) and tall (phone) version. All text is drawn as
outlines from IBM Plex (scripts/fuentes, SIL Open Font License), so it looks the same everywhere. Each glyph is
defined once per file and reused with <use>, which keeps the files small.

    pip install -r scripts/requirements.txt
    python scripts/generar.py              # everything
    python scripts/generar.py --actividad  # only the activity graph (what the monthly Action runs)

The activity graph reads the contribution calendar from the GitHub API. It needs a token in GITHUB_TOKEN
(or a logged-in `gh`). Private contributions are counted because the profile shows them.
"""
import datetime
import html
import json
import os
import random
import subprocess
import sys
import urllib.request

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
ASSETS = os.path.join(RAIZ, "assets")
USUARIO = "Montse2308"

PAL = {
    "light": dict(bg="#F4F7FB", ink="#0F1B2D", muted="#55657C", line="#D3DCE8", acc="#2B66D9", acc2="#9DB9EC", pink="#C8467E"),
    "dark": dict(bg="#0B1220", ink="#E6EDF7", muted="#91A2BA", line="#243450", acc="#6FA1FF", acc2="#34558C", pink="#F07FAE"),
}


# ───────────────────────── text as outlines
class Fuente:
    def __init__(self, nombre):
        ruta = os.path.join(AQUI, "fuentes", f"{nombre}.ttf")
        self.clave = nombre.replace("IBMPlex", "").replace("-", "").lower()  # sans400, mono600...
        self.tt = TTFont(ruta)
        self.hb = hb.Font(hb.Face(hb.Blob.from_file_path(ruta)))
        self.upem = self.tt["head"].unitsPerEm
        self.gs = self.tt.getGlyphSet()
        self.orden = self.tt.getGlyphOrder()

    def forma(self, texto):
        buf = hb.Buffer(); buf.add_str(texto); buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": True})
        return list(zip(buf.glyph_infos, buf.glyph_positions))

    def ancho(self, texto, size):
        return sum(p.x_advance for _, p in self.forma(texto)) * size / self.upem


FUENTES = {k: Fuente(n) for k, n in (("sans400", "IBMPlexSans-400"), ("sans600", "IBMPlexSans-600"),
                                     ("mono400", "IBMPlexMono-400"), ("mono600", "IBMPlexMono-600"))}


def fuente(w=400, mono=False):
    return FUENTES[f"{'mono' if mono else 'sans'}{600 if w >= 600 else 400}"]


class Lienzo:
    """Collects the glyphs used in one SVG so each one is defined only once."""

    def __init__(self):
        self.glifos = {}

    def texto(self, x, y, t, size, fill, w=400, anchor="start", mono=False):
        f = fuente(w, mono)
        ancho = f.ancho(t, size)
        x0 = x - (ancho if anchor == "end" else ancho / 2 if anchor == "middle" else 0)
        s = size / f.upem
        usos, cx = [], 0
        for info, pos in f.forma(t):
            gid = f"{f.clave}g{info.codepoint}"
            if gid not in self.glifos:
                pen = SVGPathPen(f.gs, ntos=lambda v: str(round(v)))
                f.gs[f.orden[info.codepoint]].draw(pen)
                self.glifos[gid] = pen.getCommands()
            if self.glifos[gid]:
                gx = x0 + (cx + pos.x_offset) * s
                usos.append(f'<use href="#{gid}" transform="translate({gx:.1f} {y - pos.y_offset * s:.1f}) scale({s:.5f} {-s:.5f})"/>')
            cx += pos.x_advance
        return f'<g fill="{fill}">{"".join(usos)}</g>'

    def svg(self, w, h, cuerpo, alt, extra=""):
        defs = "".join(f'<path id="{k}" d="{d}"/>' for k, d in self.glifos.items() if d)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
                f'aria-label="{html.escape(alt)}"><title>{html.escape(alt)}</title>{extra}<defs>{defs}</defs>{cuerpo}</svg>')


def parte(t, size, maxw, w=400):
    f = fuente(w)
    lineas, cur = [], ""
    for p in t.split():
        prueba = (cur + " " + p).strip()
        if cur and f.ancho(prueba, size) > maxw:
            lineas.append(cur); cur = p
        else:
            cur = prueba
    return lineas + [cur]


def parrafo(L, x, y, t, size, fill, maxw, lh=1.45):
    lineas = parte(t, size, maxw)
    return "".join(L.texto(x, y + i * size * lh, l, size, fill) for i, l in enumerate(lineas)), y + (len(lineas) - 1) * size * lh


def escribe(nombre, contenido):
    with open(os.path.join(ASSETS, nombre), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(contenido)


# ───────────────────────── content (English and Spanish). Sources: the CV, npm, GitHub.
TXT = {
    "en": dict(
        sub_banner="Software engineer · San Luis Potosí, Mexico",
        alt_banner="Montserrat Ximena Hernández Gallegos · Software engineer · San Luis Potosí, Mexico",
        mpg=dict(sub="Open-source MCP server · TypeScript · Node.js", l1="The problem",
                 t1=("At work, the main system is a legacy monolith and the first rule is: don't break production. I wanted to use "
                     "the best AI tools, but I had to know exactly what was being built at every step. And when I switched machines, "
                     "I lost the whole conversation."),
                 l2="What I built",
                 t2=("An MCP server that makes the agent work in 5 gated phases and write each one down before it touches code. "
                     "The server checks every commit against git. It started as a few prompts I kept reusing and grew one need at a time."),
                 cifras=[("1,400+", "tests on Linux, Windows and macOS"), ("0", "path escapes in 273 attack cases"),
                         ("v4.0.0", "on npm, with provenance"), ("13", "MCP tools")],
                 alt=("mcp-phase-gate, open-source MCP server in TypeScript and Node.js. It makes an AI agent work in 5 gated phases "
                      "and document each one before touching code. 1,400+ tests on Linux, Windows and macOS, 0 path escapes in 273 "
                      "attack cases, v4.0.0 on npm with provenance, 13 MCP tools.")),
        pw=dict(sub="Independent research · TypeScript · Astro", l1="How it started",
                t1=("I watched a video about the prisoner's dilemma and wondered what happens if you add more variants. There were "
                    "a thousand. The psychology is what hooked me, and I wanted a portfolio project I really cared about instead of "
                    "a generic CRUD app."),
                l2="What came out of it",
                t2=("A working paper on SSRN, backed by a deterministic simulation engine archived on Zenodo, and an illustrated "
                    "bilingual site that explains it."),
                cifras=[("2", "DOIs: SSRN and Zenodo"), ("R1–R6", "results reproduce with one command"),
                        ("~1,400", "tests on the site"), ("EN · ES", "bilingual site")],
                alt=("Promises to Whom, independent research in TypeScript and Astro. A working paper on SSRN backed by a "
                     "deterministic simulation engine on Zenodo, both with DOI. Results R1 to R6 reproduce with one command. "
                     "An illustrated bilingual site with about 1,400 tests.")),
        cats=["Languages", "Backend", "AI & integrations", "Frontend", "Data", "Testing & DevOps"],
        alt_stack="Tools I work with.",
        act=("{total} contributions in the last year", "{priv} of them in private repos · updated {fecha}", "fewer", "more", "last 26 weeks"),
        alt_act="Contribution graph: {total} contributions in the last year, {priv} of them in private repos.",
        meses=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        fecha="{mes} {dia}, {anio}",
        botones={"lang": "Español", "cv": "CV", "linkedin": "LinkedIn", "mail": "Email", "npm": "npm", "demo": "Live demo",
                 "source": "Source", "site": "Website", "paper": "Paper · SSRN", "engine": "Engine · Zenodo"},
    ),
    "es": dict(
        sub_banner="Ingeniera de software · San Luis Potosí, México",
        alt_banner="Montserrat Ximena Hernández Gallegos · Ingeniera de software · San Luis Potosí, México",
        mpg=dict(sub="Servidor MCP open source · TypeScript · Node.js", l1="El problema",
                 t1=("En mi trabajo, el sistema principal es un monolito legacy y la primera regla es no romper producción. Quería "
                     "usar las mejores herramientas de IA, pero tenía que saber en todo momento qué se estaba construyendo. Y cuando "
                     "cambiaba de máquina, perdía toda la conversación."),
                 l2="Qué construí",
                 t2=("Un servidor MCP que obliga al agente a trabajar en 5 fases con compuerta y a documentar cada una antes de tocar "
                     "código. El servidor verifica cada commit contra git. Empezó como unos prompts que reutilizaba y fue creciendo "
                     "según lo que iba necesitando."),
                 cifras=[("1,400+", "pruebas en Linux, Windows y macOS"), ("0", "escapes de ruta en 273 casos de ataque"),
                         ("v4.0.0", "en npm, con provenance"), ("13", "tools MCP")],
                 alt=("mcp-phase-gate, servidor MCP open source en TypeScript y Node.js. Obliga a un agente de IA a trabajar en 5 "
                      "fases con compuerta y a documentar cada una antes de tocar código. 1,400+ pruebas en Linux, Windows y macOS, "
                      "0 escapes de ruta en 273 casos de ataque, v4.0.0 en npm con provenance, 13 tools MCP.")),
        pw=dict(sub="Investigación independiente · TypeScript · Astro", l1="Cómo empezó",
                t1=("Vi un video sobre el dilema del prisionero y me pregunté qué pasaría si se le agregaban más variantes. Había "
                    "mil. El lado psicológico fue el que me atrapó, y quería un proyecto para mi portafolio que de verdad me "
                    "apasionara, en lugar de un CRUD genérico."),
                l2="Qué salió de ahí",
                t2=("Un working paper en SSRN, respaldado por un motor de simulación determinista archivado en Zenodo, y un sitio "
                    "ilustrado y bilingüe que lo explica."),
                cifras=[("2", "DOI: SSRN y Zenodo"), ("R1–R6", "resultados que se reproducen con un comando"),
                        ("~1,400", "pruebas en el sitio"), ("EN · ES", "sitio bilingüe")],
                alt=("Promises to Whom, investigación independiente en TypeScript y Astro. Un working paper en SSRN respaldado por "
                     "un motor de simulación determinista en Zenodo, ambos con DOI. Los resultados R1 a R6 se reproducen con un "
                     "comando. Un sitio ilustrado y bilingüe con cerca de 1,400 pruebas.")),
        cats=["Lenguajes", "Backend", "IA e integraciones", "Frontend", "Datos", "Testing y DevOps"],
        alt_stack="Herramientas con las que trabajo.",
        act=("{total} contribuciones en el último año", "{priv} en repos privados · actualizado el {fecha}", "menos", "más",
             "últimas 26 semanas"),
        alt_act="Gráfica de contribuciones: {total} en el último año, {priv} en repos privados.",
        meses=["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"],
        fecha="{dia} {mes} {anio}",
        botones={"lang": "English", "cv": "CV", "linkedin": "LinkedIn", "mail": "Correo", "npm": "npm", "demo": "Demo",
                 "source": "Código", "site": "Sitio", "paper": "Paper · SSRN", "engine": "Motor · Zenodo"},
    ),
}
TITULOS = {"mpg": "mcp-phase-gate", "pw": "Promises to Whom"}
STACK = [["TypeScript", "PHP", "JavaScript", "SQL", "Python"],
         ["Laravel", "Livewire", "NestJS", "Node.js", "REST APIs"],
         ["MCP", "n8n", "Authorize.Net", "Stripe", "Twilio"],
         ["React", "Tailwind CSS", "Astro", "Vite", "Preact"],
         ["MySQL", "PostgreSQL", "TypeORM", "pandas", "scikit-learn"],
         ["Vitest", "node:test", "Playwright", "GitHub Actions", "Git"]]


# ───────────────────────── banner (E3 · commits as a metro map)
CSS_MOV = ("<style>@keyframes mv{from{offset-distance:0%}to{offset-distance:100%}}"
           ".mv{offset-rotate:0deg;animation:mv var(--d) linear var(--b) infinite}"
           "@media (prefers-reduced-motion:reduce){.mv{animation:none}}</style>")


def metro(L, P, etiquetas):
    R = random.Random(11)
    y0 = 150
    lineas = [(600, 860, 80, P["acc2"]), (700, 1000, 225, P["pink"]), (900, 1140, 80, P["acc2"])]
    principal = f"M560,{y0} L1175,{y0}"
    out = [f'<path d="{principal}" stroke="{P["acc"]}" stroke-width="5" stroke-linecap="round" fill="none"/>']
    caminos = []
    for a, b, y, c in lineas:
        dy = abs(y - y0)
        p = f"M{a},{y0} L{a + dy},{y} L{b - dy},{y} L{b},{y0}"; caminos.append(p)
        out.append(f'<path d="{p}" stroke="{c}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round" fill="none"/>')
        for x in range(a + dy + 20, b - dy - 5, 45):
            out.append(f'<circle cx="{x}" cy="{y}" r="5.5" fill="{P["bg"]}" stroke="{c}" stroke-width="2.5"/>')
    for x in range(580, 1175, 60):
        out.append(f'<circle cx="{x}" cy="{y0}" r="5.5" fill="{P["bg"]}" stroke="{P["acc"]}" stroke-width="2.5"/>')
    for p in caminos + [principal]:
        dur, ini = R.uniform(5, 8), -R.uniform(0, 5)
        quieto = (-ini / dur) % 1 * 100  # where the dot rests when motion is reduced
        out.append(f'<circle class="mv" r="4" fill="{P["ink"]}" style="offset-path:path(\'{p}\');'
                   f'offset-distance:{quieto:.0f}%;--d:{dur:.1f}s;--b:{ini:.2f}s"/>')
    if etiquetas:
        out.append(L.texto(600, 62, "feature", 12, P["muted"], mono=True) + L.texto(700, 258, "fix", 12, P["muted"], mono=True)
                   + L.texto(1100, 175, "main", 12, P["ink"], mono=True)
                   + L.texto(1160, 288, "main · feature · fix", 12, P["muted"], anchor="end", mono=True))
    return "".join(out)


def banner(idioma, tema, var):
    P, t, L = PAL[tema], TXT[idioma], Lienzo()
    if var == "wide":
        W, H = 1200, 300
        c = (metro(L, P, True) + L.texto(60, 104, "Montserrat Ximena", 40, P["ink"], 600)
             + L.texto(60, 152, "Hernández Gallegos", 40, P["ink"], 600) + L.texto(60, 190, t["sub_banner"], 18, P["muted"])
             + f'<rect x="60" y="210" width="48" height="3" rx="1.5" fill="{P["pink"]}"/>')
    else:
        W, H = 600, 360
        c = (L.texto(30, 60, "Montserrat Ximena", 42, P["ink"], 600) + L.texto(30, 108, "Hernández Gallegos", 42, P["ink"], 600)
             + L.texto(30, 142, t["sub_banner"], 21, P["muted"]) + f'<rect x="30" y="160" width="48" height="3" rx="1.5" fill="{P["pink"]}"/>'
             + f'<g transform="translate(-436 128) scale(.85)">{metro(L, P, False)}</g>')
    fondo = f'<rect width="{W}" height="{H}" rx="14" fill="{P["bg"]}"/>'
    return L.svg(W, H, fondo + c, t["alt_banner"], CSS_MOV)


# ───────────────────────── project cards
def tarjeta(idioma, clave, tema, var):
    P, d, L = PAL[tema], TXT[idioma][clave], Lienzo()
    i, m, a, pk = P["ink"], P["muted"], P["acc"], P["pink"]
    if var == "wide":
        W = 1000
        c = L.texto(44, 66, TITULOS[clave], 36, i, 600) + L.texto(44, 98, d["sub"], 18, m)
        y = 146
        c += L.texto(44, y, d["l1"].upper(), 13, pk, 600)
        p, y = parrafo(L, 44, y + 30, d["t1"], 18.5, i, 560); c += p
        y += 44
        c += L.texto(44, y, d["l2"].upper(), 13, pk, 600)
        p, y = parrafo(L, 44, y + 30, d["t2"], 18.5, i, 560); c += p
        H = max(int(y) + 40, 380)
        c += f'<path d="M650,40V{H - 40}" stroke="{P["line"]}" stroke-width="2"/>'
        paso = (H - 80) / 4
        for k, (n, l) in enumerate(d["cifras"]):
            yy = 40 + paso * k + paso / 2
            c += L.texto(684, yy + 4, n, 34, a, 600)
            for j, ln in enumerate(parte(l, 15.5, 280)):
                c += L.texto(684, yy + 30 + j * 20, ln, 15.5, m)
    else:
        W = 440
        c = L.texto(28, 52, TITULOS[clave], 28, i, 600) + L.texto(28, 78, d["sub"], 14.5, m)
        y = 116
        c += L.texto(28, y, d["l1"].upper(), 12, pk, 600)
        p, y = parrafo(L, 28, y + 26, d["t1"], 16.5, i, 384); c += p
        y += 36
        c += L.texto(28, y, d["l2"].upper(), 12, pk, 600)
        p, y = parrafo(L, 28, y + 26, d["t2"], 16.5, i, 384); c += p
        y += 30
        c += f'<path d="M28,{y:.0f}H412" stroke="{P["line"]}" stroke-width="2"/>'
        yy = y + 50
        for fila_ in (d["cifras"][:2], d["cifras"][2:]):  # each row is as tall as its longest label
            lineas = [parte(l, 14, 175) for _, l in fila_]
            for k, (n, _) in enumerate(fila_):
                x = 28 + k * 200
                c += L.texto(x, yy, n, 28, a, 600)
                for j, ln in enumerate(lineas[k]):
                    c += L.texto(x, yy + 24 + j * 18, ln, 14, m)
            yy += 24 + max(map(len, lineas)) * 18 + 30
        H = int(yy + 4)
    caja = (f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{P["bg"]}" stroke="{P["line"]}" stroke-width="2"/>'
            f'<rect x="1" y="1" width="8" height="{H - 2}" rx="4" fill="{pk}"/>')
    return L.svg(W, H, caja + c, d["alt"])


# ───────────────────────── tools
def stack(idioma, tema, var):
    P, t, L = PAL[tema], TXT[idioma], Lienzo()
    i, m = P["ink"], P["muted"]
    alt = t["alt_stack"] + " " + " ".join(f"{n}: {', '.join(it)}." for n, it in zip(t["cats"], STACK))
    c = ""
    if var == "wide":
        W, H = 1000, 210
        for k, (n, it) in enumerate(zip(t["cats"], STACK)):
            x, y = 20 + (k % 3) * 330, 40 + (k // 3) * 96
            c += L.texto(x, y, n.upper(), 13, m, 600, mono=True)
            c += L.texto(x, y + 30, " · ".join(it[:3]), 19, i) + L.texto(x, y + 56, " · ".join(it[3:]), 19, i)
    else:
        W, H = 440, 545
        for k, (n, it) in enumerate(zip(t["cats"], STACK)):
            x, y = 16 + (k % 2) * 214, 30 + (k // 2) * 178
            c += L.texto(x, y, n.upper(), 12, m, 600, mono=True)
            for j, s in enumerate(it):
                c += L.texto(x, y + 28 + j * 25, s, 17.5, i)
    return L.svg(W, H, c, alt)


# ───────────────────────── activity
def token():
    if os.environ.get("GITHUB_TOKEN"):
        return os.environ["GITHUB_TOKEN"]
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def actividad_datos():
    q = ('{user(login:"%s"){contributionsCollection{restrictedContributionsCount contributionCalendar{totalContributions '
         'weeks{contributionDays{contributionCount}}}}}}' % USUARIO)
    req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": q}).encode(),
                                 {"Authorization": f"bearer {token()}", "Content-Type": "application/json"})
    u = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]
    semanas = [[d["contributionCount"] for d in w["contributionDays"]] for w in u["contributionCalendar"]["weeks"]]
    return semanas, u["contributionCalendar"]["totalContributions"], u["restrictedContributionsCount"]


def actividad(idioma, tema, var, datos, hoy):
    semanas, total, priv = datos
    P, t, L = PAL[tema], TXT[idioma], Lienzo()
    f = t["fecha"].format(mes=t["meses"][hoy.month - 1], dia=hoy.day, anio=hoy.year)
    total_s, priv_s = f"{total:,}", f"{priv:,}"
    niveles = [P["line"], P["acc2"], P["acc"], P["pink"]]
    color = lambda n: niveles[0] if n == 0 else niveles[1] if n < 6 else niveles[2] if n < 20 else niveles[3]
    if var == "wide":
        W, cel, gap, x0, y0, sem = 1000, 14, 3.4, 40, 74, semanas
    else:
        W, cel, gap, x0, y0, sem = 440, 12.5, 2.8, 22, 74, semanas[-26:]
    c = L.texto(x0, 34, t["act"][0].format(total=total_s), 20 if var == "wide" else 17, P["ink"], 600)
    c += L.texto(x0, 58, t["act"][1].format(priv=priv_s, fecha=f), 14 if var == "wide" else 13, P["muted"])
    for k, w in enumerate(sem):
        for d, n in enumerate(w):
            c += f'<rect x="{x0 + k * (cel + gap):.1f}" y="{y0 + d * (cel + gap):.1f}" width="{cel}" height="{cel}" rx="3" fill="{color(n)}"/>'
    H = int(y0 + 7 * (cel + gap) + 44)
    ly, lx = H - 22, x0
    c += L.texto(lx, ly + 4, t["act"][2], 12, P["muted"], mono=True); lx += fuente(mono=True).ancho(t["act"][2], 12) + 10
    for col in niveles:
        c += f'<rect x="{lx:.1f}" y="{ly - 8}" width="12" height="12" rx="3" fill="{col}"/>'; lx += 17
    c += L.texto(lx + 6, ly + 4, t["act"][3], 12, P["muted"], mono=True)
    if var == "tall":
        c += L.texto(W - 22, ly + 4, t["act"][4], 12, P["muted"], anchor="end", mono=True)
    return L.svg(W, H, c, t["alt_act"].format(total=total_s, priv=priv_s))


# ───────────────────────── buttons
def boton(texto, tema):
    P, L = PAL[tema], Lienzo()
    size, pad, h = 26, 26, 56
    w = fuente().ancho(texto, size) + pad * 2 + 22
    c = (f'<rect x="1.5" y="1.5" width="{w - 3:.0f}" height="{h - 3}" rx="{(h - 3) / 2}" fill="{P["bg"]}" stroke="{P["line"]}" stroke-width="2"/>'
         f'<circle cx="{pad + 4}" cy="{h / 2}" r="5" fill="{P["pink"]}"/>' + L.texto(pad + 22, 37, texto, size, P["ink"]))
    return L.svg(int(w), h, c, texto)


def main():
    os.makedirs(ASSETS, exist_ok=True)
    solo_actividad = "--actividad" in sys.argv
    datos, hoy = actividad_datos(), datetime.date.today()
    for idioma in TXT:
        for tema in PAL:
            for var in ("wide", "tall"):
                escribe(f"activity-{var}-{tema}.{idioma}.svg", actividad(idioma, tema, var, datos, hoy))
                if solo_actividad:
                    continue
                escribe(f"banner-{var}-{tema}.{idioma}.svg", banner(idioma, tema, var))
                escribe(f"stack-{var}-{tema}.{idioma}.svg", stack(idioma, tema, var))
                for clave in TITULOS:
                    escribe(f"card-{clave}-{var}-{tema}.{idioma}.svg", tarjeta(idioma, clave, tema, var))
            if not solo_actividad:
                for k, texto in TXT[idioma]["botones"].items():
                    escribe(f"btn-{k}-{tema}.{idioma}.svg", boton(texto, tema))
    print(f"ok · {datos[1]:,} contributions")


if __name__ == "__main__":
    main()
