import yaml

def cfgLoader(filename):
    return yaml.load(open(filename), Loader=yaml.SafeLoader)