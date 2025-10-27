import configparser

class Config:
    def __init__(self, config_file:str):
        # (interpolation=None) so that '%' is not treated like an environment variable
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read(config_file)

    def getBoolean(self, section, key):
        return self.getValue(section, key) == "True"

    def getValue(self, section, key, default_value=None):
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

    def writeFile(self, file:str):
        """
        Write the current configuration to a file.

        Args:
            file (str): Path to the file where the configuration will be written.
        """
        with open(file, 'w') as configfile:
            self.config.write(configfile)
