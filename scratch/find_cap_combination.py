import numpy as np

R1 = 49.5e3
R7 = 10e3

# Target fc = 9.06 kHz
fc = 9.06e3

# If 3 identical poles (Stage 1, 2 and 3 aligned)
fp_3poles = fc / np.sqrt(2**(1/3) - 1)
Cf1_3poles = 1.0 / (2.0 * np.pi * R1 * fp_3poles)
Cf3_3poles = 1.0 / (2.0 * np.pi * R7 * fp_3poles)

# If 2 identical poles (Stage 1 and 2, Stage 3 is very fast/no cap)
fp_2poles = fc / np.sqrt(2**(1/2) - 1)
Cf1_2poles = 1.0 / (2.0 * np.pi * R1 * fp_2poles)

print(f"To hit fc = {fc/1e3:.3f} kHz:")
print("-" * 50)
print(f"With 3 aligned poles (Stage 1, 2, 3):")
print(f"  Required fp = {fp_3poles/1e3:.3f} kHz")
print(f"  Required Cf1,2 = {Cf1_3poles*1e12:.2f} pF (or {Cf1_3poles*1e9:.4f} nF)")
print(f"  Required Cf3 = {Cf3_3poles*1e9:.4f} nF (or {Cf3_3poles*1e12:.2f} pF)")
print()
print(f"With 2 aligned poles (Stage 1, 2 only, Stage 3 no cap):")
print(f"  Required fp = {fp_2poles/1e3:.3f} kHz")
print(f"  Required Cf1,2 = {Cf1_2poles*1e12:.2f} pF (or {Cf1_2poles*1e9:.4f} nF)")
