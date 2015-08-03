import ConfigParser

class MapsEditorConfig(object):
    def __init__(self):
        config = ConfigParser.SafeConfigParser()
        config.read('../mapsClient.cfg')
        for op in config.defaults():
            setattr(self, op, config.get('DEFAULT', op))

def main():
  MapsEditorConfig()

if __name__ == '__main__':
  main()