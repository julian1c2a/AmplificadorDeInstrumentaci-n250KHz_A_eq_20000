Listed directory AmplificadorDeInstrumentaci%C3%B3n250KHz_A_eq_20000
Viewed SUPEROPAMP.CIR:1-44
Viewed superopamp_ngspice.cir:1-112
Viewed simulate_superopamp.py:1-217
Viewed analyze.py:1-60
Viewed simulate_comparison.py:1-373
Viewed ina_250khz_real.cir:1-101
Searched for "SuperOpAmp"
Edited verify_poles.py
Ran command: `python verify_poles.py`

Para determinar los **polos** y **ceros** del circuito del **SuperOpAmp Instrumentation Amplifier** en función de sus resistencias, debemos analizar la función de transferencia en lazo cerrado etapa por etapa.

El amplificador de instrumentación consta de **3 etapas en cascada**, lo que simplifica enormemente el análisis ya que las etapas están desacopladas:

1. **Etapa 1 (Buffer de entrada diferencial):** Formada por `XOP1` y `XOP2` con las resistencias $R_1, R_2, R_3$.
2. **Etapa 2 (Segunda etapa diferencial):** Formada por `XOP3` y `XOP4` con las resistencias $R_4, R_5, R_6$.
3. **Etapa 3 (Amplificador de diferencia / conversor a single-ended):** Formada por `XOP5` con las resistencias $R_7, R_8, R_9, R_{10}$.

---

### 1. Modelo de Lazo Abierto de cada Op-Amp
Cada operacional individual (`StdOpamp`) tiene una función de transferencia de lazo abierto de segundo orden:
$$A(s) = \frac{A_0}{\left(1 + \frac{s}{\omega_{p1}}\right)\left(1 + \frac{s}{\omega_{p2}}\right)}$$

Donde:
* **$A_0 = 200,000$** (Ganancia de tensión en continua / open-loop DC gain).
* **$f_{p1} = 15\text{ Hz}$** $\rightarrow$ $\omega_{p1} = 2\pi \times 15\text{ rad/s}$ (Polo dominante).
* **$f_{p2} = 9.45\text{ MHz}$** $\rightarrow$ $\omega_{p2} = 2\pi \times 9.45\times 10^6\text{ rad/s}$ (Polo secundario).
* **$\text{GBWP} = A_0 \times f_{p1} = 3\text{ MHz}$** (Producto Ganancia-Ancho de Banda).

---

### 2. Análisis por Etapas: Ganancia, Factor de Feedback ($\beta$) y Polos

Al aplicar realimentación negativa a un amplificador de segundo orden, la función de transferencia de lazo cerrado para cada etapa toma la forma estándar:
$$H_i(s) = G_{i} \cdot \frac{\beta_i A(s)}{1 + \beta_i A(s)}$$

El denominador de lazo cerrado es:
$$1 + \beta_i A(s) = 0 \implies s^2 + s(\omega_{p1} + \omega_{p2}) + \omega_{p1}\omega_{p2}(1 + \beta_i A_0) = 0$$

Como el sistema es **fuertemente sobreamortiguado** ($\zeta_i \gg 1$), esta ecuación cuadrática se descompone en dos polos reales muy separados:
1. **Polo Dominante de Lazo Cerrado:**
   $$f_{c1,i} \approx \beta_i \cdot \text{GBWP} = \beta_i \cdot (A_0 \cdot f_{p1})$$
2. **Polo Secundario de Lazo Cerrado:**
   $$f_{c2,i} \approx f_{p2} = 9.45\text{ MHz}$$

---

#### Etapa 1: Buffer Diferencial de Entrada (`XOP1`, `XOP2`)
* **Resistencias:** $R_1$, $R_2$ (típicamente $R_1 = R_2$) y $R_3$ (resistencia de ganancia $R_g$).
* **Ganancia de DC en lazo cerrado ($G_1$):**
  $$G_1 = 1 + \frac{R_1 + R_2}{R_3}$$
