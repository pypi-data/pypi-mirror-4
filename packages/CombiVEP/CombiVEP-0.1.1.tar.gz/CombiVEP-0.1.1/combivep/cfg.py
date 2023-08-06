import os
import combivep.settings as combivep_settings


class Configure(object):
    """ CombiVEP base class """


    def __init__(self):
        self.config_file = combivep_settings.COMBIVEP_CONFIGURATION_FILE
        self.config_values  = {}
        self.config_values[combivep_settings.LATEST_UCSC_DATABASE_VERSION] = '0'
        self.config_values[combivep_settings.LATEST_UCSC_FILE_NAME]        = ''
        self.config_values[combivep_settings.LATEST_LJB_DATABASE_VERSION]  = '0.1'
        self.config_values[combivep_settings.LATEST_LJB_FILE_PREFIX]       = ''

    def load_config(self):
        f = open(self.config_file, 'r')
        for line in f:
            rec = line.strip().split('=')
            if rec[0] == combivep_settings.LATEST_UCSC_DATABASE_VERSION:
                self.config_values[combivep_settings.LATEST_UCSC_DATABASE_VERSION] = rec[1]
            elif rec[0] == combivep_settings.LATEST_UCSC_FILE_NAME:
                self.config_values[combivep_settings.LATEST_UCSC_FILE_NAME] = rec[1]
            elif rec[0] == combivep_settings.LATEST_LJB_DATABASE_VERSION:
                self.config_values[combivep_settings.LATEST_LJB_DATABASE_VERSION] = rec[1]
            elif rec[0] == combivep_settings.LATEST_LJB_FILE_PREFIX:
                self.config_values[combivep_settings.LATEST_LJB_FILE_PREFIX] = rec[1]
        f.close()
        return self.config_values

    def __save(self):
        f = open(self.config_file, 'w')
        f.write("%s=%s\n" % (combivep_settings.LATEST_UCSC_DATABASE_VERSION, self.config_values[combivep_settings.LATEST_UCSC_DATABASE_VERSION]))
        f.write("%s=%s\n" % (combivep_settings.LATEST_UCSC_FILE_NAME,        self.config_values[combivep_settings.LATEST_UCSC_FILE_NAME]))
        f.write("%s=%s\n" % (combivep_settings.LATEST_LJB_DATABASE_VERSION,  self.config_values[combivep_settings.LATEST_LJB_DATABASE_VERSION]))
        f.write("%s=%s\n" % (combivep_settings.LATEST_LJB_FILE_PREFIX,       self.config_values[combivep_settings.LATEST_LJB_FILE_PREFIX]))
        f.close()

    def write_ljb_config(self, version, file_prefix):
        if os.path.exists(self.config_file):
            self.load_config()
        self.config_values[combivep_settings.LATEST_LJB_DATABASE_VERSION] = version
        self.config_values[combivep_settings.LATEST_LJB_FILE_PREFIX]      = file_prefix
        self.__save()

    def write_ucsc_config(self, version, file_name):
        self.load_config()
        self.config_values[combivep_settings.LATEST_UCSC_DATABASE_VERSION] = version
        self.config_values[combivep_settings.LATEST_UCSC_FILE_NAME]        = file_name
        self.__save()






