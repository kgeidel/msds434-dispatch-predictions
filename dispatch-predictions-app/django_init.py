import os, sys
from django import setup

# derive location to your django project setting.py
proj_path = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
proj_path = os.path.join(proj_path, "dispatch-predictions-app")
# load your settings.py
os.chdir(proj_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dispatch_predictions.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# Append proj_path to PATH
sys.path.append(proj_path)

setup()