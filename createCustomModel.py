import sys
import json
from config import Config
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# python createCustomModel.py config.ini "script test" en-US "test the script for creating a new model"

config_file = "config.ini"
if len(sys.argv) > 1:
    config_file = sys.argv[1]
    model_name = sys.argv[2]
    model_language = sys.argv[3]
    model_description = sys.argv[4]
else:
    print("Using default config filename: config.ini.")
    model_name = sys.argv[1]
    model_language = sys.argv[2]
    model_description = sys.argv[3]

config      = Config(config_file)
apikey = config.getValue("TextToSpeech", "apikey")
url = config.getValue("TextToSpeech", "service_url")

authenticator = IAMAuthenticator(apikey)
text_to_speech = TextToSpeechV1(
    authenticator=authenticator
)

text_to_speech.set_service_url(url)

custom_model = text_to_speech.create_custom_model(
    name=model_name,
    language=model_language,
    description=model_description
).get_result()
print(json.dumps(custom_model, indent=2))