import urllib2


class BaseDataSource(object):
    name = 'Unknown'

    def read_data(self):
        pass


class OpenedFileDataSource(object):
    def __init__(self, name, ofile):
        self._file = ofile
        self.name = name


    def read_data(self):
        return self._file.read()


class URLDataSource(object):
    def __init__(self, url, user_agent=None, proxy=True):
        self._url = url
        self.name = url
        self._user_agent = user_agent
        self._proxy = proxy


    def _make_request(self):
        request = urllib2.Request(self._url)
        if self._user_agent is not None:
            request.add_header('User-Agent', self._user_agent)

        return request


    def _setup_urllib(self):
        if self._proxy:
            proxy_opener = urllib2.ProxyHandler()
        else:
            proxy_opener = urllib2.ProxyHandler({})
        urllib2.install_opener(urllib2.build_opener(proxy_opener))
        

    def read_data(self):
        self._setup_urllib()
        request = self._make_request()
        data = urllib2.urlopen(request).read()

        return data


class FileDataSource(object):
    def __init__(self, fname):
        self._fname = fname
        self.name = fname


    def read_data(self):
        with open(self._fname, 'r') as f:
            return f.read()


