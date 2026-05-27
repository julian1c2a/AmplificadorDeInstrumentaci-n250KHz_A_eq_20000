import os

workspace_dir = r"c:\msys64\home\julia\ngspice\AmplificadorDeInstrumentación250KHz_A_eq_20000"
md_path = os.path.join(workspace_dir, "SuperOpAmp.md")

with open(md_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace all occurrences of accented directory path
content = content.replace("AmplificadorDeInstrumentación250KHz_A_eq_20000", "AmplificadorDeInstrumentacion250KHz_A_eq_20000")

# Append new sections
new_sections = """

---

### 8. Amplificador de Salida de Alta Potencia (`SuperOpAmpWithPowOut`)

Para dotar al SuperOpAmp de capacidades de control de corriente excepcionales, hemos diseñado un nuevo operacional con "superpoderes de salida": el **`SuperOpAmpWithPowOut`**.

Este nuevo diseño incorpora una etapa seguidora de tensión al final del circuito utilizando el macromodelo del **AD8397**.

#### 8.1 Estructura y Conexión en Seguidor
El buffer de salida `AD8397` se integra inmediatamente después de la tercera etapa (`out_pre`) en configuración de seguidor de tensión (ganancia unitaria) en lazo cerrado local:
* El terminal no inversor (`vp`) del `AD8397` se conecta a la salida de la tercera etapa (`out_pre`).
* El terminal inversor (`vn`) y el pin de salida (`out`) del `AD8397` se puentean juntos al nodo de salida global `out` del circuito.
* La realimentación de la tercera etapa se cierra a través del nodo `out_pre`, manteniendo a la etapa diferencial de bajo ruido ADA4817 totalmente desacoplada de la corriente demandada por la carga.
* Esto permite alimentar cargas extremadamente pesadas (de hasta **50 Ohms**) con distorsión mínima y corrientes de salida muy elevadas.

---

### 9. Amplificador de Instrumentación de Ganancia 20,000 (`InstrAmpl.cir`)

Utilizando el `SuperOpAmp` estándar en la etapa de entrada y el `SuperOpAmpWithPowOut` de alta potencia en la salida diferencial, hemos construido un **Amplificador de Instrumentación Completo** de ultra precisión en el archivo `InstrAmpl.cir`.

#### 9.1 Parámetros de Diseño y Ajuste de Resistencia
Para lograr una ganancia exacta de **20,000** (86.02 dB) entre 10 Hz y 500 kHz, hemos calculado y ajustado con precisión las resistencias:

1. **Etapa de Entrada Diferencial (Buffers):**
   * Dos `SuperOpAmp` instanciados como `XU1` y `XU2`.
   * Resistencia de ganancia global $R_g = 500\,\Omega$.
   * Resistencias de realimentación $R_{f1} = R_{f2} = \mathbf{49.75\text{ k}\Omega}$ (modificadas desde 49.5k).
   * Ganancia teórica de la primera etapa:
     $$A_{v1} = 1 + \frac{2 R_f}{R_g} = 1 + \frac{99.5\text{ k}}{500} = 200$$

2. **Etapa de Salida Diferencial (Diferencia de Potencia):**
   * Un `SuperOpAmpWithPowOut` instanciado como `XU3` alimentando una carga pesada de **$50\,\Omega$**.
   * Resistencias de entrada $R_{in1} = R_{in2} = 750\,\Omega$.
   * Resistencias de realimentación/referencia $R_{fb} = R_{ref} = 75\text{ k}\Omega$.
   * Ganancia de la segunda etapa:
     $$A_{v2} = \frac{R_{fb}}{R_{in}} = \frac{75\text{ k}}{750} = 100$$

3. **Ganancia Total:**
   $$A_{v,\text{total}} = A_{v1} \times A_{v2} = 200 \times 100 = \mathbf{20,000}$$

#### 9.2 Resultados de Simulación en CA (Bode)
El análisis dinámico de CA en `ngspice` ha demostrado una precisión y estabilidad extraordinarias:
* **Ganancia a 10 Hz (o menos):** **$86.0164\text{ dB}$** (Ganancia Lineal: **$19,990.2$**, error de solo **$0.048\%$**).
* **Ganancia a 500 kHz (o más):** **$86.0189\text{ dB}$** (Ganancia Lineal: **$19,996.2$**, error de solo **$0.019\%$**).
* La ganancia se mantiene increíblemente plana de forma matemática a lo largo de todo el rango espectral de interés, extendiéndose de forma lineal hasta 1 MHz.
"""

content += new_sections

with open(md_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Documentation updated successfully!")
