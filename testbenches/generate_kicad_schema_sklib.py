from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

generate_kicad_schema = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'ADA4817-1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'ADA4817-1'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='3',name='+',func=pin_types.UNSPEC),
            Pin(num='2',name='-',func=pin_types.UNSPEC),
            Pin(num='4',name='V-',func=pin_types.UNSPEC),
            Pin(num='7',name='V+',func=pin_types.UNSPEC),
            Pin(num='6',name='~',func=pin_types.UNSPEC)] }),
        Part(**{ 'name':'R', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'R'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Resistor_SMD:R_0805_2012Metric', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.UNSPEC),
            Pin(num='2',name='2',func=pin_types.UNSPEC)] }),
        Part(**{ 'name':'C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'C'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Capacitor_SMD:C_0805_2012Metric', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.UNSPEC),
            Pin(num='2',name='2',func=pin_types.UNSPEC)] })])