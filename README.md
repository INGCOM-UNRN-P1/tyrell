# TYRELL — Generador Sintético de Datasets y Casos de Prueba (.in/.out)

**TYRELL** genera colecciones deterministas de casos de prueba (`.in` y `.out`) con restricciones configurables (enteros, flotantes, cadenas, arreglos y valores extremos) para alimentar el banco de testcases de `deckard` y `nostromo`.

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
