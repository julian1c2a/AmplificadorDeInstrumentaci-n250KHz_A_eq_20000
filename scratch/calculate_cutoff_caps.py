import numpy as np

R1 = 49.5e3
R7 = 10e3

# Target cutoff frequencies
targets = [6.0, 7.0, 8.0]

print("Target fc (Hz) | Individual fp (Hz) | Req. Cf1,2 (nF) | Req. Cf3 (nF)")
print("-" * 65)
for fc in targets:
    # Individual stage pole frequency to hit fc (with 3 identical cascaded poles)
    fp = fc / np.sqrt(2**(1/3) - 1)
    
    # Calculate capacitors
    Cf1 = 1.0 / (2.0 * np.pi * R1 * fp)
    Cf3 = 1.0 / (2.0 * np.pi * R7 * fp)
    
    print(f"{fc:14.1f} | {fp:20.3f} | {Cf1*1e9:15.3f} | {Cf3*1e9:14.3f}")
