import configparser

class Config:
    config = None

    def __init__(self, config_file:str):
        # (interpolation=None) so that '%' is not treated like an environment variable
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read(config_file)

    def getBoolean(self, section, key):
        return self.getValue(section, key) == "True"

    def getValue(self, section, key):
        value = None
        if section in self.config:
           list = self.config[section]
           value = list.get(key, None)
        return value

    def getKeys(self, section):
        if section in self.config:
            return [key for key,value in self.config.items(section)]
        return None

    def setValue(self, section:str, key:str, value:str):
        if section in self.config:
           self.config.set(section, key, value)

    def writeFile(self, file_name:str):
        with open(file_name, 'w') as configfile:
            self.config.write(configfile)

        #value = None
        if section in self.config:
           self.config.set(section, key, value)
        return

    def writeFile(self, file:str):
        #value = None
        with open(file, 'w') as configfile:
            self.config.write(configfile)
        return
