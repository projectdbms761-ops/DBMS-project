import sys, traceback, importlib
sys.path.insert(0, r"d:\DBMS project")
try:
    importlib.invalidate_caches()
    m = importlib.import_module('app')
    print('IMPORT_OK')
except Exception:
    traceback.print_exc()
