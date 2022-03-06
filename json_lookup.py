#!/usr/bin/env python3
import time
import requests
from bs4 import BeautifulSoup
import sys
import json
import re

# Used dictionary here: https://github.com/matthewreagan/WebstersEnglishDictionary/blob/master/dictionary.json
# Download it to use with this code

# Constants
CSV_DELIMITER = '|'


def write_to_file(file_path, text, overwrite=False):

    write_mode = "a"
    if overwrite == True:
        write_mode = "w"

    with open(file_path, write_mode) as file:
        # Writing data to a file
        file.write(text)
        file.write('\n')


def load_terms(file_path):
    
    terms = []
    with open(file_path,'r') as file:
        for line in file:
            terms.append(line)
    
    return terms


def slow_find(json_data, clean_term):
    for word in json_data:
        if word.lower().startswith(clean_term.lower()):
            return json_data[word]


def print_usage():
    print("Usage: \n 1) scraper.py -w word1 word2 word3.... \n 2) scraper.py -f file.csv")
    sys.exit(1)

## Main
# Get arguments
if len(sys.argv) < 2:
    print_usage()

for arg_num in range(len(sys.argv)):
    if (sys.argv[arg_num] == '-d'):
        dictionary_file = sys.argv[arg_num+1]

    if (sys.argv[arg_num] == '-w'):
        terms = sys.argv[(arg_num+1):]

    if (sys.argv[arg_num] == '-f'):
        terms = load_terms(sys.argv[arg_num+1])

if len(terms) <= 0:
    print_usage()

print(f"Getting definitions for {len(terms)} terms")

# Prep the file
file_path = "output.csv"
columns = ["Word", "Definitions"]
write_to_file(file_path, CSV_DELIMITER.join(columns), True)

with open(dictionary_file) as json_file:
    json_data = json.load(json_file)

found = 0
for term in terms:
    clean_term = term.strip()

    definition = None
    if clean_term in json_data:
        definition = json_data[clean_term]
    else:
        definition = slow_find(json_data, clean_term)
    
    if definition is not None:
        
        clean_defs = re.split("[\n]+", definition)
        write_to_file(
            file_path, 
            CSV_DELIMITER.join([clean_term, f'{clean_defs[0].strip()}'])
        )
        if len(clean_defs) > 1:
            for clean_def in clean_defs[1:]:
                write_to_file(
                    file_path, 
                    CSV_DELIMITER.join(['', f'{clean_def.strip()}'])
                )
