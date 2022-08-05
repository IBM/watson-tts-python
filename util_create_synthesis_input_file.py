import pandas as pd
import sys

# python createSynthesisInputFile.py words.csv inputfile_to_synthesize.csv 

# input file need to have "words" header in the first row
input_file = sys.argv[1]
output_file = sys.argv[2]
    
if 'xlsx' in input_file:
    words = pd.read_excel(input_file)
else:
    words = pd.read_csv(input_file)

words_list = words['words'].to_list()

x = pd.DataFrame(data={"id": words_list, "text": words_list})
x.to_csv(output_file, sep=',', index=False)