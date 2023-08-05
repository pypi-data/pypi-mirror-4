from zopyx.txng3.core import *
# Inject modules into the textindexng namespace so old imports still work. This
# is necessary for old database instances loading indexes from here.
import sys
for name, module in sys.modules.items():
    if not name.startswith('zopyx.txng3.core.'):
        continue
    name = name.replace('zopyx.txng3.core.', 'textindexng.', 1)
    sys.modules[name] = module
