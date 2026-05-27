import subprocess
import os

ngspice_path = r"C:\msys64\ucrt64\bin\ngspice.exe"
workspace_dir = r"c:\msys64\home\julia\ngspice\AmplificadorDeInstrumentación250KHz_A_eq_20000"

with open(os.path.join(workspace_dir, "superopamp_ngspice.cir"), "r") as f:
    lines = f.readlines()

# Strip control block
netlist = []
in_control = False
for line in lines:
    if ".control" in line:
        in_control = True
    if not in_control:
        netlist.append(line)
    if ".endc" in line:
        in_control = False

# Add new control block for OP
netlist.append("\n.control\n")
netlist.append("  op\n")
netlist.append("  print v(3) v(4) v(5) v(6) v(out)\n")
netlist.append(".endc\n")
netlist.append(".end\n")

test_cir = os.path.join(workspace_dir, "test_op.cir")
with open(test_cir, "w") as f:
    f.writelines(netlist)

result = subprocess.run(
    [ngspice_path, "-b", "test_op.cir"],
    cwd=workspace_dir,
    capture_output=True,
    text=True
)

print(result.stdout)
if os.path.exists(test_cir):
    os.remove(test_cir)
