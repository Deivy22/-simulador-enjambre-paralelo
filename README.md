# Simulador de Enjambre 2D (Boids) — Programación Funcional y Paralelismo Real

Simulador interactivo de enjambre en 2D basado en el algoritmo de **Boids** (Craig Reynolds), desarrollado en **Python 3.x** bajo **Programación Funcional estricta** (*Functional Core, Imperative Shell*), renderizado en **Pygame** (2 pantallas y layout limpio de 2 zonas) y acelerado con paralelismo real mediante **`multiprocessing`**.

---

## Arquitectura en 3 Capas (`data/` · `core/` · `ui/`)

El proyecto prohíbe el diseño monolítico, las clases con `self` mutable y las variables globales mutables. Todo el estado dinámico vive en una única estructura inmutable `GameState` (`@dataclass(frozen=True, slots=True)`), siguiendo un flujo unidireccional estricto:

```text
InputState (Congelado)
   │
   ▼
core/state/transitions.py      (Transiciones puras: START <-> SIMULATION, 1/3/5, M, +/-, R, Pausa)
   │
   ▼
core/engine/  o  core/parallel/ (Física pura + Grilla Espacial Inmutable O(N·k) + Pool.map)
   │
   ▼
Nuevo GameState (Congelado)    + MetricsSnapshot (Ventana móvil inmutable de 60 frames)
   │
   ▼
ui/ (Solo Lectura)             Canvas 2D (960×720)  |  Panel Lateral HUD (320×720)
```

### Fronteras de Dependencia (Verificadas Automáticamente por AST)
| Capa | Responsabilidad | Restricción de Imports |
| :--- | :--- | :--- |
| **`data/`** | Contratos inmutables (`Boid`, `FlatBoidSnapshot`, `SimConfig`, `InputState`, `MetricsSnapshot`, `GameState`, `Enum`). | Solo librería estándar de Python. Cero `core/`, `ui/` o `pygame`. |
| **`core/`** | Matemáticas 2D, reglas físicas Boids, Grilla Espacial Inmutable, transiciones puras, motor secuencial, pipeline paralelo (`multiprocessing`) y ciclo de vida headless del `Pool`. | Solo `stdlib` + `data/`. **Cero `ui/` y cero `pygame`.** |
| **`ui/`** | Pantalla de Inicio, Canvas 2D, Panel Lateral HUD, captura de eventos Pygame y Game Loop (`ui/app.py`). | Puede importar `data/` y `core/`. Prohibido calcular física o mutar entidades. |
| **`tests/` y `benchmarks/`** | Pruebas unitarias, equivalencia matemática, auditoría AST y benchmarks reproducibles (`dt = 1/60`). | 100% *headless* (cero `pygame`, cero `ui/`). |

---

## Modelo Físico y Pipeline Paralelo

### Reglas Físicas Puras (Boids)
Cada boid calcula en el instante $t$ cinco fuerzas puras sin mutar a ningún vecino:
1. **Separación ($\vec{F}_{sep}$):** Repulsión dentro de `separation_radius = 18.0 px` con piso de seguridad $\varepsilon = 1.0\text{ px}$ y reescalado $r_{sep}^2$ para evitar divisiones por cero y desbalances numéricos.
2. **Alineación ($\vec{F}_{ali}$):** Ajuste hacia la velocidad promedio de los vecinos en `perception_radius = 45.0 px`.
3. **Cohesión ($\vec{F}_{coh}$):** Atracción hacia el centro de masa local en `perception_radius`.
4. **Interacción del Cursor ($\vec{F}_{mouse}$):** Fuerza progresiva $(1 - d / r_{mouse})$ dentro de `150.0 px` solo cuando el cursor está sobre el Canvas (`960×720`), dando prioridad al repulsor si se presionan ambos botones.
5. **Límites Suaves + Respaldo (*Soft Boundaries* + *Hard Clamp*):** Giro progresivo dentro de `margin = 60.0 px` sobre el área `960×720`, más acotamiento seguro en `[0, 960] × [0, 720]` y velocidad en `[90, 220] px/s` protegida ante norma cero.

### Estrategia de Paralelismo (`multiprocessing`) y Optimización IPC
Ambos modos (**Secuencial** y **Paralelo**) ejecutan exactamente la misma **Grilla Espacial Inmutable** ($O(N \cdot k)$ representada como `tuple[tuple[int, ...], ...]`) y el mismo integrador puro de una sola pasada (`integrate_boid_from_flat`), garantizando equivalencia matemática dentro de `1e-9`:

