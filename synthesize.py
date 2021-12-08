import os
import os.path
import sys
import csv
from config import Config

from watson_objects import WatsonObjects

class Synthesizer:

    def __init__(self, config):
        self.config = config
        self.TTS = self.createTTS()
        self.synthesis_count = 0

    def createTTS(self):
        return WatsonObjects(self.config).createTTS()

    def synthesize(self, input_file):
        data = []
        with open(input_file) as file:
            reader = csv.reader(file)
            data = [tuple(row) for row in reader if row]
        
        type       = self.config.getValue("Synthesis", "output_file_type")
        output_dir = self.config.getValue("Synthesis", "output_dir")

        os.makedirs(output_dir, exist_ok=True)

        for line in data:
            if line[0]=='id': continue #Ignore header row
            text = line[1]
            filename = f'{output_dir}/{line[0]}.{type}'
            self.synthesize_text_to_file(text, filename)

    def synthesize_text_to_file(self, text, output_filename):
        overwrite = self.config.getBoolean("Synthesis", "overwrite")
        if overwrite is False:
            if os.path.isfile(output_filename) and os.path.getsize(output_filename) > 0:
                print("{} already exists, will not overwrite".format(output_filename))
                return

        voice            = self.config.getValue("TextToSpeech", "voice")
        customization_id = self.config.getValue("TextToSpeech", "customization_id")
        type             = self.config.getValue("Synthesis", "output_file_type")

        with open(output_filename, 'wb') as audio_file:
            try: 
                audio_file.write(
                    self.TTS.synthesize(
                        text,
                        voice=voice,
                        accept='audio/' + type,
                        customization_id=customization_id     
                    ).get_result().content)
                self.synthesis_count += 1
                print("Wrote {}".format(output_filename))
            except:
                print(f"Error synthesizing for {output_filename} with text '{text}'")

    def report(self):
        print("Wrote {} syntheses".format(self.synthesis_count))

def main():
    config_file = "config.ini"
    if len(sys.argv) > 1:
       config_file = sys.argv[1]
    else:
       print("Using default config filename: config.ini.")

    config      = Config(config_file)
    synthesizer = Synthesizer(config)

    input_file = config.getValue("Synthesis", "input_file")
    synthesizer.synthesize(input_file)

    synthesizer.report()

if __name__ == '__main__':
    main()
