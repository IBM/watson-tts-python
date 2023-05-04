# This utility will extract potentially problematic words for TTS using a spell checker. 
# This utility can be useful if have a lot of words/messages to test and you wish to bootstrap your custom TTS model with potentially problematic words.
# The other utility scripts can then be used to update an existing custom TTS words model with these problematic words. See:
# util_add_acronym_pronounce_to_json.py
# util_add_word_phonetic_to_json.py
# util_create_synthesis_input_file.py

# Inputs:
# first: A single column csv file with one word/message per row
# second: Language code. See supported list of languages here: https://pyspellchecker.readthedocs.io/en/latest/#non-english-dictionaries

# Output: 
# CSV files containing lists of words/messages based on their punctuation. 

# Sample script execution: python util_problematic_word_extraction.py messages.csv output.csv en

import pandas as pd
# may need to do a 'pip install pyspellchecker'
from spellchecker import SpellChecker 
# https://pyspellchecker.readthedocs.io/en/latest/
import sys

def write_file(filename, contents):
    with open (filename, 'w') as f:
        for item in contents:
            f.write("%s\n" % item)
        print(f"Wrote {len(contents)} items to {filename}")

if(len(sys.argv) < 4):
    print("Error: Requires three positional arguments: input csv filename, output csv filename and language code")
    exit(2)

filename = sys.argv[1]
output_filename = sys.argv[2]
lang = sys.argv[3]

spell = SpellChecker(language=lang)
content_abbr_dict = dict()
content_abbr_count = dict()
content_abbr_dup_list = []
total_abbr=0
word_list = []
description_list = []


    
if 'xlsx' in filename:
    messages = pd.read_excel(filename)
else:
    messages = pd.read_csv(filename)

messages = messages.dropna(subset=['MSG'])
messages_list = messages['MSG'].to_list()

# Collect problematic words
print("####"*7, "Processing File: ", filename, "####"*7)

for item in range (len(messages_list)):
    # Remove words connected with common punctuation 
    striped_text = str(messages_list[item]).translate(str.maketrans('', '', ";$.,!?"))
    # striped_text = str(messages_list[item]).translate(str.maketrans('', '', "!#$%&'()*+,-.\:;<=>?@[]^_`{|}~"))
    striped_text_split = striped_text.split(" ")
    # Get misspelled words
    misspelled = spell.unknown(striped_text_split)
    if len(misspelled) > 0:
        for word in misspelled:
            if word not in word_list:
                word_list.append(word)
                description_list.append(messages_list[item])

print("Length of word list is: ", len(word_list) )
print("Length of word list is: ", len(description_list) )
dictionary = dict(zip(word_list, description_list))

print("####"*7, "Writing problematic words to: ", output_filename, "####"*7)
(pd.DataFrame.from_dict(data=dictionary, orient='index').to_csv(output_filename, header=False))
