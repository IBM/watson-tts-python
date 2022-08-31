# This utility will extract potentially problematic words for TTS using a spell checker. 
# The problematic words will then be filtered into separate files based on the punctuation contained in the words.
# e.g. "he/she" -> slash_list.csv
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
# dash_list.csv
# slash_list.csv
# pound_list.csv
# colon_list.csv
# parenthesis_list.csv
# percent_list.csv
# apostropy_list.csv
# leftover_list.csv

# Sample script execution: python util_problematic_word_extraction.py messages.csv en

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

if(len(sys.argv) < 3):
    print("Error: Requires two positional arguments: input csv filename, and language code")
    exit(2)

filename = sys.argv[1]
lang = sys.argv[2]

spell = SpellChecker(language=lang)
content_abbr_dict = dict()
content_abbr_count = dict()
content_abbr_dup_list = []
total_abbr=0
word_list = []


    
if 'xlsx' in filename:
    messages = pd.read_excel(filename)
else:
    messages = pd.read_csv(filename)

messages = messages.dropna(subset=['MSG'])

print("Number of messages: ", len(messages))
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

print("Length of word list is: ", len(word_list) )

dash_list = []
slash_list =[]
pound_list = []
colon_list = []
parenthesis_list = []
percent_list = []
apostrophy_list = []
leftover_list = []

for item in word_list:
    if "-" in item:
        dash_list.append(item)
    elif "/" in item:
        slash_list.append(item)
    elif "#" in item:
        pound_list.append(item)
    elif ":" in item:
        colon_list.append(item)
    elif "(" in item or ")" in item:
        parenthesis_list.append(item)
    elif "%" in item:
        percent_list.append(item)
    elif "'" in item:
        apostrophy_list.append(item)
    else:
        leftover_list.append(item)

print("Length of dash list is: ", len(dash_list))
print("Length of slash list is: ", len(slash_list)) 
print("Length of pound list is: ", len(pound_list))
print("Length of colon list is: ", len(colon_list))
print("Length of parenthesis list is: ", len(parenthesis_list))
print("Length of percent list is: ", len(percent_list))
print("Length of apostrophy list is: ", len(apostrophy_list))
print("Length of leftover list is: ", len(leftover_list))
total = (len(dash_list)+len(slash_list)+len(pound_list)+len(colon_list)+len(parenthesis_list)+len(percent_list)+len(apostrophy_list)+len(leftover_list))
print("Total Length of all lists is: ", total )

# Write lists to csvs
write_file('dash_list.csv', dash_list)
write_file('slash_list.csv', slash_list)
write_file('pound_list.csv', pound_list)
write_file('colon_list.csv', colon_list)
write_file('parenthesis_list.csv', parenthesis_list)
write_file('percent_list.csv', percent_list)
write_file('apostrophy_list.csv', apostrophy_list)
write_file('leftover_list.csv', leftover_list)