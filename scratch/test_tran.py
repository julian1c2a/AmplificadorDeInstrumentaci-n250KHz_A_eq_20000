import os
import subprocess
import time

workspace_dir = r"c:\msys64\home\julia\ngspice\AmplificadorDeInstrumentación250KHz_A_eq_20000"
ngspice_path = r"C:\msys64\ucrt64\bin\ngspice.exe"

def run_test():
    # Read InstrAmpl.cir
    with open(os.path.join(workspace_dir, "InstrAmpl.cir"), "r", encoding="utf-8") as f:
        content = f.read()

    # Modify transient parameters
    # Change input frequency to 100k
    content = content.replace("SIN(0 100u 10k)", "SIN(0 100u 100k)")
    # Change tran statement to 10n 30u
    content = content.replace("tran 100n 300u", "tran 10n 30u")
        
    temp_cir = os.path.join(workspace_dir, "InstrAmpl_temp_tran.cir")
    with open(temp_cir, "w", encoding="utf-8") as f:
        f.write(content)

    print("Running ngspice on temp file with 100kHz transient...")
    start_time = time.time()
    result = subprocess.run(
        [ngspice_path, "-b", "InstrAmpl_temp_tran.cir"],
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

if __name__ == "__main__":
    run_test()
