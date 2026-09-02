# TYRELL — Generador Sintético de Datasets y Casos de Prueba (.in/.out)

**TYRELL** genera colecciones deterministas de casos de prueba (`.in` y `.out`) con restricciones configurables (enteros, flotantes, cadenas, arreglos y valores extremos) para alimentar el banco de testcases de `deckard` y `nostromo`.

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