* **Factor de realimentación ($\beta_1$):**
  $$\beta_1 = \frac{R_3}{R_3 + R_1 + R_2} = \frac{1}{G_1}$$
* **Polo Dominante ($p_1$):**
  $$f_{p,Stage1} \approx \beta_1 \cdot \text{GBWP} = \frac{R_3}{R_3 + R_1 + R_2} \cdot \text{GBWP}$$

---

#### Etapa 2: Buffer Diferencial Intermedio (`XOP3`, `XOP4`)
* **Resistencias:** $R_4$, $R_5$ (típicamente $R_4 = R_5$) y $R_6$.
* **Ganancia de DC en lazo cerrado ($G_2$):**
  $$G_2 = 1 + \frac{R_4 + R_5}{R_6}$$
* **Factor de realimentación ($\beta_2$):**
  $$\beta_2 = \frac{R_6}{R_6 + R_4 + R_5} = \frac{1}{G_2}$$
* **Polo Dominante ($p_2$):**
  $$f_{p,Stage2} \approx \beta_2 \cdot \text{GBWP} = \frac{R_6}{R_6 + R_4 + R_5} \cdot \text{GBWP}$$

---

#### Etapa 3: Conversor Diferencial a Single-Ended (`XOP5`)
* **Resistencias:** $R_7$ (feedback), $R_8$ (entrada inversora), $R_9$ y $R_{10}$ (entrada no inversora).
* **Condición de balance:** Para rechazar el modo común se requiere que $\frac{R_9}{R_{10}} = \frac{R_7}{R_8}$.
* **Ganancia de DC en lazo cerrado ($G_3$):**
  $$G_3 = \frac{R_7}{R_8}$$
* **Factor de realimentación ($\beta_3$):**
  $$\beta_3 = \frac{R_8}{R_7 + R_8} = \frac{1}{1 + G_3}$$
* **Polo Dominante ($p_3$):**
  $$f_{p,Stage3} \approx \beta_3 \cdot \text{GBWP} = \frac{R_8}{R_7 + R_8} \cdot \text{GBWP}$$

---

### 3. Ceros de la Función de Transferencia Diferencial
Dado que el modelo del operacional $A(s)$ no tiene ceros en su trayectoria directa y el circuito es una cascada pura de etapas con realimentación de tensión sin caminos de alimentación directa (feedforward), **la función de transferencia diferencial global no posee ceros**. La respuesta en frecuencia está determinada en su totalidad por los polos.

---

### 4. Resumen Analítico y Valores Numéricos del Diseño Actual

A continuación se resume cómo afectan las resistencias del diseño actual ($R_1=R_2=49.5\text{k}\Omega$, $R_3=500\Omega$, $R_4=R_5=49.5\text{k}\Omega$, $R_6=500\Omega$, $R_7=R_9=10\text{k}\Omega$, $R_8=R_{10}=750\Omega$) a los polos dominantes:

| Etapa | Ganancia de DC ($G_i$) | Expresión de $\beta_i$ | Polo Dominante ($f_{p,i}$) | Valor Teórico (Aprox.) | Valor Real (Simulado/Exacto) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Etapa 1** | $1 + \frac{2 R_1}{R_3} = 200$ | $\frac{R_3}{R_3 + 2R_1} \approx \frac{1}{200}$ | $\frac{R_3}{R_3 + 2R_1} \cdot 3\text{ MHz}$ | **$15.08\text{ kHz}$** | **$15.10\text{ kHz}$** |
| **Etapa 2** | $1 + \frac{2 R_4}{R_6} = 200$ | $\frac{R_6}{R_6 + 2R_4} \approx \frac{1}{200}$ | $\frac{R_6}{R_6 + 2R_4} \cdot 3\text{ MHz}$ | **$15.08\text{ kHz}$** | **$15.10\text{ kHz}$** |
| **Etapa 3** | $\frac{R_7}{R_8} = 13.33$ | $\frac{R_8}{R_7 + R_8} \approx \frac{3}{43}$ | $\frac{R_8}{R_7 + R_8} \cdot 3\text{ MHz}$ | **$209.3\text{ kHz}$** | **$214.2\text{ kHz}$** |

