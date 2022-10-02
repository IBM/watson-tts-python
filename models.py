import json
import os
import sys
import re
import csv
from config import Config

from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import IAMTokenManager
from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator

from argparse import ArgumentParser

import os.path
from os import path

#For information to user.  stdout is preserved for command status (could be redirected to file and parsed), stderr tracks ongoing progress
def eprint(msg:str):
    print(msg, file=sys.stderr)

class ModelTool:

    def __init__(self, config, ARGS):
        self.config = config
        self.TTS = self.createTTS()
        self.ARGS = ARGS

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

    def execute(self):
        # eprint(f"operation: {self.ARGS.operation}\n"
        #       +f"type: {self.ARGS.type}\n"
        #       +f"name: {self.ARGS.name}\n"
        #       +f"description: {self.ARGS.description}\n"
        #       +f"file: {self.ARGS.file}\n"
        # )

        # Registration of all the methods we support.
        # First key is type, second key is type
        # By genericizing the invocation, we can use common response handling below.
        type_handlers = {}
        type_handlers['custom_model'] = self.get_type_custom_model_handlers
        type_handlers['word'        ] = self.get_type_word_handlers

        if self.ARGS.type in type_handlers:
            type_handler = type_handlers[self.ARGS.type]()
            if self.ARGS.operation in type_handler:
                eprint(f"Executing operation: {self.ARGS.operation} on type: {self.ARGS.type}")
                response = type_handler[self.ARGS.operation]()
                if response is not None:
                    #Could do global handling of HTTP status code, etc
                    #eprint(response.get_status_code())
                    print(json.dumps(response.get_result(), indent=2))
                else:
                    eprint(f"Error executing operation: {self.ARGS.operation} on type: {self.ARGS.type}")    
            else:
                eprint(f"Unsupported operation: {self.ARGS.operation} on type: {self.ARGS.type}")
        else:
            eprint(f"Unsupported type: {self.ARGS.type}")

    # Most methods rely on the customization ID, we can abstract the config file from those methods
    def get_customization_id(self):
        return self.config.getValue("TextToSpeech", "customization_id")

    '''
    Custom model functions
    '''

    def get_type_custom_model_handlers(self):
        handlers = {}
        handlers['list'  ] = self.list_custom_models
        handlers['create'] = self.create_custom_model
        handlers['get'   ] = self.get_custom_model
        handlers['delete'] = self.delete_custom_model
        handlers['reset'] = self.reset_custom_model
       
        return handlers

    def list_custom_models(self):
        return self.TTS.list_custom_models()

    def get_custom_model(self):
        return self.TTS.get_custom_model(self.get_customization_id())

    def create_custom_model(self):
        model_name = self.ARGS.name

        if self.ARGS.name is None:
            eprint("ERROR: Must pass a 'name' for the model")
            return None

        response = self.TTS.create_custom_model(model_name, language=self.ARGS.language, description=self.ARGS.description)

        if response is not None and 'customization_id' in response.get_result():
            #Fetch new customization id, to store it back into a new config file
            customization_id = response.get_result()['customization_id']
            self.config.setValue("TextToSpeech", "customization_id", customization_id)
            #Sanitization could be improved a bit more, see https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
            sanitized_model_name = re.sub('[ /.]','_', model_name)
            new_config_file_name = f"config.ini.{sanitized_model_name}"
            eprint(f"Writing new configuration to {new_config_file_name} which contains customization id {customization_id}")
            self.config.writeFile(new_config_file_name)

        return response

    def delete_custom_model(self):
        return self.TTS.delete_custom_model(self.get_customization_id())

    def reset_custom_model(self):
        # deleting all the words will essentially "reset" the model

        # get list of words
        word_list = []
        words_raw = self.TTS.list_words(self.get_customization_id()).get_result()
        for element in words_raw['words']:
            word_list.append(element['word'])
        eprint(f"existing word list: {word_list}")

        # loop through deleting the words
        for word in word_list:
            self.TTS.delete_word(self.get_customization_id(), word)
            eprint(f"deleted word: {word}")

        # check
        words_raw = self.TTS.list_words(self.get_customization_id())
        eprint(f"new words list: {words_raw.get_result()}")
        return words_raw

    '''
    Custom word functions
    '''

    def get_type_word_handlers(self):
        handlers = {}
        handlers['list'  ] = self.list_words
        handlers['get'   ] = self.get_word
        handlers['create'] = self.add_words
        handlers['delete'] = self.delete_word

        return handlers
    
    def list_words(self):
        return self.TTS.list_words(self.get_customization_id())

    def get_word(self):
        if self.ARGS.name is None:
            eprint(f"ERROR: A word 'name' is required.")
            return None

        return self.TTS.get_word(self.get_customization_id(), self.ARGS.name)

    def add_words(self):
        if self.ARGS.file is None:
            eprint(f"ERROR: A word 'file' is required.\nThe file format is documented in https://cloud.ibm.com/docs/text-to-speech?topic=text-to-speech-customWords#cuWordsAdd")
            return None

        with open(self.ARGS.file, 'rb') as word_contents_str:
            json_data = json.load(word_contents_str)
            words=json_data['words']
            return self.TTS.add_words(self.get_customization_id(), words)

    def delete_word(self):
        if self.ARGS.name is None:
            eprint(f"ERROR: A word 'name' is required.")
            return None

        return self.TTS.delete_word(self.get_customization_id(), self.ARGS.name)

def create_parser():
    parser = ArgumentParser(description='Run IBM Speech To Text model-related commands')
    parser.add_argument('-c', '--config_file', type=str, required=False, default="config.ini", help='Configuration file including connection details')
    parser.add_argument('-o', '--operation', type=str, required=True, choices=["list","get","create","delete","reset"], help="operation to perform")
    parser.add_argument('-t', '--type', type=str, required=True, choices=["custom_model","word"], help="type the operation works on")
    parser.add_argument('-n', '--name', type=str, required=False, help="name the operation works on, for instance 'MyModel' or 'word1'.")
    parser.add_argument('-d', '--description', type=str, required=False, help="description of the object being created; used only in create")
    parser.add_argument('-f', '--file', type=str, required=False, help="path to a file supporting the operation, for instance a word file")
    parser.add_argument('-l', '--language', type=str, required=False, help="language the operation works on, for instance 'en-US'")
    return parser

def main(ARGS):
    config     = Config(ARGS.config_file)
    model_tool = ModelTool(config, ARGS)
    
    model_tool.execute()

if __name__ == '__main__':
    ARGS = create_parser().parse_args()
    main(ARGS)