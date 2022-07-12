# Extract potentially problematic words for TTS from a CSV using a spell checker
# Divide the words up into separate files by punctuation

import pandas as pd
# may need to do a 'pip install pyspellchecker'
from spellchecker import SpellChecker 
import sys

# python problematic_word_extraction.py messages.csv

spell = SpellChecker()
content_abbr_dict = dict()
content_abbr_count = dict()
content_abbr_dup_list = []
total_abbr=0
word_list = []

filename = sys.argv[1]
    
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
parnthesis_list = []
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
        parnthesis_list.append(item)
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
print("Length of parenthesis list is: ", len(parnthesis_list))
print("Length of percent list is: ", len(percent_list))
print("Length of apostropy list is: ", len(apostrophy_list))
print("Length of leftover list is: ", len(leftover_list))
total = (len(dash_list)+len(slash_list)+len(pound_list)+len(colon_list)+len(parnthesis_list)+len(percent_list)+len(apostrophy_list)+len(leftover_list))
print("Total Length of all lists is: ", total )

# Write lists to csvs
with open ('dash_list.csv', 'w') as f:
    for item in dash_list:
        f.write("%s\n" % item)

with open ('slash_list.csv', 'w') as f:
    for item in slash_list:
        f.write("%s\n" % item)

with open ('pound_list.csv', 'w') as f:
    for item in pound_list:
        f.write("%s\n" % item)

with open ('colon_list.csv', 'w') as f:
    for item in colon_list:
        f.write("%s\n" % item)

with open ('parenthesis_list.csv', 'w') as f:
    for item in parnthesis_list:
        f.write("%s\n" % item)
    
with open ('percent_list.csv', 'w') as f:
    for item in percent_list:
        f.write("%s\n" % item)

with open ('apostropy_list.csv', 'w') as f:
    for item in apostrophy_list:
        f.write("%s\n" % item)

with open ('leftover_list.csv', 'w') as f:
    for item in leftover_list:
        f.write("%s\n" % item)