#!/usr/bin/python
import json
import urllib
import re
from bs4 import BeautifulSoup
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
    soup = BeautifulSoup(bio_data)
    raw_westminster_details = [x for x in soup.find('div', id="biography-mp").findAll('p', recursive=False)[0].get_text().replace("\r", " ").replace("\n", "  ").split('  ') if len(x) > 1]
    raw_constituency_details = [x for x in soup.find('div', id="biography-mp").findAll('p', recursive=False)[1].get_text().replace("\r", " ").replace("\n", "  ").split('  ') if len(x) > 1]
    constituency_details = get_details(raw_constituency_details)
    parliamentary_details = get_details(raw_westminster_details)
    committee_details = soup.find('div', id="biography-mp").findAll('p', recursive=False)[3].get_text()

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

def get_details(data_list):
    details_dict = {'fax': None, 'tel': None, 'email': None, 'address': None, 'website': None}
    for line in data_list:
        if "Tel:" in line:
            details_dict['tel'] = re.search("([0-9][-0-9 ]+)", line).group(1)
        elif "Fax:" in line:
            details_dict['fax'] = re.search("([0-9][-0-9 ]+)", line).group(1)
        elif "@" in line:
            details_dict['email'] = line
        elif "www" in line:
            details_dict['website'] = line
        elif "," in line:
            details_dict['address'] = line
    return details_dict


