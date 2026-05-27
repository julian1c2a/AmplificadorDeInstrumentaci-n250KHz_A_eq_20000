import sys
from skidl import *

# Define default library for opamps and passives
# In a real environment, we'd use specific footprints, but for netlist generation,
# generic ones work perfectly for the user to assign later in KiCad.

def create_superopamp(name_prefix):
    """
    Creates a SuperOpAmp block using 5 ADA4817 op-amps.
    Returns the IO pins: (vp, vn, out, ref, vcc, vee)
    """
    # Create the 5 op-amps
    # We use a generic 5-pin op-amp symbol from the 'Amplifier_Operational' library
    op1 = Part('Amplifier_Operational', 'ADA4817-1', dest=TEMPLATE, footprint='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm')
    
    xop1 = op1(ref=f'{name_prefix}_XOP1')
    xop2 = op1(ref=f'{name_prefix}_XOP2')
    xop3 = op1(ref=f'{name_prefix}_XOP3')
    xop4 = op1(ref=f'{name_prefix}_XOP4')
    xop5 = op1(ref=f'{name_prefix}_XOP5')
    
    # Resistors
    r_template = Part('Device', 'R', dest=TEMPLATE, footprint='Resistor_SMD:R_0805_2012Metric')
    c_template = Part('Device', 'C', dest=TEMPLATE, footprint='Capacitor_SMD:C_0805_2012Metric')
    
    r1, r2, r3, r4, r5, r6, r7, r8, r9, r10 = r_template(10)
    c1, c2, c3, c4, c5, c6 = c_template(6)
    
    r1.value, r2.value = '49.5K', '49.5K'
    r3.value = '500'
    c1.value, c2.value = '33nF', '33nF'
    
    r4.value, r5.value = '49.5K', '49.5K'
    r6.value = '500'
    c3.value, c4.value = '33nF', '33nF'
    
    r7.value, r9.value = '15K', '15K'
    r8.value, r10.value = '750', '750'
    c5.value, c6.value = '160nF', '160nF'
    
    # Define IO Nets for this subcircuit
    vp = Net(f'{name_prefix}_VP')
    vn = Net(f'{name_prefix}_VN')
    out = Net(f'{name_prefix}_OUT')
    ref = Net(f'{name_prefix}_REF')
    vcc = Net(f'{name_prefix}_VCC')
    vee = Net(f'{name_prefix}_VEE')
    
    # Power connections
    for op in [xop1, xop2, xop3, xop4, xop5]:
        op['V+'] += vcc
        op['V-'] += vee
        
    # Stage 1 Wiring
    xop2['+'] += vp
    xop1['+'] += vn
    
    node13 = Net(f'{name_prefix}_N13')
    node14 = Net(f'{name_prefix}_N14')
    node4 = Net(f'{name_prefix}_N4')
    node3 = Net(f'{name_prefix}_N3')
    
    # XOP2 output and feedback
    xop2['-'] += node13
    xop2['~'] += node4  # Output
    r2[1, 2] += node4, node13
    c2[1, 2] += node4, node13
    
    # XOP1 output and feedback
    xop1['-'] += node14
    xop1['~'] += node3  # Output
    r1[1, 2] += node3, node14
    c1[1, 2] += node3, node14
    
    # Rg for stage 1
    r3[1, 2] += node14, node13
    
    # Stage 2 Wiring
    xop4['+'] += node4
    xop3['+'] += node3
    
    node11 = Net(f'{name_prefix}_N11')
    node12 = Net(f'{name_prefix}_N12')
    node6 = Net(f'{name_prefix}_N6')
    node5 = Net(f'{name_prefix}_N5')
    
    xop4['-'] += node11
    xop4['~'] += node6  # Output
    r5[1, 2] += node6, node11
    c4[1, 2] += node6, node11
    
    xop3['-'] += node12
    xop3['~'] += node5  # Output
    r4[1, 2] += node5, node12
    c3[1, 2] += node5, node12
    
    # Rg for stage 2
    r6[1, 2] += node12, node11
    
    # Stage 3 Wiring (Difference Amp)
    node8 = Net(f'{name_prefix}_N8')
    node9 = Net(f'{name_prefix}_N9')
    
    r10[1, 2] += node6, node8
    r9[1, 2] += node8, ref
    c6[1, 2] += node8, ref
    
    r8[1, 2] += node5, node9
    r7[1, 2] += node9, out
    c5[1, 2] += node9, out
    
    xop5['+'] += node8
    xop5['-'] += node9
    xop5['~'] += out
    
    return vp, vn, out, ref, vcc, vee