> [!NOTE]
> Además de estos 3 polos dominantes ajustables mediante resistencias, el circuito contiene **3 polos de alta frecuencia fijos** en **$9.45\text{ MHz}$** (uno por cada etapa de operacional en lazo cerrado), los cuales dependen únicamente del diseño interno del circuito del operacional (`FPOLE2`).

### 5. Función de Transferencia Global Simplificada
Combinando todo, la función de transferencia del **SuperOpAmp** es:

$$H(s) \approx \frac{533,333}{\left(1 + \frac{s}{2\pi \cdot 15.1\text{ kHz}}\right)^2 \left(1 + \frac{s}{2\pi \cdot 214\text{ kHz}}\right) \left(1 + \frac{s}{2\pi \cdot 9.45\text{ MHz}}\right)^3}$$

* El ancho de banda del amplificador completo está dominado principalmente por el doble polo de las Etapas 1 y 2 en $\approx 15.1\text{ kHz}$.
* Si se desea desplazar los polos hacia frecuencias más altas, se debe **disminuir la ganancia** de las etapas incrementando $R_3$ y $R_6$, o disminuyendo $R_1, R_2, R_4, R_5$, lo cual incrementa el factor de realimentación $\beta$ de cada etapa de manera directa.

### 6. Como bajar los polos de lazo cerrado y de lazo abierto.

Listed directory AmplificadorDeInstrumentaci%C3%B3n250KHz_A_eq_20000
Viewed SUPEROPAMP.CIR:1-44
Viewed superopamp_ngspice.cir:1-112
Viewed simulate_superopamp.py:1-217
Viewed analyze.py:1-60
Viewed simulate_comparison.py:1-373
Viewed ina_250khz_real.cir:1-101
Searched for "SuperOpAmp"
Edited verify_poles.py
Ran command: `python verify_poles.py`

Para determinar los **polos** y **ceros** del circuito del **SuperOpAmp Instrumentation Amplifier** en función de sus resistencias, debemos analizar la función de transferencia en lazo cerrado etapa por etapa.

El amplificador de instrumentación consta de **3 etapas en cascada**, lo que simplifica enormemente el análisis ya que las etapas están desacopladas:

1. **Etapa 1 (Buffer de entrada diferencial):** Formada por `XOP1` y `XOP2` con las resistencias $R_1, R_2, R_3$.
2. **Etapa 2 (Segunda etapa diferencial):** Formada por `XOP3` y `XOP4` con las resistencias $R_4, R_5, R_6$.
3. **Etapa 3 (Amplificador de diferencia / conversor a single-ended):** Formada por `XOP5` con las resistencias $R_7, R_8, R_9, R_{10}$.

---

### 1. Modelo de Lazo Abierto de cada Op-Amp
Cada operacional individual (`StdOpamp`) tiene una función de transferencia de lazo abierto de segundo orden:
$$A(s) = \frac{A_0}{\left(1 + \frac{s}{\omega_{p1}}\right)\left(1 + \frac{s}{\omega_{p2}}\right)}$$

Donde:
* **$A_0 = 200,000$** (Ganancia de tensión en continua / open-loop DC gain).
* **$f_{p1} = 15\text{ Hz}$** $\rightarrow$ $\omega_{p1} = 2\pi \times 15\text{ rad/s}$ (Polo dominante).
* **$f_{p2} = 9.45\text{ MHz}$** $\rightarrow$ $\omega_{p2} = 2\pi \times 9.45\times 10^6\text{ rad/s}$ (Polo secundario).
* **$\text{GBWP} = A_0 \times f_{p1} = 3\text{ MHz}$** (Producto Ganancia-Ancho de Banda).

---

### 2. Análisis por Etapas: Ganancia, Factor de Feedback ($\beta$) y Polos

Al aplicar realimentación negativa a un amplificador de segundo orden, la función de transferencia de lazo cerrado para cada etapa toma la forma estándar:
$$H_i(s) = G_{i} \cdot \frac{\beta_i A(s)}{1 + \beta_i A(s)}$$

