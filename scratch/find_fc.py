import os
import numpy as np

workspace_dir = r"c:\msys64\home\julia\ngspice\AmplificadorDeInstrumentación250KHz_A_eq_20000"
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
    
    max_gain = np.max(gain_db)
    dc_gain = gain_db[0]
    target_gain = dc_gain - 3.0
    
    # Find where gain drops below target after the peak
    # The peak is around 9.33 MHz. Let's look for the first index after the peak where gain <= target_gain.
    peak_idx = np.argmax(gain_db)
    idx_3db = np.where((freq > freq[peak_idx]) & (gain_db <= target_gain))[0]
    
    if len(idx_3db) > 0:
        f_3db = freq[idx_3db[0]]
        print(f"DC Gain: {dc_gain:.2f} dB")
        print(f"Max Gain: {max_gain:.2f} dB at {freq[peak_idx]/1e6:.2f} MHz")
        print(f"-3dB Cutoff Frequency (fc): {f_3db/1e6:.2f} MHz")
    else:
        # If it doesn't drop within 10 MHz, print the gain at the end
        print(f"DC Gain: {dc_gain:.2f} dB")
        print(f"Gain at 10 MHz: {gain_db[-1]:.2f} dB")
        print("Gain does not drop by 3dB within the simulated 10 MHz range!")
else:
    print("No AC data loaded.")
