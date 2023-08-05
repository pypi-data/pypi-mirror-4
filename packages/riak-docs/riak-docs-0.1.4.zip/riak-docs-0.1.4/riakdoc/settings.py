from riak import RiakHttpTransport


class Config(object):
    def __init__(self):
        self.settings = {
            'DATABASES': {
                'DEFAULT': {
                    'HOST': 'localhost',
                    'PORT': 8098,
                    'TRANSPORT': RiakHttpTransport
                },
            }
        }

    def get(self):
        """
        Return the settings for the Riakdoc app.

        @rtype dict
        """
        return self.settings

    def set(self, d):
        """
        Set the singleton dict Riakdoc uses for settings.

        @param d: Dict of settings
        @type d: dict
        """
        if not isinstance(d, dict) or not 'DATABASES' in d:
            raise ValueError('settings must be a dictionary with a DATABASES entry.')
        self.settings = d

config = Config()