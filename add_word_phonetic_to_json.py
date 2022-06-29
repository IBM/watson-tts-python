# Parse phonetic pronunciations from TTS pronounce csv
# Add tranlations to existing custom words TTS json file

import json
import sys
import re

# python add_word_phonetic_to_json.py tts_pronounce.csv CustomWords.json

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