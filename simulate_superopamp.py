import os
import subprocess
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ngspice_path = r"C:\msys64\ucrt64\bin\ngspice.exe"
workspace_dir = r"c:\msys64\home\julia\ngspice\AmplificadorDeInstrumentación250KHz_A_eq_20000"

def run_simulation():
    cir_path = os.path.join(workspace_dir, "superopamp_ngspice.cir")
    print(f"Running ngspice simulation on: {cir_path}...")
    
    # Run ngspice in batch mode
    result = subprocess.run(
        [ngspice_path, "-b", "superopamp_ngspice.cir"],
        cwd=workspace_dir,
        capture_output=True,
        text=True
    )
    
    # Save the console output to a log file
    log_path = os.path.join(workspace_dir, "superopamp_sim_log.txt")
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(result.stdout)
        if result.stderr:
            f.write("\n=== ERRORS ===\n")
            f.write(result.stderr)
            
    print("Simulation completed.")
    return result.returncode == 0

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

def analyze_and_plot():
    # 1. Load Data
    dc_data = load_spice_data("superopamp_dc.txt")
    ac_data = load_spice_data("superopamp_ac.txt")
    tran_data = load_spice_data("superopamp_tran.txt")
    
    # Setup premium plotting style
    plt.rcParams['font.sans-serif'] = 'Arial'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['text.color'] = '#2c3e50'
    plt.rcParams['axes.labelcolor'] = '#2c3e50'
    plt.rcParams['xtick.color'] = '#2c3e50'
    plt.rcParams['ytick.color'] = '#2c3e50'
    
    # Color palette
    c_primary = '#6366f1'   # Indigo/violet
    c_secondary = '#3b82f6' # Vibrant blue
    c_phase = '#ec4899'     # Hot pink for phase
    c_grid = '#f1f5f9'
    c_border = '#e2e8f0'
    
    print("\nAnalyzing simulation results...")
    
    # Create the 3-panel figure
    fig = plt.figure(figsize=(15, 12), dpi=150)
    grid = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.25)
    
    # --- DC LINEARITY & TRANSFER CURVE ---
    ax_dc = fig.add_subplot(grid[0, 0])
    if len(dc_data) > 0:
        vin_dc = dc_data[:, 0]
        vout_dc = dc_data[:, 1]
        
        # Fit in the very linear region (+/- 15 uV)
        lin_mask = (vin_dc > -15e-6) & (vin_dc < 15e-6)
        slope, intercept = np.polyfit(vin_dc[lin_mask], vout_dc[lin_mask], 1)
        
        ax_dc.plot(vin_dc * 1e6, vout_dc, color=c_primary, linewidth=2.5, label='Static Curve')
        ax_dc.axhline(0, color='#94a3b8', linestyle=':', linewidth=1)
        ax_dc.axvline(0, color='#94a3b8', linestyle=':', linewidth=1)
        
        # Linearity error in +/- 20uV
        eval_mask = (vin_dc > -20e-6) & (vin_dc < 20e-6)
        vout_eval = vout_dc[eval_mask]
        vin_eval = vin_dc[eval_mask]
        predicted = slope * vin_eval + intercept
        lin_err = vout_eval - predicted
        max_lin_err = np.max(np.abs(lin_err))
        
        print(f"DC Differential Gain: {slope:.2f} ({20*np.log10(abs(slope)):.2f} dB)")
        print(f"Max Linearity Error (+/-20 uV): {max_lin_err * 1000:.3f} mV")
        
        ax_dc.set_title("Static DC Transfer Curve", fontsize=13, fontweight='bold', pad=12)
        ax_dc.set_xlabel("Input Differential Voltage $V_{in}$ (μV)", fontsize=11, labelpad=8)
        ax_dc.set_ylabel("Output Voltage $V_{out}$ (V)", fontsize=11, labelpad=8)
        ax_dc.grid(True, color=c_grid, linestyle='-', linewidth=1)
        ax_dc.set_xlim(-35, 35)
        ax_dc.set_ylim(-21, 21)
        
        # Display analysis text
        info_text = f"DC Gain: {slope/1e3:.2f}k ({20*np.log10(abs(slope)):.1f} dB)\nLin. Error: {max_lin_err*1e3:.2f} mV"
        ax_dc.text(-30, 12, info_text, bbox=dict(boxstyle="round,pad=0.5", fc='white', ec=c_border, alpha=0.9), fontsize=10)
    else:
        ax_dc.text(0.5, 0.5, "No DC data available", ha='center', va='center')
        
    # --- FREQUENCY RESPONSE (BODE) ---
    ax_ac_mag = fig.add_subplot(grid[0, 1])
    ax_ac_phase = ax_ac_mag.twinx()
    
    if len(ac_data) > 0:
        freq = ac_data[:, 0]
        gain_db = ac_data[:, 1]
        phase_deg = ac_data[:, 3]
        
        max_gain_db = np.max(gain_db)
        # Find 3dB bandwidth
        target_gain = max_gain_db - 3.0
        idx_3db = np.where(gain_db <= target_gain)[0]
        f_3db = freq[idx_3db[0]] if len(idx_3db) > 0 else np.nan
        
        # Find unity gain frequency (GBW)
        idx_unity = np.where(gain_db <= 0)[0]
        f_unity = freq[idx_unity[0]] if len(idx_unity) > 0 else np.nan
        
        print(f"Max AC Gain: {max_gain_db:.2f} dB")
        if not np.isnan(f_3db):
            print(f"-3dB Bandwidth (cutoff): {f_3db/1e3:.2f} kHz")
        if not np.isnan(f_unity):
            print(f"Unity Gain Frequency (GBW): {f_unity/1e6:.2f} MHz")
            
        # Plot Magnitude
        line1, = ax_ac_mag.semilogx(freq, gain_db, color=c_secondary, linewidth=2.5, label='Magnitude (dB)')
        # Plot Phase
        line2, = ax_ac_phase.semilogx(freq, phase_deg, color=c_phase, linewidth=2.0, linestyle='--', label='Phase (Deg)')
        
        ax_ac_mag.set_title("AC Frequency Response (Bode Plot)", fontsize=13, fontweight='bold', pad=12)
        ax_ac_mag.set_xlabel("Frequency (Hz)", fontsize=11, labelpad=8)
        ax_ac_mag.set_ylabel("Gain (dB)", fontsize=11, color=c_secondary, labelpad=8)
        ax_ac_phase.set_ylabel("Phase (Degrees)", fontsize=11, color=c_phase, labelpad=8)
        
        ax_ac_mag.grid(True, which="both", color=c_grid, linestyle='-', linewidth=1)
        ax_ac_mag.set_xlim(1, 100e6)
        ax_ac_mag.set_ylim(-10, 120)
        ax_ac_phase.set_ylim(-360, 45)
        
        # Bandwidth line
        if not np.isnan(f_3db):
            ax_ac_mag.axvline(f_3db, color='#94a3b8', linestyle='-.', linewidth=1.2)
            ax_ac_mag.text(f_3db*1.2, 50, f"fc = {f_3db/1e3:.1f} kHz", color='#475569', fontsize=9, fontweight='semibold')
            
        lines = [line1, line2]
        labels = [l.get_label() for l in lines]
        ax_ac_mag.legend(lines, labels, loc='lower left', frameon=True, facecolor='white', edgecolor=c_border)
    else:
        ax_ac_mag.text(0.5, 0.5, "No AC data available", ha='center', va='center')
        
    # --- TRANSIENT RESPONSE ---
    ax_tran = fig.add_subplot(grid[1, :])
    if len(tran_data) > 0:
        time_ms = tran_data[:, 0] * 1e3
        vin_tran = tran_data[:, 1]
        vout_tran = tran_data[:, 3]
        
        # Plot inputs and outputs
        ax_tran.plot(time_ms, vout_tran, color=c_primary, linewidth=2.5, label='Output voltage $V_{out}$ (Right Axis)')
        
        ax_tran_in = ax_tran.twinx()
        ax_tran_in.plot(time_ms, vin_tran * 1e6, color='#10b981', linewidth=1.5, linestyle=':', label='Input voltage $V_{in}$ (Left Axis)')
        
        ax_tran.set_title("Transient Response to 10Hz 10μV Peak Sine Input", fontsize=13, fontweight='bold', pad=12)
        ax_tran.set_xlabel("Time (ms)", fontsize=11, labelpad=8)
        ax_tran.set_ylabel("Output Voltage (V)", fontsize=11, color=c_primary, labelpad=8)
        ax_tran_in.set_ylabel("Input Voltage (μV)", fontsize=11, color='#10b981', labelpad=8)
        
        ax_tran.grid(True, color=c_grid, linestyle='-', linewidth=1)
        ax_tran.set_xlim(np.min(time_ms), np.max(time_ms))
        ax_tran.set_ylim(np.min(vout_tran)*1.2, np.max(vout_tran)*1.2)
        ax_tran_in.set_ylim(np.min(vin_tran)*1e6*1.2, np.max(vin_tran)*1e6*1.2)
        
        # Display peak-to-peak output
        v_pp = np.max(vout_tran) - np.min(vout_tran)
        print(f"Transient Output Peak-to-Peak: {v_pp:.3f} V")
        
        # Combined Legend
        lines_t = [ax_tran.get_lines()[0], ax_tran_in.get_lines()[0]]
        labels_t = [l.get_label() for l in lines_t]
        ax_tran.legend(lines_t, labels_t, loc='upper right', frameon=True, facecolor='white', edgecolor=c_border)
    else:
        ax_tran.text(0.5, 0.5, "No Transient data available", ha='center', va='center')
        
    plt.suptitle("SuperOpAmp Instrumentation Amplifier - Detailed ngspice Characterization", fontsize=16, fontweight='bold', color='#1e293b', y=0.98)
    
    # Save the figure in premium formats
    fig_png = os.path.join(workspace_dir, "superopamp_analysis.png")
    fig_svg = os.path.join(workspace_dir, "superopamp_analysis.svg")
    plt.savefig(fig_png, dpi=300, bbox_inches='tight')
    plt.savefig(fig_svg, format='svg', bbox_inches='tight')
    plt.close()
    
    print("\nVisual analysis generated successfully!")
    print(f"Saved PNG plot to: {fig_png}")
    print(f"Saved SVG plot to: {fig_svg}")

if __name__ == "__main__":
    if run_simulation():
        analyze_and_plot()
    else:
        print("Error during simulation execution.")
