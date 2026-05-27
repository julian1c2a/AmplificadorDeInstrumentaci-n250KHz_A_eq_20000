import os
import subprocess
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

workspace_dir = r"c:\msys64\home\julia\ngspice\AmplificadorDeInstrumentación250KHz_A_eq_20000"
ngspice_path = r"C:\msys64\ucrt64\bin\ngspice.exe"

# Define the results directories
results_dir = os.path.join(workspace_dir, "results")
txt_dir = os.path.join(results_dir, "data", "txt")
csv_dir = os.path.join(results_dir, "data", "csv")
png_dir = os.path.join(results_dir, "img", "png")
svg_dir = os.path.join(results_dir, "img", "svg")

os.makedirs(txt_dir, exist_ok=True)
os.makedirs(csv_dir, exist_ok=True)
os.makedirs(png_dir, exist_ok=True)
os.makedirs(svg_dir, exist_ok=True)

# Define the common header (ADA4817, AD8397, SuperOpAmp, SuperOpAmpWithPowOut)
header_models = """* HIGH-SPEED PRECISION INSTRUMENTATION AMPLIFIER (ngspice format)
* ----------------------------------------------------------------------
* HIGH-SPEED ADA4817 MACROMODEL DEFINITION (ngspice Compatible)
* ----------------------------------------------------------------------
.Subckt ADA4817 100 101 102 103 104 105 106
Rz1	102	1020	Rideal	1e-6
Rz2	103	1030	Rideal	1e-6
Ibias	1020	1030	dc	1.5e-3
DzPS	98	1020	diode
Iquies	1020	98	dc	17.5e-3
RS1	98	1030	1e-3
RPPull	1020	99	Rideal	1e7
RPPull2	99	1030	Rideal	1e7
e1	111	110	1020	110	1
e2	110	112	110	1030	1
e3	110	0	99	0	1
RS2	1	100	1e-3
RS3	9	101	1e-3
VOS	1	2	dc	0
IbiasP	110	2	dc	2e-12
IbiasN	110	9	dc	2e-12
RinCMP	110	2	Rideal	500000e6
RinCMN	9	110	Rideal	500000e6
CinCMP	110	2	1.3e-12
CinCMN	9	110	1.3e-12
IOS	9	2	1e-12
RinDiff	9	2	Rideal	500e3
CinDiff	9	2	0.3e-12
g1	3	110	110	2	0.001
RInP	3	110	Rideal	1e3
RX1	40	3	Rideal	0.001
DInP	40	41	diode
DInN	42	40	diode
VinP	111	41	dc	3.26
VinN	42	112	dc	0.46
hVn	6	5	Vmeas1	707.10678
Vmeas1	20	110	DC	0
Vvn	21	110	dc	0.65
Dvn	21	20	DVnoisy
hVn1	6	7	Vmeas2	707.10678
Vmeas2	22	110	dc	0
Vvn1	23	110	dc	0.65
Dvn1	23	22	DVnoisy
FnIN	9	110	Vmeas3	0.7071068
Vmeas3	51	110	dc	0
Vvn_in	50	110	dc	0.65
DnIN	50	51	DINnoisy
FnIN1	110	9	Vmeas4	0.7071068
Vmeas4	53	110	dc	0
Vvn_in1	52	110	dc	0.65
DnIN1	52	53	DINnoisy
FnIP	2	110	Vmeas5	0.7071068
Vmeas5	31	110	dc	0
Vvn_ip	30	110	dc	0.65
DnIP	30	31	DIPnoisy
FnIP1	110	2	Vmeas6	0.7071068
Vmeas6	33	110	dc	0
Vvn_ip1	32	110	dc	0.65
DnIP1	32	33	DIPnoisy
RcmrrP	3	10	Rideal	1e12
RcmrrN	10	9	Rideal	1e12
g10	11	110	10	110	-1e-10
Lcmrr	11	12	1e-12
Rcmrr	12	110	Rideal	1e3
e4	5	3	11	110	1
VPD	111	80	dc	3
VPD1	81	0	dc	2
RPD	111	106	Rideal	1e6
ePD	80	113	82	0	1
RP1	82	0	Rideal	1e3
CPD	82	0	1e-10
RS5	81	82	1e-3
CDP1	83	0	1e-12
RPD2	106	83	1e6
RF	105	104	Rideal	0.001
g200	200	110	7	9	1
R200	200	110	Rideal	250
DzSlewP	201	200	DzSlewP
DzSlewN	201	110	DzSlewN
g210	210	110	200	110	11.5515e-6
R210	210	110	Rideal	0.55e6
C210	210	110	1e-012
RX2	60	210	Rideal	0.001
DzVoutP	61	60	DzVoutP
DzVoutN	60	62	DzVoutN
DVoutP	61	63	diode
DVoutN	64	62	diode
VoutP	65	63	dc	6.404
VoutN	64	66	dc	6.512
e60	65	110	111	110	1.08
e61	66	110	112	110	1.08
g220	220	110	210	110	0.001
R220	220	110	Rideal	1000
R221	220	221	Rideal	9e3
C220	221	110	17.6839e-12
g230	230	110	220	110	0.001
R230	230	110	Rideal	1000
C230	230	110	0.0804e-12
g240	240	110	230	110	0.001
R240	240	110	Rideal	1000
C240	240	110	0.0751e-12
g245	245	110	240	110	0.001
R245	245	110	Rideal	1000
C245	245	110	0.0531e-12
g250	250	110	245	110	0.001
R250	250	110	Rideal	1000
g255	255	110	250	110	0.001
R255	255	110	Rideal	1000
g260	260	110	255	110	0.001
R260	260	110	Rideal	1000
g265	265	110	260	110	0.001
R265	265	110	Rideal	1000
g270	270	110	265	110	0.001
R270	270	110	Rideal	1000
e280	280	110	270	110	1
R280	280	285	Rideal	10
e290	290	110	285	110	1
R290	290	292	Rideal	10
L290	290	291	5305.159e-9
C290	291	292	212206.351e-12
R291	292	110	Rideal	13.929
e295	295	110	292	110	1.7179
g300	300	110	295	110	0.001
R300	300	110	Rideal	1000
e301	301	110	300	110	1
Rout	302	303	Rideal	 8
Lout	303	310	 5.6e-9
Cout	310	110	 1.3e-12
H1	301	304	Vsense1	100
Vsense1	301	302	dc	0
VIoutP	305	304	dc	16.336
VIoutN	304	306	dc	9.336
DIoutP	307	305	diode
DIoutN	306	307	diode
Rx3	307	300	Rideal	0.001
VoutP1	111	73	dc	1.685
VoutN1	74	112	dc	1.685
DVoutP1	75	73	diode
DVoutN1	74	75	diode
RX4	75	310	Rideal	0.001
FIoVcc	314	110	Vmeas8	1
Vmeas8	310	311	dc	0
R314	110	314	Rideal	1e9
DzOVcc	110	314	diode
DOVcc	102	314	diode
RX5	311	312	Rideal	0.001
FIoVee	315	110	Vmeas9	1
Vmeas9	312	313	dc	0
R315	315	110	Rideal	1e9
DzOVee	315	110	diode
DOVee	315	103	diode
RS4	104	313	1e-3
.model	diode	d(bv=100)
.model	Switch	sw(vt=2.0 vh=0.005 ron=0.001 roff=1e6)
.model	DzVoutP	D(BV=4.3)
.model	DzVoutN	D(BV=4.3)
.model	DzSlewP	D(BV=75.79)
.model	DzSlewN	D(BV=75.79)
.model	DVnoisy	D(IS=5e-16 KF=7.07e-15)
.model	DINnoisy	D(IS=2.38e-22 KF=0.00e0)
.model	DIPnoisy	D(IS=2.38e-22 KF=0.00e0)
.model	Rideal	res(T_ABS=-273)
.ends ADA4817
* ----------------------------------------------------------------------

* ----------------------------------------------------------------------
* HIGH-OUTPUT-CURRENT AD8397 OP-AMP MACROMODEL DEFINITION
* ----------------------------------------------------------------------
.subckt AD8397 vp vn out vcc vee
Rin vp vn 10Meg
Cin vp vn 1.5p
G1 0 int vp vn 1m
R1 int 0 100Meg
C1 int 0 2.3e-12
E2 int2 0 int 0 1
R2 int2 int3 1k
C2 int3 0 1.99e-12
E3 out_pre 0 int3 0 1
Rout out_pre out 1.5
.ends AD8397
* ----------------------------------------------------------------------

* ----------------------------------------------------------------------
* STANDARD SUPEROPAMP SUBCIRCUIT DEFINITION
* ----------------------------------------------------------------------
.subckt SuperOpAmp vp vn out ref vcc vee
C2          13 4 1.6P 
C1          3 14 1.6P 
R3          14 13 500 
R2          4 13 49.5K 
R1          3 14 49.5K 
XOP2         vp 13 vcc vee 4 4 vcc ADA4817
XOP1         vn 14 vcc vee 3 3 vcc ADA4817
C4          11 6 1.6P 
C3          5 12 1.6P 
R6          12 11 500 
R5          6 11 49.5K 
R4          5 12 49.5K 
XOP4         4 11 vcc vee 6 6 vcc ADA4817
XOP3         3 12 vcc vee 5 5 vcc ADA4817
C6          ref 8 8P 
C5          9 out 8P 
R10         6 8 750 
R9          8 ref 15K 
R8          5 9 750 
R7          9 out 15K 
XOP5         8 9 vcc vee out out vcc ADA4817
.ends SuperOpAmp
* ----------------------------------------------------------------------

* ----------------------------------------------------------------------
* HIGH-POWER SUPEROPAMPWITHPOWOUT SUBCIRCUIT DEFINITION
* ----------------------------------------------------------------------
.subckt SuperOpAmpWithPowOut vp vn out ref vcc vee
C2          13 4 1.6P 
C1          3 14 1.6P 
R3          14 13 500 
R2          4 13 49.5K 
R1          3 14 49.5K 
XOP2         vp 13 vcc vee 4 4 vcc ADA4817
XOP1         vn 14 vcc vee 3 3 vcc ADA4817
C4          11 6 1.6P 
C3          5 12 1.6P 
R6          12 11 500 
R5          6 11 49.5K 
R4          5 12 49.5K 
XOP4         4 11 vcc vee 6 6 vcc ADA4817
XOP3         3 12 vcc vee 5 5 vcc ADA4817
C6          ref 8 8P 
C5          9 out_pre 8P 
R10         6 8 750 
R9          8 ref 15K 
R8          5 9 750 
R7          9 out_pre 15K 
XOP5         8 9 vcc vee out_pre out_pre vcc ADA4817
XOUT         out_pre out out vcc vee AD8397
.ends SuperOpAmpWithPowOut
* ----------------------------------------------------------------------
"""

