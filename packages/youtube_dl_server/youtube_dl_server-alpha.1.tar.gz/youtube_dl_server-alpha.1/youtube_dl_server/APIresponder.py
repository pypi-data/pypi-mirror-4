import webapp2

#Format modules
import json
import yaml

import youtube_dl

class NoneFile(object):
    '''
    A file-like object that does nothing
    '''
    def write(self,*args,**kaargs):
        pass
    def flush(self,*args,**kaargs):
        pass

class SimpleFileDownloader(youtube_dl.FileDownloader):
    def __init__(self,*args,**kargs):
        super(SimpleFileDownloader,self).__init__(*args,**kargs)
        self._screen_file=NoneFile()
        self.videos_info=[]
        self.ie=None
    def _addVideos(self,vids):
        for vid in vids:
            self.videos_info.append(vid)
    def _addIE(self,ie):
        if not self.ie:
            self.ie = ie
    def _extract(self,url):
        ies = youtube_dl.gen_extractors()
        for ie in ies:
            ie.set_downloader(self)
            if ie.suitable(url):
                vids = ie.extract(url)
                return vids,ie
    def download(self, url_list):
        '''Hack, some IE call it for downloading video urls'''
        for url in url_list:
            vids,ie = self._extract(url)
            if vids:
                self._addVideos(vids)
                self._addIE(ie)

    def extract(self,url):
        videos_info,ie = self._extract(url)
        if videos_info:
            self._addVideos(videos_info)
            self._addIE(ie)
        return self.videos_info,self.ie

def videos(url):
    '''
    Get a list with a dict for every video founded
    '''
    fd = SimpleFileDownloader({'outtmpl':'%(title)s'})
    return fd.extract(url)

class Api(webapp2.RequestHandler):
    @property
    def out_format(self):
        """The format the response must use"""
        return self.request.get("format","json")
    @property
    def content_type(self):
        """Content type for the response"""
        if self.out_format == "json":
            return "application/json"
        if self.out_format == "yaml":
            return "application/yaml"
    def dumps(self,dic):
        """Dump a dic to a string using the format specified in the reques"""
        if self.out_format == "json":
            return json.dumps(dic)
        elif self.out_format == "yaml":
            return yaml.safe_dump(dic)
    def get(self):
        #Allow javascript get requests from other domains
        self.response.headers["Access-Control-Allow-Origin"] = "*"
        self.response.headers["Content-Type"] = self.content_type
        
        errors = (youtube_dl.DownloadError, youtube_dl.ExtractorError)
        try:
            url = self.request.get("url")
            vids,ie = videos(url)
            dic = {'youtube-dl.version':youtube_dl.__version__,
                   'url':url,
                   'ie':ie.IE_NAME,
                   'videos':vids}
        except errors as err:
            dic = {'error': str(err)}
        response = self.dumps(dic)
        self.response.out.write(response)
