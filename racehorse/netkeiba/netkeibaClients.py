from bs4 import SoupStrainer
from netkeiba.scraping import Scraper, RenderScraper
import urllib.parse
from bs4.element import ResultSet
from bs4 import BeautifulSoup

class NetKeibaClient:
    """ netkeibaに対する処理を行うクラス
    """
    def __init__(self):
        self.__webClient = NetKeibaWebClient()
        self.__dataDestructor = NetKeibaDestructor()
    
    def getAllRaceDataInMonth(self, year:int, month:int, outputF):
        """ ある月のすべてのレース結果を出力する
        """
        for raceDate in self.__webClient.getRaceDatesInMonth(year, month):
            for raceId in self.__webClient.getRaceIdsOnDateStr(raceDate):
                try:
                    for soup in self.__webClient.getRaceResultPageDataForId(raceId=raceId):
                        outputF(raceDate, raceId, self.__dataDestructor.getRaceDetails(soup=soup))
                except Exception as ex:
                    pass


class NetKeibaWebClient:
    """ netkeiba(web)に対する処理を行うクラス
    """
    __resultPage = 'https://race.netkeiba.com/race/result.html'
    __calendarPage = 'https://race.netkeiba.com/top/calendar.html'
    __raceListPage = 'https://race.netkeiba.com/top/race_list.html'

    def __init__(self):
        self.__scraper = Scraper()
        self.__renderScraper = RenderScraper()

    def getRaceDatesInMonth(self, year:int, month:int):
        """ ある月のレース開催日をすべて得る
        """
        strainer = SoupStrainer('td', {'class':'RaceCellBox'})
        yield from [cell.a.get('href')[-8:] for cell in self.__scraper.getPageDataSoup(url=self.__calendarPage, params={'year':year, 'month':month}, strainer=strainer).find_all('td') if cell.a]
    
    def getRaceIdsOnDateStr(self, dStr:str):
        """ ある日の開催レースのIDをすべて得る
        """
        yield from [self.__extractRaceId(link.attrs['href']) for link in self.__renderScraper.getElements(url=self.__raceListPage, params={'kaisai_date':dStr}).find("div#RaceTopRace li a:first-of-type")]
    
    def getRaceResultPageDataForId(self, raceId:str):
        """ レースIDを用いてレース結果を取得する
        """
        yield self.__scraper.getPageDataSoup(url=self.__resultPage, params={'race_id': raceId})

    def __extractRaceId(self, href:str):
        key = 'race_id'
        params = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
        return params[key][0] if key in params else None

class NetKeibaDestructor:
    """ netkeibaのレース結果ページを解析してデータ抽出するクラス
    """
    def __init__(self):
        pass

    def getRaceDetails(self, soup:BeautifulSoup):
        raceInfo = self.__destructReceInfos(soup=soup)
        raceResults = self.__destructRaceResults(soup=soup)
        return {**raceInfo, **raceResults}

    def __parseYen(self, str:str):
        return int(str.replace(',', '').replace('円', ''))

    def __parseYens(self, str:str):
        if not str:
            return None
        else:
            return [self.__parseYen(s) for s in str.split('円') if s]

    def __destructReceInfos(self, soup:BeautifulSoup):
        surfaceStr = soup.find('div', class_='RaceData01').find('span').text.strip()
        raceIcon = soup.find('div', class_='RaceName').find('span', class_='Icon_GradeType')
        grade = None
        if raceIcon:
            if 'Icon_GradeType1' in raceIcon['class']:
                grade = 'GI'
            elif 'Icon_GradeType2' in raceIcon['class']:
                grade = 'GII'
            elif 'Icon_GradeType3' in raceIcon['class']:
                grade = 'GIII'

        raceData02spans = soup.find('div', class_='RaceData02').find_all('span')
        return {
            'raceNum' : int(soup.find('span', class_='RaceNum').text[:-1]), 
            'raceName' : soup.find('div', class_='RaceName').text.strip(),
            'raceCource' : raceData02spans[1].text,
            '開催情報' : ''.join([span.text.strip() for span in raceData02spans[0:3]]), 
            '付加情報' : ';'.join([span.text.strip() for span in raceData02spans[3:]]), 
            'grade' : grade,
            'surface' : surfaceStr[0:1],
            'length' : int(surfaceStr[1:5]),
        }

    def __destructRaceResults(self, soup:BeautifulSoup):
        raceData01contents = soup.find('div', class_='RaceData01').contents
        details = [self.__destructRow(row) for row in soup.find_all('tr', class_='HorseList')]
        raceResults = {
            '天候' : raceData01contents[3][-1:],
            '馬場' : raceData01contents[6].text[5:],
            '結果詳細' : details,
            '出走馬' : [detail['nkHorseId'] for detail in details],
            '参加騎手' : [detail['nkJockeyId'] for detail in details],
            '順位なし' : [detail['nkHorseId'] for detail in details if not detail['rank']],
            '払い戻し' : self.__destructPayouts(soup),
        }

        cornersTable = soup.find('table', summary='コーナー通過順位')
        if cornersTable:
            raceResults['コーナー通過順'] = {row.find('th').text : row.find('td').text for row in cornersTable.find_all('tr')}
        return raceResults

    def __destructPayouts(self, soup:BeautifulSoup):
        payouts = {}

        for (pattern ,name) in [('Tansho', '単勝'), ('Fukusho', '複勝'), ('Wakuren', '枠連'), ('Umaren', '馬連'), ('Wide', 'ワイド'), ('Umatan', '馬単'), ('Fuku3', '3連複'), ('Tan3', '3連単')]:
            tr = soup.find('tr', class_= pattern)
            if tr:
                payouts[name] = self.__parseYens(tr.find('td', class_='Payout').text)

        return payouts

    def __destructRow(self, row:ResultSet):
        cells = row.find_all('td')
        weightStr = cells[14].text.strip()
        sexAge = cells[4].text.strip()

        return {
            'rank': self.__toInt(cells[0].text.strip()),
            'bracket' : self.__toInt(cells[1].text.strip()),
            'number': self.__toInt(cells[2].text.strip()),
            'horseName' : cells[3].text.strip(),
            'nkHorseId' : cells[3].span.a.get('href')[-10:],
            'sex' : sexAge[0:1],
            'age' : self.__toInt(sexAge[1:]),
            'handicap' : self.__toFloat(cells[5].text.strip()),
            'jockeyName': cells[6].text.strip(),
            'nkJockeyId': cells[6].find('a').get('href')[-6:-1],
            'time' : cells[7].text.strip(),
            'diff' : cells[8].text.strip(),
            'voteRank' : self.__toInt(cells[9].text.strip()),
            'odds' : self.__toFloat(cells[10].text.strip()),
            'final3F' : self.__toFloat(cells[11].text.strip()),
            'atCorners': cells[12].text.strip(),
            'weight' : self.__toInt(weightStr[0:3]),
            'weightDiff' : self.__toInt(weightStr[4:-1]),
        }

    def __toInt(self, str:str):
        try:
            return int(str)
        except:
            return None

    def __toFloat(self, str:str):
        try:
            return float(str)
        except:
            return None