from config import Config

from ibm_watson import AssistantV1
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import IAMTokenManager
from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator

class WatsonObjects:

    def __init__(self, config):
        self.config = config

    def createTTS(self):
        apikey            = self.config.getValue("TextToSpeech", "apikey")
        url               = self.config.getValue("TextToSpeech", "service_url")
        use_bearer_token  = self.config.getBoolean("TextToSpeech", "use_bearer_token")

        if use_bearer_token != True:
            authenticator = IAMAuthenticator(apikey)
        else:
            iam_token_manager = IAMTokenManager(apikey=apikey)
            bearerToken       = iam_token_manager.get_token()
            authenticator     = BearerTokenAuthenticator(bearerToken)

        text_to_speech = TextToSpeechV1(authenticator=authenticator)

        text_to_speech.set_service_url(url)
        text_to_speech.set_default_headers({'x-watson-learning-opt-out': "true"})
        return text_to_speech

    def createWA(self):
        apikey            = self.config.getValue("Assistant", "apikey")
        url               = self.config.getValue("Assistant", "service_url")
        use_bearer_token  = self.config.getBoolean("Assistant", "use_bearer_token")

        if use_bearer_token != True:
            authenticator = IAMAuthenticator(apikey)
        else:
            iam_token_manager = IAMTokenManager(apikey=apikey)
            bearerToken       = iam_token_manager.get_token()
            authenticator     = BearerTokenAuthenticator(bearerToken)

        assistant = AssistantV1(authenticator=authenticator, version="2021-11-05")

        assistant.set_service_url(url)
        assistant.set_default_headers({'x-watson-learning-opt-out': "true"})
        return assistant