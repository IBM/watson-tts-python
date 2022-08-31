# This utility will create simple translations for acronyms and add them as new words to an existing custom words TTS json file.
# The simple translation is to add spaces between the letters and a comma at the end, e.g. IBM -> I B M,
# This utility requires an existing words json file.

# Inputs:
# first: a single column csv file with one acronym in each row
# second: the filename of an existing custom words TTS json to be updated with the acronyms and their translations

# Output:
# The existing custom words TTS json file will be updated with a new word and its translation for each acronym from the input csv. 

# Sample script execution: python util_add_acronym_pronounce_to_json.py test_terms.csv CustomWords.json

import json
import sys

if(len(sys.argv) < 3):
    print("Error: Requires two positional arguments: input csv filename, and JSON file")
    exit(2)

def contains_term(word_list, term):
    for word in word_list:
        if word['word'] == term:
            return True
    return False

terms_filename = sys.argv[1]
custom_words_json_filename = sys.argv[2]

term_list = open(terms_filename).read().splitlines()
json_data = json.load(open(custom_words_json_filename))

# loop through the list of acronyms
for i in range(len(term_list)):
    term = term_list[i]
    if(contains_term(json_data['words'], term)):
        continue
    
    translation_list = []
    # break out the letters in the acronym
    for t in term:
        translation_list.append(t)
    # formulate the translation string
    trans_string = " ".join(str(x) for x in translation_list)
    # add translations to json data
    json_data['words'].append({
    "translation": trans_string,
    "word": term
    })

# update the json file
with open(custom_words_json_filename, 'w') as outfile:
    json.dump(json_data, outfile)

print(f"Added {len(term_list)} words to {custom_words_json_filename}")