# TTS-Python-Tool
TTS Python tools to assist customers in experimentation and configuration

Some sample files are available under the "template-samples" sub-folder.
There is an evaluation template spreadsheet to help document feedback from reviewers

## Installation
Requires Python 3.x installation.

All of the watson-tts-python dependencies are installed at once with `pip`:

```
pip install -r requirements.txt
```

**Note:**  If receiving an SSL Certificate error (CERTIFICATE_VERIFY_FAILED) when running the python scripts, try the following commands to tell python to use the system certificate store.

**_Windows_**
```
pip install --trusted-host pypi.org --trustedhost files.python.org python-certifi-win32
```

**_MacOS_**

Open a terminal and change to the location of your python installation to execute `Install Certificates.command`, for example:
```
cd /Applications/Python 3.6
./Install Certificates.command
```

## synthesize.py
Takes an input CSV file with IDs and text, synthesizes each text into an audio file as specified by the ID.  Global configuration is updated in `config.ini` file.

Example input file:

|id|text|  
|--|--|
|quickbrown|"The quick brown fox"|
|lazydog|"jumped over the lazy dog"|

Will produce output files quickbrown.wav and lazydog.wav

Use `config.ini` to specify information about your text to speech service and model in `[TextToSpeech]` section.  Specify output details into `[Synthesis]` section.

`voice` can be a single voice or a comma-separated list of voices. `voice_selection_mode` can be set to `random` or `all` (default).
Sample wav file output for input file with three texts with config settings: `voice=en-US_MichaelV3Voice,en-US_AllisonV3Voice,en-US_EmilyV3Voice` and `voice_selection_mode=random` which gives one file for each text using a random voice:
```
id1-en-US_AllisonV3Voice.wav
id2-en-US_EmilyV3Voice.wav
id3-en-US_MichaelV3Voice.wav
```
Changing `voice_selection_mode=all` gives multiple files for each text using each voice:
```
id1-en-US_MichaelV3Voice.wav
id1-en-US_AllisonV3Voice.wav
id1-en-US_EmilyV3Voice.wav
id2-en-US_MichaelV3Voice.wav
id2-en-US_AllisonV3Voice.wav
id2-en-US_EmilyV3Voice.wav
id3-en-US_MichaelV3Voice.wav
id3-en-US_AllisonV3Voice.wav
id3-en-US_EmilyV3Voice.wav
```

If `reference_transcriptions_file` is provided, the synthesis builds a reference file for use in [watson-stt-wer-python](https://github.com/IBM/watson-stt-wer-python).

```
[TextToSpeech]
apikey=xxxxxxxxx-xxxxx-xxxxx-xxxxxxxxxxx
service_url=https://....
use_bearer_token=False
voice=en-US_MichaelV3Voice
;customization_id=xxxxxxxxx-xxxxx-xxxxx-xxxxxxxxxxx

[Synthesis]
output_dir=synthesis
output_file_type=mp3
input_file = inputfile_to_synthesize.csv
overwrite = True
#Optional
reference_transcriptions_file=reference_transcriptions.csv
```

## pronounce.py
Takes an input file with one word/word phrase per line and generates pronunciations.  Global configuration is updated in `config.ini` file. Note, If `voice` is set to multiple voices, only the first one will be used. The output file from this process is suitable for passing as an input file to `synthesize.py`.

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
Takes a Watson Assistant skill and extracts types of text requested in the configuration file.
There are three options:
* all of the output text "spoken" by the assistant (`extract_dialog`)
* all of the intent training text (`extract_intents`)
* all of the entity training text (`extract_entities`)

The output file from this process is suitable for passing as an input file to `synthesize.py`.  The dialog text is useful for inspecting what Watson Assistant will sound like, the intent/entity text is useful for bootstrapping test data for [watson-stt-wer-python](https://github.com/IBM/watson-stt-wer-python).

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

#Which data to extrat
extract_dialog = True
extract_intents = False
extract_entities = False
```

## Model training
The `models.py` script has wrappers for many model-related tasks including creating and deleting models and adding and deleting words.

### Setup
Update the parameters in your `config.ini` file.

Required configuration parameters:
* apikey - API key for your Speech to Text instance
* service_url - Reference URL for your Speech to Text instance

## Execution
For general help, execute:
```
python models.py
```

The script requires a type (one of custom_model or word) and an operation (one of list,get,create,delete,reset)
The script optionally takes a config file as an argument with `-c config_file_name_goes_here`, otherwise using a default file of `config.ini` which contains the connection details for your speech to text instance.
Depending on the specified operation, the script also accepts a name, description, and file for an associated resource.  For instance, new custom models should have a name and description.

## Examples

List all custom models:
```
python models.py -o list -t custom_model
```

Create a custom model:
```
python models.py -o create -t custom_model -n "model1" -d "my first model -l "en-US"
```

Reset a custom model (delete all the words from the model):
```
python models.py -o reset -t custom_model
```

Add words from a JSON file:
```
python models.py -o create -t word -f CustomWords.json
```

Note some parameter combinations are not possible.  The operations supported all wrap the SDK methods documented at https://cloud.ibm.com/apidocs/text-to-speech.


## Utility Scripts
### util_add_acronym_pronounce_to_json.py
Process a csv of acronyms and translate them, e.g. IBM -> I B M,  
Then add the tranlations to an existing custom words TTS json file.  
Sample script execution: `python util_add_acronym_pronounce_to_json.py test_terms.csv CustomWords.json`

### util_add_word_phonetic_to_json.py
Parse phonetic pronunciations from the csv output file from `pronounce.py`  
Then add the tranlations to an existing custom words TTS json file.  
Sample script execution: `python util_add_word_phonetic_to_json.py tts_pronounce.csv CustomWords.json`

### util_create_synthesis_input_file.py
Create a synthesis input csv file from a csv file of words to synthesize.
Sample script execution: `python util_createSynthesisInputFile.py words.csv inputfile_to_synthesize.csv `

### util_problematic_word_extraction.py
Extract potentially problematic words for TTS from a CSV using a spell checker. Then divide the words up into separate files based on punctuation found in the words.  
Sample script execution: `python util_problematic_word_extraction.py messages.csv`