El denominador de lazo cerrado es:
$$1 + \beta_i A(s) = 0 \implies s^2 + s(\omega_{p1} + \omega_{p2}) + \omega_{p1}\omega_{p2}(1 + \beta_i A_0) = 0$$

Como el sistema es **fuertemente sobreamortiguado** ($\zeta_i \gg 1$), esta ecuación cuadrática se descompone en dos polos reales muy separados:
1. **Polo Dominante de Lazo Cerrado:**
   $$f_{c1,i} \approx \beta_i \cdot \text{GBWP} = \beta_i \cdot (A_0 \cdot f_{p1})$$
2. **Polo Secundario de Lazo Cerrado:**
   $$f_{c2,i} \approx f_{p2} = 9.45\text{ MHz}$$

---

#### Etapa 1: Buffer Diferencial de Entrada (`XOP1`, `XOP2`)
* **Resistencias:** $R_1$, $R_2$ (típicamente $R_1 = R_2$) y $R_3$ (resistencia de ganancia $R_g$).
* **Ganancia de DC en lazo cerrado ($G_1$):**
  $$G_1 = 1 + \frac{R_1 + R_2}{R_3}$$
* **Factor de realimentación ($\beta_1$):**
  $$\beta_1 = \frac{R_3}{R_3 + R_1 + R_2} = \frac{1}{G_1}$$
* **Polo Dominante ($p_1$):**
  $$f_{p,Stage1} \approx \beta_1 \cdot \text{GBWP} = \frac{R_3}{R_3 + R_1 + R_2} \cdot \text{GBWP}$$

---

#### Etapa 2: Buffer Diferencial Intermedio (`XOP3`, `XOP4`)
* **Resistencias:** $R_4$, $R_5$ (típicamente $R_4 = R_5$) y $R_6$.
* **Ganancia de DC en lazo cerrado ($G_2$):**
  $$G_2 = 1 + \frac{R_4 + R_5}{R_6}$$
* **Factor de realimentación ($\beta_2$):**
  $$\beta_2 = \frac{R_6}{R_6 + R_4 + R_5} = \frac{1}{G_2}$$
* **Polo Dominante ($p_2$):**
  $$f_{p,Stage2} \approx \beta_2 \cdot \text{GBWP} = \frac{R_6}{R_6 + R_4 + R_5} \cdot \text{GBWP}$$

---

#### Etapa 3: Conversor Diferencial a Single-Ended (`XOP5`)
* **Resistencias:** $R_7$ (feedback), $R_8$ (entrada inversora), $R_9$ y $R_{10}$ (entrada no inversora).
* **Condición de balance:** Para rechazar el modo común se requiere que $\frac{R_9}{R_{10}} = \frac{R_7}{R_8}$.
* **Ganancia de DC en lazo cerrado ($G_3$):**
  $$G_3 = \frac{R_7}{R_8}$$
* **Factor de realimentación ($\beta_3$):**
  $$\beta_3 = \frac{R_8}{R_7 + R_8} = \frac{1}{1 + G_3}$$
* **Polo Dominante ($p_3$):**
  $$f_{p,Stage3} \approx \beta_3 \cdot \text{GBWP} = \frac{R_8}{R_7 + R_8} \cdot \text{GBWP}$$

---

### 3. Ceros de la Función de Transferencia Diferencial
Dado que el modelo del operacional $A(s)$ no tiene ceros en su trayectoria directa y el circuito es una cascada pura de etapas con realimentación de tensión sin caminos de alimentación directa (feedforward), **la función de transferencia diferencial global no posee ceros**. La respuesta en frecuencia está determinada en su totalidad por los polos.

---

### 4. Resumen Analítico y Valores Numéricos del Diseño Actual