1. **Fase 1 — Segmentación y Empaquetado Compacto:** Se construye una única Grilla Espacial Inmutable del frame $t$, se empaquetan `(x, y, vx, vy)` en `PackedBoidBuffer` (4 bloques inmutables `bytes` IEEE-754 float64) y se divide `[0, N)` en **1 chunk balanceado por worker** (`compute_chunk_ranges`), repartiendo equitativamente cualquier residuo.
2. **Fase 2 — Mapeo Paralelo (*Spawn-Safe*):** Un `multiprocessing.Pool` **persistente** (creado una sola vez con `max(1, os.cpu_count() - 1)` workers por defecto) despacha tareas hacia la función pura de nivel superior `process_boid_chunk` (sin `lambda` ni *closures*), que lee las coordenadas en solo-lectura (`memoryview.cast("d")` → tuplas C una vez por chunk) y evalúa las 9 celdas vecinas 3×3.
3. **Fase 3 — Sincronización y Consolidación Inmutable:** `Pool.map` actúa como barrera de sincronización; los segmentos devueltos se consolidan en orden exacto `0..N-1` en una nueva tupla de `Boid` congelados para construir el nuevo `GameState`.
4. **Cierre Limpio Obligatorio:** Al presionar `ESC`, cerrar la ventana, cambiar de workers (`+`/`-`) o volver a la Pantalla de Inicio (`Backspace` / botón `Menú`), `pool_lifecycle.py` cierra y sincroniza el `Pool` (`close()` + `join()`) en un bloque `try...finally` para evitar procesos huérfanos (*zombies*).

---

## Instalación y Ejecución

### Requisitos
* Python **3.10+** (probado en Python **3.13.15** en Windows 11).

```powershell
pip install -r requirements.txt
```

### Ejecutar el Simulador Interactivo
```powershell
python main.py
```

### Ejecutar Pruebas Unitarias, Equivalencia y Auditoría Funcional (AST)
```powershell
python -m pytest -v
```

### Ejecutar Benchmark Reproducible (1,000 / 3,000 / 5,000 Entidades)
```powershell
python -m benchmarks.run_benchmark
```
Parámetros opcionales: `--frames 8 --workers 3 --seed 42`.

---

## Controles Interactivos

### Pantalla 1 — Inicio (`1280×720`)
* **Clic** (o teclas `1` / `3` / `5`): Seleccionar carga inicial (**1,000**, **3,000** o **5,000** boids).
* **Clic** (o teclas `S` / `P`): Seleccionar modo inicial (**Secuencial** o **Paralelo**).
* **Botón `INICIAR SIMULACIÓN`** (o `Enter` / `Espacio`): Inicia la simulación en el layout de 2 zonas.

### Pantalla 2 — Simulación (`Canvas 960×720` + `Panel Lateral 320×720`)
| Tecla / Acción | Función |
| :--- | :--- |
| `1` / `3` / `5` | Cambia en vivo a **1,000**, **3,000** o **5,000** entidades (reinicia ventana de FPS). |
| `M` | Alterna en vivo entre **Modo Secuencial (1 núcleo)** y **Modo Paralelo (N workers)**. |
| `+` / `-` | Aumenta o disminuye en 1 los workers activos (`1` hasta `os.cpu_count()`). |
| `Clic Izquierdo` (en Canvas) | **Atractor:** el enjambre persigue el cursor. |
| `Clic Derecho` (en Canvas) | **Repulsor:** el enjambre huye del cursor (tiene prioridad sobre atractor). |
| `R` | Reinicia el enjambre con la semilla determinista. |
| `Espacio` | Pausa / reanuda la simulación. |
| `Backspace` / Botón `Menú` | Regresa a la Pantalla de Inicio cerrando el `Pool` limpiamente. |
| `ESC` | Cierra el simulador y termina los procesos hijos limpiamente. |

---

## Evidencia de Paralelismo y Rendimiento

Resultados reproducibles ejecutados en modo *headless* (`dt = 1/60 s`, `seed = 42`, sin cuello de botella de renderizado Pygame) mediante `python -m benchmarks.run_benchmark`:

* **Procesador (CPU):** `[PENDIENTE: HARDWARE DE PRUEBA]`
* **Memoria RAM:** `[PENDIENTE: HARDWARE DE PRUEBA]`
* **Sistema Operativo / Python:** `[PENDIENTE: HARDWARE DE PRUEBA]`
* **Núcleos Físicos / Lógicos Detectados (`os.cpu_count()`):** `[PENDIENTE: HARDWARE DE PRUEBA]`
* **Workers Activos en Modo Paralelo:** `[PENDIENTE]` (`max(1, os.cpu_count() - 1)`)
* **Estrategia de Partición:** 1 chunk balanceado por worker sobre Grilla Espacial Inmutable $O(N \cdot k)$ + `PackedBoidBuffer` (`bytes` float64)

| Cantidad de Entidades | Modo Secuencial (1 Núcleo) | Modo Paralelo (`N` Workers) | Mejora / Speedup | Costo IPC (`pickle`) |
| :--- | :---: | :---: | :---: | :---: |
| **1,000 entidades** | `[PENDIENTE] FPS (ms)` | `[PENDIENTE] FPS (ms)` | `[PENDIENTE]` | `[PENDIENTE]` |
| **3,000 entidades** | `[PENDIENTE] FPS (ms)` | `[PENDIENTE] FPS (ms)` | `[PENDIENTE]` | `[PENDIENTE]` |
| **5,000 entidades** | `[PENDIENTE] FPS (ms)` | `[PENDIENTE] FPS (ms)` | `[PENDIENTE]` | `[PENDIENTE]` |

> **Nota analítica (*Crossover Point* e IPC):** `[PENDIENTE: completar tras ejecutar python -m benchmarks.run_benchmark en la máquina de prueba oficial del equipo]`

---

## Equipo de Desarrollo

* **Deivy Anthony Prudente Merejildo**
* **Ronald David Parraga Mendoza**
* **Javier Infante**
* **Carlos Bernabé**
