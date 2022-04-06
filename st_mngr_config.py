import configparser
import os

ini_filename = "st_mngr_settings.ini"

def create_config(filename):
    """Create a config file"""
    config = configparser.ConfigParser()

    config.add_section("URLs")
    config.set("URLs", "twitter", "https://www.twitter.com")
    config.set("URLs", "linkedin", "https://www.linkedin.com")
    config.set("URLs", "gmail", "https://www.gmail.com")
    config.set("URLs", "techcrunch", "https://www.techcrunch.com")

    config.add_section("S_Time")
    config.set("Session_Time", "twitter", "5")
    config.set("Session_Time", "linkedin", "8")
    config.set("Session_Time", "gmail", "8")
    config.set("Session_Time", "techcrunch", "8")

    with open(filename, "w") as config_file:
        config.write(config_file)


def get_config(filename):
    """Return the config obj"""
    if not os.path.exists(filename):
        create_config(filename)

    config = configparser.ConfigParser()
    config.read(filename)
    return config
    

def get_setting(filename, section, setting):
    """Print out a setting"""
    config = get_config(path)
    value = config.get(section, setting)
    msg = f"{section} {setting} is {value}"
    print(msg)
    return value


if __name__ == "__main__":
    print('Navigate to the st_mngr script folder.')
    print(f'Then check whether {ini_filename} exists.')
    print('Call create_config() to create one if not.')
