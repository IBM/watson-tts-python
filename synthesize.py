import os
import os.path
import sys
import csv
import random
from config import Config

from watson_objects import WatsonObjects

class Synthesizer:

    def __init__(self, config):
        self.config = config
        self.TTS = self.createTTS()
        self.synthesis_count = 0
        self.tuples = []

    def createTTS(self):
        return WatsonObjects(self.config).createTTS()

    def synthesize(self, input_file):
        data = []
        with open(input_file) as file:
            reader = csv.reader(file)
            data = [tuple(row) for row in reader if row]
        
        type       = self.config.getValue("Synthesis", "output_file_type")
        output_dir = self.config.getValue("Synthesis", "output_dir")
        voice            = self.config.getValue("TextToSpeech", "voice")
        voice_selection_mode            = self.config.getValue("TextToSpeech", "voice_selection_mode")
        
        if voice_selection_mode == "" or not voice_selection_mode:
            voice_selection_mode = "all"

        if voice == "" or not voice:
                print("Error: invalid voice")
        else:
            voice_list = voice.split(",")

        

        os.makedirs(output_dir, exist_ok=True)

        for line in data:
            if line[0]=='id': continue #Ignore header row
            text = line[1]

            # voice_selection_mode=random 
            # pick a random voice
            if voice_selection_mode.lower() == "random" and voice_list[0]:
                voice = random.choice(voice_list)
                filename = f'{output_dir}/{line[0]}-{voice}.{type}'
                self.synthesize_text_to_file(text, filename, voice)
                self.tuples.append({"Audio File Name": filename, "Reference": text})

            # voice_selection_mode=all
            # loop through all voices and create a new file for each one
            # add voice name to each filename
            elif voice_selection_mode.lower() == "all" and voice_list[0]:
                for element in voice_list:
                    filename = f'{output_dir}/{line[0]}-{element}.{type}'
                    self.synthesize_text_to_file(text, filename, element)
                    self.tuples.append({"Audio File Name": filename, "Reference": text})

            elif not voice_list[0]:
                print("Error: invalid voice")
            elif voice_selection_mode.lower() != "all" or voice_selection_mode.lower() != "random":
                print("Error: invalid voice_selection_mode")

    def synthesize_text_to_file(self, text, output_filename, voice):
        overwrite = self.config.getBoolean("Synthesis", "overwrite")
        if overwrite is False:
            if os.path.isfile(output_filename) and os.path.getsize(output_filename) > 0:
                print("{} already exists, will not overwrite".format(output_filename))
                return


        customization_id = self.config.getValue("TextToSpeech", "customization_id")
        type             = self.config.getValue("Synthesis", "output_file_type")

        with open(output_filename, 'wb') as audio_file:
            # synthesize seems to have errors when processing large CSVs
            # adding retry logic to retry up to 3 times
            for attempt in range(3):
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
                    print(f"Attempt {attempt} failed")
                    print(f"Error synthesizing for {output_filename} with text '{text}'")
                    print("Retrying...")
                    continue
                break

    def report(self):
        print("Wrote {} syntheses".format(self.synthesis_count))

        reference_transcriptions_file = self.config.getValue("Synthesis", "reference_transcriptions_file")
        if reference_transcriptions_file:
            keys = self.tuples[0].keys()

            with open(reference_transcriptions_file, 'w', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(self.tuples)
                print(f"Wrote STT reference output to {reference_transcriptions_file}")

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
