import os
import subprocess

workspace_dir = r"c:\msys64\home\julia\ngspice\AmplificadorDeInstrumentación250KHz_A_eq_20000"
ngspice_path = r"C:\msys64\ucrt64\bin\ngspice.exe"

def run_test(disable_tran=False):
    # Read InstrAmpl.cir
    with open(os.path.join(workspace_dir, "InstrAmpl.cir"), "r", encoding="utf-8") as f:
        content = f.read()

    if disable_tran:
        # Comment out the tran line
        content = content.replace("  tran 100n 300u", "  * tran 100n 300u")
        content = content.replace("  wrdata instrampl_tran.txt v(vp,vn) v(vout_final)", "  * wrdata instrampl_tran.txt v(vp,vn) v(vout_final)")
        
    temp_cir = os.path.join(workspace_dir, "InstrAmpl_temp.cir")
    with open(temp_cir, "w", encoding="utf-8") as f:
        f.write(content)

    print("Running ngspice on temp file...")
    result = subprocess.run(
        [ngspice_path, "-b", "InstrAmpl_temp.cir"],
        cwd=workspace_dir,
        capture_output=True,
        text=True
    )
    
    print("Return code:", result.returncode)
    print("STDOUT length:", len(result.stdout))
    print("STDERR length:", len(result.stderr))
    if len(result.stderr) > 0:
        print("STDERR:")
        print(result.stderr)
    if len(result.stdout) > 0:
        print("STDOUT (last 500 chars):")
        print(result.stdout[-500:])
        
    # Clean up temp file
    if os.path.exists(temp_cir):
        os.remove(temp_cir)

if __name__ == "__main__":
    print("--- Test with TRAN disabled ---")
    run_test(disable_tran=True)
