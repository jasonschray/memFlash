# appengine_config.py
from google.appengine.ext import vendor
#import vendor
# Add any libraries install in the "lib" folder.
vendor.add('lib')

# Patch os.path.expanduser. This should be fixed in GAE
# versions released after Nov 2016.
import os.path


def patched_expanduser(path):
    return path

os.path.expanduser = patched_expanduser