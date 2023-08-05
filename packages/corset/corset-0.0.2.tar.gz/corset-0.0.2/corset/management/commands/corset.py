from django.core.management.base import BaseCommand, CommandError
from django.template import Context, Template
from django.conf import settings
from corset import JS_DIRS
import requests, os, glob

CLOSURE_URL = 'http://closure-compiler.appspot.com/compile'
payload = {'compilation_level': 'SIMPLE_OPTIMIZATIONS', 'output_format': 'json', 'output_info': 'compiled_code'}

class Command(BaseCommand):
    def handle(self, *args, **options):
        JS_DIRS = []
        for root, dirs, files in os.walk(settings.PROJECT_ROOT):
            for d in dirs:
                if d == "js":
                    path = os.path.join(root, d)
                    JS_DIRS.append(path)
                    for d in path:
                        src = os.path.join(d, "src")
                        build = os.path.join(d, "build")
                        for f in glob.glob(os.path.join(src, '*.js')):
                            payload['js_code'] = open(os.path.join(src, f), 'r').read()
                            r = requests.post(CLOSURE_URL, data = payload)
                            compiled_code = r.json['compiledCode']
                            build_file = open("%s.min.js" % os.path.join(build, os.path.splitext(os.path.basename(f))[0]), 'w')
                            build_file.write(compiled_code)
                            build_file.close()