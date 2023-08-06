""" See COPYING for license information """
from softlayer_messaging.compat import json
import os

VERSION = "1.0.1"
this_dir, this_filename = os.path.split(__file__)

with open(os.path.join(this_dir, "resources", "config.json")) as f:
    ENDPOINTS = json.load(f)['endpoints']
