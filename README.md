# Panel de estado — cómo mantenerlo y publicarlo

Panel de una página para contrastar el avance real contra el plan. Autocontenido: un solo `index.html`, sin dependencias, sin servidor. Se abre con doble clic.

---

## 1. Las dos vistas

El panel abre siempre en **Resumen ejecutivo**: hitos, proyección de fecha, calendario de bloques con su
porcentaje de avance, línea de contenido, riesgos y decisiones pendientes. Sin detalle de tareas.

El botón **Vista completa** agrega las 41 tareas con su criterio de término y las inconsistencias detectadas
en el plan. La vista queda registrada en la URL:

- `https://<usuario>.github.io/panel-lms/` → resumen ejecutivo
- `https://<usuario>.github.io/panel-lms/?v=full` → vista completa

El botón **Copiar link de esta vista** te da la dirección con la vista que estás viendo, para mandar a cada
audiencia la que corresponde. Imprimir (`Ctrl+P`) respeta la vista activa: el resumen ejecutivo sale en
formato de reunión, sin controles ni tablas de tareas.

**Por qué importa el orden.** El resumen es el estado por defecto a propósito: si dirección entra y lo primero
que ve son 41 tareas, la conversación se va al detalle de ejecución en vez de a las decisiones que solo ellos
pueden tomar. El detalle sigue estando a un clic para quien lo pida — la transparencia no se pierde, solo deja
de ser lo primero.

---

## 2. Cómo se actualiza

Todo lo editable está en el bloque `const DATOS = {...}` al inicio del `<script>`. Nada más hay que tocar.

**Al cerrar una tarea `Tx.y`:** buscar su línea y cambiar `e:"todo"` por `e:"done"`.

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

## 3. Cómo publicarlo en GitHub Pages

El repo del sistema es **privado**, y GitHub Pages sobre repos privados requiere plan de pago. Por eso este panel va en un **repo independiente y público**, exactamente igual que el MockUP.

### Antes de publicar: qué NO puede contener

El sitio queda accesible para cualquiera con el link y es indexable por buscadores. El panel ya está escrito sanitizado, pero al editarlo hay que mantener la regla:

- ❌ Nombre del colegio, de personas, correos institucionales.
- ❌ Subdominio de producción, IPs, rutas de servidor, nombres de usuario del sistema.
- ❌ Datos de estudiantes, de cualquier tipo.
- ❌ Frases de negociación interna sacadas de contexto ("no cabe", "el compromiso es inviable").
- ✅ Bloques, tareas, horas, fechas, riesgos formulados como riesgos de proyecto.

El `index.html` incluye `<meta name="robots" content="noindex, nofollow">`, que pide a los buscadores no indexarlo. Es una petición, no una garantía: no reemplaza la regla de arriba.

### Pasos

1. **Crear el repo en GitHub** (interfaz web, cuenta personal): nuevo repositorio público, nombre sugerido `panel-lms`, sin README ni `.gitignore`.

2. **Inicializar y subir.** Desde la carpeta `Panel_Estado/`, uno por uno:

   ```bash
   git init
   ```
   *Crea un repositorio git nuevo en esta carpeta. Sin riesgo; no toca el repo del sistema, que está una carpeta más arriba.*

   ```bash
   git add index.html README.md
   ```
   *Marca los dos archivos para el primer commit. Sin riesgo.*

   ```bash
   git commit -m "Panel de estado inicial"
   ```
   *Guarda la primera versión en el historial local. Sin riesgo.*

   ```bash
   git branch -M main
   ```
   *Renombra la rama a `main`, que es lo que GitHub Pages espera. Sin riesgo.*

   ```bash
   git remote add origin https://github.com/<tu-usuario>/panel-lms.git
   ```
   *Apunta este repo local al repo que creaste en GitHub. Sin riesgo; solo guarda una dirección.*

   ```bash
   git push -u origin main
   ```
   *Sube el contenido a GitHub. **Este es el comando que expone el contenido públicamente** — revisa antes que no haya datos sensibles, porque queda en el historial aunque después lo borres.*

3. **Activar Pages:** en el repo → `Settings` → `Pages` → Source: `Deploy from a branch` → rama `main`, carpeta `/ (root)` → `Save`. En 1–2 minutos queda disponible en `https://<tu-usuario>.github.io/panel-lms/`.

4. **Actualizaciones posteriores:** editar `index.html`, luego `git add index.html`, `git commit -m "Actualiza estado al <fecha>"`, `git push`. El sitio se refresca solo en un par de minutos.

### Aislarlo del repo del sistema

`Panel_Estado/` vive dentro de la carpeta del proyecto pero es un repo git aparte. Para que el repo privado no intente versionarlo, agregar al `.gitignore` del proyecto:

```
Panel_Estado/
```

Misma convención que `MockUP/`.

---

## 4. Advertencia sobre las cifras

Las horas pendientes son **estimaciones del plan técnico**, no compromisos. La única medición real hasta ahora es la del Bloque 0, y es del bloque más automatizable del proyecto — el panel lo dice explícitamente para que nadie proyecte con ese ratio.

La sección "Inconsistencias detectadas en el plan" documenta cuatro desalineaciones entre el plan y el registro de horas. Cuando se corrijan en los documentos fuente, hay que quitarlas de aquí.
