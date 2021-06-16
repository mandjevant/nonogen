from flask import Flask
import configparser
import sys
import os


class Config:
    conf = None

    @staticmethod
    def initiate_config() -> bool:
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
