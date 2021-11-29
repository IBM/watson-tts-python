# TTS-Python-Tool
TTS Python tools to assist customers in experimentation and configuration

## synthesize.py
Takes an input CSV file with IDs and text, synthesizes each text into an audio file as specified by the ID.  Global configuration is updated in `config.ini` file.

Example input file:

|id|text|  
|--|--|
|quickbrown|"The quick brown fox"|
|lazydog|"jumped over the lazy dog"|

Will produce output files quickbrown.wav and lazydog.wav

Use `config.ini` to specify information about your text to speech service and model in `[TextToSpeech]` section.  Specify output details into `[Synthesis]` section.

```
[TextToSpeech]
apikey=xxxxxxxxx-xxxxx-xxxxx-xxxxxxxxxxx
service_url=https://....
use_bearer_token=False
voice=en-US_MichaelV3Voice
;customization_id=xxxxxxxxx-xxxxx-xxxxx-xxxxxxxxxxx

[Synthesis]
output_dir=transcriptions
output_file_type=mp3
input_file = inputfile_to_transcribe.csv
overwrite = True
```

## pronounce.py
Takes an input file with one word/word phrase per line and generates pronunciations.  Global configuration is updated in `config.ini` file.    The output file from this process is suitable for passing as an input file to `synthesize.py`.

Example input file:
```
lazy
thirty
```

Example configuration section:
```
[Pronunciation]
input_file = words_to_pronounce.txt
#ipa or ibm
phonetic = ipa
#This file is suitable for use in [Synthesis] as `input_file`
output_file=tts_pronounce.csv
```

Example output file:

|id|text|  
|--|--|
|lazy_ipa|`<speak version='1.0'><phoneme alphabet='ipa' ph='.ˈleɪ.zi'>lazy</phoneme></speak>`|
|thirty_ipa|`<speak version='1.0'><phoneme alphabet='ipa' ph='.ˈθɜ.ɾi'>thirty</phoneme></speak>`|


## extract_skill_text.py
Takes a Watson Assistant skill and extracts all of the text "spoken" by the assistant.  The output file from this process is suitable for passing as an input file to `synthesize.py`.

Example output file:

|id|text|  
|--|--|
|node_10_1555510543911|"Hi! Welcome to the assistant."|
|node_10_1555532190998|"Thanks for calling. Goodbye!"|

You can configure this mode with a pre-downloaded `skill_json_file` or can provide the Watson Assistant connection information.  `skill_json_file` takes precedence.

```
[Assistant]
#This file is suitable for use in [Synthesis] as `input_file`
extracted_skill_text_file=skill_text_output.csv

#Exported JSON from Watson Assistant
skill_json_file=myskill.json

#These are only used if `skill_json_file` is not set
apikey=xxxxxxxxx-xxxxx-xxxxx-xxxxxxxxxxx
service_url=https://....
use_bearer_token=False
workspace_id=xxxxxxxxx-xxxxx-xxxxx-xxxxxxxxxxx
```