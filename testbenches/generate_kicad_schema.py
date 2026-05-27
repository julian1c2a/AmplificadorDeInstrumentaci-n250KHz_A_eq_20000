import sys
from skidl import *

# Create template components inline to avoid KiCad library dependencies on the local system
op_template = Part(name='ADA4817-1', tool=SKIDL, dest=TEMPLATE, footprint='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm')
op_template += Pin(num='3', name='+')
op_template += Pin(num='2', name='-')
op_template += Pin(num='4', name='V-')
op_template += Pin(num='7', name='V+')
op_template += Pin(num='6', name='~')

r_template = Part(name='R', tool=SKIDL, dest=TEMPLATE, footprint='Resistor_SMD:R_0805_2012Metric')
r_template += Pin(num='1', name='1')
r_template += Pin(num='2', name='2')

c_template = Part(name='C', tool=SKIDL, dest=TEMPLATE, footprint='Capacitor_SMD:C_0805_2012Metric')
c_template += Pin(num='1', name='1')
c_template += Pin(num='2', name='2')

def create_superopamp(name_prefix):
    """
    Creates a SuperOpAmp block using 5 ADA4817 op-amps.
    Returns the IO pins: (vp, vn, out, ref, vcc, vee)
    """
    xop1 = op_template(ref=f'{name_prefix}_XOP1')
    xop2 = op_template(ref=f'{name_prefix}_XOP2')
    xop3 = op_template(ref=f'{name_prefix}_XOP3')
    xop4 = op_template(ref=f'{name_prefix}_XOP4')
    xop5 = op_template(ref=f'{name_prefix}_XOP5')
    
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
    
    vp = Net(f'{name_prefix}_VP')
    vn = Net(f'{name_prefix}_VN')
    out = Net(f'{name_prefix}_OUT')
    ref = Net(f'{name_prefix}_REF')
    vcc = Net(f'{name_prefix}_VCC')
    vee = Net(f'{name_prefix}_VEE')
    
    for op in [xop1, xop2, xop3, xop4, xop5]:
        op['V+'] += vcc
        op['V-'] += vee
        
    xop2['+'] += vp
    xop1['+'] += vn
    
    node13 = Net(f'{name_prefix}_N13')
    node14 = Net(f'{name_prefix}_N14')
    node4 = Net(f'{name_prefix}_N4')
    node3 = Net(f'{name_prefix}_N3')
    
    xop2['-'] += node13
    xop2['~'] += node4
    r2[1, 2] += node4, node13
    c2[1, 2] += node4, node13
    
    xop1['-'] += node14
    xop1['~'] += node3
    r1[1, 2] += node3, node14
    c1[1, 2] += node3, node14
    
    r3[1, 2] += node14, node13
    
    xop4['+'] += node4
    xop3['+'] += node3
    
    node11 = Net(f'{name_prefix}_N11')
    node12 = Net(f'{name_prefix}_N12')
    node6 = Net(f'{name_prefix}_N6')
    node5 = Net(f'{name_prefix}_N5')
    
    xop4['-'] += node11
    xop4['~'] += node6
    r5[1, 2] += node6, node11
    c4[1, 2] += node6, node11
    
    xop3['-'] += node12
    xop3['~'] += node5
    r4[1, 2] += node5, node12
    c3[1, 2] += node5, node12
    
    r6[1, 2] += node12, node11
    
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
    
    vcc = Net('VCC')
    vee = Net('VEE')
    gnd = Net('GND')
    
    vp_in = Net('IN+')
    vn_in = Net('IN-')
    out_final = Net('OUT_FINAL')
    
    u1_vp, u1_vn, u1_out, u1_ref, u1_vcc, u1_vee = create_superopamp('U1')
    u2_vp, u2_vn, u2_out, u2_ref, u2_vcc, u2_vee = create_superopamp('U2')
    u3_vp, u3_vn, u3_out, u3_ref, u3_vcc, u3_vee = create_superopamp('U3')
    
    vcc += u1_vcc, u2_vcc, u3_vcc
    vee += u1_vee, u2_vee, u3_vee
    gnd += u1_ref, u2_ref, u3_ref
    
    u1_vp += vp_in
    u2_vp += vn_in
    
    node_vn1 = u1_vn
    node_vn2 = u2_vn
    
    R_g = r_template(value='500', ref='Rg')
    R_g[1, 2] += node_vn1, node_vn2
    
    R_f1 = r_template(value='49.75K', ref='Rf1')
    R_f2 = r_template(value='49.75K', ref='Rf2')
    R_f1[1, 2] += u1_out, node_vn1
    R_f2[1, 2] += u2_out, node_vn2
    
    R_in1 = r_template(value='750', ref='Rin1')
    R_ref = r_template(value='75K', ref='Rref')
    R_in2 = r_template(value='750', ref='Rin2')
    R_fb  = r_template(value='75K', ref='Rfb')
    
    R_in1[1, 2] += u1_out, u3_vp
    R_ref[1, 2] += u3_vp, gnd
    
    R_in2[1, 2] += u2_out, u3_vn
    R_fb[1, 2] += u3_out, u3_vn
    
    out_final += u3_out
    
    R_L = r_template(value='50', ref='RL')
    R_L[1, 2] += out_final, gnd
    
    print("Generating KiCad Netlist 'InstrAmpl.net'...")
    ERC()
    generate_netlist(file_='InstrAmpl.net')
    print("Done! You can import 'InstrAmpl.net' into KiCad.")

if __name__ == '__main__':
    build_instrumentation_amplifier()
