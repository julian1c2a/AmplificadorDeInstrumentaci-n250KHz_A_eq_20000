import os
import subprocess
import time

workspace_dir = r"c:\msys64\home\julia\ngspice\AmplificadorDeInstrumentación250KHz_A_eq_20000"
ngspice_path = r"C:\msys64\ucrt64\bin\ngspice.exe"

def run_test(use_original=False):
    # Read InstrAmpl.cir
    with open(os.path.join(workspace_dir, "InstrAmpl.cir"), "r", encoding="utf-8") as f:
        content = f.read()

    # Add .options method=gear
    opt_line = "\n.options method=gear reltol=1e-3\n"
    content = content.replace(".TEMP 27", ".TEMP 27" + opt_line)

    if not use_original:
        # Modify transient parameters for faster test
        content = content.replace("SIN(0 100u 10k)", "SIN(0 100u 100k)")
        content = content.replace("tran 100n 300u", "tran 10n 30u")
        
    temp_cir = os.path.join(workspace_dir, "InstrAmpl_temp_gear.cir")
    with open(temp_cir, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Running ngspice on temp file with Gear integration (original_tran={use_original})...")
    start_time = time.time()
    result = subprocess.run(
        [ngspice_path, "-b", "InstrAmpl_temp_gear.cir"],
        cwd=workspace_dir,
        capture_output=True,
        text=True
    )
    duration = time.time() - start_time
    print(f"Completed in {duration:.2f} seconds.")
    print("Return code:", result.returncode)
    
    # Clean up temp file
    if os.path.exists(temp_cir):
        os.remove(temp_cir)
        
    return result.returncode == 0

if __name__ == "__main__":
    print("--- Test with Gear and 100kHz tran ---")
    success = run_test(use_original=False)
    if success:
        print("--- Test with Gear and original 10kHz tran ---")
        run_test(use_original=True)