def load_spice_data(filename):
    path = os.path.join(txt_dir, filename)
    data = []
    if not os.path.exists(path):
        return np.array([])
    with open(path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    data.append([float(x) for x in parts])
                except ValueError:
                    pass
    return np.array(data)

def run_simulation(netlist_content, netlist_name):
    path = os.path.join(workspace_dir, netlist_name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(netlist_content)
    
    subprocess.run(
        [ngspice_path, "-b", netlist_name],
        cwd=workspace_dir,
        capture_output=True,
        text=True
    )
    
    if os.path.exists(path):
        os.remove(path)

# --- 1. RUN AC / DC CHARACTERIZATION ---
ac_dc_netlist = header_models + """
.TEMP 27
V3          cc 0 DC 20
V2          0 dd DC 20

* Balanced Differential Input Source
Vdiff_node   vdiff_node 0 DC 0 AC 1 SIN(0 100u 10k)
E_in_p       vp 0 vdiff_node 0 0.5
E_in_n       vn 0 vdiff_node 0 -0.5

* --- STAGE 1: Composite Input Buffers (Av1 = 200) ---
XU1          vp vn1 vout1 0 cc dd SuperOpAmp
XU2          vn vn2 vout2 0 cc dd SuperOpAmp
Rg           vn1 vn2 500
R_f1         vout1 vn1 49.75K
R_f2         vout2 vn2 49.75K

* --- STAGE 2: Composite Power Difference Amplifier (Av2 = 100) ---
XU3          vp3 vn3 vout_final 0 cc dd SuperOpAmp
R_in1        vout1 vp3 750
R_ref        vp3 0 75K
R_in2        vout2 vn3 750
R_fb         vout_final vn3 75K

RL           vout_final 0 10K

.options method=gear cmin=1e-12 reltol=1e-3

.control
  * DC sweep from -2mV to +2mV (covers negative sat, positive sat, and linear region)
  dc Vdiff_node -2m 2m 5u
  wrdata results/data/txt/instrampl_dc_char.txt v(vout_final)
  
  * AC sweep up to 500MHz to find cutoff frequency
  ac dec 100 1 500meg
  let gain_db = vdb(vout_final)
  let phase_rad = ph(v(vout_final))
  let phase_deg = phase_rad * 180 / 3.141592653589793
  wrdata results/data/txt/instrampl_ac_char.txt gain_db phase_deg
.endc
.END
"""

print("Executing AC & DC Linearity simulation...")
run_simulation(ac_dc_netlist, "char_ac_dc.cir")

# --- 2. RUN COMMON-MODE RESPONSE FOR CMRR ---
cm_netlist = header_models + """
.TEMP 27
V3          cc 0 DC 20
V2          0 dd DC 20

* Common-Mode Input Source (in-phase on both vp and vn)
Vdiff_node   vdiff_node 0 DC 0 AC 1
E_in_p       vp 0 vdiff_node 0 1.0
E_in_n       vn 0 vdiff_node 0 1.0

XU1          vp vn1 vout1 0 cc dd SuperOpAmp
XU2          vn vn2 vout2 0 cc dd SuperOpAmp
Rg           vn1 vn2 500
R_f1         vout1 vn1 49.75K
R_f2         vout2 vn2 49.75K

XU3          vp3 vn3 vout_final 0 cc dd SuperOpAmp
R_in1        vout1 vp3 750
R_ref        vp3 0 75K
R_in2        vout2 vn3 750
R_fb         vout_final vn3 75K

RL           vout_final 0 10K

.options method=gear cmin=1e-12 reltol=1e-3

.control
  ac dec 100 1 500meg
  let gain_db = vdb(vout_final)
  wrdata results/data/txt/instrampl_ac_cm_char.txt gain_db
.endc
.END
"""

print("Executing Common-Mode AC simulation...")
run_simulation(cm_netlist, "char_cm.cir")

# --- 3. RUN OUTPUT IMPEDANCE SIMULATION ---
zout_netlist = header_models + """
.TEMP 27
V3          cc 0 DC 20
V2          0 dd DC 20

* Inputs are grounded for Zout simulation
Vdiff_node   vdiff_node 0 DC 0 AC 0
E_in_p       vp 0 vdiff_node 0 0.5
E_in_n       vn 0 vdiff_node 0 -0.5

XU1          vp vn1 vout1 0 cc dd SuperOpAmp
XU2          vn vn2 vout2 0 cc dd SuperOpAmp
Rg           vn1 vn2 500
R_f1         vout1 vn1 49.75K
R_f2         vout2 vn2 49.75K

XU3          vp3 vn3 vout_final 0 cc dd SuperOpAmp
R_in1        vout1 vp3 750
R_ref        vp3 0 75K
R_in2        vout2 vn3 750
R_fb         vout_final vn3 75K

* AC Current test source of 1A at the output node
Itest        vout_final 0 DC 0 AC 1

.options method=gear cmin=1e-12 reltol=1e-3

.control
  ac dec 100 1 100meg
  * Output voltage directly corresponds to Zout (Z = V / 1A)
  let zout_mag = vm(vout_final)
  wrdata results/data/txt/instrampl_ac_zout_char.txt zout_mag
.endc
.END
"""

print("Executing Output Impedance simulation...")
run_simulation(zout_netlist, "char_zout.cir")

# Load AC & DC data to find exact fc
dc_data = load_spice_data("instrampl_dc_char.txt")
ac_data = load_spice_data("instrampl_ac_char.txt")
ac_cm_data = load_spice_data("instrampl_ac_cm_char.txt")
ac_zout_data = load_spice_data("instrampl_ac_zout_char.txt")

freq = ac_data[:, 0]
gain_db = ac_data[:, 1]
phase_deg = ac_data[:, 3]

dc_gain_db = gain_db[0]
target_gain = dc_gain_db - 3.0
peak_idx = np.argmax(gain_db)
idx_3db = np.where((freq > freq[peak_idx]) & (gain_db <= target_gain))[0]
fc = freq[idx_3db[0]] if len(idx_3db) > 0 else 16.6e6

print(f"\nDiscovered cutoff frequency (fc) = {fc/1e6:.2f} MHz")

# --- 4. RUN TRANSIENT SIMULATIONS AT 0.25fc, 0.5fc, fc, 2fc, 10fc, 50fc ---
frequencies = {
    "0_25_fc": (0.25 * fc, "0.25 fc"),
    "0_5_fc": (0.5 * fc, "0.5 fc"),
    "fc": (fc, "1.0 fc"),
    "2_fc": (2.0 * fc, "2.0 fc"),
    "10_fc": (10.0 * fc, "10.0 fc"),
    "50_fc": (50.0 * fc, "50.0 fc")
}

for key, (f_val, label) in frequencies.items():
    print(f"Executing Transient simulation at {label} ({f_val/1e6:.2f} MHz)...")
    
    period = 1.0 / f_val
    t_step = period / 40.0  # 40 points per period for speed and accuracy
    t_stop = 8.0 * period   # 8 periods (steady state is reached in <2 periods at MHz)
    
    tran_netlist = header_models + f"""
.TEMP 27
V3          cc 0 DC 20
V2          0 dd DC 20

* Balanced input source at specific transient frequency
Vdiff_node   vdiff_node 0 DC 0 AC 1 SIN(0 100u {f_val:.6e})
E_in_p       vp 0 vdiff_node 0 0.5
E_in_n       vn 0 vdiff_node 0 -0.5

XU1          vp vn1 vout1 0 cc dd SuperOpAmp
XU2          vn vn2 vout2 0 cc dd SuperOpAmp
Rg           vn1 vn2 500
R_f1         vout1 vn1 49.75K
R_f2         vout2 vn2 49.75K

XU3          vp3 vn3 vout_final 0 cc dd SuperOpAmp
R_in1        vout1 vp3 750
R_ref        vp3 0 75K
R_in2        vout2 vn3 750
R_fb         vout_final vn3 75K

RL           vout_final 0 10K

.options method=gear cmin=1e-12 reltol=1e-3

.control
  tran {t_step:.6e} {t_stop:.6e}
  wrdata results/data/txt/instrampl_tran_{key}.txt v(vp,vn) v(vout_final)
.endc
.END
"""
    run_simulation(tran_netlist, f"char_tran_{key}.cir")

# SETUP PLOTS
print("\nSimulations finished. Starting analysis and generation of plots...")
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['text.color'] = '#1e293b'
plt.rcParams['axes.labelcolor'] = '#1e293b'
plt.rcParams['xtick.color'] = '#475569'
plt.rcParams['ytick.color'] = '#475569'

c_primary = '#4f46e5'   # Indigo
c_secondary = '#0ea5e9' # Ocean blue
c_phase = '#db2777'     # Deep pink
c_dark = '#0f172a'
c_grid = '#f1f5f9'
c_border = '#cbd5e1'

# --- PLOT 1: DC LINEARITY & SATURATION WITH ELBOWS ZOOM ---
vin_dc = dc_data[:, 0]
vout_dc = dc_data[:, 1]

# Local gain calculation (derivative)
local_gain = np.gradient(vout_dc, vin_dc)

# Fit polynomial in the highly linear region (+/- 0.6 mV)
lin_mask = (vin_dc > -0.6e-3) & (vin_dc < 0.6e-3)
vin_lin = vin_dc[lin_mask]
vout_lin = vout_dc[lin_mask]
coefs = np.polyfit(vin_lin, vout_lin, 3)  # Vout = c3*Vin^3 + c2*Vin^2 + c1*Vin + c0
# coefs is [c3, c2, c1, c0]
c3, c2, c1, c0 = coefs

print(f"\nPolynomial component expansion in the linear region:")
print(f"Vout(Vin) = {c3:.4e}*Vin^3 + {c2:.4e}*Vin^2 + {c1:.4f}*Vin + {c0:.6f}")
print(f"- Constant offset (c0): {c0*1e3:.4f} mV")
print(f"- Linear gain (c1): {c1:.2f} (Target: 20000, Error: {abs(c1-20000)/200:.4f}%)")
print(f"- Quadratic component (c2): {c2:.4e} V^-1 (representing even harmonic distortion)")
print(f"- Cubic component (c3): {c3:.4e} V^-2 (representing odd harmonic distortion)")

fig = plt.figure(figsize=(16, 12), dpi=150)
grid = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.25)

# Main DC Transfer Curve Plot
ax_dc = fig.add_subplot(grid[0, :])
ax_dc.plot(vin_dc * 1e3, vout_dc, color=c_primary, linewidth=3, label='Static Transfer Curve')
ax_dc.axhline(0, color='#94a3b8', linestyle=':', linewidth=1)
ax_dc.axvline(0, color='#94a3b8', linestyle=':', linewidth=1)

# Annotate regions
ax_dc.fill_between(vin_dc * 1e3, -21, 21, where=(vin_dc < -1.0e-3), color='#fee2e2', alpha=0.3, label='Negative Saturation')
ax_dc.fill_between(vin_dc * 1e3, -21, 21, where=(vin_dc > 1.0e-3), color='#fee2e2', alpha=0.3)
ax_dc.fill_between(vin_dc * 1e3, -21, 21, where=((vin_dc >= -1.0e-3) & (vin_dc <= 1.0e-3)), color='#ecfdf5', alpha=0.3, label='Linear Region')

ax_dc.set_title("Full DC Static Transfer Curve (Saturation to Saturation)", fontsize=14, fontweight='bold', pad=15)
ax_dc.set_xlabel("Input Differential Voltage $V_{in}$ (mV)", fontsize=11, labelpad=8)
ax_dc.set_ylabel("Output Voltage $V_{out}$ (V)", fontsize=11, labelpad=8)
ax_dc.grid(True, color=c_grid, linestyle='-', linewidth=1)
ax_dc.set_xlim(-2.1, 2.1)
ax_dc.set_ylim(-21, 21)
ax_dc.legend(loc='lower right', frameon=True, facecolor='white', edgecolor=c_border)

# Inset Text for Polynomial
poly_text = (
    f"Linear Fit in +/-0.6mV region:\\n"
    f"$V_{{out}} = c_3 V_{{in}}^3 + c_2 V_{{in}}^2 + c_1 V_{{in}} + c_0$\\n"
    f"  $c_0$ (Offset) = {c0*1e3:.3f} mV\\n"
    f"  $c_1$ (Gain) = {c1:.1f} ({20*np.log10(c1):.2f} dB)\\n"
    f"  $c_2$ (Quadratic) = {c2:.3e} $V^{{-1}}$\\n"
    f"  $c_3$ (Cubic) = {c3:.3e} $V^{{-2}}$"
)
ax_dc.text(-2.0, 5, poly_text, bbox=dict(boxstyle="round,pad=0.5", fc='white', ec=c_border, alpha=0.9), fontsize=10, family='monospace')

# --- ZOOM INTO CODOS (ELBOWS) ---
# Negative Elbow: near -1.0 mV
ax_neg_elbow = fig.add_subplot(grid[1, 0])
neg_mask = (vin_dc > -1.2e-3) & (vin_dc < -0.8e-3)
ax_neg_elbow.plot(vin_dc[neg_mask] * 1e3, vout_dc[neg_mask], color=c_secondary, linewidth=2.5, label='Vout')
ax_neg_elbow_gain = ax_neg_elbow.twinx()
ax_neg_elbow_gain.plot(vin_dc[neg_mask] * 1e3, local_gain[neg_mask], color=c_phase, linestyle='--', linewidth=2, label='Local Gain')
ax_neg_elbow.set_title("Negative Elbow Transition Detail ($V_{in} \\approx -1.0$ mV)", fontsize=12, fontweight='bold', pad=10)
ax_neg_elbow.set_xlabel("Input Differential Voltage $V_{in}$ (mV)", fontsize=10)
ax_neg_elbow.set_ylabel("Output Voltage (V)", fontsize=10, color=c_secondary)
ax_neg_elbow_gain.set_ylabel("Local Gain $dV_{out}/dV_{in}$", fontsize=10, color=c_phase)
ax_neg_elbow.grid(True, color=c_grid)
ax_neg_elbow.set_xlim(-1.2, -0.8)

# Positive Elbow: near +1.0 mV
ax_pos_elbow = fig.add_subplot(grid[1, 1])
pos_mask = (vin_dc > 0.8e-3) & (vin_dc < 1.2e-3)
ax_pos_elbow.plot(vin_dc[pos_mask] * 1e3, vout_dc[pos_mask], color=c_secondary, linewidth=2.5)
ax_pos_elbow_gain = ax_pos_elbow.twinx()
ax_pos_elbow_gain.plot(vin_dc[pos_mask] * 1e3, local_gain[pos_mask], color=c_phase, linestyle='--', linewidth=2)
ax_pos_elbow.set_title("Positive Elbow Transition Detail ($V_{in} \\approx +1.0$ mV)", fontsize=12, fontweight='bold', pad=10)
ax_pos_elbow.set_xlabel("Input Differential Voltage $V_{in}$ (mV)", fontsize=10)
ax_pos_elbow.set_ylabel("Output Voltage (V)", fontsize=10, color=c_secondary)
ax_pos_elbow_gain.set_ylabel("Local Gain $dV_{out}/dV_{in}$", fontsize=10, color=c_phase)
ax_pos_elbow.grid(True, color=c_grid)
ax_pos_elbow.set_xlim(0.8, 1.2)

plt.suptitle("Instrumentation Amplifier - DC Linearity & Saturation Elbow Analysis", fontsize=16, fontweight='bold', y=0.98)
fig_dc_png = os.path.join(png_dir, "instrampl_dc_characterization.png")
fig_dc_svg = os.path.join(svg_dir, "instrampl_dc_characterization.svg")
plt.savefig(fig_dc_png, dpi=300, bbox_inches='tight')
plt.savefig(fig_dc_svg, format='svg', bbox_inches='tight')
plt.close()

# --- PLOT 2: AC BODE PLOT ---
fig_ac = plt.figure(figsize=(10, 7), dpi=150)
ax_mag = fig_ac.add_subplot(111)
ax_ph = ax_mag.twinx()

line1, = ax_mag.semilogx(freq, gain_db, color=c_primary, linewidth=2.5, label='Magnitude (dB)')
line2, = ax_ph.semilogx(freq, phase_deg, color=c_phase, linewidth=2.0, linestyle='--', label='Phase (Deg)')

ax_mag.set_title("AC Bode Response & Cutoff Frequency (fc)", fontsize=14, fontweight='bold', pad=15)
ax_mag.set_xlabel("Frequency (Hz)", fontsize=11, labelpad=8)
ax_mag.set_ylabel("Gain (dB)", fontsize=11, color=c_primary, labelpad=8)
ax_ph.set_ylabel("Phase (Degrees)", fontsize=11, color=c_phase, labelpad=8)

ax_mag.grid(True, which="both", color=c_grid, linestyle='-', linewidth=1)
ax_mag.set_xlim(10, 500e6)
ax_mag.set_ylim(-10, 100)
ax_ph.set_ylim(-270, 45)

# Cutoff line
ax_mag.axvline(fc, color='#64748b', linestyle='-.', linewidth=1.5)
ax_mag.text(fc*1.1, 40, f"fc = {fc/1e6:.2f} MHz\\nPhase = {phase_deg[idx_3db[0]]:.1f}°", color='#334155', fontsize=10, fontweight='bold')

lines = [line1, line2]
labels = [l.get_label() for l in lines]
ax_mag.legend(lines, labels, loc='lower left', frameon=True, edgecolor=c_border)

fig_ac_png = os.path.join(png_dir, "instrampl_ac_characterization.png")
fig_ac_svg = os.path.join(svg_dir, "instrampl_ac_characterization.svg")
plt.savefig(fig_ac_png, dpi=300, bbox_inches='tight')
plt.savefig(fig_ac_svg, format='svg', bbox_inches='tight')
plt.close()

# --- PLOT 3: CMRR PLOT ---
gain_cm_db = ac_cm_data[:, 1]
cmrr = gain_db - gain_cm_db

print(f"\nCommon-Mode Rejection Ratio (CMRR) results:")
for target_f in [10, 500e3, fc]:
    idx = np.argmin(np.abs(freq - target_f))
    print(f"- CMRR at {freq[idx]/1e3:.2f} kHz: {cmrr[idx]:.2f} dB")

fig_cmrr = plt.figure(figsize=(10, 6), dpi=150)
ax_cmrr = fig_cmrr.add_subplot(111)
ax_cmrr.semilogx(freq, cmrr, color=c_secondary, linewidth=2.5, label='CMRR (dB)')
ax_cmrr.set_title("Common-Mode Rejection Ratio (CMRR) vs Frequency", fontsize=14, fontweight='bold', pad=15)
ax_cmrr.set_xlabel("Frequency (Hz)", fontsize=11, labelpad=8)
ax_cmrr.set_ylabel("CMRR (dB)", fontsize=11, labelpad=8)
ax_cmrr.grid(True, which="both", color=c_grid, linestyle='-', linewidth=1)
ax_cmrr.set_xlim(10, 500e6)
ax_cmrr.set_ylim(0, 160)

# Annotate DC & 500kHz CMRR
idx_dc = 0
idx_500k = np.argmin(np.abs(freq - 500e3))
ax_cmrr.plot(freq[idx_dc], cmrr[idx_dc], 'o', color=c_primary, markersize=8)
ax_cmrr.text(freq[idx_dc]*2, cmrr[idx_dc]-5, f"CMRR (Low Freq) = {cmrr[idx_dc]:.1f} dB", color=c_dark, fontsize=9, fontweight='bold')
ax_cmrr.plot(freq[idx_500k], cmrr[idx_500k], 'o', color=c_primary, markersize=8)
ax_cmrr.text(freq[idx_500k]*0.05, cmrr[idx_500k]+5, f"CMRR (500 kHz) = {cmrr[idx_500k]:.1f} dB", color=c_dark, fontsize=9, fontweight='bold')

fig_cmrr_png = os.path.join(png_dir, "instrampl_cmrr_characterization.png")
fig_cmrr_svg = os.path.join(svg_dir, "instrampl_cmrr_characterization.svg")
plt.savefig(fig_cmrr_png, dpi=300, bbox_inches='tight')
plt.savefig(fig_cmrr_svg, format='svg', bbox_inches='tight')
plt.close()

# --- PLOT 4: OUTPUT IMPEDANCE PLOT ---
freq_zout = ac_zout_data[:, 0]
zout_mag = ac_zout_data[:, 1]

print(f"\nOutput Impedance (Zout) results:")
for target_f in [10, 500e3, fc]:
    idx = np.argmin(np.abs(freq_zout - target_f))
    print(f"- Zout at {freq_zout[idx]/1e3:.2f} kHz: {zout_mag[idx]:.4f} Ohm")

fig_zout = plt.figure(figsize=(10, 6), dpi=150)
ax_zout = fig_zout.add_subplot(111)
ax_zout.loglog(freq_zout, zout_mag, color='#10b981', linewidth=2.5, label='Zout (Ohm)')
ax_zout.set_title("Output Impedance $Z_{out}$ vs Frequency", fontsize=14, fontweight='bold', pad=15)
ax_zout.set_xlabel("Frequency (Hz)", fontsize=11, labelpad=8)
ax_zout.set_ylabel("Impedance $Z_{out}$ ($\Omega$)", fontsize=11, labelpad=8)
ax_zout.grid(True, which="both", color=c_grid, linestyle='-', linewidth=1)
ax_zout.set_xlim(10, 100e6)
ax_zout.set_ylim(1e-3, 100)

fig_zout_png = os.path.join(png_dir, "instrampl_zout_characterization.png")
fig_zout_svg = os.path.join(svg_dir, "instrampl_zout_characterization.svg")
plt.savefig(fig_zout_png, dpi=300, bbox_inches='tight')
plt.savefig(fig_zout_svg, format='svg', bbox_inches='tight')
plt.close()

# --- PLOT 5: TRANSIENT GRID (0.25fc, 0.5fc, fc, 2fc, 10fc, 50fc) ---
fig_tran, axes = plt.subplots(3, 2, figsize=(15, 15), dpi=150, gridspec_kw={'hspace': 0.35, 'wspace': 0.25})
axes = axes.flatten()

# --- NEW PLOT 6: FFT SPECTRUM GRID ---
fig_spec, axes_spec = plt.subplots(3, 2, figsize=(15, 15), dpi=150, gridspec_kw={'hspace': 0.35, 'wspace': 0.25})
axes_spec = axes_spec.flatten()

print(f"\nTransient Response & FFT Spectrum Analysis at Multiple Frequencies:")

for i, (key, (f_val, label)) in enumerate(frequencies.items()):
    ax = axes[i]
    ax_spec = axes_spec[i]
    tran_data = load_spice_data(f"instrampl_tran_{key}.txt")
    
    if len(tran_data) > 0:
        time_sec = tran_data[:, 0]
        vin_tran = tran_data[:, 1]
        vout_tran = tran_data[:, 3]
        
        # Calculate exactly the period and keep last 4 periods (periods 4 to 8)
        period = 1.0 / f_val
        t_start_extract = 4.0 * period
        
        extract_mask = time_sec >= t_start_extract
        t_extracted = (time_sec[extract_mask] - t_start_extract) * 1e9  # nanoseconds
        vin_extracted = vin_tran[extract_mask]
        vout_extracted = vout_tran[extract_mask]
        
        # Calculate peak-to-peak output and actual gain
        v_pp_in = np.max(vin_extracted) - np.min(vin_extracted)
        v_pp_out = np.max(vout_extracted) - np.min(vout_extracted)
        actual_gain = v_pp_out / v_pp_in
        
        # Plot waveforms (AC-coupled for clarity, removing transient DC drift)
        vout_dc_offset = np.mean(vout_extracted)
        vout_ac = vout_extracted - vout_dc_offset
        
        # --- RIGOROUS FFT & THD ANALYSIS ---
        # Uniform interpolation to avoid uneven time-step issues (SPICE uses variable time steps)
        n_samples = 2048
        t_uniform = np.linspace(t_extracted[0], t_extracted[-1], n_samples)
        # Convert t_extracted (in ns) to seconds for interpolation
        vout_uniform = np.interp(t_uniform, t_extracted, vout_ac)
        
        # Compute FFT
        dt = (t_uniform[1] - t_uniform[0]) * 1e-9  # time step in seconds
        yf = np.fft.fft(vout_uniform)
        xf = np.fft.fftfreq(n_samples, dt)
        
        # Keep positive frequencies
        pos_mask_fft = xf >= 0
        freqs_pos = xf[pos_mask_fft]
        mags_pos = 2.0 / n_samples * np.abs(yf[pos_mask_fft]) # Peak amplitude
        
        # Locate fundamental peak
        idx_fund = np.argmin(np.abs(freqs_pos - f_val))
        window = 1
        start_w = max(0, idx_fund - window)
        end_w = min(len(freqs_pos), idx_fund + window + 1)
        fund_peak_idx = start_w + np.argmax(mags_pos[start_w:end_w])
        
        fund_amp = mags_pos[fund_peak_idx]
        fund_freq = freqs_pos[fund_peak_idx]
        
        # Locate harmonics (2nd to 5th order)
        harm_amps = []
        harm_freqs = []
        for h_order in [2, 3, 4, 5]:
            target_h_freq = h_order * fund_freq
            idx_h = np.argmin(np.abs(freqs_pos - target_h_freq))
            start_h = max(0, idx_h - window)
            end_h = min(len(freqs_pos), idx_h + window + 1)
            h_peak_idx = start_h + np.argmax(mags_pos[start_h:end_h])
            harm_amps.append(mags_pos[h_peak_idx])
            harm_freqs.append(freqs_pos[h_peak_idx])
            
        # Compute THD in %
        thd = np.sqrt(np.sum(np.square(harm_amps))) / fund_amp * 100.0 if fund_amp > 0 else 0.0
        
        # Calculate phase shift in degrees by correlation / zero-crossings
        z_cross_in = np.where(np.diff(np.sign(vin_extracted)) > 0)[0]
        z_cross_out = np.where(np.diff(np.sign(vout_extracted)) > 0)[0]
        
        phase_shift_deg = 0.0
        if len(z_cross_in) > 0 and len(z_cross_out) > 0:
            dt_ns = t_extracted[z_cross_out[0]] - t_extracted[z_cross_in[0]]
            phase_shift_deg = (dt_ns / (period * 1e9)) * 360.0
            if phase_shift_deg > 180.0:
                phase_shift_deg -= 360.0
            elif phase_shift_deg < -180.0:
                phase_shift_deg += 360.0
                
        print(f"- {label} ({f_val/1e6:.2f} MHz): Peak-to-Peak Input = {v_pp_in*1e6:.2f} uV, Output = {v_pp_out:.3f} V, Actual Gain = {actual_gain:.1f} ({20*np.log10(actual_gain):.2f} dB), Phase Shift = {phase_shift_deg:.1f}°, THD = {thd:.4f}%")
        
        # --- TIME DOMAIN PLOT ---
        ax.plot(t_extracted, vout_ac, color=c_primary, linewidth=2.5, label='AC Output $V_{out}$ (Right Axis)')
        ax_in = ax.twinx()
        ax_in.plot(t_extracted, vin_extracted * 1e6, color='#10b981', linewidth=1.5, linestyle=':', label='Input $V_{in}$ (Left Axis)')
        
        ax.set_title(f"Response at {label} ({f_val/1e6:.2f} MHz)", fontsize=11, fontweight='bold', pad=8)
        ax.set_xlabel("Time (ns)", fontsize=9)
        ax.set_ylabel("AC Output Voltage (V)", fontsize=9, color=c_primary)
        ax_in.set_ylabel("Input Voltage (uV)", fontsize=9, color='#10b981')
        ax.grid(True, color=c_grid)
        
        # Display characteristics
        stats_text = f"Gain: {actual_gain:.0f} ({20*np.log10(actual_gain):.1f} dB)\nPhase: {phase_shift_deg:.1f}°\nTHD: {thd:.4f}%\nDC Shift: {vout_dc_offset:.1f}V"
        ax.text(0.05, 0.05, stats_text, transform=ax.transAxes, bbox=dict(boxstyle="round,pad=0.4", fc='white', ec=c_border, alpha=0.9), fontsize=9, family='monospace')
        
        # Combine legends
        lines_a = [ax.get_lines()[0], ax_in.get_lines()[0]]
        labels_a = [l.get_label() for l in lines_a]
        if i == 0:
            ax.legend(lines_a, labels_a, loc='upper right', frameon=True, facecolor='white', edgecolor=c_border, fontsize=8)
            
        # --- FREQUENCY SPECTRUM FFT PLOT ---
        spec_limit_idx = np.argmin(np.abs(freqs_pos - 6.0 * fund_freq))
        # Plot continuous spectrum in dBV (or linear mV)
        ax_spec.plot(freqs_pos[:spec_limit_idx] / fund_freq, mags_pos[:spec_limit_idx] * 1e3, color=c_primary, linewidth=2, label='Continuous Spectrum')
        # Highlight fundamental and harmonics
        ax_spec.plot(1.0, fund_amp * 1e3, 'o', color='#10b981', markersize=8, label=f'Fundamental ({fund_amp*1e3:.1f} mV)')
        for order, amp in zip([2, 3, 4, 5], harm_amps):
            ax_spec.plot(order, amp * 1e3, 'x', color='red', markersize=8, markeredgewidth=2)
            
        ax_spec.set_title(f"FFT Spectrum at {label} ({f_val/1e6:.2f} MHz)", fontsize=11, fontweight='bold', pad=8)
        ax_spec.set_xlabel("Harmonic Order ($f / f_{fundamental}$)", fontsize=9)
        ax_spec.set_ylabel("Amplitude Peak (mV)", fontsize=9)
        ax_spec.grid(True, color=c_grid)
        ax_spec.set_xlim(0, 6)
        
        # Display THD and specs on spectrum
        spec_text = f"THD: {thd:.4f}%\n$f_0$: {fund_freq/1e6:.3f} MHz\nFund: {fund_amp*1e3:.1f} mV\n2nd Harm: {harm_amps[0]*1e6:.1f} uV\n3rd Harm: {harm_amps[1]*1e6:.1f} uV"
        ax_spec.text(0.48, 0.62, spec_text, transform=ax_spec.transAxes, bbox=dict(boxstyle="round,pad=0.4", fc='white', ec=c_border, alpha=0.9), fontsize=8, family='monospace')
        
        # Save to CSV
        tran_df = pd.DataFrame({
            'Time_s': time_sec[extract_mask],
            'Time_ns': t_extracted,
            'Vin_V': vin_extracted,
            'Vout_V': vout_extracted,
            'Vout_AC_V': vout_ac
        })
        tran_csv_path = os.path.join(csv_dir, f"instrampl_tran_{key}.csv")
        tran_df.to_csv(tran_csv_path, index=False)
            
    else:
        ax.text(0.5, 0.5, "Simulation failed", ha='center', va='center')
        ax_spec.text(0.5, 0.5, "Simulation failed", ha='center', va='center')

plt.suptitle("Instrumentation Amplifier - Transient Response at Multiple Frequencies (Last 4 Cycles of 8)", fontsize=16, fontweight='bold', y=0.99)
fig_tran_png = os.path.join(png_dir, "instrampl_transient_characterization.png")
fig_tran_svg = os.path.join(svg_dir, "instrampl_transient_characterization.svg")
plt.savefig(fig_tran_png, dpi=300, bbox_inches='tight')
plt.savefig(fig_tran_svg, format='svg', bbox_inches='tight')
plt.close()

# Save FFT spectrum figure
fig_spec.suptitle("Instrumentation Amplifier - FFT Frequency Spectra & Total Harmonic Distortion (THD)", fontsize=16, fontweight='bold', y=0.99)
fig_spec_png = os.path.join(png_dir, "instrampl_transient_spectra.png")
fig_spec_svg = os.path.join(svg_dir, "instrampl_transient_spectra.svg")
fig_spec.savefig(fig_spec_png, dpi=300, bbox_inches='tight')
fig_spec.savefig(fig_spec_svg, format='svg', bbox_inches='tight')
plt.close(fig_spec)

# Save non-transient datasets to CSV
dc_df = pd.DataFrame({
    'Vin_V': vin_dc,
    'Vout_V': vout_dc,
    'Local_Gain': local_gain
})
dc_df.to_csv(os.path.join(csv_dir, "instrampl_dc_char.csv"), index=False)

ac_df = pd.DataFrame({
    'Frequency_Hz': freq,
    'Gain_dB': gain_db,
    'Phase_deg': phase_deg
})
ac_df.to_csv(os.path.join(csv_dir, "instrampl_ac_char.csv"), index=False)

cmrr_df = pd.DataFrame({
    'Frequency_Hz': freq,
    'Gain_Diff_dB': gain_db,
    'Gain_CM_dB': gain_cm_db,
    'CMRR_dB': cmrr
})
cmrr_df.to_csv(os.path.join(csv_dir, "instrampl_cmrr_char.csv"), index=False)

zout_df = pd.DataFrame({
    'Frequency_Hz': freq_zout,
    'Zout_Ohm': zout_mag
})
zout_df.to_csv(os.path.join(csv_dir, "instrampl_zout_char.csv"), index=False)

print("\nAll simulations completed, analyzed and plotted successfully!")
print(f"- DC Curve plots: {fig_dc_png} / {fig_dc_svg}")
print(f"- AC Bode plots: {fig_ac_png} / {fig_ac_svg}")
print(f"- CMRR plots: {fig_cmrr_png} / {fig_cmrr_svg}")
print(f"- Output Impedance plots: {fig_zout_png} / {fig_zout_svg}")
print(f"- Transient Grid plots: {fig_tran_png} / {fig_tran_svg}")
print(f"- Transient Spectra plots: {fig_spec_png} / {fig_spec_svg}")
