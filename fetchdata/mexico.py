import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from fetchdata.dataclass import CovidData

fbase = Path('data/mexico/')

class CovidMexico(CovidData):

    def __init__(self):
        population = 126014024 
        super().__init__('Mexico', population)
        
    def _download_data(self, dtime):
        url = 'https://datos.covid-19.conacyt.mx/Downloads/Files/Casos_Diarios_Municipio_Confirmados_{}.csv'\
            .format(dtime.strftime('%Y%m%d'))
        fpath = fbase / Path(dtime.strftime('%Y_%m_%d') + '.csv')
        if not fpath.exists():
            print('Download new csv file')
            r = requests.get(url)
            if r.ok is True:
                with open(fpath, 'wb') as f:
                    f.write(r.content)
            else:
                raise Exception('Remote file not found')
        else:
            print('Local data already up to date.')

    def fetch_data(self):
        today = datetime.today()

        for i in range(0, 101):
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

        files = fbase.glob('2*.csv')
        date_created = lambda f: f.stat().st_ctime
        fpath = max(files, key=date_created)
        cpath = fbase / 'claves.csv'

        if fpath is not None and fpath.exists():
            data = pd.read_csv(fpath, parse_dates=True)
            # last date often not correct
            data = data.iloc[:, :-1]
            claves = pd.read_csv(cpath)

            # map to states
            claves.drop_duplicates(subset='Entidad Federativa', inplace=True)
            claves.set_index('Clave de la\nEntidad\nFederativa', inplace=True)
            claves = claves['Entidad Federativa']
            claves = claves.to_dict()
            
            cve = list(map(lambda x: int(str(x)[:-3]), data['cve_ent']))
            data['state'] = cve
            data.replace({'state': claves}, inplace=True)

            # columns to row index
            data = data.drop(['cve_ent', 'poblacion'], axis=1)
            data = data.melt(id_vars=['state', 'nombre'], var_name='date', value_name='cases')
            data = data.rename(columns={'nombre':'municipality'})
            data['date'] = pd.to_datetime(data['date'], dayfirst=True)

            self.data = data
            
        else:
            raise FileNotFoundError()