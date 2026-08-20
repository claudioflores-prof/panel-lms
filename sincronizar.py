#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincroniza el panel de estado con el historial de git del repo del sistema.

QUE HACE
    Lee los mensajes de commit del repositorio padre, extrae los ids de tarea
    (T0.1, T1.2, ...) y marca esas tareas como "en curso" en el panel.

QUE NO HACE, A PROPOSITO
    Nunca marca una tarea como CERRADA. Un commit demuestra que hay codigo
    escrito, no que el criterio de termino se haya verificado en el navegador
    real. Cerrar una tarea sigue siendo una decision tuya: se escribe a mano
    e:"done" en index.html.
    Tampoco toca las horas reales: git no sabe cuanto tiempo te tomo algo, y
    esa es justamente la cifra de la que depende la decision D6.

USO
    python sincronizar.py            actualiza el panel
    python sincronizar.py --simular  muestra que haria, sin escribir nada
"""

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PANEL = AQUI / "index.html"
REPO = AQUI.parent                      # el repo del sistema, una carpeta arriba
RECORDATORIO = AQUI / "pendientes_de_cierre.txt"

SIMULAR = "--simular" in sys.argv or "--dry-run" in sys.argv

# El id cuenta como trabajo SOLO si abre el mensaje del commit ("T0.11: ...").
# Es la convencion real del proyecto y evita falsos positivos: el commit
# "D13: ... tabla Activity en T4.1" MENCIONA T4.1, no la trabaja.
# El bloque puede ser un digito (T4.13) o la R del Bloque R de retrabajo
# (TR.1), creado por D40 el 19 ago 2026. Sin la R, el panel era ciego
# justamente al bloque que existe para que el retrabajo no se pierda de vista.
PATRON_INICIO = re.compile(r"^\s*T([R\d])\.(\d{1,2})\b")
# Cualquier mencion, para reportarla aparte sin actuar sobre ella.
PATRON_MENCION = re.compile(r"\bT([R\d])\.(\d{1,2})\b")


def salir(msg, codigo=1):
    print(f"\n  ERROR: {msg}\n")
    sys.exit(codigo)


def ids_en_los_commits():
    """Devuelve (trabajadas, solo_mencionadas).

    trabajadas       {id: fecha}  el id abre el mensaje del commit
    solo_mencionadas {id: fecha}  el id aparece de pasada, no se actua sobre el
    """
    try:
        salida = subprocess.run(
            ["git", "log", "--pretty=format:%ad|%s", "--date=short"],
            cwd=REPO, capture_output=True, text=True, encoding="utf-8", timeout=60,
        )
    except FileNotFoundError:
        salir("no encuentro git. Instalalo o revisa el PATH.")
    except subprocess.TimeoutExpired:
        salir("git no respondio en 60 segundos.")

    if salida.returncode != 0:
        salir(f"git log fallo en {REPO}:\n{salida.stderr.strip()}")

    trabajadas, mencionadas = {}, {}
    for linea in salida.stdout.splitlines():
        if "|" not in linea:
            continue
        fecha, mensaje = linea.split("|", 1)
        # git log va de lo mas nuevo a lo mas viejo: el primero que aparece
        # es el commit mas reciente de esa tarea
        m = PATRON_INICIO.match(mensaje)
        if m:
            trabajadas.setdefault(f"T{m.group(1)}.{m.group(2)}", fecha)
        for bloque, num in PATRON_MENCION.findall(mensaje):
            tid = f"T{bloque}.{num}"
            if not (m and tid == f"T{m.group(1)}.{m.group(2)}"):
                mencionadas.setdefault(tid, fecha)
    # una tarea trabajada no se reporta ademas como simple mencion
    mencionadas = {k: v for k, v in mencionadas.items() if k not in trabajadas}
    return trabajadas, mencionadas


def estado_actual(html, tid):
    """Devuelve el estado de esa tarea en el panel, o None si no existe."""
    m = re.search(rf'\{{id:"{re.escape(tid)}".*?e:"(\w+)"', html, re.S)
    return m.group(1) if m else None


def marcar_en_curso(html, tid):
    """Pasa una tarea de todo a wip. No toca done ni cut."""
    patron = re.compile(rf'(\{{id:"{re.escape(tid)}".*?e:")todo(")', re.S)
    return patron.subn(r"\1wip\2", html, count=1)


def actualizar_fechas(html, hoy):
    html = re.sub(r'(actualizado:\s*")[\d-]+(")', rf"\g<1>{hoy}\g<2>", html, count=1)
    html = re.sub(r'(hoy:\s*")[\d-]+(")', rf"\g<1>{hoy}\g<2>", html, count=1)
    return html


def main():
    print()
    print("=" * 60)
    print("  Sincronizando el panel con el historial de git")
    if SIMULAR:
        print("  MODO SIMULACION: no se escribe nada")
    print("=" * 60)

    if not PANEL.exists():
        salir(f"no encuentro el panel en {PANEL}")
    if not (REPO / ".git").exists():
        salir(f"{REPO} no parece un repositorio git")

    html = PANEL.read_text(encoding="utf-8")
    original = html
    commits, mencionadas = ids_en_los_commits()

    if not commits:
        print("\n  Ningun commit empieza con un id de tarea.")
        print("  Convencion del proyecto: un commit por tarea, con el id al inicio")
        print('  del mensaje. Ejemplo:  "T1.1: Postgres local y rol de la app"\n')
        return

    print(f"\n  Tareas con commits propios: {len(commits)}\n")

    cambiadas, ya_cerradas, en_curso, desconocidas = [], [], [], []

    for tid in sorted(commits, key=lambda t: (t[1], float(t.split(".")[1]))):
        estado = estado_actual(html, tid)
        if estado is None:
            desconocidas.append(tid)
        elif estado == "done":
            ya_cerradas.append(tid)
        elif estado == "cut":
            pass                                  # fuera de alcance, se ignora
        elif estado == "wip":
            en_curso.append(tid)
        else:                                     # todo -> wip
            html, n = marcar_en_curso(html, tid)
            if n:
                cambiadas.append(tid)

    if cambiadas:
        print("  Pasan a EN CURSO:")
        for t in cambiadas:
            print(f"     {t}   (ultimo commit: {commits[t]})")
        print()
    if en_curso:
        print(f"  Ya estaban en curso: {', '.join(en_curso)}\n")
    if ya_cerradas:
        print(f"  Ya cerradas, sin tocar: {', '.join(ya_cerradas)}\n")
    if desconocidas:
        print("  AVISO: ids en commits que no existen en el panel:")
        print(f"     {', '.join(desconocidas)}")
        print("     Puede ser un typo en el mensaje del commit, o una tarea")
        print("     que falta agregar al bloque DATOS.\n")
    if mencionadas:
        print("  Mencionadas de pasada, NO contadas como trabajo:")
        for t, f in sorted(mencionadas.items()):
            print(f"     {t}   (en un commit del {f})")
        print("     Un id en medio del mensaje suele ser una referencia, no")
        print("     trabajo hecho. Si si lo era, marcala a mano en el panel.\n")

    # --- recordatorio de cierre manual ---
    por_cerrar = cambiadas + en_curso
    if por_cerrar:
        texto = [
            "TAREAS CON COMMITS QUE SIGUEN SIN CERRAR",
            f"(generado el {date.today().isoformat()})",
            "",
            "El panel las muestra EN CURSO. Para pasarlas a cerradas hacen falta",
            "las tres escrituras: criterio verificado en el navegador real,",
            "horas en Registro_Horas.md, y e:\"done\" en Panel_Estado/index.html.",
            "",
        ]
        texto += [f"  {t}   ultimo commit: {commits[t]}" for t in por_cerrar]
        if not SIMULAR:
            RECORDATORIO.write_text("\n".join(texto) + "\n", encoding="utf-8")

    hoy = date.today().isoformat()
    html = actualizar_fechas(html, hoy)

    if html == original:
        print("  Sin cambios: el panel ya estaba al dia.\n")
        return

    if SIMULAR:
        print(f"  [simulacion] Se habrian aplicado {len(cambiadas)} cambios de estado")
        print(f"  [simulacion] y la fecha se habria puesto en {hoy}.\n")
        return

    PANEL.write_text(html, encoding="utf-8")
    print(f"  Panel actualizado. Fecha: {hoy}")
    if por_cerrar:
        print(f"  Recordatorio de cierre escrito en {RECORDATORIO.name}")
    print()


if __name__ == "__main__":
    main()
