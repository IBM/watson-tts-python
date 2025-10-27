from config import Config

from ibm_watson import AssistantV1
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import IAMTokenManager
from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator

class WatsonObjects:
    """
    A class for creating Watson service objects with proper authentication.
    """

    def __init__(self, config):
        """
        Initialize with configuration.

        Args:
            config (Config): Configuration object containing service settings
        """
        self.config = config

    def _create_authenticator(self, service_name):
        """
        Create an authenticator for Watson services based on configuration.

        Args:
            service_name (str): Name of the service section in config (e.g., "TextToSpeech")

        Returns:
            Authenticator: Configured authenticator for the service
        """
        apikey = self.config.getValue(service_name, "apikey")
        bearer_token = self.config.getValue(service_name, "bearer_token", None)
        use_bearer_token = self.config.getBoolean(service_name, "use_bearer_token")
        
        if bearer_token is not None:
            return BearerTokenAuthenticator(bearer_token)
        elif use_bearer_token is not True:
            return IAMAuthenticator(apikey)
        else:
            iam_token_manager = IAMTokenManager(apikey=apikey)
            bearer_token = iam_token_manager.get_token()
            return BearerTokenAuthenticator(bearer_token)

    def createTTS(self):
        """
        Create and configure a Watson Text-to-Speech service instance.

        Returns:
            TextToSpeechV1: Configured Text-to-Speech service
        """
        service_name = "TextToSpeech"
        authenticator = self._create_authenticator(service_name)
        url = self.config.getValue(service_name, "service_url")
        
        text_to_speech = TextToSpeechV1(authenticator=authenticator)
        text_to_speech.set_service_url(url)
        text_to_speech.set_default_headers({'x-watson-learning-opt-out': "true"})
        return text_to_speech

    def createWA(self):
        """
        Create and configure a Watson Assistant service instance.

        Returns:
            AssistantV1: Configured Assistant service
        """
        service_name = "Assistant"
        authenticator = self._create_authenticator(service_name)
        url = self.config.getValue(service_name, "service_url")
        
        assistant = AssistantV1(authenticator=authenticator, version="2021-11-05")
        assistant.set_service_url(url)
        assistant.set_default_headers({'x-watson-learning-opt-out': "true"})
        return assistant
