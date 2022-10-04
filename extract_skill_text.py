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
            tuples = []
            if self.config.getBoolean("Assistant", "extract_dialog") or "extract_dialog" not in self.config.getKeys("Assistant"):
                tuples.extend(self.getOutputTextInSkill(data))
            
            if self.config.getBoolean("Assistant", "extract_intents"):
                tuples.extend(self.getIntentTextInSkill(data))

            if self.config.getBoolean("Assistant", "extract_entities"):
                tuples.extend(self.getEntityTextInSkill(data))

            return tuples

    def getIntentTextInSkill(self, raw_data:json):
        interesting_text = []
        data = raw_data
        #Dialog skill has intents at root, Action skill puts them under 'workspace'
        if 'workspace' in data:
            data = data['workspace']

        if 'intents' in data:
            for node in data['intents']:
                if 'examples' in node:
                    for example in node['examples']:
                        interesting_text.append(example['text'])

        tuples = []
        for text in interesting_text:
            id = "".join([x if x.isalnum() else "_" for x in text])
            tuples.append({'id': id, 'text':text})
        return tuples

    def getEntityTextInSkill(self, raw_data:json):
        interesting_text = []
        data = raw_data
        #Dialog skill has entities at root, Action skill puts them under 'workspace'
        if 'workspace' in data:
            data = data['workspace']

        #All entity examples and synonyms
        if 'entities' in data:
            for node in data['entities']:
                if 'values' in node:
                    for v in node['values']:
                        if 'value' in v:
                            interesting_text.append(v['value'])
                        if 'synonyms' in v:
                            for synonym in v['synonyms']:
                                interesting_text.append(synonym)
        
        tuples = []
        for text in interesting_text:
            id = "".join([x if x.isalnum() else "_" for x in text])
            tuples.append({'id': id, 'text':text})
        return tuples

    def getOutputTextInSkill(self, data:json):
        #Dialog skill
        if 'dialog_nodes' in data:
            return self.getOutputTextInDialogSkill(data)
        elif 'workspace' in data:
            return self.getOutputTextInActionSkill(data)
        else:
            print('Unexpected format found in Watson Assistant skill.')
            return None

    def getOutputTextInDialogSkill(self, data:json):
        tuples = []
        dialog_node_list = data['dialog_nodes']
        for dialog_node in dialog_node_list:
            node_id = dialog_node.get('dialog_node')
            tuples += self.getTextFromNode(dialog_node, node_id)

        return tuples

    def getOutputTextInActionSkill(self, data:json):
        tuples = []
        action_node_list = data['workspace']['actions']
        for action_node in action_node_list:
            for step_node in action_node['steps']:
                node_id = action_node['action'] + "_" + step_node['step']
                tuples += self.getTextFromNode(step_node, node_id)
                for handler_node in step_node['handlers']:
                    handler_node_id = node_id + "_" + handler_node['title']
                    tuples += self.getTextFromNode(handler_node, handler_node_id)

        return tuples

    def getTextFromNode(self, dialog_node, node_id):
        tuples = []
        # Disabled nodes are not visible on the Web UI but can still exist in the skill
        if dialog_node.get('disabled') == True or dialog_node.get('disabled') == 'true':
            return tuples

        if 'output' not in dialog_node:
            return tuples

        out_node = dialog_node.get('output')
        if 'generic' not in out_node:
            return tuples

        for generic in out_node.get('generic'):
            if 'values' in generic:
                values = generic.get('values')
                use_sequence = False
                sequence_no = 1
                if(len(values) > 1):
                    use_sequence = True
                for value in values:
                    #Dialog main format, sometimes used by actions
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

                    #Action-specific format
                    text_expr_node = value.get('text_expression', None)
                    if text_expr_node is not None and 'concat' in text_expr_node:
                        #text_expression has concat array of {'scalar':text_value}
                        concat_sequence_no = 1
                        for concat_node in text_expr_node['concat']:
                            id = f"{node_id}_{sequence_no}"
                            text = concat_node.get('scalar')
                            text = "".join(l for l in text.splitlines() if l)

                            tuples.append({'id': id, 'text':text})
                            concat_sequence_no += 1

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
