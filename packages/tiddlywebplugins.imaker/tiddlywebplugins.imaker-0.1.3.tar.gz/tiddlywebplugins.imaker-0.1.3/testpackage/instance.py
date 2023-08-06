
store_structure = {
        'bags': {
            'testbag': {
                'desc': 'A test bag',
                'policy': {
                    'read': [],
                    'write': ['R:ADMIN'],
                    'create': ['R:ADMIN'],
                    'delete': ['R:ADMIN'],
                    'manage': ['R:ADMIN'],
                    'accept': ['NONE'],
                    'onwer': 'acow'
                }
            }
        }
}

instance_config = {
        'system_plugins': ['testpackage'],
        'arbitrary': 'nonsense'
}