def build_instrumentation_amplifier():
    print("Building Skidl Circuit: Amplificador de Instrumentacion 250KHz...")
    
    # Global Nets
    vcc = Net('VCC')
    vee = Net('VEE')
    gnd = Net('GND')
    
    # Inputs
    vp_in = Net('IN+')
    vn_in = Net('IN-')
    out_final = Net('OUT_FINAL')
    
    # Instatiate 3 SuperOpAmps
    u1_vp, u1_vn, u1_out, u1_ref, u1_vcc, u1_vee = create_superopamp('U1')
    u2_vp, u2_vn, u2_out, u2_ref, u2_vcc, u2_vee = create_superopamp('U2')
    u3_vp, u3_vn, u3_out, u3_ref, u3_vcc, u3_vee = create_superopamp('U3')
    
    # Power
    vcc += u1_vcc, u2_vcc, u3_vcc
    vee += u1_vee, u2_vee, u3_vee
    gnd += u1_ref, u2_ref, u3_ref
    
    # Stage 1 Instrumentation Buffers
    u1_vp += vp_in
    u2_vp += vn_in
    
    node_vn1 = u1_vn
    node_vn2 = u2_vn
    
    # Gain resistor Rg
    R_g = Part('Device', 'R', value='500', footprint='Resistor_SMD:R_0805_2012Metric')
    R_g[1, 2] += node_vn1, node_vn2
    
    # Feedback resistors (Rf) are connected from OUT to VN inside the SuperOpAmp block naturally?
    # Wait, in InstrAmpl.cir:
    # XU1 vp vn1 vout1 0 cc dd SuperOpAmp
    # R_f1 vout1 vn1 49.75K
    # That means the SuperOpAmp is used as a standard op-amp here.
    R_f1 = Part('Device', 'R', value='49.75K', footprint='Resistor_SMD:R_0805_2012Metric')
    R_f2 = Part('Device', 'R', value='49.75K', footprint='Resistor_SMD:R_0805_2012Metric')
    
    R_f1[1, 2] += u1_out, node_vn1
    R_f2[1, 2] += u2_out, node_vn2
    
    # Stage 2 Difference Amplifier
    # XU3 vp3 vn3 vout_final 0 cc dd SuperOpAmp
    # R_in1 vout1 vp3 750
    # R_ref vp3 0 75K
    # R_in2 vout2 vn3 750
    # R_fb vout_final vn3 75K
    
    R_in1 = Part('Device', 'R', value='750', footprint='Resistor_SMD:R_0805_2012Metric')
    R_ref = Part('Device', 'R', value='75K', footprint='Resistor_SMD:R_0805_2012Metric')
    R_in2 = Part('Device', 'R', value='750', footprint='Resistor_SMD:R_0805_2012Metric')
    R_fb  = Part('Device', 'R', value='75K', footprint='Resistor_SMD:R_0805_2012Metric')
    
    R_in1[1, 2] += u1_out, u3_vp
    R_ref[1, 2] += u3_vp, gnd
    
    R_in2[1, 2] += u2_out, u3_vn
    R_fb[1, 2] += u3_out, u3_vn
    
    out_final += u3_out
    
    # Add a load resistor for completion
    R_L = Part('Device', 'R', value='50', footprint='Resistor_SMD:R_1206_3216Metric')
    R_L[1, 2] += out_final, gnd
    
    print("Generating KiCad Netlist 'InstrAmpl.net'...")
    # ERC might complain about unconnected power nets, disable it or attach power sources
    ERC()
    generate_netlist(file_='InstrAmpl.net')
    
    print("Done! You can import 'InstrAmpl.net' into KiCad.")

if __name__ == '__main__':
    build_instrumentation_amplifier()
