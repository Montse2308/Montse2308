"""Writes README.md (English) and README.es.md (Spanish) from one template, so both always say the same thing.
Run it after generar.py whenever the text changes."""
import html
import os

import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from generar import TXT  # noqa: E402

LINKS = {
    "linkedin": "https://www.linkedin.com/in/montserrat-ximena-hern%C3%A1ndez-gallegos-536195276",
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


def btn(k, link, idioma):
    alt = TXT[idioma]["botones"][k]
    return (f'<a href="{link}"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/btn-{k}-dark.{idioma}.svg">'
            f'<img src="assets/btn-{k}-light.{idioma}.svg" alt="{html.escape(alt)}" height="28"></picture></a>')


def fila(idioma, *pares, align="left"):
    return f'<p align="{align}">\n' + "\n".join(btn(k, l, idioma) for k, l in pares) + "\n</p>"


def readme(idioma):
    t, x = TEXTO[idioma], TXT[idioma]
    return f"""{pic("banner", idioma, x["alt_banner"])}

{fila(idioma, ("lang", t["otro"]), ("cv", t["cv"]), ("linkedin", LINKS["linkedin"]), ("mail", LINKS["mail"]), align="center")}

{t["quien"]}

### {t["h_proy"]}

{pic("card-mpg", idioma, x["mpg"]["alt"])}

{fila(idioma, ("npm", LINKS["npm"]), ("demo", LINKS["demo"]), ("source", LINKS["mpg"]))}

{pic("card-pw", idioma, x["pw"]["alt"])}

{fila(idioma, ("site", LINKS["site"]), ("paper", LINKS["paper"]), ("engine", LINKS["engine"]), ("source", LINKS["engine_src"]))}

### {t["h_stack"]}

{pic("stack", idioma, x["alt_stack"])}

### {t["h_act"]}

{pic("activity", idioma, x["alt_act"].split(":")[0])}

<sub>{t["edu"]}<br>{t["personal"]}</sub>
"""


if __name__ == "__main__":
    for idioma, t in TEXTO.items():
        with open(os.path.join(RAIZ, t["archivo"]), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(readme(idioma))
    print("ok")
