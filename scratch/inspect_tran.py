import os
import subprocess
import numpy as np

workspace_dir = r"c:\msys64\home\julia\ngspice\AmplificadorDeInstrumentación250KHz_A_eq_20000"
ngspice_path = r"C:\msys64\ucrt64\bin\ngspice.exe"

import sys
sys.path.append(workspace_dir)
from simulate_characterization import header_models

def run_single_tran():
    f_val = 16.88e6  # fc
    period = 1.0 / f_val
    t_step = period / 40.0
    t_stop = 8.0 * period
    
    netlist = header_models + f"""
.TEMP 27
V3          cc 0 DC 20
V2          0 dd DC 20

Vdiff_node   vdiff_node 0 DC 0 AC 1 SIN(0 100u {f_val:.6e})
E_in_p       vp 0 vdiff_node 0 0.5
E_in_n       vn 0 vdiff_node 0 -0.5

XU1          vp vn1 vout1 0 cc dd SupOpAmp
XU2          vn vn2 vout2 0 cc dd SupOpAmp
Rg           vn1 vn2 500
R_f1         vout1 vn1 49.75K
R_f2         vout2 vn2 49.75K

XU3          vp3 vn3 vout_final 0 cc dd SupOpAmpWithPowOut
R_in1        vout1 vp3 750
R_ref        vp3 0 75K
R_in2        vout2 vn3 750
R_fb         vout_final vn3 75K

RL           vout_final 0 50

.options method=gear cmin=1e-12 reltol=1e-3

.control
  tran {t_step:.6e} {t_stop:.6e}
  wrdata instrampl_tran_inspect.txt v(vp,vn) v(vout_final)
.endc
.END
"""
    with open("temp_inspect.cir", "w") as f:
        f.write(netlist)
        
    subprocess.run([ngspice_path, "-b", "temp_inspect.cir"], cwd=workspace_dir)
    os.remove("temp_inspect.cir")
    
    # Read the data
    data = []
    with open(os.path.join(workspace_dir, "instrampl_tran_inspect.txt"), "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    data.append([float(x) for x in parts])
                except ValueError:
                    pass
    tran_data = np.array(data)
    
    time_sec = tran_data[:, 0]
    vin = tran_data[:, 1]
    vout = tran_data[:, 3]
    
    print(f"Total points: {len(time_sec)}")
    print(f"Time range: {time_sec[0]*1e9:.2f} ns to {time_sec[-1]*1e9:.2f} ns")
    print(f"Vout range: {np.min(vout):.6f} V to {np.max(vout):.6f} V")
    
    # Let's print the last few periods (from 4 periods to 8 periods)
    t_start = 4.0 * period
    mask = time_sec >= t_start
    t_ext = time_sec[mask]
    vout_ext = vout[mask]
    vin_ext = vin[mask]
    
    print(f"Extracted range: {t_ext[0]*1e9:.2f} ns to {t_ext[-1]*1e9:.2f} ns")
    print(f"Extracted Vout range: {np.min(vout_ext):.6f} V to {np.max(vout_ext):.6f} V")
    
    # Let's print the first 5 and last 5 elements of extracted Vout
    print("First 10 elements of Vout:")
    for i in range(10):
        print(f"t={t_ext[i]*1e9:.3f} ns: Vout={vout_ext[i]:.6f} V, Vin={vin_ext[i]*1e6:.3f} uV")
        
    os.remove(os.path.join(workspace_dir, "instrampl_tran_inspect.txt"))

if __name__ == "__main__":
    run_single_tran()
