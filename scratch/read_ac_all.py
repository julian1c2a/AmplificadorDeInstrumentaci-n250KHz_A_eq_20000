import numpy as np

ac_data = []
with open("superopamp_ac.txt", "r") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) >= 4:
            try:
                ac_data.append([float(parts[0]), float(parts[1]), float(parts[3])])
            except ValueError:
                pass

ac_data = np.array(ac_data)
if len(ac_data) > 0:
    print("Freq (Hz) | Gain (dB) | Phase (deg)")
    print("-" * 35)
    # Select points logarithmically
    indices = np.unique(np.logspace(0, np.log10(len(ac_data)-1), 15).astype(int))
    for idx in indices:
        row = ac_data[idx]
        print(f"{row[0]:9.2e} | {row[1]:9.3f} | {row[2]:9.3f}")
else:
    print("No AC data found.")
