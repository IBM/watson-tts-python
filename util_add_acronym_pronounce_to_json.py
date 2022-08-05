# Use csv of acronyms and translate, e.g. IBM -> I B M,
# Add tranlations to existing custom words TTS json file

import json
import sys

# python add_acronym_pronounce_to_json.py test_terms.csv CustomWords.json

terms_filename = sys.argv[1]
custom_words_json_filename = sys.argv[2]

term_list = open(terms_filename).read().splitlines()
json_data = json.load(open(custom_words_json_filename))

# loop through the list of acronyms
for i in range(len(term_list)):
    term = term_list[i]
    translation_list = []
    # break out the letters in the acronym
    for t in term:
        translation_list.append(t)
    # formulate the translation string
    trans_string = " ".join(str(x) for x in translation_list)+","
    # add translations to json data
    json_data['words'].append({
    "translation": trans_string,
    "word": term
    })

# update the json file
with open(custom_words_json_filename, 'w') as outfile:
    json.dump(json_data, outfile)