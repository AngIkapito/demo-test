import os
import sys

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackapsite.settings')

import django
from django.template.loader import get_template

try:
    django.setup()
    tmpl = get_template('member/home.html')
    print('OK: template compiled successfully')
except Exception as e:
    print('ERROR:', type(e).__name__, str(e))
    sys.exit(1)