A continuación se resume cómo afectan las resistencias del diseño actual ($R_1=R_2=49.5\text{k}\Omega$, $R_3=500\Omega$, $R_4=R_5=49.5\text{k}\Omega$, $R_6=500\Omega$, $R_7=R_9=10\text{k}\Omega$, $R_8=R_{10}=750\Omega$) a los polos dominantes:

| Etapa | Ganancia de DC ($G_i$) | Expresión de $\beta_i$ | Polo Dominante ($f_{p,i}$) | Valor Teórico (Aprox.) | Valor Real (Simulado/Exacto) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Etapa 1** | $1 + \frac{2 R_1}{R_3} = 200$ | $\frac{R_3}{R_3 + 2R_1} \approx \frac{1}{200}$ | $\frac{R_3}{R_3 + 2R_1} \cdot 3\text{ MHz}$ | **$15.08\text{ kHz}$** | **$15.10\text{ kHz}$** |
| **Etapa 2** | $1 + \frac{2 R_4}{R_6} = 200$ | $\frac{R_6}{R_6 + 2R_4} \approx \frac{1}{200}$ | $\frac{R_6}{R_6 + 2R_4} \cdot 3\text{ MHz}$ | **$15.08\text{ kHz}$** | **$15.10\text{ kHz}$** |
| **Etapa 3** | $\frac{R_7}{R_8} = 13.33$ | $\frac{R_8}{R_7 + R_8} \approx \frac{3}{43}$ | $\frac{R_8}{R_7 + R_8} \cdot 3\text{ MHz}$ | **$209.3\text{ kHz}$** | **$214.2\text{ kHz}$** |

> [!NOTE]
> Además de estos 3 polos dominantes ajustables mediante resistencias, el circuito contiene **3 polos de alta frecuencia fijos** en **$9.45\text{ MHz}$** (uno por cada etapa de operacional en lazo cerrado), los cuales dependen únicamente del diseño interno del circuito del operacional (`FPOLE2`).

### 5. Función de Transferencia Global Simplificada

Para lograr ambos objetivos (bajar el polo de lazo abierto del op-amp a $0.1\text{ Hz}$ y reducir drásticamente el polo de lazo cerrado de las etapas 1 y 2), tenemos dos enfoques muy claros: el enfoque de simulación (macromodelo) y el enfoque físico (hardware/circuitos).

Método 1: Modificación del Macromodelo (Enfoque de Simulación)
Si el objetivo es alterar las propiedades internas del operacional en la simulación de SPICE, cambiar el parámetro FPOLE1 de $15\text{ Hz}$ a $0.1\text{ Hz}$ resuelve ambos problemas simultáneamente:

Polo de lazo abierto del Op-Amp ($f_{p1}$): Al cambiar FPOLE1 = 0.1 en los parámetros de la directiva .subckt StdOpamp, el polo dominante en lazo abierto cae directamente a $0.1\text{ Hz}$.

Efecto automático en las Etapas 1 y 2 ($f_{p,Stage1}$): Al reducir $f_{p1}$ en un factor de 150, el producto ganancia-ancho de banda ($\text{GBWP}$) del operacional disminuye en la misma proporción: $$\text{GBWP}{\text{nuevo}} = A_0 \times f{p1, \text{nuevo}} = 200,000 \times 0.1\text{ Hz} = 20\text{ kHz}$$ Dado que el polo en lazo cerrado de las Etapas 1 y 2 depende directamente del $\text{GBWP}$: $$f_{p,Stage1} \approx \beta_1 \cdot \text{GBWP} = \frac{1}{199} \cdot 20\text{ kHz} \approx 100.5\text{ Hz}$$

Resultado exacto calculado por la ecuación del sistema:

Polos Etapas 1 y 2: $100.5\text{ Hz}$ (antes $15.1\text{ kHz}$)
Polo Etapa 3: $1.395\text{ kHz}$ (antes $214.2\text{ kHz}$)
Para implementarlo en el netlist superopamp_ngspice.cir (o SUPEROPAMP.CIR), simplemente se editan las llamadas de los operacionales modificando el parámetro FPOLE1:

