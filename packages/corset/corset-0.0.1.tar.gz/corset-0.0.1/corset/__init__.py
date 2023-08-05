import os
from django.conf import settings
from django.core import management

JS_DIRS = []
for root, dirs, files in os.walk(settings.PROJECT_ROOT):
    for d in dirs:
        if d == "js":
            path = os.path.join(root, d)
            JS_DIRS.append(path)