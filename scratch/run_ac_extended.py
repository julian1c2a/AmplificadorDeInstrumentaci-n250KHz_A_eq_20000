import os
import subprocess
import numpy as np

workspace_dir = r"c:\msys64\home\julia\ngspice\AmplificadorDeInstrumentación250KHz_A_eq_20000"
ngspice_path = r"C:\msys64\ucrt64\bin\ngspice.exe"

def run_extended_ac():
    # Read InstrAmpl.cir
    with open(os.path.join(workspace_dir, "InstrAmpl.cir"), "r", encoding="utf-8") as f:
        content = f.read()

    # Disable transient analysis
    content = content.replace("  tran 100n 300u", "  * tran 100n 300u")
    content = content.replace("  wrdata instrampl_tran.txt v(vp,vn) v(vout_final)", "  * wrdata instrampl_tran.txt v(vp,vn) v(vout_final)")

    # Change AC sweep up to 100MHz
    content = content.replace("ac dec 100 1 10meg", "ac dec 100 1 100meg")

    temp_cir = os.path.join(workspace_dir, "InstrAmpl_temp_ext_ac.cir")
    with open(temp_cir, "w", encoding="utf-8") as f:
        f.write(content)

    print("Running extended AC sweep to 100MHz...")
    subprocess.run(
        [ngspice_path, "-b", "InstrAmpl_temp_ext_ac.cir"],
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
    
    if os.path.exists(temp_cir):
        os.remove(temp_cir)
        
    if len(ac_data) > 0:
        freq = ac_data[:, 0]
        gain_db = ac_data[:, 1]
        
        max_gain = np.max(gain_db)
        dc_gain = gain_db[0]
        target_gain = dc_gain - 3.0
        
        peak_idx = np.argmax(gain_db)
        idx_3db = np.where((freq > freq[peak_idx]) & (gain_db <= target_gain))[0]
        
        print(f"DC Gain: {dc_gain:.2f} dB")
        print(f"Max Gain: {max_gain:.2f} dB at {freq[peak_idx]/1e6:.2f} MHz")
        if len(idx_3db) > 0:
            print(f"-3dB Cutoff Frequency (fc): {freq[idx_3db[0]]/1e6:.2f} MHz")
            return freq[idx_3db[0]]
        else:
            print(f"Gain at 100 MHz: {gain_db[-1]:.2f} dB. Still hasn't dropped by 3dB!")
            return 100e6
    return None

if __name__ == "__main__":
    run_extended_ac()
