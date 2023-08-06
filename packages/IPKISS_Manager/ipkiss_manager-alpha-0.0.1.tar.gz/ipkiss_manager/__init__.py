import os

FIXTURES = os.path.join(os.path.abspath( os.path.dirname(__file__) ), 'fixtures')

if os.name == 'nt':
    LOCAL_DATA_FOLDER = os.path.join(os.environ['appdata'], 'IPKISS_manager')
elif os.name == 'posix':
    LOCAL_DATA_FOLDER = os.path.join(os.environ['HOME'], '.IPKISS_manager')
else:
    raise Exception('Not supported OS family: %s\n.' % os.name)
