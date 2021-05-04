import requests
import json
import traceback
from pathlib import Path
from datetime import datetime
import pandas as pd
from fetchdata.dataclass import CovidData

url_date = 'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/ArcGIS/rest/services/RKI_COVID19/FeatureServer/0/query?where=&objectIds=&time=&resultType=none&outFields=Meldedatum&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=%5B%7B%22statisticType%22%3A%22max%22%2C%22onStatisticField%22%3A%22Meldedatum%22%2C%22outStatisticFieldName%22%3A%22Meldedatum%22%7D%5D&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=json&token='
url_delta = 'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/ArcGIS/rest/services/RKI_COVID19/FeatureServer/0/query?where=NeuerFall+IN%28-1%2C1%29&objectIds=&time=&resultType=none&outFields=AnzahlFall%2CLandkreis%2CBundesland&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=Landkreis%2CBundesland&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22AnzahlFall%22%2C%22outStatisticFieldName%22%3A%22AnzahlFall%22%7D%5D&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=json&token='
url_data1 = 'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/ArcGIS/rest/services/RKI_COVID19/FeatureServer/0/query?where=NeuerFall+%3D+0&objectIds=&time=&resultType=none&outFields=AnzahlFall%2C+Meldedatum&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=Meldedatum+DESC&groupByFieldsForStatistics=Meldedatum&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22AnzahlFall%22%2C%22outStatisticFieldName%22%3A%22AnzahlFallGestern%22%7D%5D&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=json&token='
ulr_data2 = 'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/ArcGIS/rest/services/RKI_COVID19/FeatureServer/0/query?where=NeuerFall+%3D+1&objectIds=&time=&resultType=none&outFields=AnzahlFall%2C+Meldedatum&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=Meldedatum+DESC&groupByFieldsForStatistics=Meldedatum&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22AnzahlFall%22%2C%22outStatisticFieldName%22%3A%22AnzahlFallHeute%22%7D%5D&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=json&token='
fbase = Path('data/germany/')

class CovidGermany(CovidData):

    def __init__(self):
        population = 83000000    
        super().__init__('Germany', population)

    def fetch_data(self):
        response = requests.get(url_date)
        date = pd.json_normalize(response.json(), 'features')
        last_date_remote = datetime.fromtimestamp(date['attributes.Meldedatum'] / 1000)
        fpath = fbase / Path(last_date_remote.strftime('%Y_%m_%d') + '.csv')

        if not fpath.exists():
            print('Download new data.')
            response = requests.get(url_delta)
            data = pd.json_normalize(response.json(), 'features')

            data.rename(columns={'attributes.AnzahlFall':'cases',
                                'attributes.Landkreis':'municipality',
                                'attributes.Bundesland':'state'},
                                inplace=True)

            data.to_csv(fpath)
        else:
            print('Local data up to date.')

        self.read_data()

    def read_data(self):
        print('Read local data.')
        data = pd.DataFrame(columns=['date', 'cases', 'municipality', 'state'])
        files = fbase.glob('*.csv')

        for f in files:
            if f is not None:
                df = pd.read_csv(f, index_col=0)
                last_date = datetime.fromisoformat(f.stem.replace('_', '-'))
                df['date'] = last_date
                data = data.append(df, ignore_index=True, verify_integrity=True)

        self.data = data