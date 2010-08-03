#!/www/HomePage/bin/python
import os
import sys
os.environ.setdefault('PATH', '/bin:/usr/bin')
os.environ['PATH'] = '/www/HomePage/bin:' + os.environ['PATH']
os.environ['VIRTUAL_ENV'] = '/www/HomePage'
os.chdir('/www/HomePage')

sys.path.insert(0, "/www/HomePage")

from flup.server.fcgi import WSGIServer
from homepage import app
WSGIServer(app, bindAddress='/tmp/homepage.sock').run()
