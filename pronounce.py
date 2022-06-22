import os
import os.path
import sys
import csv
import json
from config import Config

from watson_objects import WatsonObjects

class Pronouncer:

    def __init__(self, config):
        self.config = config
        self.TTS = self.createTTS()
        self.pronunciations = list()

    def createTTS(self):
        return WatsonObjects(self.config).createTTS()

    def pronounce(self, input_file):
        data = []
        with open(input_file) as file:
            reader = csv.reader(file)
            data = [tuple(row) for row in reader if row]

        num_total        = len(data)
        num_pronounced   = 0
        # use the first voice in the list
        voice            = self.config.getValue("TextToSpeech", "voice").split(",")[0]
        customization_id = self.config.getValue("TextToSpeech", "customization_id")
        phonetic         = self.config.getValue("Pronunciation", "phonetic")

        print(f"Pronouncing {num_total} inputs from {input_file}")
        for datum in data:
            num_pronounced += 1
            text = datum[0]
            ssml_input= f"<speak version=\"1.0\">{text}</speak>"
            id = f"{text.replace(' ','_')}_{phonetic}"

            try:
                pronunciation = self.TTS.get_pronunciation(
                    customization_id=customization_id,
                    text=ssml_input,
                    voice=voice,
                    format=phonetic
                ).get_result()

                phoneme_sequence = pronunciation['pronunciation']
                phoneme_sequence = phoneme_sequence.replace('`','').replace('[','').replace(']','') #Remove IBM SPR special characters
                ssml_out = f"<speak version='1.0'><phoneme alphabet='{phonetic}' ph='{phoneme_sequence}'>{text}</phoneme></speak>"
                self.pronunciations.append({'id':id, 'text':ssml_out})
                print(f"  Pronounced \"{text}\" ({num_pronounced} of {num_total})")
            except:
                print(f"Error pronouncing \"{text}\" ({num_pronounced} of {num_total})")

    def report(self):
        output_filename = self.config.getValue("Pronunciation", "output_file")
        keys = self.pronunciations[0].keys()

        with open(output_filename, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.pronunciations)
            print(f"Wrote pronunciations to {output_filename}")

def main():
    config_file = "config.ini"
    if len(sys.argv) > 1:
       config_file = sys.argv[1]
    else:
       print("Using default config filename: config.ini.")

    config      = Config(config_file)
    pronouncer  = Pronouncer(config)

    input_file = config.getValue("Pronunciation", "input_file")
    pronouncer.pronounce(input_file)

    pronouncer.report()

if __name__ == '__main__':
    main()