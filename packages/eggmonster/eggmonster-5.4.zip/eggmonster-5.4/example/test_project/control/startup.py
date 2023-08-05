import os

import fab
import eggmonster
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fab.config['base'] = base
eggmonster.update_locals({'base' : base})
eggmonster.load_default_yaml(file=os.path.join(base, 'etc', 'defaults.yaml'))
