
class Browsers(object):
    __instance = None
    __browsers = {}

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def set_browser(self, id, browser):
        self.__browsers[id] = browser

    def get_browser(self, id):
        return self.__browsers[id]