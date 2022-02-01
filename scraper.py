import time
import requests
from bs4 import BeautifulSoup
import sys

# Constants
CSV_DELIMITER = '|'

WORD = 'Word'
PRONUNCIATION = 'Pronunciation'
POS = "POS"
DEFINITION = 'Definition'
SYNONYMS = 'Synonyms'
ANTONYMS = 'Antonyms'
ORIGIN = 'Origin'
WOF = 'Word form'
STEM = 'Stem'
EXAMPLE = 'Example'

def get_page_data(url):
    print(f'- Getting page data from {url}...')
    page = requests.get(url)
    return page.content


def get_dictionary_api(term):
    print('- Getting data from Dictionary API...')
    word_response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{term}")
    if word_response.status_code == 200:
        return word_response.json()

    return None


def parse_dictionary(page_data):
    response = {}
    soup = BeautifulSoup(page_data, "html.parser")

    word_form_box = soup.find('div', {'class': 'expandable content-hidden css-12x6sdt e1fc5zsj0'})
    wof_elements = word_form_box.findChildren('span', { 'class': 'luna-runon bold'})

    wof_entries = []
    for element in wof_elements:
        wof_entries.append(element.text.replace(',', ''))
        print(f'- Parsing element: {element}', end="\n"*2)

    response[WOF] = ','.join(wof_entries)
    return response


def parse_etymonline(page_data):
    response = {}

    soup = BeautifulSoup(page_data, "html.parser")


    definition_box = soup.find('div', { "class": "css-1avshm7 e16867sm0" })
    pos_elements = definition_box.findChildren("span", { "class": "luna-pos"})
    
    pos_entries = []
    for element in pos_elements:
        pos_entries.append(element.text)
        #print(element, end="\n"*2)

    response[POS] = pos_entries
    return response


def write_to_file(file_path, text, overwrite=False):

    write_mode = "a"
    if overwrite == True:
        write_mode = "w"

    with open(file_path, write_mode) as file:
        # Writing data to a file
        file.write(text + "\n")


## Main
# Get arguments
terms = sys.argv[1:]

if len(terms) <= 0:
    print("Usage: scraper.py <term1> <term2> ...")
    sys.exit(1)

print(f"Getting defintions for terms: {terms}")

# Prep the file
file_path = "output.csv"
columns = [WORD, PRONUNCIATION, POS, DEFINITION, SYNONYMS, ANTONYMS, ORIGIN, WOF, STEM, EXAMPLE]
write_to_file(file_path, CSV_DELIMITER.join(columns), True)

for term in terms:
    # Get the page data
    url = f"https://www.dictionary.com/browse/{term}"
    page_data = get_page_data(url)
    dictionary_data = parse_dictionary(page_data)

    # Get API data. Do some retries since it is unreliable
    api_data = None
    max_retries = 5
    while api_data is None:
        api_data = get_dictionary_api(term)
        if api_data is None:
            print('Error getting API data, retrying in 5 seconds')
            time.sleep(5)

    if (api_data is None):
        print("Could get any data from the API")
        sys.exit(1)

    # Write output
    word_entry = {}

    for word in api_data:
        for meaning in word['meanings']:
            word_entry[WORD] = word['word']
            word_entry[PRONUNCIATION] = word['phonetic']
            word_entry[POS] = meaning["partOfSpeech"]
            word_entry[DEFINITION] = meaning['definitions'][0]['definition']
            word_entry[SYNONYMS] = ','.join(meaning['definitions'][0]['synonyms'])
            word_entry[ANTONYMS] = ','.join(meaning['definitions'][0]['antonyms'])
            if 'origin' in word:
                word_entry[ORIGIN] = word['origin']
            else:
                word_entry[ORIGIN] = 'N/A'
            word_entry[WOF] = dictionary_data[WOF]
            word_entry[STEM] = 'N/A'
            if 'example' in meaning['definitions'][0]:
                word_entry[EXAMPLE] = meaning['definitions'][0]['example']
            else:
                word_entry[EXAMPLE] = 'N/A'
            
            # Output to the file
            write_to_file(
                file_path, 
                CSV_DELIMITER.join(list(map(lambda entry: word_entry[entry], columns)))
            )
