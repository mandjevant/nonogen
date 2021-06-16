from flask import Flask
import configparser
import sys
import os


class Config:
    """
    Class to check conf.ini for existence
     and load it in
    """
    conf = None

    @staticmethod
    def initiate_config() -> bool:
        """
        Initiate configuration by
         checking if conf.ini exists
         loading in conf.ini
        :return: success | bool
        """
        try:
            Config.conf = configparser.ConfigParser()
            if os.path.exists(os.getcwd() + '\\conf.ini'):
                Config.conf.read(os.getcwd() + '\\conf.ini')
            else:
                print("Config file, conf.ini, was not found.")
                return False

            return True

        except Exception as e:
            print("Could not initiate conf." + str(e))
            return False


if not Config.initiate_config():
    sys.exit()

app = Flask(__name__)
app.secret_key = Config.conf.get('CONSTANTS', 'SECRET_KEY')

from app import routes, errors

app.run()
