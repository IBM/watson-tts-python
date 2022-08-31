# This utility will take the output csv file from the pronounce.py script and add its new words to an existing custom words TTS json file.
# This utility requires an existing words json file.

# Inputs:
# first: the csv output from the pronounce.py script
# second: the filename of an existing words json to be updated with the words and their pronunciation translations

# Output:
# The existing custom words TTS json file will be updated with a new word and its translation for each pronunciation from the input csv. 

# Sample script execution: python util_add_word_phonetic_to_json.py tts_pronounce.csv CustomWords.json

import json
import sys
import re

if(len(sys.argv) < 3):
    print("Error: Requires two positional arguments: input csv filename, and JSON file")
    exit(2)

def contains_term(word_list, term):
    for word in word_list:
        if word['word'] == term:
            return True
    return False

pronounce_filename = sys.argv[1]
custom_words_json_filename = sys.argv[2]

pronounce_list = open(pronounce_filename).read().splitlines()
json_data = json.load(open(custom_words_json_filename))

# loop through the list of phonetic pronunciations
for item in pronounce_list[1:]:
    # parse the pronunciation and word parts
    pronouciation_raw = item.split(",")[1]
    ph_part = pronouciation_raw.split("phoneme alphabet=")[1]
    alphabet = ph_part.split("'")[1]
    ph = ph_part.split("'")[3]
    word_raw = ph_part.split("'")[4]
    word = re.search(r'\>(.*?)\<',word_raw).group(1)

    if(contains_term(json_data['words'], word)):
        continue
    # using a list will ensure the backslashes are inserted into the json
    translation_list = ['<phoneme alphabet=', '"', alphabet, '" ', 'ph=', '"', ph, '..."></phoneme>']
    translation_str = ''
    for x in translation_list:
        translation_str += x
    # add translations to json data
    json_data['words'].append({
    "translation": translation_str,
    "word": word
    })

# update the json file
with open(custom_words_json_filename, 'w') as outfile:
    json.dump(json_data, outfile)

print(f"Added {len(pronounce_list)-1} words to {custom_words_json_filename}")
