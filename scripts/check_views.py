import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackapsite.settings')

import django

def main():
    try:
        django.setup()
        # Import the officer views module to catch syntax/import errors
        import importlib
        importlib.import_module('trackapsite.officer_views')
        print('OK: officer_views imported successfully')
    except Exception as e:
        print('ERROR:', type(e).__name__, e)
        sys.exit(1)

if __name__ == '__main__':
    main()
