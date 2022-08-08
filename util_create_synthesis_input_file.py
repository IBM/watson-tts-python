# This utility will create the synthesis input csv file for the synthesis.py script using a csv file with words/messages.
# This utility can be useful if you have a spreadsheet with words/messages that you want to test your TTS model audios with.

# Inputs:
# first: A single column csv file with one word/message per row
# Note: The first row of the csv must be a single entry of "words"
# second: A filename for the synthesis csv
# Note: The audio filename column in the synthesis csv will be set to the row number of the input csv

# Output: 
# A csv file formatted correctly to be used as an input to synthesis.py

# Sample script execution: python util_create_synthesis_input_file.py messages.csv inputfile_to_synthesize.csv

import pandas as pd
import sys
import csv

input_file = sys.argv[1]
output_file = sys.argv[2]
    
if 'xlsx' in input_file:
    words = pd.read_excel(input_file)
else:
    words = pd.read_csv(input_file)

words_list = words['words'].to_list()

x = pd.DataFrame(data={"id": pd.Index.values, "text": words_list})
x['id'] = x.index

x.to_csv(output_file, sep=',', index=False, quotechar='"',quoting=csv.QUOTE_NONNUMERIC)