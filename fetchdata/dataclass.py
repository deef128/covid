# ToDo: rework plotting stuff and dashboard 

import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

class CovidData:

    def __init__(self, country_name, population):
        self.country = country_name
        self.population = population

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        if data is not None:
            days = data['date'].unique()
            days.sort()
            self.dates = days
            self.last_date = days[-1]
            self.last_date_dt = pd.to_datetime(self.last_date)
            self.last_date_str = self.last_date_dt.strftime('%d/%m/%Y')
            self.num_days = len(self.dates)

    def plot_cases(self, axis=None):
        d = self.data[['date', 'cases']].groupby('date').sum('cases')
        axis = d.plot(ax=axis)
        axis.title.set_text(f'Daily new cases for {self.country}\n{self._create_cases_str(d)}')
        plt.tight_layout()

    def plot_cases_per_state(self, axis=None):
        axis = self.data.loc[self.data['date'] == self.last_date]\
            .groupby('state')\
                .sum('cases')\
                    .sort_values(by='cases', ascending=False)\
                        .plot(kind='bar', ax=axis)
        axis.title.set_text(f'New cases for {self.country} per state on the {self.last_date_str}')
        plt.tight_layout()

    def plot_cases_for_state(self, state_name, axis=None):
        self._check_state(state_name)

        d = self.data.loc[self.data['state'] == state_name]\
            .groupby('date')\
                .sum('cases')\
                    .sort_index()
        axis = d.plot(ax=axis)
        axis.title.set_text(f'Daily new cases for {state_name} ({self.country})\n{self._create_cases_str(d)}')
        plt.tight_layout()

    def plot_cases_largest_for_state(self, state_name, n):
        self._check_state(state_name)

        self.data.loc[self.data['date'] == self.last_date]\
            .loc[self.data['state'] == state_name]\
                .groupby('municipality')\
                    .sum('cases')\
                        .nlargest(20, columns='cases')\
                            .plot(kind='bar')
        plt.title(f'Daily new cases for {state_name} ({self.country})')
        plt.tight_layout()

    def plot_cases_for_municipality(self, municipality_name, axis=None):
        self._check_municipality(municipality_name)

        d = self.data.loc[self.data['municipality'] == municipality_name]\
            .set_index('date')\
                .reindex(self.dates, fill_value=0)\
                    ['cases']
        axis = d.plot(ax=axis)
        axis.title.set_text(f'Daily new cases for {municipality_name} ({self.country})\n{self._create_cases_str(d)}')
        plt.tight_layout()            
        
    def plot_incidence(self, axis=None):
        grouped = self.data.groupby('date').sum('cases')
        incidence = list()

        for i in range(7, self.num_days+1):
            inci = grouped[i-7:i].sum() / self.population * 100000
            incidence.append(inci.item())

        if axis is None:
            plt.figure()
            axis = plt.plot(self.dates[6:], incidence)
        else:
            axis.plot(self.dates[6:], incidence)
        s = 'Incidence on {}: {:.2f} ({:.2f})'.format(self.last_date_str, incidence[-1], -1*(incidence[-2] - incidence[-1]))
        axis.title.set_text(f'Incidence for {self.country}\n{s}')
        plt.tight_layout()

    def plot_dashboard(self, **kwargs):
        if len(kwargs) == 0:
            fig, axes = plt.subplots(nrows=1, ncols=3, figsize=[20, 5])
        else:
            fig, axes = plt.subplots(nrows=2, ncols=3, figsize=[20, 10])
            axes = axes.flatten()
        
        self.plot_cases(axes[0])
        self.plot_incidence(axes[1])
        self.plot_cases_per_state(axes[2])

        i = 3
        for key, value in kwargs.items():
            if key == 'state':
                for s in value:
                    self.plot_cases_for_state(s, axes[i])
                    i = i+1
            elif key == 'municipality':
                for m in value:
                    self.plot_cases_for_municipality(m, axes[i])
                    i = i+1
            else:
                raise KeyError()
        fig.tight_layout()

    def _create_cases_str(self, c):
        cpm = -1 * int(c.iloc[-2] - c.iloc[-1])
        s = 'New cases on {}: {} ({})'.format(self.last_date_str, c.iloc[-1].item(), cpm)
        return s

    def _check_state(self, state_name):
        if state_name not in self.data['state'].unique():
            raise KeyError('State not found')

    def _check_municipality(self, municipality_name):
        if municipality_name not in self.data['municipality'].unique():
            raise KeyError('Municipality not found')

    def print_cases(self):
        c = self.data.groupby('date').sum('cases').iloc[-2:]
        s = self._create_cases_str(c)
        print(self.country)
        print(s)

    def print_cases_for_state(self, state_name):
        self._check_state(state_name)
        
        c = self.data.loc[self.data['state'] == state_name].\
            groupby('date').sum('cases').iloc[-2:]
        s = self._create_cases_str(c)
        print(state_name)
        print(s)

    def print_cases_for_municipality(self, municipality_name):
        self._check_municipality(municipality_name)

        c = self.data.loc[self.data['municipality'] == municipality_name]\
            .set_index('date')\
                .reindex(self.dates, fill_value=0)\
                    ['cases'].iloc[-2:]
        s = self._create_cases_str(c)
        print(municipality_name)
        print(s)