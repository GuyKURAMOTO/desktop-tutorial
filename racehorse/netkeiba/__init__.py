import sys
import json
from datetime import datetime
from dateutil.rrule import rrule, MONTHLY
from netkeiba.netkeibaClients import NetKeibaClient

client = NetKeibaClient()

def output(raceDate:str, raceId:str, data:dict):
    fileName = f'netkeiba_{raceDate}_{raceId}.json'
    with open(fileName, mode='w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    pass


def monthsGen(fromYear:int, fromMonth:int, toYear:int, toMonth:int):
    dtstart = datetime(year=fromYear, month=fromMonth, day=1)
    dtend = datetime(year=toYear, month=toMonth, day=1)

    return rrule(freq=MONTHLY, dtstart=dtstart, until=dtend)

def collectDataBetween(fromYear:int, fromMonth:int, toYear:int, toMonth:int):
    """ 期間内のレース結果をレースごとにjsonファイルに出力する
    """
    for yearMonth in monthsGen(fromYear, fromMonth, toYear, toMonth):
        client.getAllRaceDataInMonth(yearMonth.year, yearMonth.month, output)
            

def main() -> None:
    fromYear = int(sys.argv[1])
    fromMonth = int(sys.argv[2])
    toYear = int(sys.argv[3])
    toMonth = int(sys.argv[4])
    collectDataBetween(fromYear, fromMonth, toYear, toMonth)



