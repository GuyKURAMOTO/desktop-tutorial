import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup, SoupStrainer
import time
import lxml
import cchardet as chardet

class Scraper:
    """ 画面描画をせずにHTMLデータを抽出する
    """
    
    __headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

    def __init__(self):
        self.__session = requests.Session()
        self.__waitTime = 0

    def __wait(self):
        time.sleep(self.__waitTime)

    def getPageDataSoup(self, url, params={}, strainer:SoupStrainer = None):
        soup:BeautifulSoup = None
        while not soup:
            try:
                self.__wait()
                res = self.__session.get(url=url, params=params, headers=self.__headers)
                res.raise_for_status()
                soup = BeautifulSoup(res.content, 'lxml', parse_only=strainer)
                if res.elapsed.seconds >= 20:
                    self.__waitTime = 30
                else:
                    self.__waitTime = 0
            except Exception as ex:
                print(ex)
                self.__waitTime = 30
        return soup

class RenderScraper:
    """ 画面描画を行ってHTMLデータを抽出する
    """

    def __init__(self):
        self.__session = HTMLSession()
        self.__timeout = 8.0

    def getElements(self, url:str, params={}):
        html = None
        while not html:
            try:
                r = self.__session.get(url, params=params)
                r.html.render(timeout=self.__timeout)
                html = r.html
                self.__timeout = 8.0
            except Exception as ex:
                print(ex)
                self.__timeout += 5.0
        
        return html
