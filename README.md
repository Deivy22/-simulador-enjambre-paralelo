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

