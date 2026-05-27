import os
import re
import uuid

symbols_dir = r"C:\msys64\ucrt64\share\kicad\symbols"
output_dir = r"c:\msys64\home\julia\ngspice\AmplificadorDeInstrumentacion250KHz_A_eq_20000"

def get_uuid():
    return str(uuid.uuid4())

def extract_symbol_definition(lib_name, symbol_name):
    path = os.path.join(symbols_dir, f"{lib_name}.kicad_sym")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Library not found: {path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # regex search for the start of the symbol
    # The symbol name can be in quotes or not
    pattern = rf'\(symbol\s+"?{re.escape(symbol_name)}"?\s'
    match = re.search(pattern, content)
    if not match:
        raise ValueError(f"Symbol '{symbol_name}' not found in library '{lib_name}'")
    
    start_idx = match.start()
    paren_count = 0
    end_idx = start_idx
    for i in range(start_idx, len(content)):
        char = content[i]
        if char == '(':
            paren_count += 1
        elif char == ')':
            paren_count -= 1
            if paren_count == 0:
                end_idx = i + 1
                break
    
    sym_def = content[start_idx:end_idx]
    
    # Rename the symbol to "lib_name:symbol_name" in the header of the definition
    # This is critical so KiCad can match the library ID exactly!
    pattern_replace = rf'^\(symbol\s+("?){re.escape(symbol_name)}("?)\s'
    new_header = f'(symbol "{lib_name}:{symbol_name}" '
    sym_def = re.sub(pattern_replace, new_header, sym_def, count=1)
    
    # Also rename the sub-symbols defined within, e.g. "R_0_1" to "Device:R_0_1"
    # KiCad stores sub-symbols like (symbol "R_0_1" ...) inside (symbol "R" ...)
    # Wait, let's keep them as original (without library prefix) because KiCad expects
    # them to be named relative to the parent symbol or starts with the symbol name, not full library ID!
    # So we do NOT rename sub-symbols!
    pass
    
    return sym_def

# S-Expression Project Template (.kicad_pro)
kicad_pro_content = """{
  "meta": {
    "version": 1
  },
  "project": {
    "back_annotated_footprints": [],
    "board": {
      "design_rules": {
        "rule_severity": {
          "allow_microvia": "error",
          "blind_buried_via": "error",
          "difference_pair_gap_out_of_range": "error",
          "dupe_pad": "error",
          "edge_clearance": "error",
          "hole_near_hole": "error",
          "hole_to_dev": "error",
          "microvia_drill_out_of_range": "error",
          "min_annular_ring": "error",
          "min_via_diameter": "error",
          "parity_class_diff_pair_gap": "error",
          "relative_gap": "error",
          "relative_width": "error",
          "silk_clearance": "error",
          "silk_over_copper": "warning",
          "silk_over_mask": "warning",
          "through_hole_drill_out_of_range": "error",
          "track_width": "error",
          "via_drill_out_of_range": "error",
          "via_to_dev": "error",
          "via_to_track": "error"
        }
      }
    },
    "sheets": [
      [
        "00000000-0000-0000-0000-000000000000",
        ""
      ]
    ]
  }
}"""

# Component Coordinates & Rotation
# Page size A3 is 420mm x 297mm.
# Margins: ~20mm. Coordinate area: X: 30 to 390, Y: 30 to 260
# Op-amps: pin 2 is inverting (-), pin 3 is non-inverting (+), pin 6 is output
# Resistors: pin 1 is top/left, pin 2 is bottom/right (length: 7.62mm, pin 1 is at (0, 3.81), pin 2 at (0, -3.81))

def gen_symbol_placement(lib_id, ref, value, x, y, rot=0, mirror="", unit=1):
    u = get_uuid()
    
    # Calculate property offsets
    ref_y = y - 6 if rot == 0 else y
    ref_x = x if rot == 0 else x - 6
    val_y = y + 6 if rot == 0 else y
    val_x = x if rot == 0 else x + 6
    
    mirror_str = f" (mirror {mirror})" if mirror else ""
    
    pins_expr = ""
    # Add dummy uuids for standard pins (to make the schematic file robust)
    # R: 1, 2. C: 1, 2. Opamp: 1..8
    if "LM741" in lib_id:
        for p in range(1, 9):
            pins_expr += f'\n    (pin "{p}" (uuid "{get_uuid()}"))'
    elif "Q_NPN" in lib_id or "Q_PNP" in lib_id:
        for p in ["B", "C", "E"]:
            pins_expr += f'\n    (pin "{p}" (uuid "{get_uuid()}"))'
    else:
        for p in ["1", "2"]:
            pins_expr += f'\n    (pin "{p}" (uuid "{get_uuid()}"))'
            
    return f"""  (symbol (lib_id "{lib_id}") (at {x} {y} {rot}){mirror_str} (unit {unit})
    (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes)
    (uuid "{u}")
    (property "Reference" "{ref}" (at {ref_x} {ref_y} {rot})
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{value}" (at {val_x} {val_y} {rot})
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "~" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    ){pins_expr}
  )"""

def gen_wire(x1, y1, x2, y2):
    return f"""  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))
    (stroke (width 0) (type solid))
    (uuid "{get_uuid()}")
  )"""

def gen_junction(x, y):
    return f"""  (junction (at {x} {y}) (diameter 0) (color 0 0 0 0) (uuid "{get_uuid()}") )"""

def gen_global_label(text, x, y, rot=0, shape="input"):
    # shape can be: input, output, bidirectional, tri_state, passive
    return f"""  (global_label "{text}" (shape {shape}) (at {x} {y} {rot}) (fields_autoplaced yes)
    (uuid "{get_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
  )"""

def gen_text(text, x, y, rot=0, size=1.27):
    # escape quotes and replace newlines
    escaped_text = text.replace('"', '\\"').replace('\n', '\\n')
    return f"""  (text "{escaped_text}" (at {x} {y} {rot})
    (effects (font (size {size} {size})))
    (uuid "{get_uuid()}")
  )"""

print("Extracting library symbols from system...")

lib_symbols_defs = []
try:
    lib_symbols_defs.append(extract_symbol_definition("Device", "R"))
    lib_symbols_defs.append(extract_symbol_definition("Device", "C"))
    lib_symbols_defs.append(extract_symbol_definition("Device", "D"))
    lib_symbols_defs.append(extract_symbol_definition("Device", "Q_NPN"))
    lib_symbols_defs.append(extract_symbol_definition("Device", "Q_PNP"))
    lib_symbols_defs.append(extract_symbol_definition("power", "GND"))
    lib_symbols_defs.append(extract_symbol_definition("power", "+15V"))
    lib_symbols_defs.append(extract_symbol_definition("power", "-15V"))
    lib_symbols_defs.append(extract_symbol_definition("Amplifier_Operational", "LM741"))
    print("All standard symbols extracted successfully!")
except Exception as e:
    print(f"Error extracting symbols: {e}")
    exit(1)

# Format the lib_symbols section
lib_symbols_expr = "\n".join(lib_symbols_defs)

# Generate Placement
placements = []
wires = []
junctions = []

# --- STAGE 1: INPUT DIFFERENTIAL STAGE ---
# U1: (70, 75)
placements.append(gen_symbol_placement("Amplifier_Operational:LM741", "U1", "LF357", 70, 75))
# U2: (70, 205) - let's keep it standard or rot 0, no mirror. Let's make U1 non-inverting pin (+) at bottom, inverting (-) at top.
# In KiCad LM741, Pin 3 (+) is at (-7.62, 2.54), Pin 2 (-) is at (-7.62, -2.54).
# So:
# U1+ is at (62.38, 77.54)
# U1- is at (62.38, 72.46)
# U1_out is at (77.62, 75.0)
# U1_V+ (pin 7) is at (67.46, 82.62) -> let's route to +15V
# U1_V- (pin 4) is at (67.46, 67.38) -> let's route to -15V

# U2: (70, 205)
placements.append(gen_symbol_placement("Amplifier_Operational:LM741", "U2", "LF357", 70, 205))
# U2+ is at (62.38, 207.54)
# U2- is at (62.38, 202.46)
# U2_out is at (77.62, 205.0)

# Input global labels
placements.append(gen_global_label("Vin+", 40, 77.54, 180, "input"))
wires.append(gen_wire(40, 77.54, 62.38, 77.54))

placements.append(gen_global_label("Vin-", 40, 207.54, 180, "input"))
wires.append(gen_wire(40, 207.54, 62.38, 207.54))

# Rg: vertical at (50, 137.5). Let's connect Rg between U1- and U2-
# Let's place Rg at (50, 137.5) with rot 90.
# Rg pin 1 (top) is at (50, 133.69)
# Rg pin 2 (bottom) is at (50, 141.31)
placements.append(gen_symbol_placement("Device:R", "Rg", "100", 50, 137.5, rot=0))

# Wire U1- to Rg1
wires.append(gen_wire(62.38, 72.46, 50, 72.46))
wires.append(gen_wire(50, 72.46, 50, 133.69))
junctions.append(gen_junction(50, 72.46))

# Wire U2- to Rg2
wires.append(gen_wire(62.38, 202.46, 50, 202.46))
wires.append(gen_wire(50, 202.46, 50, 141.31))
junctions.append(gen_junction(50, 202.46))

# R1: feedback for U1. Horizontal at (105, 55).
# R1 pin 1 (left) is at (101.19, 55), pin 2 (right) is at (108.81, 55)
placements.append(gen_symbol_placement("Device:R", "R1", "2.45k", 105, 55, rot=90))
wires.append(gen_wire(50, 72.46, 50, 55))
wires.append(gen_wire(50, 55, 101.19, 55))
wires.append(gen_wire(108.81, 55, 120, 55))
wires.append(gen_wire(120, 55, 120, 75))
wires.append(gen_wire(77.62, 75, 120, 75))
junctions.append(gen_junction(120, 75))

# R2: feedback for U2. Horizontal at (105, 225).
placements.append(gen_symbol_placement("Device:R", "R2", "2.45k", 105, 225, rot=90))
wires.append(gen_wire(50, 202.46, 50, 225))
wires.append(gen_wire(50, 225, 101.19, 225))
wires.append(gen_wire(108.81, 225, 120, 225))
wires.append(gen_wire(120, 225, 120, 205))
wires.append(gen_wire(77.62, 205, 120, 205))
junctions.append(gen_junction(120, 205))


# --- STAGE 2: DIFFERENTIAL TO SINGLE-ENDED (U3) ---
# U3: (195, 140)
placements.append(gen_symbol_placement("Amplifier_Operational:LM741", "U3", "OPAMP", 195, 140))
# U3+ is at (187.38, 142.54)
# U3- is at (187.38, 137.46)
# U3_out is at (202.62, 140.0)

# R3: from U1 out (120, 75) to U3- (187.38, 137.46).
# R3 is horizontal at (155, 120). Pin 1: (151.19, 120), Pin 2: (158.81, 120)
placements.append(gen_symbol_placement("Device:R", "R3", "1k", 155, 120, rot=90))
wires.append(gen_wire(120, 75, 120, 120))
wires.append(gen_wire(120, 120, 151.19, 120))
wires.append(gen_wire(158.81, 120, 175, 120))
wires.append(gen_wire(175, 120, 175, 137.46))
wires.append(gen_wire(175, 137.46, 187.38, 137.46))

# R5: from U2 out (120, 205) to U3+ (187.38, 142.54).
# R5 is horizontal at (155, 160). Pin 1: (151.19, 160), Pin 2: (158.81, 160)
placements.append(gen_symbol_placement("Device:R", "R5", "1k", 155, 160, rot=90))
wires.append(gen_wire(120, 205, 120, 160))
wires.append(gen_wire(120, 160, 151.19, 160))
wires.append(gen_wire(158.81, 160, 187.38, 160))
wires.append(gen_wire(187.38, 160, 187.38, 142.54))

# R4: feedback for U3. Horizontal at (195, 105). Pin 1: (191.19, 105), Pin 2: (198.81, 105)
placements.append(gen_symbol_placement("Device:R", "R4", "20k", 195, 105, rot=90))
wires.append(gen_wire(175, 120, 175, 105))
wires.append(gen_wire(175, 105, 191.19, 105))
junctions.append(gen_junction(175, 120))

wires.append(gen_wire(198.81, 105, 215, 105))
wires.append(gen_wire(215, 105, 215, 140))
wires.append(gen_wire(202.62, 140, 215, 140))
junctions.append(gen_junction(215, 140))

# R6: grounding U3+ to GND. Vertical at (187.38, 180). Pin 1 (top): (187.38, 176.19), Pin 2 (bottom): (187.38, 183.81)
placements.append(gen_symbol_placement("Device:R", "R6", "20k", 187.38, 180, rot=0))
wires.append(gen_wire(187.38, 160, 187.38, 176.19))
junctions.append(gen_junction(187.38, 160))

# GND for R6
placements.append(gen_symbol_placement("power:GND", "#FLG01", "GND", 187.38, 190))
wires.append(gen_wire(187.38, 183.81, 187.38, 190))


# --- STAGE 3: ADDITIONAL GAIN (U4) ---
# U4: (270, 140)
placements.append(gen_symbol_placement("Amplifier_Operational:LM741", "U4", "OPAMP", 270, 140))
# U4+ is at (262.38, 142.54)
# U4- is at (262.38, 137.46)
# U4_out is at (277.62, 140.0)

# Wire U3 out to U4+
wires.append(gen_wire(215, 140, 262.38, 142.54))

# R10: feedback for U4. Horizontal at (270, 105). Pin 1: (266.19, 105), Pin 2: (273.81, 105)
placements.append(gen_symbol_placement("Device:R", "R10", "24k", 270, 105, rot=90))
wires.append(gen_wire(245, 137.46, 262.38, 137.46))
wires.append(gen_wire(245, 137.46, 245, 105))
wires.append(gen_wire(245, 105, 266.19, 105))

wires.append(gen_wire(273.81, 105, 290, 105))
wires.append(gen_wire(290, 105, 290, 140))
wires.append(gen_wire(277.62, 140, 290, 140))
junctions.append(gen_junction(290, 140))

# R9: U4- to GND. Vertical at (245, 165). Pin 1 (top): (245, 161.19), Pin 2 (bottom): (245, 168.81)
placements.append(gen_symbol_placement("Device:R", "R9", "1k", 245, 165, rot=0))
wires.append(gen_wire(245, 137.46, 245, 161.19))
junctions.append(gen_junction(245, 137.46))

# GND for R9
placements.append(gen_symbol_placement("power:GND", "#FLG02", "GND", 245, 175))
wires.append(gen_wire(245, 168.81, 245, 175))


# --- STAGE 4: LOW PASS RC FILTER ---
# Rf: horizontal at (315, 140). Pin 1: (311.19, 140), Pin 2: (318.81, 140)
placements.append(gen_symbol_placement("Device:R", "Rf", "636.6", 315, 140, rot=90))
wires.append(gen_wire(290, 140, 311.19, 140))

# Cf: vertical at (330, 165). Pin 1 (top): (330, 161.19), Pin 2 (bottom): (330, 168.81)
placements.append(gen_symbol_placement("Device:C", "Cf", "1nF", 330, 165, rot=0))
wires.append(gen_wire(318.81, 140, 330, 140))
wires.append(gen_wire(330, 140, 330, 161.19))

# GND for Cf
placements.append(gen_symbol_placement("power:GND", "#FLG03", "GND", 330, 175))
wires.append(gen_wire(330, 168.81, 330, 175))


# --- STAGE 5: BUFFER AND PUSH-PULL ---
# U5: (370, 140)
placements.append(gen_symbol_placement("Amplifier_Operational:LM741", "U5", "OPAMP", 370, 140))
# U5+ is at (362.38, 142.54)
# U5- is at (362.38, 137.46)
# U5_out is at (377.62, 140.0)

# Wire filter out to U5+
wires.append(gen_wire(330, 140, 362.38, 142.54))
junctions.append(gen_junction(330, 140))

# Rb1: vertical at (395, 75). Pin 1 (top): (395, 71.19), Pin 2 (bottom): (395, 78.81)
placements.append(gen_symbol_placement("Device:R", "Rb1", "1k", 395, 75, rot=0))
placements.append(gen_symbol_placement("power:+15V", "#FLG04", "+15V", 395, 60))
wires.append(gen_wire(395, 60, 395, 71.19))

# D1: vertical at (395, 110). Pin 1 (Cathode/top): (395, 106.19), Pin 2 (Anode/bottom): (395, 113.81).
# In standard Device:D, pin 1 is Cathode (K) at -3.81, pin 2 is Anode (A) at 3.81.
# So if we rotate it 90 degrees:
# Pin 1 (Cathode) is at (395, 110 + 3.81) = (395, 113.81)
# Pin 2 (Anode) is at (395, 110 - 3.81) = (395, 106.19)
# Let's rotate 270 degrees to place Anode at top, Cathode at bottom!
# With rot 270:
# Pin 1 (Cathode) is at (395, 110 - 3.81) = (395, 106.19) - wait, rot 270 swaps it!
# Let's place it at rot 270:
placements.append(gen_symbol_placement("Device:D", "D1", "1N4148", 395, 110, rot=270))
wires.append(gen_wire(395, 78.81, 395, 106.19))
junctions.append(gen_junction(395, 78.81))

# Wire U5 out to the junction of D1 cathode and D2 anode!
# U5 out is at (377.62, 140). Connection point is at (395, 140)
# D2: vertical at (395, 170) with rot 270. Anode at top (395, 166.19), Cathode at bottom (395, 173.81)
placements.append(gen_symbol_placement("Device:D", "D2", "1N4148", 395, 170, rot=270))
wires.append(gen_wire(377.62, 140, 395, 140))
wires.append(gen_wire(395, 113.81, 395, 166.19))
junctions.append(gen_junction(395, 140))

# Rb2: vertical at (395, 205). Pin 1 (top): (395, 201.19), Pin 2 (bottom): (395, 208.81)
placements.append(gen_symbol_placement("Device:R", "Rb2", "1k", 395, 205, rot=0))
wires.append(gen_wire(395, 173.81, 395, 201.19))
junctions.append(gen_junction(395, 173.81))

placements.append(gen_symbol_placement("power:-15V", "#FLG05", "-15V", 395, 220))
wires.append(gen_wire(395, 208.81, 395, 220))

# Transistors: Q1 (TIP31 NPN) and Q2 (TIP32 PNP).
# Placing Q1 at (430, 80) and Q2 at (430, 200).
# Pins for Q_NPN and Q_PNP:
# Base (B) is at (-5.08, 0).
# Collector (C) is at (2.54, 5.08) relative to center (passive line, at 2.54 5.08 270) -> points down
# Emitter (E) is at (2.54, -5.08) relative to center (passive line, at 2.54 -5.08 90) -> points up
# Wait, for Q1 (NPN):
# Base is at (424.92, 80)
# Collector is at (432.54, 85.08) -> connected to VCC (+15V)
# Emitter is at (432.54, 74.92) -> connected to output node!
# Wait, if we want collector to point UP and emitter to point DOWN, we should look at the orientation!
# In standard KiCad Q_NPN, base is on left, collector is on top, emitter is on bottom (with arrow pointing out).
# Let's verify the coordinates from our parser:
# Base: (-5.08, 0). Collector: (2.54, 5.08) -> wait, in KiCad, Y is positive down!
# So 5.08 is DOWN, meaning Collector pin is actually at bottom? Or is Emitter pin at bottom?
# Let's check `parse_q_npn.py` output:
# Base (B): (-5.08, 0)
# Collector (C): (2.54, 5.08) (which is DOWN in KiCad coordinates)
# Emitter (E): (2.54, -5.08) (which is UP in KiCad coordinates)
# Wait, that means Collector is at bottom, Emitter is at top!
# To place Q1 with Collector pointing UP (to +15V) and Emitter pointing DOWN (to output):
# We can mirror the symbol or rotate it!
# Wait, let's keep it in standard orientation, and connect accordingly, or if it's standard:
# Let's check standard Q_NPN symbol. Yes, standard Q_NPN has C on top and E on bottom. The S-expression has C pin at top and E pin at bottom. Let's make sure!
# Wait, let's look at `parse_q_npn.py`'s output:
# Pin C: (2.54, 5.08 270) -> pin points down, so the wire connects at (2.54, 5.08) and goes down! That means the pin connection point is at bottom.
# Pin E: (2.54, -5.08 90) -> pin points up, so the wire connects at (2.54, -5.08) and goes up! That means the pin connection point is at top.
# Ah! So Emitter is at top and Collector is at bottom!
# If so, we should connect:
# - Q1 Collector to +15V (so we connect Q1 Pin C at (432.54, 85.08) to +15V).
# - Q1 Emitter to output (so we connect Q1 Pin E at (432.54, 74.92) to output).
# Let's write the connections cleanly!
placements.append(gen_symbol_placement("Device:Q_NPN", "Q1", "TIP31", 430, 80))
wires.append(gen_wire(395, 78.81, 424.92, 80)) # Base to Rb1/D1 junction

# Connect Collector (Pin C) to +15V!
# Collector is at (432.54, 85.08)
placements.append(gen_symbol_placement("power:+15V", "#FLG06", "+15V", 432.54, 95))
wires.append(gen_wire(432.54, 85.08, 432.54, 95))

# Q2 (PNP) at (430, 200)
placements.append(gen_symbol_placement("Device:Q_PNP", "Q2", "TIP32", 430, 200))
wires.append(gen_wire(395, 173.81, 424.92, 200)) # Base to D2/Rb2 junction

# Connect Collector (Pin C) to -15V!
# Collector is at (432.54, 205.08)
placements.append(gen_symbol_placement("power:-15V", "#FLG07", "-15V", 432.54, 215))
wires.append(gen_wire(432.54, 205.08, 432.54, 215))

# Connect Emitters together!
# Q1 Emitter is at (432.54, 74.92)
# Q2 Emitter is at (432.54, 194.92)
wires.append(gen_wire(432.54, 74.92, 432.54, 137.5))
wires.append(gen_wire(432.54, 194.92, 432.54, 137.5))
junctions.append(gen_junction(432.54, 137.5))

# Wire Emitter junction to U5- for feedback!
# U5- is at (362.38, 137.46)
wires.append(gen_wire(432.54, 137.5, 432.54, 50))
wires.append(gen_wire(432.54, 50, 350, 50))
wires.append(gen_wire(350, 50, 350, 137.46))
wires.append(gen_wire(350, 137.46, 362.38, 137.46))

# RL: vertical load resistor at (455, 160). Pin 1 (top): (455, 156.19), Pin 2 (bottom): (455, 168.81)
placements.append(gen_symbol_placement("Device:R", "RL", "10", 455, 160, rot=0))
wires.append(gen_wire(432.54, 137.5, 455, 137.5))
wires.append(gen_wire(455, 137.5, 455, 156.19))
junctions.append(gen_junction(455, 137.5))

# GND for RL
placements.append(gen_symbol_placement("power:GND", "#FLG08", "GND", 455, 180))
wires.append(gen_wire(455, 168.81, 455, 180))

# Vout Output Label
placements.append(gen_global_label("Vout", 480, 137.5, 0, "output"))
wires.append(gen_wire(455, 137.5, 480, 137.5))


# --- ADD POWER SUPPLY CONNECTIONS FOR ALL OP-AMPS ---
# U1 V+ (pin 7) is at (67.46, 82.62) -> +15V
placements.append(gen_symbol_placement("power:+15V", "#FLG09", "+15V", 67.46, 92.62))
wires.append(gen_wire(67.46, 82.62, 67.46, 92.62))

# U1 V- (pin 4) is at (67.46, 67.38) -> -15V
placements.append(gen_symbol_placement("power:-15V", "#FLG10", "-15V", 67.46, 57.38))
wires.append(gen_wire(67.46, 67.38, 67.46, 57.38))

# U2 V+ (pin 7) is at (67.46, 212.62) -> +15V
placements.append(gen_symbol_placement("power:+15V", "#FLG11", "+15V", 67.46, 222.62))
wires.append(gen_wire(67.46, 212.62, 67.46, 222.62))

# U2 V- (pin 4) is at (67.46, 197.38) -> -15V
placements.append(gen_symbol_placement("power:-15V", "#FLG12", "-15V", 67.46, 187.38))
wires.append(gen_wire(67.46, 197.38, 67.46, 187.38))

# U3 V+ (pin 7) is at (192.46, 147.62) -> +15V
placements.append(gen_symbol_placement("power:+15V", "#FLG13", "+15V", 192.46, 157.62))
wires.append(gen_wire(192.46, 147.62, 192.46, 157.62))

# U3 V- (pin 4) is at (192.46, 132.38) -> -15V
placements.append(gen_symbol_placement("power:-15V", "#FLG14", "-15V", 192.46, 122.38))
wires.append(gen_wire(192.46, 132.38, 192.46, 122.38))

# U4 V+ (pin 7) is at (267.46, 147.62) -> +15V
placements.append(gen_symbol_placement("power:+15V", "#FLG15", "+15V", 267.46, 157.62))
wires.append(gen_wire(267.46, 147.62, 267.46, 157.62))

# U4 V- (pin 4) is at (267.46, 132.38) -> -15V
placements.append(gen_symbol_placement("power:-15V", "#FLG16", "-15V", 267.46, 122.38))
wires.append(gen_wire(267.46, 132.38, 267.46, 122.38))

# U5 V+ (pin 7) is at (367.46, 147.62) -> +15V
placements.append(gen_symbol_placement("power:+15V", "#FLG17", "+15V", 367.46, 157.62))
wires.append(gen_wire(367.46, 147.62, 367.46, 157.62))

# U5 V- (pin 4) is at (367.46, 132.38) -> -15V
placements.append(gen_symbol_placement("power:-15V", "#FLG18", "-15V", 367.46, 122.38))
wires.append(gen_wire(367.46, 132.38, 367.46, 122.38))


# Add descriptive titles and labels on the schematic sheet!
placements.append(gen_text("Amplificador de Instrumentacion 250kHz, Ganancia = 25000", 210, 30, size=2.5))
placements.append(gen_text("Etapa 1: Entrada Diferencial\nGanancia = 50", 70, 40))
placements.append(gen_text("Etapa 2: Diferencial a Single\nGanancia = 20", 175, 40))
placements.append(gen_text("Etapa 3: Amplificacion\nGanancia = 25", 260, 40))
placements.append(gen_text("Etapa 4: Filtro LPF\nfc = 250kHz", 325, 40))
placements.append(gen_text("Etapa 5: Buffer AB\nCarga de 10 Ohm", 420, 40))


# Combine everything
schematic_elements = "\n".join(placements + wires + junctions)

# Assemble schematic file content (.kicad_sch)
kicad_sch_content = f"""(kicad_sch (version 20231114) (generator "antigravity")
  (uuid "{get_uuid()}")
  (paper "A3")
  (lib_symbols
{lib_symbols_expr}
  )
  (sheet_instances
    (path "/" (page "1"))
  )
{schematic_elements}
)"""

# Write files
print("Writing project files...")
with open(os.path.join(output_dir, "AmplificadorDeInstrumentacion.kicad_pro"), "w", encoding="utf-8") as f:
    f.write(kicad_pro_content)

with open(os.path.join(output_dir, "AmplificadorDeInstrumentacion.kicad_sch"), "w", encoding="utf-8") as f:
    f.write(kicad_sch_content)

print("KiCad project and schematic generated successfully!")
