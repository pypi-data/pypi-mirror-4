import configparser
import os.path

default_config = {'main': {\
    'user-agent': 'Taxonome (in testing)',
    'name-fuzzy-threshold': '0.7',
    'author-fuzzy-threshold': '0.6',
    'load-tdwg-regions': 'True',
    },
'cache': {\
    'location': '~/.taxonome',
    'user-choices': '%(location)s/user_choices',
    'expiry-days': '30',
    'clean-on-load': 'True',
    },
'api-keys': {\
    # Programmatic users should get their own API keys.
    'tropicos': '',
    },
}

def load_config(filename="~/.taxonome/taxonome.cfg"):
    config = configparser.ConfigParser()
    config.read_dict(default_config)
    config.read([os.path.expanduser(filename)])
    return config

def save_config(tosave=None, filename="~/.taxonome/taxonome.cfg"):
    if tosave is None:
        tosave = config
    with open(os.path.expanduser(filename), 'w') as f:
        config.write(f)

config = load_config()
    
