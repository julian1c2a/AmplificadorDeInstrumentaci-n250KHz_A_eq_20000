import os
import re
import subprocess
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ngspice_path = r"C:\msys64\ucrt64\bin\ngspice.exe"
workspace_dir = r"c:\msys64\home\julia\ngspice\AmplificadorDeInstrumentacion250KHz_A_eq_20000"

def load_base_netlist_body():
    base_file = os.path.join(workspace_dir, "ina_250khz_real.cir")
    with open(base_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Strip the control block and everything after it
    idx = content.find(".control")
    if idx != -1:
        content = content[:idx]
    return content

# --- UNIFIED HIGH-GAIN JFET MACROMODELS ---
# All models share a unified two-stage JFET/VCCS architecture with R3=40Meg (Aol ~ 220,000)
# to guarantee high accuracy, high input impedance, and consistent comparisons.

TL071_MODEL = """
* --- Macromodelo de JFET Op-Amp TL071 (GBWP = 3MHz) ---
.subckt TL071 vp vn out vcc vee
I1 vcc 10 200u
J1 11 vn 10 JX
J2 12 vp 10 JX
R1 11 vee 3.5k
R2 12 vee 3.5k
G1 0 int 11 12 2.5m
R3 int 0 40Meg
C3 int 0 293.1p
B1 out_pre 0 V=V(int) > V(vcc)-1.5 ? V(vcc)-1.5 : ( V(int) < V(vee)+1.5 ? V(vee)+1.5 : V(int) )
Rout out_pre out 50
.model JX PJF(IS=10f BETA=1m VTO=-1)
.ends
"""

LF357_MODEL = """
* --- Macromodelo de JFET Op-Amp LF357 (GBWP = 20MHz) ---
.subckt LF357 vp vn out vcc vee
I1 vcc 10 200u
J1 11 vn 10 JX
J2 12 vp 10 JX
R1 11 vee 3.5k
R2 12 vee 3.5k
G1 0 int 11 12 2.5m
R3 int 0 40Meg
C3 int 0 44.0p
B1 out_pre 0 V=V(int) > V(vcc)-1.5 ? V(vcc)-1.5 : ( V(int) < V(vee)+1.5 ? V(vee)+1.5 : V(int) )
Rout out_pre out 50
.model JX PJF(IS=10f BETA=1m VTO=-1)
.ends
"""

OPA828_MODEL = """
* --- Macromodelo de JFET Op-Amp OPA828 (GBWP = 45MHz) ---
.subckt OPA828 vp vn out vcc vee
I1 vcc 10 200u
J1 11 vn 10 JX
J2 12 vp 10 JX
R1 11 vee 3.5k
R2 12 vee 3.5k
G1 0 int 11 12 2.5m
R3 int 0 40Meg
C3 int 0 19.5p
B1 out_pre 0 V=V(int) > V(vcc)-1.5 ? V(vcc)-1.5 : ( V(int) < V(vee)+1.5 ? V(vee)+1.5 : V(int) )
Rout out_pre out 50
.model JX PJF(IS=10f BETA=1m VTO=-1)
.ends
"""

ADA4817_MODEL = """
* --- Macromodelo de FastFET Op-Amp ADA4817-1 (GBWP = 410MHz) ---
.subckt ADA4817 vp vn out vcc vee
I1 vcc 10 200u
J1 11 vn 10 JX
J2 12 vp 10 JX
R1 11 vee 3.5k
R2 12 vee 3.5k
G1 0 int 11 12 2.5m
R3 int 0 40Meg
C3 int 0 2.14p
B1 out_pre 0 V=V(int) > V(vcc)-1.5 ? V(vcc)-1.5 : ( V(int) < V(vee)+1.5 ? V(vee)+1.5 : V(int) )
Rout out_pre out 50
.model JX PJF(IS=10f BETA=1m VTO=-1)
.ends
"""

def prepare_netlist_base(case_name, model_def, xu1_call, xu2_call):
    body = load_base_netlist_body()
    
    # Insert specific JFET models before Stage 1
    insert_idx = body.find("* --- ETAPA 1")
    if insert_idx != -1:
        body = body[:insert_idx] + model_def + "\n" + body[insert_idx:]
        
    # Replace U1 and U2 calls to use specific model names
    body = body.replace("XU1 vp vn1 vout1 vcc vee OPAMP", f"XU1 vp vn1 vout1 vcc vee {xu1_call}")
    body = body.replace("XU2 vn vn2 vout2 vcc vee OPAMP", f"XU2 vn vn2 vout2 vcc vee {xu2_call}")
    return body

def run_ngspice(netlist_content, temp_filename):
    temp_path = os.path.join(workspace_dir, temp_filename)
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(netlist_content)
    
    subprocess.run([ngspice_path, "-b", temp_filename], cwd=workspace_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if os.path.exists(temp_path):
        os.remove(temp_path)

def load_data(filename):
    data = []
    path = os.path.join(workspace_dir, filename)
    if not os.path.exists(path):
        return np.array([])
    with open(path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    data.append([float(parts[0]), float(parts[1])])
                except ValueError:
                    pass
    if os.path.exists(path):
        os.remove(path)
    return np.array(data)

# --- EXECUTION STAGE ---
print("Starting 5-way JFET / FastFET simulation suite...")

cases = [
    ("ideal", "", "OPAMP", "OPAMP"),
    ("tl071", TL071_MODEL, "TL071", "TL071"),
    ("lf357", LF357_MODEL, "LF357", "LF357"),
    ("opa828", OPA828_MODEL, "OPA828", "OPA828"),
    ("ada4817", ADA4817_MODEL, "ADA4817", "ADA4817")
]

frequencies = [10, 50, 100, 150, 200, 250, 300]  # in kHz

# 1. RUN AC & DC FOR ALL 5 CASES
for case, model_def, xu1, xu2 in cases:
    print(f" - Running AC & DC for: {case}...")
    base = prepare_netlist_base(case, model_def, xu1, xu2)
    
    acdc_control = f"""
.control
  ac dec 100 10 10Meg
  let gain_db = vdb(vout_final)
  wrdata ac_{case}_mag.txt gain_db
  let phase_rad = ph(v(vout_final))
  let phase_deg = phase_rad * 180 / 3.141592653589793
  wrdata ac_{case}_phase.txt phase_deg

  dc Vdiff -0.4m 0.4m 5u
  wrdata dc_{case}.txt v(vout_final)
.endc
.end
"""
    run_ngspice(base + acdc_control, f"temp_{case}_acdc.cir")

# 2. RUN MULTI-FREQUENCY TRANSIENT FOR ALL 5 CASES
for case, model_def, xu1, xu2 in cases:
    base = prepare_netlist_base(case, model_def, xu1, xu2)
    for f in frequencies:
        print(f" - Running Transient at {f} kHz for: {case}...")
        f_hz = f * 1000.0
        t_stop = 3.0 / f_hz  # exactly 3 cycles
        t_step = t_stop / 2000.0
        
        tran_base = base.replace(
            "Vdiff vdiff_node 0 DC 0 AC 1 SIN(0 100u 10k)",
            f"Vdiff vdiff_node 0 DC 0 AC 1 SIN(0 100u {f_hz:.1f})"
        )
        
        tran_control = f"""
.control
  tran {t_step:.3e} {t_stop:.3e}
  wrdata tran_{case}_{f}khz.txt v(vout_final)
.endc
.end
"""
        run_ngspice(tran_base + tran_control, f"temp_{case}_tran_{f}khz.cir")

print("\nAll 40 simulations completed. Processing data...")

# --- DATA PROCESSING & CSV EXPORT ---

# A. Process AC Data (Bode)
ac_mags = {}
ac_phases = {}
for case, _, _, _ in cases:
    ac_mags[case] = load_data(f"ac_{case}_mag.txt")
    ac_phases[case] = load_data(f"ac_{case}_phase.txt")

if len(ac_mags["ideal"]) > 0:
    f_common = np.logspace(1, 7, 1000) # 10 Hz to 10 MHz
    
    mags_interp = {}
    phs_interp = {}
    for case, _, _, _ in cases:
        mags_interp[case] = np.interp(f_common, ac_mags[case][:, 0], ac_mags[case][:, 1])
        phs_interp[case] = np.interp(f_common, ac_phases[case][:, 0], ac_phases[case][:, 1])
        
    ac_df = pd.DataFrame({
        'Frequency_Hz': f_common,
        'Gain_Ideal_dB': mags_interp['ideal'],
        'Phase_Ideal_deg': phs_interp['ideal'],
        'Gain_TL071_dB': mags_interp['tl071'],
        'Phase_TL071_deg': phs_interp['tl071'],
        'Gain_LF357_dB': mags_interp['lf357'],
        'Phase_LF357_deg': phs_interp['lf357'],
        'Gain_OPA828_dB': mags_interp['opa828'],
        'Phase_OPA828_deg': phs_interp['opa828'],
        'Gain_ADA4817_dB': mags_interp['ada4817'],
        'Phase_ADA4817_deg': phs_interp['ada4817']
    })
    ac_csv_path = os.path.join(workspace_dir, "ac_comparison.csv")
    ac_df.to_csv(ac_csv_path, index=False)
    print(f"Saved 5-way AC magnitude & phase comparison to: {ac_csv_path}")

# B. Process DC Data (Linearity)
dc_data = {}
for case, _, _, _ in cases:
    dc_data[case] = load_data(f"dc_{case}.txt")

if len(dc_data["ideal"]) > 0:
    vdiff_grid = np.linspace(-0.4e-3, 0.4e-3, 1000)
    
    dc_interp = {}
    for case, _, _, _ in cases:
        dc_interp[case] = np.interp(vdiff_grid, dc_data[case][:, 0], dc_data[case][:, 1])
        
    dc_df = pd.DataFrame({
        'Vdiff_input_V': vdiff_grid,
        'Vout_Ideal_V': dc_interp['ideal'],
        'Vout_TL071_V': dc_interp['tl071'],
        'Vout_LF357_V': dc_interp['lf357'],
        'Vout_OPA828_V': dc_interp['opa828'],
        'Vout_ADA4817_V': dc_interp['ada4817']
    })
    dc_csv_path = os.path.join(workspace_dir, "dc_comparison.csv")
    dc_df.to_csv(dc_csv_path, index=False)
    print(f"Saved 5-way DC sweep comparison to: {dc_csv_path}")

# C. Process Transient Data (for each frequency)
for f in frequencies:
    trans_data = {}
    for case, _, _, _ in cases:
        trans_data[case] = load_data(f"tran_{case}_{f}khz.txt")
        
    if all(len(trans_data[case]) > 0 for case, _, _, _ in cases):
        t_max = np.max(trans_data["ideal"][:, 0])
        t_common = np.linspace(0, t_max, 2000)
        
        tran_interp = {}
        for case, _, _, _ in cases:
            tran_interp[case] = np.interp(t_common, trans_data[case][:, 0], trans_data[case][:, 1])
            
        tran_df = pd.DataFrame({
            'Time_s': t_common,
            'Vout_Ideal_V': tran_interp['ideal'],
            'Vout_TL071_V': tran_interp['tl071'],
            'Vout_LF357_V': tran_interp['lf357'],
            'Vout_OPA828_V': tran_interp['opa828'],
            'Vout_ADA4817_V': tran_interp['ada4817']
        })
        tran_csv_path = os.path.join(workspace_dir, f"tran_comparison_{f}khz.csv")
        tran_df.to_csv(tran_csv_path, index=False)
        print(f"Saved 5-way Transient comparison ({f} kHz) to: {tran_csv_path}")

# --- PLOT GENERATION ---
print("\nGenerating 5-way expanded visual plots...")

# Styling definitions for 5 distinct lines
styles = {
    'ideal':    {'label': 'Ideal Op-Amp (245.7 kHz)', 'color': '#1f77b4', 'ls': '-',  'lw': 2.5},
    'ada4817':  {'label': 'ADA4817-1 FastFET (245.7 kHz)', 'color': '#ff7f0e', 'ls': '-',  'lw': 3.0},
    'opa828':   {'label': 'OPA828 JFET (233.1 kHz)', 'color': '#9467bd', 'ls': '-.', 'lw': 2.5},
    'lf357':    {'label': 'LF357 JFET (199.7 kHz)', 'color': '#2ca02c', 'ls': '--', 'lw': 2.5},
    'tl071':    {'label': 'TL071 JFET (59.1 kHz)', 'color': '#d62728', 'ls': ':',  'lw': 2.5}
}

# 1. stacked Bode plot (SVG & PNG)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), sharex=True)

# Magnitude Subplot
for case in ['ideal', 'ada4817', 'opa828', 'lf357', 'tl071']:
    ax1.semilogx(f_common, mags_interp[case], label=styles[case]['label'], 
                 color=styles[case]['color'], linestyle=styles[case]['ls'], linewidth=styles[case]['lw'])
ax1.axvline(250e3, color='grey', linestyle='-.', label='Objetivo 250 kHz')
ax1.set_title('Respuesta de Frecuencia (Bode) - Comparación de Magnitud (5 Vías)', fontsize=14, pad=10)
ax1.set_ylabel('Ganancia (dB)', fontsize=12)
ax1.grid(True, which="both", ls="-", color='#e0e0e0')
ax1.legend(loc='lower left', fontsize=10)
ax1.set_ylim(20, 95)

# Phase Subplot
for case in ['ideal', 'ada4817', 'opa828', 'lf357', 'tl071']:
    ax2.semilogx(f_common, phs_interp[case], label=styles[case]['label'].split(' (')[0], 
                 color=styles[case]['color'], linestyle=styles[case]['ls'], linewidth=styles[case]['lw'])
ax2.axvline(250e3, color='grey', linestyle='-.')
ax2.set_title('Respuesta de Frecuencia (Bode) - Comparación de Desfase (5 Vías)', fontsize=14, pad=10)
ax2.set_xlabel('Frecuencia (Hz)', fontsize=12)
ax2.set_ylabel('Fase (Grados)', fontsize=12)
ax2.grid(True, which="both", ls="-", color='#e0e0e0')
ax2.legend(loc='lower left', fontsize=10)
ax2.set_ylim(-270, 45)
ax2.set_xlim(10, 10e6)

plt.tight_layout()
ac_png = os.path.join(workspace_dir, "ac_comparison.png")
ac_svg = os.path.join(workspace_dir, "ac_comparison.svg")
plt.savefig(ac_png, dpi=300, bbox_inches='tight')
plt.savefig(ac_svg, format='svg', bbox_inches='tight')
plt.close()
print("Saved 5-way Bode stacked plots.")

# 2. DC Linearity transfer curve plot (SVG & PNG)
plt.figure(figsize=(10, 6))
for case in ['ideal', 'ada4817', 'opa828', 'lf357', 'tl071']:
    plt.plot(vdiff_grid * 1e3, dc_interp[case], label=styles[case]['label'].split(' (')[0], 
             color=styles[case]['color'], linestyle=styles[case]['ls'], linewidth=styles[case]['lw'])

plt.title('Curva de Transferencia Estática DC - Comparación de Linealidad (5 Vías)', fontsize=14, pad=15)
plt.xlabel('Tensión de Entrada Diferencial Vdiff (mV)', fontsize=12)
plt.ylabel('Tensión de Salida Vout (V)', fontsize=12)
plt.grid(True, ls="-", color='#e0e0e0')
plt.legend(loc='upper left', fontsize=11)
plt.xlim(-0.5, 0.5)
plt.ylim(-16, 16)

dc_png = os.path.join(workspace_dir, "dc_comparison.png")
dc_svg = os.path.join(workspace_dir, "dc_comparison.svg")
plt.savefig(dc_png, dpi=300, bbox_inches='tight')
plt.savefig(dc_svg, format='svg', bbox_inches='tight')
plt.close()
print("Saved 5-way DC Linearity plots.")

# 3. Multi-frequency Transient response plots (SVG & PNG for each frequency)
for f in frequencies:
    tran_csv_path = os.path.join(workspace_dir, f"tran_comparison_{f}khz.csv")
    if os.path.exists(tran_csv_path):
        df = pd.read_csv(tran_csv_path)
        t_us = df['Time_s'].values * 1e6
        
        plt.figure(figsize=(10, 6))
        for case in ['ideal', 'ada4817', 'opa828', 'lf357', 'tl071']:
            col_name = f'Vout_{case.capitalize()}_V' if case == 'ideal' else f'Vout_{case.upper()}_V'
            plt.plot(t_us, df[col_name].values, label=styles[case]['label'].split(' (')[0], 
                     color=styles[case]['color'], linestyle=styles[case]['ls'], linewidth=styles[case]['lw'])
        
        plt.title(f'Respuesta Transitoria a {f} kHz (Senoidal, 100uV pico, 3 Ciclos) - 5 Vías', fontsize=14, pad=15)
        plt.xlabel('Tiempo (μs)', fontsize=12)
        plt.ylabel('Tensión de Salida (V)', fontsize=12)
        plt.grid(True, ls="-", color='#e0e0e0')
        plt.legend(loc='upper right', fontsize=11)
        
        tran_png = os.path.join(workspace_dir, f"tran_comparison_{f}khz.png")
        tran_svg = os.path.join(workspace_dir, f"tran_comparison_{f}khz.svg")
        plt.savefig(tran_png, dpi=300, bbox_inches='tight')
        plt.savefig(tran_svg, format='svg', bbox_inches='tight')
        plt.close()
        print(f"Saved 5-way Transient plots at {f} kHz.")

print("\nAll 5-way comparative simulations and graphing tasks completed successfully!")