spice
* Ejemplo en XOP1 a XOP5:
XOP1 0 13 cc dd 12 StdOpamp PARAMS: GAIN=200K ... FPOLE1=0.1 FPOLE2=9.45MEG ...
Método 2: Modificación de Resistencias (Enfoque de Lazo Cerrado / Hardware)
Si deseamos mantener las características físicas del operacional intactas ($\text{GBWP} = 3\text{ MHz}$, $f_{p1} = 15\text{ Hz}$) pero queremos reducir el polo dominante de las etapas 1 y 2 actuando únicamente sobre los componentes externos (resistencias), podemos aplicar las siguientes técnicas:

Opción A: Modificación de los valores de resistencia (Aumento de Ganancia)
Como el polo de lazo cerrado es inversamente proporcional a la ganancia de la etapa ($f_{p,Stage1} \approx \frac{\text{GBWP}}{G_1}$), podemos disminuir la frecuencia del polo aumentando la ganancia mediante resistencias:

Reducir $R_3$ y $R_6$: Si bajamos $R_3$ y $R_6$ de $500,\Omega$ a $5,\Omega$, la ganancia $G_1$ sube de $200$ a $19,801$, lo que disminuye el polo dominante de la etapa en un factor de 100: $$f_{p,Stage1} \approx \frac{3\text{ MHz}}{19801} \approx 151\text{ Hz}$$
Aumentar $R_1, R_2, R_4, R_5$: Si subimos estas resistencias de $49.5\text{ k}\Omega$ a $4.95\text{ M}\Omega$ (manteniendo $R_3 = 500,\Omega$), obtenemos exactamente el mismo efecto de reducción del polo a $151\text{ Hz}$.


WARNING

Desventaja: Modificar la ganancia de esta manera aumentará drásticamente la ganancia total del circuito ($A_v \gg 500,000$), lo cual puede provocar saturación en continua con señales de entrada extremadamente pequeñas.

Opción B: Compensación Capacitiva Activa (Solución Física Recomendada)
Para reducir el polo de las Etapas 1 y 2 sin alterar la ganancia de continua (DC), se añaden condensadores de compensación ($C_f$) en paralelo con las resistencias de realimentación $R_1$, $R_2$, $R_4$ y $R_5$.

Esto introduce un polo de baja frecuencia controlado por: $$f_{p, \text{filtro}} = \frac{1}{2\pi \cdot R_{\text{feedback}} \cdot C_f}$$

Por ejemplo, para fijar el polo de las Etapas 1 y 2 en $100\text{ Hz}$ manteniendo la ganancia intacta, seleccionamos $C_f$: $$C_f = \frac{1}{2\pi \cdot 49.5\text{ k}\Omega \cdot 100\text{ Hz}} \approx 32.15\text{ nF}$$

Colocando un capacitor de $32\text{ nF}$ en paralelo con cada resistencia de $49.5\text{ k}\Omega$ se logra bajar el polo de lazo cerrado a la frecuencia deseada de forma robusta e independiente de las variaciones del operacional.

Para que los condensadores paralelos a $R_7$ y $R_9$ en la Etapa 3 (los llamaremos $C_{f3}$) se "acompasen" o acoplen dinámicamente con los de las Etapas 1 y 2, existen dos estrategias de diseño profesional dependiendo de qué efecto dinámico desees priorizar:

Opción 1: Alineación de Polos (Filtro Homogéneo a $\approx 97\text{ Hz}$)
Si el objetivo es que las tres etapas tengan exactamente el mismo ancho de banda y empiecen a atenuar juntas a la misma frecuencia, debemos igualar la constante de tiempo (el polo dominante) de la Etapa 3 con la de las Etapas 1 y 2:

$$f_{p,Stage3} = f_{p,Stage1,2} \implies R_7 \cdot C_{f3} = R_1 \cdot C_{f1}$$

Despejando $C_{f3}$: $$C_{f3} = C_{f1} \cdot \frac{R_1}{R_7}$$

