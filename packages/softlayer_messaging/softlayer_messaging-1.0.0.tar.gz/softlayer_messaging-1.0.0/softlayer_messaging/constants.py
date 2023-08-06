""" See COPYING for license information """
import json
import os

this_dir, this_filename = os.path.split(__file__)

with open(os.path.join(this_dir, "resources", "config.json")) as f:
    ENDPOINTS = json.load(f)['endpoints']
