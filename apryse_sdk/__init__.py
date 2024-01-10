import site, os, platform, sys

try:
    site.addsitedir(os.path.dirname(__file__))
except:
    sys.path.append(os.path.join(os.path.dirname(__file__)))

from PDFNetPython import *
