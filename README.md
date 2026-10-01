# TYRELL — Generador Sintético de Datasets y Casos de Prueba (.in/.out)

> 📖 **Manual de Usuario:** Para una guía exhaustiva de comandos, banderas, arquitectura y ejemplos, consultá el [Manual de Uso](MANUAL.md).

**TYRELL** genera colecciones deterministas de casos de prueba (`.in` y `.out`) con restricciones configurables (enteros, flotantes, cadenas, arreglos y valores extremos) en el formato que lee `nostromo test <binario> <directorio>` (un `caso.in` y su `caso.out` por caso; hay un test de extremo a extremo que lo verifica). No hay integración automática con `deckard` ni con el resto de los orquestadores: los archivos se copian a mano al ejercicio o al banco que corresponda.

---

## 🎯 Alcance

### Qué cubre
- Generación sintética y procedimental de datasets de prueba y casos de test (`.in / .out`) para programas C.
- Generación pseudoaleatoria determinista controlada por semillas para garantizar reproducibilidad en prácticas y exámenes.
- Ejecución y contraste automático contra binarios canónicos de referencia para sintetizar los archivos de salida esperada (`.out`).
- Inyección parametrizada de valores límite numéricos y secuencias estructuradas.

### Qué no cubre (Límites y Delegación)
- Generación de cuestionarios Moodle XML anti-copia (delegado a `idkfa`).
- Inyección de fallos en llamadas al sistema (delegado a `holden` / `vasquez`).
- Evaluación y corrección masiva de alumnos (delegado a `dredd`).

---

## 📋 Requisitos

### Requisitos de Sistema y Entorno
- Multiplataforma. Python >= 3.10.

### Dependencias Externas y Binarios
- `gcc` (para compilar soluciones de referencia canónicas si se requiere generar salidas esperadas).

### Integración en el Ecosistema
- CLI `tyrell`. Plugin registrado en `ripley.plugins` (`dataset_generator`).

---

## 🚀 Uso Rápido

```bash
# Generar 20 casos de enteros deterministas
tyrell generate -n 20 --min 1 --max 1000 -o tests/

# Generar casos y contrastar contra binario de referencia para crear los .out
tyrell generate -n 10 -o tests/ --reference ./solucion_canon

# Generar a partir de especificación YAML
tyrell generate spec.yaml -o tests/
```

### Especificación YAML (`spec.yaml`)

```yaml
name: suite            # nombre descriptivo (opcional)
count: 10              # cantidad de casos, >= 1
seed: 42               # semilla: misma semilla, mismos casos
format_template: "{a} {b}\n"   # DEBE usar {nombre} de cada regla
rules:
  - name: a
    type: integer      # integer | float | string | array
    min_val: 1
    max_val: 100
  - name: b
    type: array
    length: 5
    min_val: 0
    max_val: 9
```

Reglas de validación (se rechaza con código de salida 2 y un mensaje concreto):

- `type` solo admite `integer`, `float`, `string` y `array`.
- Las claves desconocidas (por ejemplo `max_value` en lugar de `max_val`) son un error.
- `format_template` debe usar cada `{nombre}` de las reglas: sin placeholders todos
  los casos saldrían idénticos, y un placeholder sin regla o una regla sin usar son error.
- Un archivo de especificación inexistente es un error; ya no se genera un dataset por defecto.

**Precedencia:** con un YAML, la especificación manda. `--count`, `--seed`, `--type`,
`--min` y `--max` se ignoran (y se avisa cuáles). Sin YAML se usan esas opciones.

<!-- p1:referencia:inicio — generado por p1-tools/scripts/readme_generado.py: no editar a mano -->

## Referencia rápida

### Requisitos

- Python ≥ 3.11 y [uv](https://docs.astral.sh/uv/getting-started/installation/).

### Comandos

| Comando | Descripción |
|:--|:--|
| `tyrell generate` | Genera casos de prueba .in (y .out con binario de referencia) deterministas. |
| `tyrell version` | Muestra la versión de TYRELL. |
| `tyrell doctor` | Verifica el estado del entorno de TYRELL (Python, GCC opcional). |

Ayuda de cada comando: `tyrell <comando> -h`.

### Salida JSON

Con `--json`, estos comandos emiten el resultado como JSON por la salida estándar, para usarlo desde scripts, ripley o dredd: `tyrell generate`, `tyrell doctor`. El de `doctor --json` lleva `schema_version` y `ok`.

### Códigos de salida

| Código | Significado |
|:--|:--|
| `0` | Terminó bien (en `doctor`: está todo lo requerido). |
| `1` | El comando encontró problemas (hallazgos, pruebas que fallan, un umbral que no se alcanza) o un dato no se pudo usar (un archivo ilegible, un formato inválido). |
| `2` | Error de uso: comando, opción o argumento inválido. |

<!-- p1:referencia:fin -->
