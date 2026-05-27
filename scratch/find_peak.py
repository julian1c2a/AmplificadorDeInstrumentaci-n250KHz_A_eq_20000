import numpy as np

ac_data = []
with open("superopamp_ac.txt", "r") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) >= 2:
            try:
                ac_data.append([float(parts[0]), float(parts[1])])
            except ValueError:
                pass

ac_data = np.array(ac_data)
if len(ac_data) > 0:
    max_idx = np.argmax(ac_data[:, 1])
    max_gain = ac_data[max_idx, 1]
    max_freq = ac_data[max_idx, 0]
    print(f"Max Gain in superopamp_ac.txt: {max_gain:.4f} dB at {max_freq/1e3:.4f} kHz")
    
    # Find where the gain is around 114 dB or check values near 9.06 kHz
    near_9khz = ac_data[(ac_data[:, 0] > 8000) & (ac_data[:, 0] < 10000)]
    print("\nData around 9.06 kHz:")
    for row in near_9khz:
        print(f"  Freq: {row[0]/1e3:.3f} kHz | Gain: {row[1]:.3f} dB")
        
    # Find the maximum gain and print the first 10 rows
    print("\nFirst 10 rows of AC data:")
    for row in ac_data[:10]:
        print(f"  Freq: {row[0]:.3f} Hz | Gain: {row[1]:.3f} dB")
else:
    print("No AC data found.")
