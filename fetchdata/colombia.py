import pandas as pd
from sodapy import Socrata
from pathlib import Path
from fetchdata.dataclass import CovidData

fpath = Path('data/colombia/data.csv')

class CovidColombia(CovidData):

    def __init__(self):
        population = 54340000    
        super().__init__('Colombia', population)

    def fetch_data(self):
        # Unauthenticated client only works with public data sets. Note 'None'
        # in place of application token, and no username or password:
        client = Socrata("www.datos.gov.co", None)

        # Example authenticated client (needed for non-public datasets):
        # client = Socrata(www.datos.gov.co,
        #                  MyAppToken,
        #                  userame="user@example.com",
        #                  password="AFakePassword")

        fpath = Path('data/colombia/data.csv')
        select_str = 'fecha_reporte_web,departamento_nom,ciudad_municipio_nom,COUNT(id_de_caso)'
        group_str = 'fecha_reporte_web,departamento_nom,ciudad_municipio_nom'
        limit = 9999999999
        
        print('Download remote data.')
        results = client.get("gt2j-8ykr", select=select_str, group=group_str, limit=limit)
        df = pd.DataFrame.from_records(results)
        df['fecha_reporte_web'] = pd.to_datetime(df['fecha_reporte_web'], dayfirst=True)
        last_date_remote = df['fecha_reporte_web'].max()

        try:
            self.read_data()
            store_new = last_date_remote > self.last_date.dt
        except:
            store_new = True

        if store_new:
            print('Store new data.')
            df.to_csv(fpath)
            self.read_data()
        else:
            print('Local data is already up to date.')

    def read_data(self):
        print('Read local data.')
        if fpath.exists():
            data = pd.read_csv(fpath, index_col=0)
            data['fecha_reporte_web'] = pd.to_datetime(data['fecha_reporte_web'], dayfirst=True)
            data.rename(columns={'fecha_reporte_web':'date',
                                'departamento_nom':'state',
                                'ciudad_municipio_nom':'municipality',
                                'COUNT_id_de_caso':'cases'}, 
                        inplace=True)
            print('Data Loaded.')
            self.data = data
        else:
            raise FileNotFoundError()
