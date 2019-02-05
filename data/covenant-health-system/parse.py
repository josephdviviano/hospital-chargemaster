#!/usr/bin/env python

import os
from glob import glob
import json
import pandas
import datetime

here = os.path.dirname(os.path.abspath(__file__))
folder = os.path.basename(here)
latest = '%s/latest' % here
year = datetime.datetime.today().year

output_data = os.path.join(here, 'data-latest.tsv')
output_year = os.path.join(here, 'data-%s.tsv' % year)

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

# First parse standard charges (doesn't have DRG header)
for result in results:
    filename = os.path.join(latest, result['filename'])
    if not os.path.exists(filename):
        print('%s is not found in latest folder.' % filename)
        continue

    if os.stat(filename).st_size == 0:
        print('%s is empty, skipping.' % filename)
        continue

    print("Parsing %s" % filename)

    charge_type = 'standard'
    if "DRG" in filename:
        charge_type = 'drg'

    print("Parsing %s" % filename)

    if filename.endswith('xlsx'):

        if charge_type == "standard":

            # ['HOSPITAL SYSTEM CHARGE CODE', 'CHARGE DESCRIPTION', 'INPATIENT PRICE', 'OUTPATIENT PRICE'],
            content = pandas.read_excel(filename, skiprows=8)

            for row in content.iterrows():

                # Inpatient
                idx = df.shape[0] + 1
                entry = [row[1]['HOSPITAL SYSTEM CHARGE CODE'], # charge code
                         row[1]['INPATIENT PRICE'],              # price
                         row[1]['CHARGE DESCRIPTION'], # description
                         result["hospital_id"],     # hospital_id
                         result['filename'],
                         "inpatient"]            
                df.loc[idx,:] = entry

                # Outpatient
                idx = df.shape[0] + 1
                entry = [row[1]['HOSPITAL SYSTEM CHARGE CODE'], # charge code
                         row[1]['OUTPATIENT PRICE'],              # price
                         row[1]['CHARGE DESCRIPTION'], # description
                         result["hospital_id"],     # hospital_id
                         result['filename'],
                         "outpatient"]            
                df.loc[idx,:] = entry

        else:

            # 'Facility', 'MS DRG', 'Description', 'Number of Claims', 'Average Proposed Charge'
            content = pandas.read_excel(filename, skiprows=8)
   
            for row in content.iterrows():

                idx = df.shape[0] + 1
                entry = [row[1]['MS DRG'],            # charge code
                         row[1]['Average Proposed Charge'], # price
                         row[1].Description,          # description
                         row[1].Facility,            # hospital_id
                         result['filename'],
                         charge_type]                # filename
                df.loc[idx,:] = entry


# Remove empty rows
df = df.dropna(how='all')

# Save data!
print(df.shape)
df.to_csv(output_data, sep='\t', index=False)
df.to_csv(output_year, sep='\t', index=False)