#!/usr/bin/python
from mpinfo import utils as mpinfo_utils
import json
import sys

postcode = sys.argv[1]
mp = mpinfo_utils.get_mp_from_postcode(postcode)
json_dict = {'name': mp.name,
             'party': mp.party,
             'select_committees': mp.select_committee_info}
print json.dumps(json_dict)
