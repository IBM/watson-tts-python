import os
import os.path
import sys
import csv
import random
from config import Config
from html_table import HTMLTable

from watson_objects import WatsonObjects

class Synthesizer:
    """
    A class for synthesizing text to speech using Watson TTS service.
    """

    def __init__(self, config):
        """
        Initialize the Synthesizer with configuration.

        Args:
            config (Config): Configuration object containing TTS settings
        """
        self.config = config
        self.TTS = self.createTTS()
        self.synthesis_count = 0
        self.tuples = []

    def createTTS(self):
        """
        Create and return a Watson Text-to-Speech service instance.

        Returns:
            TextToSpeechV1: Configured Watson TTS service instance
        """
        return WatsonObjects(self.config).createTTS()

    def synthesize(self, input_file):
        """
        Synthesize text from a CSV input file to audio files.

        Args:
            input_file (str): Path to the CSV input file containing text to synthesize
        """
        data = []
        try:
            with open(input_file, encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                data = [tuple(row) for row in reader if row]
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found")
            return
        except Exception as e:
            print(f"Error reading input file '{input_file}': {e}")
            return

        type                 = self.config.getValue("Synthesis", "output_file_type")
        output_dir           = self.config.getValue("Synthesis", "output_dir")
        voice                = self.config.getValue("TextToSpeech", "voice")
        voice_selection_mode = self.config.getValue("TextToSpeech", "voice_selection_mode")
        voice_list           = []

        if voice_selection_mode == "" or not voice_selection_mode:
            voice_selection_mode = "all"

        if voice == "" or not voice:
            print("Error: invalid voice")
            exit(-1)
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
            elif voice_selection_mode.lower() != "all" and voice_selection_mode.lower() != "random":
                print("Error: invalid voice_selection_mode")

    def synthesize_text_to_file(self, text, output_filename, voice):
        """
        Synthesize text to an audio file using the Watson TTS service.

        Args:
            text (str): The text to synthesize
            output_filename (str): Path to the output audio file
            voice (str): The voice to use for synthesis
        """
        overwrite = self.config.getBoolean("Synthesis", "overwrite")
        if overwrite is False:
            if os.path.isfile(output_filename) and os.path.getsize(output_filename) > 0:
                print("{} already exists, will not overwrite".format(output_filename))
                return

        customization_id = self.config.getValue("TextToSpeech", "customization_id")
        # Use the file type from the filename extension instead of fetching again
        type = output_filename.split('.')[-1]

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
                except Exception as e:
                    print(f"Attempt {attempt} failed")
                    print(f"Error synthesizing for {output_filename} with text '{text}'", e)
                    print("Retrying...")
                    continue
                break

    def report(self):
        """
        Generate reports after synthesis is complete.

        Creates HTML table and reference transcription files if configured.
        """
        print("Wrote {} syntheses".format(self.synthesis_count))

        # Skip reporting if no syntheses were performed
        if not self.tuples:
            print("No syntheses to report")
            return

        # Generate HTML report if configured
        generate_html_to = self.config.getValue("TextToSpeech", "generate_html_to")
        if generate_html_to:
            try:
                html_table = HTMLTable(generate_html_to)
                html_table.create()
                for t in self.tuples:
                    row = t["Reference"] + ';;' + t['Audio File Name'] + \
                          ';;' + (t['Audio File Name'] + ' ')
                    html_table.add_row(row, ';;')
                html_table.close()
                print(f"Generated HTML report at {generate_html_to}")
            except Exception as e:
                print(f"Error generating HTML report: {e}")

        # Generate reference transcriptions file if configured
        reference_transcriptions_file = self.config.getValue("Synthesis", "reference_transcriptions_file")
        if reference_transcriptions_file:
            try:
                keys = self.tuples[0].keys()
                with open(reference_transcriptions_file, 'w', newline='', encoding='utf-8-sig') as output_file:
                    dict_writer = csv.DictWriter(output_file, keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(self.tuples)
                    print(f"Wrote STT reference output to {reference_transcriptions_file}")
            except Exception as e:
                print(f"Error writing reference transcriptions file: {e}")

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
