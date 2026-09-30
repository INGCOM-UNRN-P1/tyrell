# Manual de Uso y Referencia Técnica: tyrell

> **TYRELL** — Generador sintético y determinista de datasets y casos de prueba (.in/.out) con restricciones
> **Versión:** `0.1.0` · **CLI principal:** `tyrell` · **Plugin Ripley:** `dataset_generator`

---

## 1. Arquitectura y Propósito Pedagógico

`tyrell` forma parte del ecosistema de herramientas de la cátedra de Programación 1 (UNRN). Su objetivo central es resolver de forma modular, determinista y automatizada las tareas asociadas a su dominio específico dentro del ciclo de desarrollo, evaluación y aprendizaje de software en C.

### Alcance Funcional (Qué cubre)
- Generación sintética y procedimental de datasets de prueba y casos de test (`.in / .out`) para programas C.
- Generación pseudoaleatoria determinista controlada por semillas para garantizar reproducibilidad en prácticas y exámenes.
- Ejecución y contraste automático contra binarios canónicos de referencia para sintetizar los archivos de salida esperada (`.out`).
- Inyección parametrizada de valores límite numéricos y secuencias estructuradas.

### Límites de Responsabilidad y Delegación (Qué no cubre)
- Generación de cuestionarios Moodle XML anti-copia (delegado a `idkfa`).
- Inyección de fallos en llamadas al sistema (delegado a `holden` / `vasquez`).
- Evaluación y corrección masiva de alumnos (delegado a `dredd`).

### Principios de Diseño
- **Enfoque Pedagógico:** Diagnósticos y mensajes en español rioplatense orientados a facilitar la comprensión de errores conceptuales.
- **Salida Estructurada Dual:** Soporte nativo para visualización enriquecida en terminal (Rich) y salida parseable para orquestadores (`--json`).
- **Integración Contractual:** Capacidad de emitir secciones de reporte para `dredd` (`dredd-section`) y actuar como satélite orquestado por `ripley`.
- **Idempotencia y Robustez:** Validación de precondiciones y comandos de autodiagnóstico (`doctor`) para verificación del entorno.

---

## 2. Instalación y Requisitos

### Requisitos del Sistema
- **Python:** `>= 3.10` (recomendado Python 3.11 o 3.12).
- **Gestor de paquetes:** [`uv`](https://github.com/astral-sh/uv) (entorno estándar de cátedra).
- **Toolchain C (si aplica):** GCC / Clang, Make, GDB y bibliotecas estándar de desarrollo.

### Instalación en el Entorno de Usuario
Para instalar la herramienta de forma global y aislada en el sistema mediante `uv tool`:
```bash
uv tool install git+https://github.com/INGCOM-UNRN-P1/tyrell
```

### Verificación de Instalación
Ejecutá el comando `doctor` para constatar que todas las dependencias y binarios requeridos estén presentes y operativos:
```bash
tyrell doctor
```

---

## 3. Guía Integral de Comandos (CLI)

| Comando | Descripción Breve |
| :--- | :--- |
| [`tyrell generate`](#generate) | Genera casos de prueba .in (y .out con binario de referencia) deterministas. |
| [`tyrell version`](#version) | Muestra la versión de TYRELL. |
| [`tyrell doctor`](#doctor) | Verifica el estado del entorno de TYRELL (Python, GCC opcional). |

### `tyrell generate`

Genera casos de prueba .in (y .out con binario de referencia) deterministas.

Con un YAML, la especificación manda: `--count`, `--seed`, `--type`, `--min`
y `--max` se ignoran (se avisa cuáles). Sin YAML se usan esas opciones.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--ctx` | `<class 'typer.models.Context'>` | `None` | - |
| `--spec-file` | `Optional[pathlib._local.Path]` | `None` | Archivo YAML de especificación de dataset |
| `--count`, `-n` | `<class 'int'>` | `10` | Cantidad de casos de prueba a generar |
| `--seed`, `-s` | `<class 'int'>` | `42` | Semilla para reproducibilidad |
| `--type`, `-t` | `<class 'str'>` | `integer` | Tipo de dato si no se pasa YAML (integer, float, string, array) |
| `--min` | `<class 'int'>` | `0` | Valor mínimo |
| `--max` | `<class 'int'>` | `100` | Valor máximo |
| `--output`, `-o` | `<class 'pathlib._local.Path'>` | `tests` | Directorio de destino de los archivos .in/.out |
| `--reference`, `-r` | `Optional[pathlib._local.Path]` | `None` | Binario ejecutable de referencia para generar los .out |
| `--json` | `<class 'bool'>` | `False` | Emitir salida en formato JSON estructurado |

#### Ejemplo de Invocación
```bash
tyrell generate
```

### `tyrell version`

Muestra la versión de TYRELL.

#### Ejemplo de Invocación
```bash
tyrell version
```

### `tyrell doctor`

Verifica el estado del entorno de TYRELL (Python, GCC opcional).

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--json` | `<class 'bool'>` | `False` | Emitir diagnóstico en formato JSON estructurado. |

#### Ejemplo de Invocación
```bash
tyrell doctor
```

---

## 4. Formatos de Salida e Integración con el Ecosistema

### Modo Interactivo / Terminal (Rich)
Por defecto, la herramienta renderiza paneles, árboles y tablas estilizadas para facilitar la lectura del estudiante y docente en terminales modernas con soporte ANSI.

### Modo Estructurado JSON (`--json`)
Para integración con pipelines de CI/CD, scripts de automatización u orquestadores externos, la opción `--json` emite un documento JSON estricto por la salida estándar (`stdout`), dirigiendo cualquier mensaje de logging a `stderr`:
```bash
tyrell generate --json
```

### Integración con Dredd (`dredd-section`)
Cuando la herramienta genera reportes de evaluación para entregas de alumnos, produce una sección Markdown estandarizada conforme al contrato de integración de Dredd (v1.0.0):
```markdown
<!-- dredd-section: tyrell, tool=tyrell, version=0.1.0, status=ok -->
```
Este encabezado garantiza la agregación determinista de los hallazgos en la rúbrica docente.

### Integración con Ripley
`tyrell` está registrada en el catálogo de plugins satélites de Ripley (`SATELLITE_CATALOG`). Puede invocarse directamente a través del motor de evaluación de Ripley configurando el análisis en `ripley.toml`.

---

## 5. Diagnóstico y Códigos de Salida

### Códigos de Retorno (`exit code`)
| Código | Significado |
| :---: | :--- |
| `0` | Ejecución exitosa sin hallazgos críticos ni errores de sintaxis. |
| `1` | Hallazgos pedagógicos detectados, infracción de reglas o advertencias activas. |
| `2` | Error de sintaxis en argumentos CLI o archivo fuente no encontrado. |
| `>2` | Error no recuperable del sistema, fallo de memoria o excepción interna. |

### Diagnóstico del Entorno (`doctor`)
Ante comportamientos inesperados, verificá el estado operativo con:
```bash
tyrell doctor
```
Comprueba la presencia de las dependencias requeridas y la integridad de los componentes del paquete.