Sustituyendo los valores actuales ($R_1 = 49.5\text{ k}\Omega$, $R_7 = 10\text{ k}\Omega$, $C_{f1} = 33\text{ nF}$): $$C_{f3} = 33\text{ nF} \cdot \frac{49.5\text{ k}\Omega}{10\text{ k}\Omega} = 33\text{ nF} \cdot 4.95 = 163.35\text{ nF}$$

Valor comercial recomendado: $160\text{ nF}$ (o $150\text{ nF} + 13\text{ nF}$ en paralelo para máxima precisión).
Resultado: El polo de la Etapa 3 se desplaza exactamente a $97.4\text{ Hz}$. Las tres etapas operan en perfecta sincronía temporal, logrando una pendiente de atenuación muy pronunciada de $-60\text{ dB/década}$ inmediatamente después de los $97\text{ Hz}$.
Opción 2: Cancelación Polo-Cero (Filtrado de Ruido Óptimo a $\approx 19.5\text{ kHz}$)
Las Etapas 1 y 2 introducen dos ceros en lazo cerrado a $19.5\text{ kHz}$ debido al condensador de $33\text{ nF}$. Estos ceros hacen que a altas frecuencias la ganancia vuelva a subir (a $+40\text{ dB/década}$), anulando el efecto del filtro pasa-bajos y dejando pasar ruido de alta frecuencia.

Para contrarrestar esto, podemos diseñar el polo de la Etapa 3 para que cancele exactamente uno de los ceros en lazo cerrado de las primeras etapas. Para ello, igualamos el polo de la Etapa 3 a la frecuencia del cero de las etapas anteriores ($19.5\text{ kHz}$):

$$f_{p,Stage3} = f_{z,Stage1,2} \implies \frac{1}{2\pi \cdot R_7 \cdot C_{f3}} = 19.49\text{ kHz}$$

Despejando $C_{f3}$: $$C_{f3} = \frac{1}{2\pi \cdot 10\text{ k}\Omega \cdot 19.49\text{ kHz}} \approx 817\text{ pF}$$

Valor comercial recomendado: $820\text{ pF}$ (un valor sumamente estándar y económico).
Resultado: El polo de la Etapa 3 se sitúa en $19.4\text{ kHz}$, cancelando dinámicamente uno de los ceros de las etapas anteriores. Esto mantiene la atenuación de alta frecuencia muy alta y estable (evitando que la ganancia vuelva a subir a frecuencias medias/altas).
Resumen de Recomendaciones
Si deseas un pasa-bajos agresivo y uniforme en baja frecuencia, elige la Opción 1 ($160\text{ nF}$).
Si deseas evitar que el ruido de alta frecuencia se amplifique debido al efecto de los ceros de las primeras etapas, elige la Opción 2 ($820\text{ pF}$).

---

Método 2: En Hardware Real (Selección de Componentes Físicos)
En un diseño físico real en placa de circuito impreso (PCB), para alejar estos polos y garantizar estabilidad absoluta de alta frecuencia contra oscilaciones parásitas, se debe reemplazar el modelo de operacional común por uno de alta velocidad (High-Speed / Wideband Op-Amp).

Utilizar integrados de alto rendimiento desplaza estos polos a valores astronómicos:

OPA828 (JFET de precisión): Con un $\text{GBWP} = 45\text{ MHz}$ y un polo secundario muy alto, desplaza los polos parásitos de lazo cerrado a frecuencias superiores a los $20\text{ MHz}$.
ADA4817-1 (FastFET ultra-rápido): Con un $\text{GBWP} = 410\text{ MHz}$, empuja estos polos de lazo cerrado por encima de los $100\text{ MHz}$, volviéndolos completamente imperceptibles y eliminando cualquier riesgo de inestabilidad o acoplamiento parásito en el rango útil del instrumento.
Resumen de Acción Recomendada:
Para tu simulación actual en SUPEROPAMP_PSPICE.CIR, edita el valor de FPOLE2 en las líneas 34, 39, 41, 46 y 48 de:

FPOLE2=9.45MEG $\rightarrow$ a FPOLE2=100MEG (o superior).