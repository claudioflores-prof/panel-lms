# Panel de estado — cómo mantenerlo y publicarlo

Panel de una página para contrastar el avance real contra el plan. Autocontenido: un solo `index.html`, sin dependencias, sin servidor. Se abre con doble clic.

---

## 1. Las dos vistas

El panel abre siempre en **Resumen ejecutivo**: hitos, proyección de fecha, calendario de bloques con su
porcentaje de avance, línea de contenido, riesgos y decisiones pendientes. Sin detalle de tareas.

El botón **Vista completa** agrega las 41 tareas con su criterio de término y las inconsistencias detectadas
en el plan. La vista queda registrada en la URL:

- <https://claudioflores-prof.github.io/panel-lms/> → resumen ejecutivo (para dirección)
- <https://claudioflores-prof.github.io/panel-lms/?v=full> → vista completa (para el equipo)

El botón **Copiar link de esta vista** te da la dirección con la vista que estás viendo, para mandar a cada
audiencia la que corresponde. Imprimir (`Ctrl+P`) respeta la vista activa: el resumen ejecutivo sale en
formato de reunión, sin controles ni tablas de tareas.

**Por qué importa el orden.** El resumen es el estado por defecto a propósito: si dirección entra y lo primero
que ve son 41 tareas, la conversación se va al detalle de ejecución en vez de a las decisiones que solo ellos
pueden tomar. El detalle sigue estando a un clic para quien lo pida — la transparencia no se pierde, solo deja
de ser lo primero.

---

## 2. El proceso nocturno automático

Cada noche, un proceso lee el historial de git del repo del sistema, busca los commits cuyo mensaje **empieza** con un id de tarea (`T1.1: ...`) y marca esas tareas como **en curso** en el panel. Después publica.

**Instalación (una sola vez):** doble clic en `instalar_tarea_nocturna.bat`. Pide confirmación antes de registrar nada. Hora por defecto: 22:30.

**Para probarlo sin esperar:** doble clic en `nocturno.bat`.

### Los tres límites, que son deliberados

**1. Nunca marca una tarea como cerrada.** Un commit demuestra que hay código escrito, no que el criterio de término se haya verificado en el navegador real. El cierre lo escribes tú a mano (`e:"done"`). Si el proceso cerrara tareas solo, el panel mostraría como terminado lo que está a medias — y ese panel lo mira dirección. La credibilidad del panel vale más que ahorrarte diez segundos.

**2. No sabe las horas.** Git registra qué tocaste, no cuánto tardaste. Y las horas son justamente la cifra de la que depende D6. `Registro_Horas.md` sigue siendo manual, sin alternativa.

**3. Solo cuenta el id si abre el mensaje.** El commit `D13: ... tabla Activity en T4.1` menciona T4.1 pero no la trabaja. El script reporta esas menciones aparte, sin actuar sobre ellas. Es la razón por la que conviene mantener la convención de poner el id al principio.

**Si el equipo está apagado a esa hora, la tarea no corre** y no se recupera sola. Como el script recalcula todo desde cero cada vez, la noche siguiente se pone al día — pero si vas a estar días sin encender el equipo, ejecuta `nocturno.bat` a mano al volver.

### Archivos que genera

| Archivo | Qué es |
|---|---|
| `nocturno.log` | Registro de cada ejecución nocturna |
| `publicar.log` | Registro del último `git push` |
| `pendientes_de_cierre.txt` | Tareas con commits que siguen sin cerrar — tu lista de las tres escrituras pendientes |

Los tres están en el `.gitignore` del panel: son locales y no se publican.

---

## 3. Cerrar una tarea

**Doble clic en `cerrar.bat`.** Te lista las tareas abiertas (las que tienen commits aparecen marcadas y primero), te muestra el **criterio de término** de la que elijas y te pide confirmar que lo verificaste. Si dices que no, no toca nada.

Después pide las horas reales, marca la tarea como cerrada en el panel, y te imprime la línea ya formateada para que la pegues en `Registro_Horas.md`. Si con esa tarea el bloque queda completo, te lo avisa para que anotes también el total del bloque.

**Por qué te muestra el criterio y no lo da por hecho:** es el único momento del flujo en que alguien revisa si la tarea está realmente terminada. Sin ese paso, cerrar sería un trámite y el panel acabaría mostrando a dirección como listo lo que está a medias.

