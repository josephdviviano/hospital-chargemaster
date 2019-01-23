#!/usr/bin/env python

import os
import requests
import json
import datetime
import shutil
from bs4 import BeautifulSoup

here = os.path.dirname(os.path.abspath(__file__))

url ='https://www.adventhealth.com/pricelist'

today = datetime.datetime.today().strftime('%Y-%m-%d')
outdir = os.path.join(here, today)
if not os.path.exists(outdir):
    os.mkdir(outdir)

prefix = "https://www.adventhealth.com"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

# Each folder will have a list of records
records = []

for entry in soup.find_all('a', href=True):
    download_url = prefix + entry['href']
    if '.xml' in download_url:  
        filename =  os.path.basename(download_url.split('?')[0])  

        entry_name = entry.text
        entry_uri = entry_name.strip().lower().replace(' ','-')

        # Some filenames are repeated (CFR)
        filename = "%s-%s" %(entry_uri, filename).strip()

        # We want to get the original file, not write a new one
        output_file = os.path.join(outdir, filename)
        os.system('wget -O "%s" "%s"' % (output_file, download_url))

        record = { 'hospital_id': entry_uri,
                   'filename': filename,
                   'date': today,
                   'uri': entry_uri,
                   'name': entry_name,
                   'url': download_url }

        records.append(record)

# Keep json record of all files included
records_file = os.path.join(outdir, 'records.json')
with open(records_file, 'w') as filey:
    filey.write(json.dumps(records, indent=4))

# This folder is also latest.
latest = os.path.join(here, 'latest')
if os.path.exists(latest):
    shutil.rmtree(latest)

shutil.copytree(outdir, latest)
