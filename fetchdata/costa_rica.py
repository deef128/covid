import urllib.request
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from fetchdata.dataclass import CovidData

fbase = Path('data/costa_rica/')

class CovidCR(CovidData):

    def __init__(self):
        population = 5048000    
        super().__init__('Costa Rica', population)
        
    def _download_data(self, dtime):
        url = 'https://geovision.uned.ac.cr/oges/archivos_covid/{}/{}_CSV_POSITIVOS.csv'\
            .format(dtime.strftime('%Y_%m_%d'), dtime.strftime('%m_%d_%y'))
        fpath = fbase / Path(dtime.strftime('%m_%d_%y') + '.csv')

        if not fpath.exists():
            print('Download new csv file')
            urllib.request.urlretrieve(url, fpath)
        else:
            print('Local data already up to date.')

    def fetch_data(self):
        today = datetime.today()

        for i in range(1, 101):
            fdate = today - timedelta(days=i)
            try:
                self._download_data(fdate)
                break
            except Exception as e:
                print(e)
                print('Data for {} not found. Trying for the day before'.format(fdate.strftime('%m/%d/%Y')))

        self.read_data()

    def read_data(self):
        print('Read csv file')

        files = fbase.glob('*.csv')
        date_created = lambda f: f.stat().st_ctime
        fpath = max(files, key=date_created)

        if fpath is not None and fpath.exists():
            try:
                data = pd.read_csv(fpath, sep=';', encoding='latin1', parse_dates=True)
            except:
                data = pd.read_csv(fpath, sep=',', encoding='macintosh', parse_dates=True)

            # reverse cumsum values
            values = data.iloc[:, 4:].to_numpy()
            values_shifted = np.insert(values[:, :-1], 0, 0, 1)
            data.iloc[:, 4:] = values - values_shifted

            # columns to row index
            data = data.drop(['cod_provin', 'cod_canton'], axis=1)
            data = data.melt(id_vars=['provincia', 'canton'], var_name='date', value_name='cases')
            data = data.rename(columns={'provincia':'state', 'canton':'municipality'})
            data['date'] = pd.to_datetime(data['date'], dayfirst=True)

            self.data = data
            
        else:
            raise FileNotFoundError()