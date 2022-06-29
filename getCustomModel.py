import sys
import json
from config import Config
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# python getCustomModel.py config.ini

config_file = "config.ini"
if len(sys.argv) > 1:
    config_file = sys.argv[1]
else:
    print("Using default config filename: config.ini.")

config      = Config(config_file)
apikey = config.getValue("TextToSpeech", "apikey")
url = config.getValue("TextToSpeech", "service_url")
customization_id = config.getValue("TextToSpeech", "customization_id")

authenticator = IAMAuthenticator(apikey)
text_to_speech = TextToSpeechV1(
    authenticator=authenticator
)

text_to_speech.set_service_url(url)

custom_model = text_to_speech.get_custom_model(customization_id).get_result()
print(json.dumps(custom_model, indent=2))