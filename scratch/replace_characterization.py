import os

workspace_dir = r"c:\msys64\home\julia\ngspice\AmplificadorDeInstrumentación250KHz_A_eq_20000"
script_path = os.path.join(workspace_dir, "simulate_characterization.py")

with open(script_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace XU3 instantiations in netlists
content = content.replace("XU3          vp3 vn3 vout_final 0 cc dd SuperOpAmpWithPowOut", "XU3          vp3 vn3 vout_final 0 cc dd SuperOpAmp")

# Replace load resistor RL values in netlists
content = content.replace("RL           vout_final 0 50", "RL           vout_final 0 10K")

with open(script_path, "w", encoding="utf-8") as f:
    f.write(content)

print("simulate_characterization.py updated successfully!")
