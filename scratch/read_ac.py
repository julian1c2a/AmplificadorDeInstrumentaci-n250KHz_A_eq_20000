import os
import numpy as np

workspace_dir = r"c:\msys64\home\julia\ngspice\AmplificadorDeInstrumentación250KHz_A_eq_20000"

def load_spice_data(filename):
    path = os.path.join(workspace_dir, filename)
    data = []
    if not os.path.exists(path):
        print(f"Warning: File {filename} not found.")
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

ac_data = load_spice_data("instrampl_ac.txt")
if len(ac_data) > 0:
    freq = ac_data[:, 0]
    gain_db = ac_data[:, 1]
    phase_deg = ac_data[:, 3]
    
    max_gain = np.max(gain_db)
    max_gain_freq = freq[np.argmax(gain_db)]
    print(f"Maximum gain: {max_gain:.2f} dB at {max_gain_freq/1e3:.2f} kHz")
    
    # Let's print gain at some key frequencies
    for f_target in [10, 100, 1000, 10000, 100000, 250000, 500000, 1000000]:
        idx = np.argmin(np.abs(freq - f_target))
        print(f"Gain at {freq[idx]/1e3:.2f} kHz: {gain_db[idx]:.2f} dB, Phase: {phase_deg[idx]:.2f} deg")
else:
    print("No AC data loaded.")
