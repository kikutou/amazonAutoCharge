import time


class Browsers(object):
    __instance = None
    __browsers = {}

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def set_browser(self, id, browser):

        # for __id, __browser in self.__browsers.items():
        #     if __browser['browser'] is None:
        #         self.__browsers.pop(__id)
        #     elif time.time() - __browser['time'] > 900:
        #         __browser['browser'].quit()
        #         self.__browsers.pop(__id)

        self.__browsers[id] = {'browser': browser, 'time': time.time()}

    def get_browser(self, id):
        return self.__browsers[id]['browser']


# class Xvfb(object):
#     __instance = None
#     __xvfb = {}
#
#     def __new__(cls, *args, **kwargs):
#         if cls.__instance is None:
#             cls.__instance = object.__new__(cls)
#         return cls.__instance
#
#     def set_xvfb(self, id, xvfb):
#         self.__xvfb[id] = xvfb
#
#     def get_xvfb(self, id):
#         return self.__xvfb[id]