**Por qué no escribe `Registro_Horas.md` solo:** ese archivo tiene formatos distintos por bloque y es el insumo de la decisión D6. Un script que lo reescriba mal corrompe el dato que más importa del proyecto. Prefiero que copies una línea.

### Alternativas

- **Claude Code**, siguiendo la regla de las tres escrituras de `CLAUDE.md`.
- **A mano:** en el bloque `const DATOS = {...}`, cambiar `e:"wip"` por `e:"done"`.

```js
{id:"T1.1", t:"Base de datos en el servidor...", h:1.5, e:"done", c:"..."}
```

**Al cerrar un bloque:** anotar las horas reales en el bloque correspondiente.

```js
{ id:"B1", nombre:"Despliegue base", semIni:3, semFin:4, real:5.5, ... }
```

**Siempre:** actualizar `actualizado` y `hoy` a la fecha del día.

Estados válidos por tarea: `"done"` (cerrada y verificada), `"wip"` (en curso), `"todo"` (pendiente), `"cut"` (eliminada del alcance; deja de contar horas y aparece tachada).

Todo lo demás —porcentajes, proyecciones de fecha, barras, línea de tiempo— se recalcula solo.

**Sugerencia de convención:** incorporarlo a la regla de "un commit por tarea". Al cerrar `Tx.y` se actualizan tres cosas: el código, el `Registro_Horas.md` y este panel. Si el panel no se actualiza en el mismo momento, en tres semanas nadie confía en él y se abandona.

---

## 4. Cómo publicarlo

**Ya está publicado.** Para cada actualización posterior basta con **doble clic en `publicar.bat`**: sube los cambios y el sitio se refresca solo en 1–2 minutos. Deja el detalle de lo ocurrido en `publicar.log`.

El resto de esta sección documenta cómo quedó montado, por si hay que rehacerlo.

- Repo: `claudioflores-prof/panel-lms`, **público**. El repo del sistema es privado y Pages sobre repos privados requiere plan de pago; por eso el panel va aparte, igual que el MockUP.
- Pages: `Settings` → `Pages` → `Deploy from a branch` → `main` + `/ (root)`.
- La dirección del remoto lleva el usuario delante (`https://claudioflores-prof@github.com/...`) **a propósito**: sin eso, git reutiliza las credenciales guardadas de la otra cuenta (`balker123456`) y el push falla con error 403 «Permission denied».

### Antes de publicar: qué NO puede contener

El sitio queda accesible para cualquiera con el link y es indexable por buscadores. El panel ya está escrito sanitizado, pero al editarlo hay que mantener la regla:

- ❌ Nombre del colegio, de personas, correos institucionales.
- ❌ Subdominio de producción, IPs, rutas de servidor, nombres de usuario del sistema.
- ❌ Datos de estudiantes, de cualquier tipo.
- ❌ Frases de negociación interna sacadas de contexto ("no cabe", "el compromiso es inviable").
- ✅ Bloques, tareas, horas, fechas, riesgos formulados como riesgos de proyecto.

El `index.html` incluye `<meta name="robots" content="noindex, nofollow">`, que pide a los buscadores no indexarlo. Es una petición, no una garantía: no reemplaza la regla de arriba.

### Si algún día hay que rehacerlo desde cero

1. Crear el repositorio en GitHub: **público**, sin README ni `.gitignore`.
2. Desde `Panel_Estado/`, ejecutar `publicar.bat` — hace `init`, `add`, `commit`, configura el remoto y hace `push`.
3. Activar Pages: `Settings` → `Pages` → `Deploy from a branch` → `main` + `/ (root)` → `Save`.

El paso irreversible es el `push`: lo que sube queda en el historial público aunque después se borre.

### Aislarlo del repo del sistema

`Panel_Estado/` vive dentro de la carpeta del proyecto pero es un repo git aparte. Para que el repo privado no intente versionarlo, agregar al `.gitignore` del proyecto:

```
Panel_Estado/
```

Misma convención que `MockUP/`.

---

## 5. Advertencia sobre las cifras

Las horas pendientes son **estimaciones del plan técnico**, no compromisos. La única medición real hasta ahora es la del Bloque 0, y es del bloque más automatizable del proyecto — el panel lo dice explícitamente para que nadie proyecte con ese ratio.

La sección "Inconsistencias detectadas en el plan" documenta cuatro desalineaciones entre el plan y el registro de horas. Cuando se corrijan en los documentos fuente, hay que quitarlas de aquí.
