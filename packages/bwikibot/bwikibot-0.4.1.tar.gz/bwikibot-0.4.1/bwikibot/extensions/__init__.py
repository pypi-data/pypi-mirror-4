import os
from glob import glob

# import all extensions
for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    try:
        __import__(module[:-3], locals(), globals())
    except Exception as e:
        print('Exception {} in extension {}'.format(e, module))
del module
