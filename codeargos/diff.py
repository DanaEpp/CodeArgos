class Diff:
    def __init__(self, id, url, content, date):
            self.__diff_id = id
            self.__diff_url = url
            self.__diff_content = content
            self.__diff_date = date

    @property
    def url(self):
        return self.__diff_url

    @property
    def id(self):
        return self.__diff_id

    @property
    def content(self):
        return self.__diff_content

    @property
    def date(self):
        return self.__diff_date

    def __repr__(self):
        return "{ id:\"{0}\", url:\"{1}\", content: \"{2}\", date: \"{3}\" }".format(self.__diff_id, self.__diff_url, self.__diff_content, self.__diff_date)
    
    def __str__(self):
        return "Diff('{0}', '{1}', '{2}', '{3}')".format(self.__diff_id, self.__diff_url, self.__diff_content, self.__diff_date) 
