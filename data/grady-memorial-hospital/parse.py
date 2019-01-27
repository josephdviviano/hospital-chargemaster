#!/usr/bin/env python

import os
from glob import glob
import json
import pandas
import datetime
import sys

here = os.path.dirname(os.path.abspath(__file__))
folder = os.path.basename(here)
latest = '%s/latest' % here
year = datetime.datetime.today().year
output_data = os.path.join(here, 'data-latest.tsv')
output_year = os.path.join(here, 'data-%s.tsv' % year)

# Function read zip into memory
def extract_zip(input_file):
    input_zip = ZipFile(input_file)
    return {name: input_zip.read(name) for name in input_zip.namelist()}

# Don't continue if we don't have latest folder
if not os.path.exists(latest):
    print('%s does not have parsed data.' % folder)
    sys.exit(0)

# Don't continue if we don't have results.json
results_json = os.path.join(latest, 'records.json')
if not os.path.exists(results_json):
    print('%s does not have results.json' % folder)
    sys.exit(1)

with open(results_json, 'r') as filey:
    results = json.loads(filey.read())

columns = ['charge_code', 
           'price', 
           'description', 
           'hospital_id', 
           'filename', 
           'charge_type']

df = pandas.DataFrame(columns=columns)

for result in results:
    filename = os.path.join(latest, result['filename'])
    if not os.path.exists(filename):
        print('%s is not found in latest folder.' % filename)
        continue

    if os.stat(filename).st_size == 0:
        print('%s is empty, skipping.' % filename)
        continue

    contents = None
    if filename.endswith('txt'):

        # ['DESCRIPTION', 'Unnamed: 1', 'PRICE']
        contents = pandas.read_csv(filename)
        contents = contents.dropna(how='all') 

        print("Parsing %s" % filename)
        print(contents.head())

        # Update by row
        for row in contents.iterrows():
            idx = df.shape[0] + 1
            price = row[1]['PRICE'].replace('$','').replace(',','').strip()
            entry = [None,                              # charge code
                     price,                             # price
                     row[1]["DESCRIPTION"],             # description
                     result['hospital_id'],             # hospital_id
                     result['filename'],
                     'standard']                        # filename
            df.loc[idx,:] = entry

# Remove empty rows
df = df.dropna(how='all')

# Save data!
print(df.shape)
df.to_csv(output_data, sep='\t', index=False)
df.to_csv(output_year, sep='\t', index=False)
