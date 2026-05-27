import os
import subprocess
import time

workspace_dir = r"c:\msys64\home\julia\ngspice\AmplificadorDeInstrumentación250KHz_A_eq_20000"
ngspice_path = r"C:\msys64\ucrt64\bin\ngspice.exe"

def run_test(cmin="1p", method="gear"):
    # Read InstrAmpl.cir
    with open(os.path.join(workspace_dir, "InstrAmpl.cir"), "r", encoding="utf-8") as f:
        content = f.read()

    # Add options
    opt_line = f"\n.options method={method} cmin={cmin} reltol=1e-3\n"
    content = content.replace(".TEMP 27", ".TEMP 27" + opt_line)

    # Modify transient parameters for faster test (100kHz transient, 30u)
    content = content.replace("SIN(0 100u 10k)", "SIN(0 100u 100k)")
    content = content.replace("tran 100n 300u", "tran 10n 30u")
        
    temp_cir = os.path.join(workspace_dir, "InstrAmpl_temp_cmin.cir")
    with open(temp_cir, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Running transient test with cmin={cmin}, method={method}...")
    start_time = time.time()
    result = subprocess.run(
        [ngspice_path, "-b", "InstrAmpl_temp_cmin.cir"],
        cwd=workspace_dir,
        capture_output=True,
        text=True
    )
    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.2f} seconds.")
    print("Return code:", result.returncode)
    
    # Clean up temp file
    if os.path.exists(temp_cir):
        os.remove(temp_cir)
        
    return result.returncode == 0

if __name__ == "__main__":
    # Test different cmin values
    for cmin_val in ["1e-12", "1e-13", "1e-14"]:
        print(f"\n--- Testing cmin = {cmin_val} ---")
        if run_test(cmin=cmin_val, method="gear"):
            print("Success!")
            break
