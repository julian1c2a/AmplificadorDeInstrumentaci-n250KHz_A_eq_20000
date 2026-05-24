import numpy as np

def load_data(filename):
    data = []
    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    data.append([float(parts[0]), float(parts[1])])
                except ValueError:
                    pass
    return np.array(data)

ac_data = load_data('ac_response.txt')
dc_data = load_data('dc_response.txt')
tran_data = load_data('tran_response.txt')

# 1. AC Analysis
if len(ac_data) > 0:
    freq = ac_data[:, 0]
    gain_db = ac_data[:, 1]
    max_gain = np.max(gain_db)
    print(f"Max Gain (dB): {max_gain:.2f}")
    
    # Find -3dB freq
    target = max_gain - 3.0
    idx = np.where(gain_db <= target)[0]
    if len(idx) > 0:
        f3db = freq[idx[0]]
        print(f"F-3dB: {f3db/1000:.2f} kHz")
    else:
        print("F-3dB not reached in simulated range.")

# 2. DC Linearity
if len(dc_data) > 0:
    vdiff = dc_data[:, 0]
    vout = dc_data[:, 1]
    
    # check slope (gain) in the linear region (-0.2m to 0.2m)
    # vout = gain * vdiff
    linear_idx = np.where((vdiff > -0.2e-3) & (vdiff < 0.2e-3))
    if len(linear_idx[0]) > 1:
        vdiff_lin = vdiff[linear_idx]
        vout_lin = vout[linear_idx]
        slope, intercept = np.polyfit(vdiff_lin, vout_lin, 1)
        print(f"DC Gain (Slope): {slope:.2f}")
        
        # Linearity error
        predicted = slope * vdiff_lin + intercept
        max_error = np.max(np.abs(vout_lin - predicted))
        print(f"Max DC Linearity Error in +/- 0.2mV: {max_error:.6f} V")

# 3. TRAN
if len(tran_data) > 0:
    t = tran_data[:, 0]
    v = tran_data[:, 1]
    v_pp = np.max(v) - np.min(v)
    print(f"TRAN Vpp: {v_pp:.2f} V")
