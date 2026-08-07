#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cierra una tarea del plan en el panel de estado.

POR QUE EXISTE
    Cerrar una tarea son tres escrituras: el commit, las horas reales en
    Registro_Horas.md y el estado en el panel. Tres cosas que se olvidan por
    separado. Esto las convierte en un solo gesto deliberado.

QUE HACE
    1. Lista las tareas abiertas y te deja elegir una.
    2. Te muestra su CRITERIO DE TERMINO y te obliga a confirmar que lo
       verificaste. Ese paso es el punto del programa: sin criterio
       verificado la tarea no esta cerrada, por mas codigo que tenga.
    3. Pide las horas reales.
    4. Marca la tarea como cerrada en el panel.
    5. Imprime la linea ya formateada para que la pegues en
       Registro_Horas.md. No reescribe ese archivo: su formato varia por
       bloque y es el insumo de la decision D6; un script que lo edite mal
       corrompe el dato que mas importa.
"""

import re
import sys
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PANEL = AQUI / "index.html"

RE_TAREA = re.compile(
    r'\{id:"(T\d\.\d{1,2})",\s*t:"([^"]*)",\s*h:([\d.]+),\s*e:"(\w+)",\s*c:"([^"]*)"\}'
)
RE_BLOQUE = re.compile(r'\{\s*id:"(B\d)",\s*nombre:"([^"]*)"')

ETIQUETA = {"done": "cerrada", "wip": "en curso", "todo": "pendiente", "cut": "fuera de alcance"}


def leer_tareas(html):
    """Lista de dicts en el orden en que aparecen, con su bloque."""
    tareas, bloque = [], "?"
    for linea in html.splitlines():
        mb = RE_BLOQUE.search(linea)
        if mb:
            bloque = mb.group(1)
        for m in RE_TAREA.finditer(linea):
            tareas.append({
                "id": m.group(1), "titulo": m.group(2), "h": float(m.group(3)),
                "estado": m.group(4), "criterio": m.group(5), "bloque": bloque,
            })
    return tareas


def preguntar(texto, validas=None):
    try:
        r = input(texto).strip()
    except (EOFError, KeyboardInterrupt):
        print("\n\n  Cancelado. No se toco nada.\n")
        sys.exit(0)
    if validas and r.lower() not in validas:
        return None
    return r


def envolver(texto, ancho=66, sangria="     "):
    palabras, linea, salida = texto.split(), "", []
    for p in palabras:
        if len(linea) + len(p) + 1 > ancho:
            salida.append(sangria + linea)
            linea = p
        else:
            linea = f"{linea} {p}".strip()
    if linea:
        salida.append(sangria + linea)
    return "\n".join(salida)


def main():
    if not PANEL.exists():
        print(f"\n  ERROR: no encuentro el panel en {PANEL}\n")
        sys.exit(1)

    html = PANEL.read_text(encoding="utf-8")
    tareas = leer_tareas(html)
    abiertas = [t for t in tareas if t["estado"] in ("todo", "wip")]

    print()
    print("=" * 70)
    print("  CERRAR UNA TAREA DEL PLAN")
    print("=" * 70)

    if not abiertas:
        print("\n  No queda ninguna tarea abierta en el panel.\n")
        return

    # las en curso primero: son las que tienen commits
    abiertas.sort(key=lambda t: (t["estado"] != "wip",))
    print()
    for i, t in enumerate(abiertas[:15], 1):
        marca = "*" if t["estado"] == "wip" else " "
        print(f"  {marca} {i:2}. {t['id']:6} {t['titulo'][:52]:52} {t['h']:>4} h")
    if len(abiertas) > 15:
        print(f"       ... y {len(abiertas) - 15} mas")
    print("\n  (*) tiene commits: el proceso nocturno la marco en curso")

    r = preguntar("\n  Numero de la tarea a cerrar (Enter para salir): ")
    if not r:
        print("\n  Cancelado. No se toco nada.\n")
        return
    if not r.isdigit() or not (1 <= int(r) <= len(abiertas[:15])):
        print("\n  Numero fuera de rango. No se toco nada.\n")
        return

    t = abiertas[int(r) - 1]

    # --- el paso que importa ---
    print()
    print("-" * 70)
    print(f"  {t['id']} — {t['titulo']}")
    print("-" * 70)
    print("\n  CRITERIO DE TERMINO:\n")
    print(envolver(t["criterio"]))
    print()
    print("  La regla del proyecto: ninguna tarea se cierra sin verificar su")
    print("  criterio en el navegador real, no solo con tests.")
    print()

    ok = preguntar("  Verificaste esto en el navegador real? (si/no): ", {"si", "sí", "no", "s", "n"})
    if ok is None or ok.lower() in ("no", "n"):
        print("\n  Entonces la tarea no esta cerrada. No se toco nada.")
        print("  Verifica el criterio y vuelve a ejecutar esto.\n")
        return

    # --- horas ---
    hr = preguntar(f"\n  Horas reales de {t['id']} (estimado: {t['h']} h): ")
    try:
        horas = float((hr or "").replace(",", "."))
        if horas <= 0:
            raise ValueError
    except ValueError:
        print("\n  Eso no es un numero de horas valido. No se toco nada.\n")
        return

    # --- escribir el panel ---
    patron = re.compile(rf'(\{{id:"{re.escape(t["id"])}".*?e:")(?:todo|wip)(")', re.S)
    html_nuevo, n = patron.subn(r"\1done\2", html, count=1)
    if not n:
        print(f"\n  ERROR: no pude encontrar {t['id']} para modificarlo.\n")
        return

    hoy = date.today().isoformat()
    html_nuevo = re.sub(r'(actualizado:\s*")[\d-]+(")', rf"\g<1>{hoy}\g<2>", html_nuevo, count=1)
    html_nuevo = re.sub(r'(hoy:\s*")[\d-]+(")', rf"\g<1>{hoy}\g<2>", html_nuevo, count=1)
    PANEL.write_text(html_nuevo, encoding="utf-8")

    # --- resultado ---
    desvio = horas - t["h"]
    signo = "por debajo de" if desvio < 0 else "por sobre" if desvio > 0 else "igual a"
    ratio = t["h"] / horas if horas else 0

    print()
    print("=" * 70)
    print(f"  {t['id']} cerrada en el panel.")
    print("=" * 70)
    print(f"\n  Estimado {t['h']} h · real {horas} h · "
          f"{abs(desvio):.1f} h {signo} lo estimado (ratio {ratio:.1f}x)")

    # --- linea para Registro_Horas.md ---
    nota = "" if abs(desvio) < 0.5 else ("mas rapido de lo estimado" if desvio < 0 else "mas lento de lo estimado")
    linea = f"| {t['id']} | {t['titulo']} | {t['h']:g} h | **{horas:g} h** | {nota} |"
    print("\n  PEGA ESTA LINEA EN Registro_Horas.md (bloque "
          f"{t['bloque']}):\n")
    print(f"  {linea}")
    print()

    # --- cierre de bloque ---
    restantes = [x for x in leer_tareas(PANEL.read_text(encoding="utf-8"))
                 if x["bloque"] == t["bloque"] and x["estado"] in ("todo", "wip")]
    if not restantes:
        print("  " + "!" * 66)
        print(f"  Con esta, el bloque {t['bloque']} queda COMPLETO.")
        print(f"  Anota tambien el total real del bloque en Registro_Horas.md")
        print(f"  y ponlo en el panel:  real: <horas>  del bloque {t['bloque']}.")
        print("  " + "!" * 66)
        print()

    print("  Falta publicar: doble clic en publicar.bat")
    print("  (o espera al proceso nocturno)\n")


if __name__ == "__main__":
    main()
