---
title: "Manual de Referencia: tyrell"
subtitle: "Tyrell — Generador Sintético y Determinista de Datasets y Casos de Prueba con Semillas"
author: "Cátedra de Algoritmos y Programación"
date: "2026-08-31"
---

(manual-tyrell)=
# Tyrell — Generador Sintético y Determinista de Datasets y Casos de Prueba con Semillas

````{abstract}
**Rol en el ecosistema:** Generación determinista y reproducible de datasets masivos (números, matrices, cadenas, registros estructurados) mediante generadores pseudoaleatorios con semilla fija para pruebas de carga y benchmarking.
````

---

(manual-tyrell-proposito)=
## 1. Propósito y Filosofía Pedagógica

La herramienta **`tyrell`** forma parte del ecosistema oficial de software de la cátedra. Su diseño sigue principios pedagógicos rigurosos:

1. **Evidencia Técnica Directa**: Todo diagnóstico se fundamenta en la norma ISO C (C11/C23), en el modelo de memoria del sistema o en convenciones arquitectónicas formales.
2. **Acción Correctiva Concreta**: Cada advertencia incluye la prescripción técnica inmediata para resolver el defecto sin recurrir a conjeturas.
3. **Autonomía del Estudiante**: Facilita la autoevaluación local antes de la entrega final del trabajo práctico.
4. **Objetividad Docente**: Estandariza la corrección automática eliminando discrepancias subjetivas en la evaluación.

---

(manual-tyrell-instalacion)=
## 2. Instalación y Diagnóstico del Entorno

````{important}
Asegurate de contar con el compilador GCC/Clang y las librerías del sistema instaladas antes de ejecutar `tyrell`.
````

Para comprobar el estado de salud de tu entorno de trabajo y las dependencias auxiliares:

````{code-block} bash
# Comprobación de dependencias del sistema
tyrell doctor
````

Si se detecta la falta de alguna utilidad (como `gdb`, `valgrind`, `clang-format` o `typst`), el comando indicará el paquete exacto a instalar según tu distribución GNU/Linux o entorno MSYS2.

---

(manual-tyrell-comandos)=
## 3. Referencia Completa de Comandos CLI

A continuación se detallan los subcomandos principales disponibles en `tyrell`:

| Sintaxis del Comando | Descripción y Efecto |
| :--- | :--- |
| `tyrell generate --schema dataset.yaml -n 1000 -o datos.in` | Genera un dataset de 1000 registros estructurados. |
| `tyrell matrix --rows 100 --cols 100 --seed 42 -o matriz.in` | Genera una matriz aleatoria determinista. |
| `tyrell fuzz-strings -n 50 -o strings.in` | Genera cadenas de prueba con caracteres especiales y UTF-8. |
| `tyrell doctor` | Verifica generadores de datos y esquemas. |

````{tip}
Podés agregar el flag `--json` a la mayoría de los comandos para exportar resultados en formato estructurado o `--md` para generar reportes Markdown para el informe de entrega.
````

---

(manual-tyrell-tutorial)=
## 4. Tutorial Paso a Paso con Ejemplos Reales

### Caso de Estudio

Considerá el siguiente fragmento de código representativo:

````{code-block} c
:linenos:
// Esquema YAML procesado por Tyrell:
// schema:
//   - name: id
//     type: integer
//     min: 1000
//     max: 9999
//   - name: promedio
//     type: float
//     min: 1.0
//     max: 10.0
````

### Ejecución de la Herramienta

Ejecutá el análisis desde tu terminal:

````{code-block} bash
tyrell generate --schema dataset.yaml -n 1000 -o datos.in
````

### Salida Obtenida en Consola

````{code-block} text
[✓] Generados 1,000 registros en datos.in (Semilla: 0x1337BEEF)
[✓] Tamaño del archivo: 42.5 KB | Integridad SHA-256: 8f4a3c2...
[✓] Salida reproducible: la misma semilla generará exactamente los mismos datos.
````

````{note}
Prestá atención a la explicación pedagógica generada: la herramienta no solo señala la línea del problema, sino que explica la causa raíz y el impacto en memoria o arquitectura.
````

---

(manual-tyrell-ejercicios)=
## 5. Ejercicios Prácticos y Desafíos

Practicá el uso avanzado de **`tyrell`** resolviendo los siguientes ejercicios:

````{exercise} Desafío 1: Generación de Vector de 100,000 Elementos
Crear un archivo de entrada para pruebas de rendimiento de algoritmos de ordenamiento.

**Instrucción de ejecución:**
```bash
tyrell generate --type int --count 100000 --seed 12345 -o vector_grande.in
```
````

````{solution} Desafío 1
```bash
tyrell generate --type int --count 100000 --seed 12345 -o vector_grande.in
# Verificá que la operación concluya exitosamente con código de salida 0.
```
````

````{exercise} Desafío 2: Dataset de Estructuras para TDA
Generar archivo de texto con datos de paquetes postales para pruebas del TP.

**Instrucción de ejecución:**
```bash
tyrell generate --schema schemas/envios.yaml -n 500 -o envios.in
```
````

````{solution} Desafío 2
```bash
tyrell generate --schema schemas/envios.yaml -n 500 -o envios.in
# Revisá el archivo generado o el informe en terminal para confirmar la resolución del problema.
```
````

````{exercise} Desafío 3: Casos de Prueba con Caracteres Extremos
Generar cadenas con caracteres nulos, emojis y secuencias de escape.

**Instrucción de ejecución:**
```bash
tyrell fuzz-strings -n 100 -o strings_extremos.in
```
````

````{solution} Desafío 3
```bash
tyrell fuzz-strings -n 100 -o strings_extremos.in
# Comprobá que la salida confirme la ausencia de advertencias o errores pendientes.
```
````

---

(manual-tyrell-makefile)=
## 6. Integración en el Flujo de Trabajo y Makefile

Para incorporar `tyrell` de forma automática a tu flujo de desarrollo, agregá la siguiente regla en el `Makefile` de tu proyecto:

````{code-block} makefile
check-tyrell:
	@echo "=== Ejecutando verificación con tyrell ==="
	tyrell check src/ include/

.PHONY: check-tyrell
````

Ejecutá `make check-tyrell` antes de cada commit para asegurar que tu código conserve el estado de aprobación.
