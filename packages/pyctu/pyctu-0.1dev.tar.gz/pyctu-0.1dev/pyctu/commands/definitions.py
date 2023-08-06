ebl_types = {
    '0': 'Coordinator AT',
    '1': 'Coordinator API',
    '2': 'Router AT',
    '3': 'Router API',
    '8': 'End Device AT',
    '9': 'End Device API'
}

baudrates = [
    (0, 1200),
    (1, 2400),
    (2, 4800),
    (3, 9600),
    (4, 19200),
    (5, 38400),
    (6, 57600),
    (7, 115200)
]

power_levels = [
    (0, '-10/10dBm'),
    (1, '-6/12dBm'),
    (2, '-4/14dBm'),
    (3, '-2/16dBm'),
    (4, '0/18dBm')
]

coordinator = [
    (0,  'End Device'),
    (1, 'Coordinator')
]

mac_mode = [
    (0, 'MaxStream Mode'),
    (1, '802.15.4 (no ACKs)'),
    (2, '802.15.4 (with ACKs)')
]

api_mode = [
    (0, 'Disabled'),
    (1, 'API enabled'),
    (2, 'API enabled (w/escaped control characters)')
]

encryption = [
    (0, 'Disabled'),
    (1, 'Enabled'),
]

s2_pull_up = [
    'DIO4 (Pin 11)',
    'AD3 / DIO3 (Pin 17)',
    'AD2 / DIO2 (Pin 18)',
    'AD1 / DIO1 (Pin 19)',
    'AD0 / DIO0 (Pin 20)',
    'RTS / DIO6 (Pin 16)',
    'DTR / Sleep Request / DIO8 (Pin 9)',
    'DIN / Config (Pin 3)',
    'Associate / DIO5 (Pin 15)',
    'On/Sleep / DIO9 (Pin 13)',
    'DIO12 (Pin 4)',
    'PWM0 / RSSI / DIO10 (Pin 6)',
    'PWM1 / DIO11 (Pin 7)',
    'CTS / DIO7 (Pin 12)'
]

s1_pull_up = [
    'AD4/DIO4 (pin11)',
    'AD3 / DIO3 (pin17)',
    'AD2/DIO2 (pin18)',
    'AD1/DIO1 (pin19)',
    'AD0 / DIO0 (pin20)',
    'RTS / AD6 / DIO6 (pin16)',
    'DTR / SLEEP_RQ / DI8 (pin9)',
    'DIN/CONFIG (pin3)'
]

d5 = [
    (0, 'Disabled'),
    (1, 'Associated indicator'),
    (2, 'ADC'),
    (3, 'DI'),
    (4, 'DO low'),
    (5, 'DO high'),
]

d0_d4 = [
    (0, 'Disabled '),
    (1, '(n/a) '),
    (2, 'ADC '),
    (3, 'DI'),
    (4, 'DO low '),
    (5, 'DO high')
]

adc = [
    (0, 'VREF pin'),
    (1, 'Internal')
]

association_indication = {
    '00': 'Successfully formed or joined a network.',
    '21': 'Scan found no PANs',
    '22': 'Scan found no valid PANs based on current SC and ID settings',
    '23': 'Valid Coordinator or Routers found, but they are not allowing joining (NJ expired)',
    '24': 'No joinable beacons were found',
    '25': 'Unexpected state, node should not be attempting to join at this time',
    '27': 'Node Joining attempt failed (typically due to incompatible security settings)',
    '2A': 'Coordinator Start attempt failed',
    '2B': 'Checking for an existing coordinator',
    '2C': 'Attempt to leave the network failed',
    'AB': 'Attempted to join a device that did not respond.',
    'AC': 'Secure join error - network security key received unsecured',
    'AD': 'Secure join error - network security key not received',
    'AF': 'Secure join error - joining device does not have the right preconfigured link key',
    'FF': 'Scanning for a ZigBee network (routers and end devices)'
}

fields = {
    'networking': {
        'pan': {'command': 'ID', 'writeable': True, 'value': None},
        'address_high': {'command': 'SH', 'writeable': False, 'value': None},
        'address_low': {'command': 'SL', 'writeable': False, 'value': None},
        'destination_address_high': {'command': 'DH', 'writeable': True, 'value': None},
        'destination_address_low': {'command': 'DL', 'writeable': True, 'value': None},
        'source_address': {'command': 'MY', 'writeable': True, 'value': None},
        'node_id': {'command': 'NI', 'writeable': True, 'value': None},
        'channel': {'command': 'CH', 'writeable': True, 'value': None},
        'coordinator': {'command': 'CE', 'writeable': True, 'value': None, 'vocabulary': coordinator},
        'mac_mode': {'command': 'CE', 'writeable': True, 'value': None, 'vocabulary': mac_mode},
        'node_discover': {'command': 'ND', 'writeable': True, 'value': None, 'special_command': True},
        'xbee_retries': {'command': 'RR', 'writeable': True, 'value': None},
        'aes_encryption_enable': {'command': 'EE', 'writeable': True, 'value': None, 'vocabulary': encryption},
        'aes_key': {'command': 'KY', 'writeable': True, 'value': None},
    },
    'serial': {
        'baud_rate': {'command': 'BD', 'writeable': True, 'value': None, 'vocabulary': baudrates},
        'api_mode': {'command': 'AP', 'writeable': True, 'value': None, 'vocabulary': api_mode},
        'pull_up_resistors': {'command': 'PR', 'writeable': True, 'value': None, 'bits': s2_pull_up},
        'reset': {'command': 'RE', 'writeable': True, 'value': None, 'special_command': True},
        },
    # 'diagnostics': {
    #     'firmware': {'command': 'VR', 'writeable': False, 'value': None},
    #     'hardware': {'command': 'HV', 'writeable': False, 'value': None},
    #     'association_indication': {'command': 'AI', 'writeable': False, 'value': None},
    #     'signal_strength': {'command': 'DB', 'writeable': False, 'value': None},
    #     'ack_failures': {'command': 'EA', 'writeable': True, 'value': None},
    #     'reset': {'command': 'RE', 'writeable': True, 'value': None},
    #     'energy_scan': {'command': 'ED', 'writeable': True, 'value': None, 'special_command': True},
    #     'supply_voltage': {'command': '%V', 'writeable': False, 'value': None},
    #     },
    # 'at_options': {
    #     'command_mode_timeout': {'command': 'CT', 'writeable': True, 'value': None},
    #     },
    'rf': {
        'power_level': {'command': 'PL', 'writeable': True, 'value': None, 'vocabulary': power_levels},
        },
    # 'io': {
    #     'd0': {'command': 'D0', 'writeable': True, 'value': None, 'vocabulary': d0_d4},
    #     'd1': {'command': 'D1', 'writeable': True, 'value': None, 'vocabulary': d0_d4},
    #     'd2': {'command': 'D2', 'writeable': True, 'value': None, 'vocabulary': d0_d4},
    #     'd3': {'command': 'D3', 'writeable': True, 'value': None, 'vocabulary': d0_d4},
    #     'd4': {'command': 'D4', 'writeable': True, 'value': None, 'vocabulary': d0_d4},
    #     'd5': {'command': 'D5', 'writeable': True, 'value': None, 'vocabulary': d5},
    #     'adc_voltage_reference': {'command': 'AV', 'writeable': True, 'value': None, 'vocabulary': adc},
    #     }
    }
