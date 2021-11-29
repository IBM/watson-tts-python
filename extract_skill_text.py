import json
import sys
import os
import re
import csv
from config import Config

from watson_objects import WatsonObjects

class SkillExtractor:

    def __init__(self, config):
        self.config = config

        input_json_file = config.getValue("Assistant", "skill_json_file")
        if input_json_file is not None:
            print(f"Reading skill from file {input_json_file}")
            self.tuples = self.getTextInFile(input_json_file)
        else:
            workspace_id = self.config.getValue("Assistant", "workspace_id")
            print(f"Reading skill from Watson Assistant API")
            WA = self.createWA()
            skill_json = WA.get_workspace(workspace_id=workspace_id, export=True, sort="stable").get_result()
            print(f"Read skill from Watson Assistant API with skill id {workspace_id}")
            self.tuples = self.getTextInSkill(skill_json)


    def report(self):
        output_filename = self.config.getValue("Assistant", "extracted_skill_text_file")
        keys = self.tuples[0].keys()

        with open(output_filename, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.tuples)
            print(f"Wrote skill extraction data to {output_filename}")

    def createWA(self):
        return WatsonObjects(self.config).createWA()

    def getTextInFile(self, file:str):
        with open(file, 'r') as jsonFile:
            data = json.load(jsonFile)
            return self.getTextInSkill(data)

    def getTextInSkill(self, data:json):
        tuples = []
        dialog_node_list = data['dialog_nodes']
        for dialog_node in dialog_node_list:
            node_id = dialog_node.get('dialog_node')

            # Disabled nodes are not visible on the Web UI but can still exist in the skill
            if dialog_node.get('disabled') == True or dialog_node.get('disabled') == 'true':
                continue

            if 'output' not in dialog_node:
                continue

            out_node = dialog_node.get('output')
            if 'generic' not in out_node:
                continue

            for generic in out_node.get('generic'):
                if 'values' in generic:
                    values = generic.get('values')
                    use_sequence = False
                    sequence_no = 1
                    if(len(values) > 1):
                        use_sequence = True
                    for value in values:
                        text = value.get('text', None)
                        if text is not None and len(text) > 0:
                            #ID is the dialog_node_id, unless that node has multiple responses, in which case we serialize them separately.
                            id = node_id
                            if use_sequence:
                                id = f"{node_id}_{sequence_no}"

                            #Remove newlines from text for easier CSV parsing later.
                            text = value.get('text')
                            text = "".join(l for l in text.splitlines() if l)

                            tuples.append({'id': id, 'text':text})
                        sequence_no += 1

        return tuples

if __name__ == '__main__':
    config_file = "config.ini"
    if len(sys.argv) > 1:
       config_file = sys.argv[1]
    else:
       print("Using default config filename: config.ini.")

    config          = Config(config_file)
    extractor       = SkillExtractor(config)

    extractor.report()
