#!/usr/bin/python
import json
import urllib
import re
from classes import MPDetails

def get_mp_from_postcode(postcode):
    mp = MPDetails()
    data = urllib.urlopen(
            "http://findyourmp.parliament.uk/api/search?q=%s&f=js" % postcode)
    constituencies = json.load(data)['results']['constituencies']
    if len(constituencies) != 1:
        print "Postcode %s is invalid or"\
              "maps to multiple constituencies." % postcode
        return mp
    parsed_data = constituencies[0]

    twfy_data = json.load(urllib.urlopen("http://www.theyworkforyou.com"\
                "/api/getMP?postcode=%s&output=js"\
                "&key=CqiGfBD4nmmDAFMRR8ETJ6jY" % postcode))

    bio_data = urllib.urlopen(parsed_data["member_biography_url"]).read()
    prog = re.compile("<strong>Constituency</strong>.*?<p>(.*?)</p>", 
                        flags=re.DOTALL)
    prog_wm = re.compile("<strong>Westminster</strong>.*?<p>(.*?)</p>", 
                        flags=re.DOTALL)
    prog_sc = re.compile("<h4>Select committees</h4>.*?<p>(.*?)</p>", 
                        flags=re.DOTALL)
    constituency_details = get_details(prog, bio_data)
    parliamentary_details = get_details(prog_wm, bio_data)
    committee_details = prettify_block(prog_sc.search(bio_data).group(1))

    mp.name = parsed_data["member_name"]
    mp.party = parsed_data["member_party"]
    mp.constituency_addr = constituency_details['address']
    mp.constituency_tel = constituency_details['tel']
    mp.constituency_fax = constituency_details['fax']
    mp.constituency_email = constituency_details['email']
    mp.parliamentary_addr = parliamentary_details['address']
    mp.parliamentary_tel = parliamentary_details['tel']
    mp.parliamentary_fax = parliamentary_details['fax']
    mp.parliamentary_email = parliamentary_details['email']
    mp.select_committee_info = committee_details

    if 'office' in twfy_data:
        mp.government_position = twfy_data['office'][0]['position']
    return mp

def prettify_block(data):
    details = re.sub("<.*?>", "", data)
    details = re.sub("\n[ ]+", "\n", details)
    details = re.sub("\r", "", details)
    details = re.sub("^\s+", "", details)
    details = re.sub("\s+$", "", details)
    return details

def get_details(regexp, data):
    match_obj = regexp.search(data)
    details_dict = {'fax': None, 'tel': None, 'email': None, 'address': None}
    details = prettify_block(match_obj.group(1))
    for line in match_obj.group(1).split("\n"):
        if "Tel:" in line:
            details_dict['tel'] = re.search("([0-9][-0-9 ]+)", line).group(1)
        elif "Fax:" in line:
            details_dict['fax'] = re.search("([0-9][-0-9 ]+)", line).group(1)
        elif "mailto" in line:
            details_dict['email'] = re.search("mailto:(.*?)\"", line).group(1)
    for line in details.split("\n"):
        if "," in line:
            details_dict['address'] = line
    return details_dict


