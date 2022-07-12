import sys
import json
from config import Config
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# python addWordsFromJSON.py config.ini CustomWords.json

config_file = "config.ini"
if len(sys.argv) > 1:
    config_file = sys.argv[1]
    json_file = sys.argv[2]
else:
    print("Using default config filename: config.ini.")
    json_file = sys.argv[1]

config      = Config(config_file)
apikey = config.getValue("TextToSpeech", "apikey")
url = config.getValue("TextToSpeech", "service_url")
customization_id = config.getValue("TextToSpeech", "customization_id")

authenticator = IAMAuthenticator(apikey)
text_to_speech = TextToSpeechV1(
    authenticator=authenticator
)

text_to_speech.set_service_url(url)

json_data = json.load(open(json_file))

text_to_speech.add_words(
    customization_id,
    words=json_data['words']
)