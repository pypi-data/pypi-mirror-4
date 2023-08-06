from configobj import ConfigObj
import shutil
import os,sys
from spockpy.utils import confirm

def check_and_create_config(default_config_path,config_path):
    """
    :param default_config_path: path with a default ConfigObj type config
    :param config_path: path to install new config to
    :return: a ConfigObj instance configured with config_path
    """
    if not os.path.exists(config_path):
        if confirm('No configuration file exists, would you like to create a default one in {0}?'.format(config_path),default=True):
            if not os.path.exists(os.path.dirname(config_path)):
                os.mkdir(os.path.dirname(config_path))
            shutil.copyfile(default_config_path,config_path)
            print >> sys.stderr, "Done.  Before proceeding, please edit {0}".format(config_path)
        sys.exit(1)
        # Creating settings dictionary
    return ConfigObj(config_path)