class ArticleInfo:

    def __init__(self, title, info, artphoto):
        self.__artid = ''
        self.__title = title
        self.__info = info
        self.__artphoto = artphoto

    def get_title(self):
        return self.__title

    def set_title(self, title):
        self.__title = title

    def get_info(self):
        return self.__info

    def set_info(self, info):
        self.__info = info

    def set_artphoto(self, artphoto):
        self.__artphoto = artphoto

    def get_artphoto(self):
        return self.__artphoto

    def set_artid(self, artid):
        self.__artid = artid

    def get_artid(self):
        return self.__artid
