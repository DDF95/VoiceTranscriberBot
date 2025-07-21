from configparser import ConfigParser
from pathlib import Path


main_directory = Path(__file__).absolute().parent

cfg = ConfigParser(interpolation=None)
cfg.read(f"{main_directory}/config.ini")

BOT_TOKEN = cfg.get("bot", "bot_token")
BOT_ADMINS = [int(admin) for admin in cfg["bot_admins"].values()]