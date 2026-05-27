import pandas as pd
import numpy as np

# Load ac_comparison.csv
try:
    df = pd.read_csv("ac_comparison.csv")
    print("Columns in ac_comparison.csv:", df.columns.tolist())
    
    # Print the gain at 10 Hz for all columns
    low_freq_row = df.iloc[0]
    print("\nLow Frequency Gains (at 10 Hz):")
    for col in df.columns:
        if "Gain" in col:
            print(f"  {col}: {low_freq_row[col]:.3f} dB")
            
    # Find the -3dB cutoff frequency for each case
    print("\nCutoff Frequencies (-3dB from low frequency gain):")
    for col in df.columns:
        if "Gain" in col:
            mags = df[col].values
            freqs = df['Frequency_Hz'].values
            max_gain = mags[0]
            target_gain = max_gain - 3.0
            idx = np.where(mags <= target_gain)[0]
            if len(idx) > 0:
                print(f"  {col}: {freqs[idx[0]]/1e3:.3f} kHz (at {mags[idx[0]]:.3f} dB, max was {max_gain:.3f} dB)")
            else:
                print(f"  {col}: No cutoff found")
except Exception as e:
    print("Error:", e)
