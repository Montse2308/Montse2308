"""Writes README.md (English) and README.es.md (Spanish) from one template, so both always say the same thing.

Only the banner and the activity grid are images. Everything that is read (links, paragraphs, numbers, tools) is
real text, so it stays sharp on any screen. The activity numbers come from assets/activity.json, which
generar.py --actividad refreshes; the monthly Action runs both scripts.
"""
import datetime
import html
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from generar import SECCIONES, STACK, TITULOS, TXT  # noqa: E402

RAW = "https://github.com/Montse2308/Montse2308/raw/main/"  # /raw/ makes GitHub download the file
LINKS = {
    "linkedin": "https://www.linkedin.com/in/montserrat-ximena-hernandez-gallegos",
    "mail": "mailto:gallegos230804@gmail.com",
    "npm": "https://www.npmjs.com/package/mcp-phase-gate",
    "demo": "https://montse2308.github.io/mcp-phase-gate/demo/",
    "mpg": "https://github.com/Montse2308/mcp-phase-gate",
    "site": "https://whykeepapromise.org",
    "paper": "https://doi.org/10.2139/ssrn.7580218",
    "engine": "https://doi.org/10.5281/zenodo.23222610",
    "engine_src": "https://github.com/Montse2308/promises-to-whom-engine",
}

TEXTO = {
    "en": dict(
        archivo="README.md", otro="README.es.md", cv="CV_HernandezGallegos_Montserrat_EN_GitHub.pdf",
        quien=("I'm a software engineer from San Luis Potosí, Mexico. I work full stack on internal systems, mostly on the "
               "backend: payment integrations, REST APIs and webhooks, and AI agents connected through MCP. I've always said "
               "I'm not a programmer, I'm an engineer, and an engineer solves problems. For me that means understanding the "
               "problem before writing code, and when something in my work keeps repeating, building something to fix it."),
        h_proy="Projects", h_stack="Tools I work with", h_act="Activity",
        edu="B.Eng. in Intelligent Systems Engineering, UASLP · CENEVAL Award for Excellence (EGEL national exit exam)",
        personal="Outside of code: football, rugby and the gym, poetry and philosophy, physics, and being outdoors.",
    ),
    "es": dict(
        archivo="README.es.md", otro="README.md", cv="CV_HernandezGallegos_Montserrat_ES_GitHub.pdf",
        quien=("Soy ingeniera de software, de San Luis Potosí, México. Trabajo full stack en sistemas internos, sobre todo en el "
               "backend: integraciones de pago, REST APIs y webhooks, y agentes de IA conectados por MCP. Siempre he dicho que no "
               "soy programadora, soy ingeniera, y un ingeniero resuelve problemas. Para mí eso significa entender el problema "
               "antes de escribir código y, cuando algo en mi trabajo se repite, construir algo que lo resuelva."),
        h_proy="Proyectos", h_stack="Herramientas con las que trabajo", h_act="Actividad",
        edu="Ingeniería en Sistemas Inteligentes, UASLP · Premio Ceneval al Desempeño de Excelencia-EGEL",
        personal="Fuera del código: fútbol, rugby y gym, poesía y filosofía, física, y el aire libre.",
    ),
}


def pic(base, idioma, alt):
    a = f"assets/{base}"
    return (f'<picture><source media="(prefers-color-scheme: dark) and (max-width: 600px)" srcset="{a}-tall-dark.{idioma}.svg">'
            f'<source media="(prefers-color-scheme: dark)" srcset="{a}-wide-dark.{idioma}.svg">'
            f'<source media="(max-width: 600px)" srcset="{a}-tall-light.{idioma}.svg">'
            f'<img src="{a}-wide-light.{idioma}.svg" alt="{html.escape(alt)}" width="100%"></picture>')


def enlaces(idioma, *pares):
    b = TXT[idioma]["botones"]
    return " · ".join(f"[{b[k]}]({l})" for k, l in pares)


def cifras(lista):
    """2 x 2 table: it stays readable on a phone, where 4 columns get squeezed."""
    celdas = [f'<td width="50%" valign="top"><b>{html.escape(n)}</b><br>{html.escape(l)}</td>' for n, l in lista]
    filas = "".join(f"<tr>{celdas[k]}{celdas[k + 1]}</tr>\n" for k in range(0, len(celdas), 2))
    return f"<table>\n{filas}</table>"


def proyecto(idioma, clave, links):
    """Card image (name and numbers, large type only), then the paragraphs as real text, then the links."""
    d = TXT[idioma][clave]
    alt = f"{TITULOS[clave]}, {d['sub']}. " + "; ".join(f"{n} {l}" for n, l in d["cifras"]) + "."
    return (f"{pic('card-' + clave, idioma, alt)}\n\n**{d['l1']}.** {d['t1']}\n\n**{d['l2']}.** {d['t2']}\n\n"
            f"{enlaces(idioma, *links)}")


def seccion(idioma, clave):
    texto = dict(SECCIONES[idioma])[clave]
    return pic(f"h-{clave}", idioma, texto)


def herramientas(idioma):
    celdas = [f'<td width="50%" valign="top"><b>{html.escape(n)}</b><br>{" ".join(f"<kbd>{html.escape(i)}</kbd>" for i in it)}</td>'
              for n, it in zip(TXT[idioma]["cats"], STACK)]
    filas = "".join(f"<tr>{celdas[k]}{celdas[k + 1]}</tr>\n" for k in range(0, len(celdas), 2))
    return f"<table>\n{filas}</table>"


def actividad(idioma):
    with open(os.path.join(RAIZ, "assets", "activity.json"), encoding="utf-8") as fh:
        a = json.load(fh)
    t, f = TXT[idioma], datetime.date.fromisoformat(a["fecha"])
    fecha = t["fecha"].format(mes=t["meses"][f.month - 1], dia=f.day, anio=f.year)
    total, priv = f"{a['total']:,}", f"{a['priv']:,}"
    return (f"**{t['act'][0].format(total=total)}**<br>\n"
            f"<sub>{t['act'][1].format(priv=priv, fecha=fecha)}</sub>\n\n"
            f"{pic('activity', idioma, t['alt_act'].format(total=total, priv=priv))}")


def readme(idioma):
    t, x = TEXTO[idioma], TXT[idioma]
    mpg = proyecto(idioma, "mpg", (("npm", LINKS["npm"]), ("demo", LINKS["demo"]), ("source", LINKS["mpg"])))
    pw = proyecto(idioma, "pw", (("site", LINKS["site"]), ("paper", LINKS["paper"]),
                                 ("engine", LINKS["engine"]), ("source", LINKS["engine_src"])))
    return f"""{pic("banner", idioma, x["alt_banner"])}

<div align="center">

{enlaces(idioma, ("lang", t["otro"]), ("cv", RAW + t["cv"]), ("linkedin", LINKS["linkedin"]), ("mail", LINKS["mail"]))}

</div>

{t["quien"]}

{seccion(idioma, "projects")}

{mpg}

{pw}

{seccion(idioma, "tools")}

{herramientas(idioma)}

{seccion(idioma, "activity")}

{actividad(idioma)}

<sub>{t["edu"]}<br>{t["personal"]}</sub>
"""


if __name__ == "__main__":
    for idioma, t in TEXTO.items():
        with open(os.path.join(RAIZ, t["archivo"]), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(readme(idioma))
    print("ok")
