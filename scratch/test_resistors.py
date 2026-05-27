import os
import subprocess
import numpy as np

workspace_dir = r"c:\msys64\home\julia\ngspice\AmplificadorDeInstrumentación250KHz_A_eq_20000"
ngspice_path = r"C:\msys64\ucrt64\bin\ngspice.exe"

def test_gain(rf_val="49.75K"):
    with open(os.path.join(workspace_dir, "InstrAmpl.cir"), "r", encoding="utf-8") as f:
        content = f.read()

    # Disable transient analysis in content
    content = content.replace("  tran 100n 300u", "  * tran 100n 300u")
    content = content.replace("  wrdata instrampl_tran.txt v(vp,vn) v(vout_final)", "  * wrdata instrampl_tran.txt v(vp,vn) v(vout_final)")

    # Replace Rf resistors
    content = content.replace("R_f1         vout1 vn1 49.5K", f"R_f1         vout1 vn1 {rf_val}")
    content = content.replace("R_f2         vout2 vn2 49.5K", f"R_f2         vout2 vn2 {rf_val}")

    temp_cir = os.path.join(workspace_dir, "InstrAmpl_temp_res.cir")
    with open(temp_cir, "w", encoding="utf-8") as f:
        f.write(content)

    subprocess.run(
        [ngspice_path, "-b", "InstrAmpl_temp_res.cir"],
        cwd=workspace_dir,
        capture_output=True,
        text=True
    )

    # Read AC data
    ac_file = os.path.join(workspace_dir, "instrampl_ac.txt")
    data = []
    with open(ac_file, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    data.append([float(x) for x in parts])
                except ValueError:
                    pass
    ac_data = np.array(data)
    
    if len(ac_data) > 0:
        freq = ac_data[:, 0]
        gain_db = ac_data[:, 1]
        
        for f_target in [10, 100, 10000, 500000]:
            idx = np.argmin(np.abs(freq - f_target))
            g_val = 10**(gain_db[idx]/20.0)
            print(f"Gain at {freq[idx]/1e3:.2f} kHz: {gain_db[idx]:.4f} dB (Linear: {g_val:.2f})")
            
    if os.path.exists(temp_cir):
        os.remove(temp_cir)

if __name__ == "__main__":
    print("--- Testing Rf = 49.75K (Nominal Gain = 20000) ---")
    test_gain("49.75K")
