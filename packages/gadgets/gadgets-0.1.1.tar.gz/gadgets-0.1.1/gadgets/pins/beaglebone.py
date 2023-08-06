
"""
ehrpwm.0:0
ehrpwm.0:1
ehrpwm.1:0 1a
ehrpwm.1:1 1b
ehrpwm.2:0 2a
ehrpwm.2:1 2b

"""

pins = {
    'adc': {
        9: {
            35:{'name': 'ain7'},
            36:{'name': 'ain6'},
            33:{'name': 'ain5'},
            37:{'name': 'ain3'},
            38:{'name': 'ain4'},
            39:{'name': 'ain1'},
            40:{'name': 'ain2'},
        },
    },
    'pwm': {
        8: {
            13:{
                'mux': 'gpmc_ad9',
                'directory': 'ehrpwm.2:1',#ehrpwm2B
                'mode':4
                },
            19: {
                'mux': 'gpmc_ad8',
                'directory': 'ehrpwm.2:0',#ehrpwm2A
                'mode':4
                },
            },
        9: {
            14: {
                'mux': 'gpmc_a2',
                'directory': 'ehrpwm.1:0', #ehrpwm1A_mux1
                'mode': 6
            },
            16:{
                'mux': 'gpmc_a3',
                'directory': 'ehrpwm.1:1',
                'mode': 6
            },
            21:{
                'mux': 'spi0_d0',
                'directory': 'ehrpwm.0:1',
                'mode': 3
            },
            22:{
                'mux': 'spi0_sclk',
                'directory': 'ehrpwm.0:0',
                'mode': 3
            },
        },
    },
    'gpio': {
        8: {
            3: {
                'mux':'gpmc_ad6',
                'export':38
            },
            11: {
                'mux':'gpmc_ad13',
                'export':45
            },
            12: {
                'mux':'gpmc_ad12',
                'export':44
            },
            14: {
                'mux':'gpmc_ad10',
                'export':26
            },
            15: {
                'mux':'gpmc_ad15',
                'export':47
            },
            16: {
                'mux':'gpmc_ad14',
                'export':46
            },
            17: {
                'mux':'gpmc_ad11',
                'export':27
            },
            22: {
                'mux':'gpmc_ad5',
                'export':37
            },
            23: { #defaults to pulldown
                'mux':'gpmc_ad4',
                'export':36
            },
            24: {
                'mux':'gpmc_ad1',
                'export':33
            },
            25: {
                'mux':'gpmc_ad0',
                'export':32
            },
            26: { #defaults to pulldown
                'mux':'gpmc_csn0',
                'export':61
            },
            27: { 
                'mux':'lcd_vsync',
                'export':86
            },
            28: { 
                'mux':'lcd_pclk',
                'export':88
            },
            29: { 
                'mux':'lcd_hsync',
                'export':87
            },
            30: { 
                'mux':'lcd_ac_bias_en',
                'export':89
            }
        },
        9: {
        }
    },
}



