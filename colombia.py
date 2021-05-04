# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import fetchdata.colombia as fcolombia


# %%
covid = fcolombia.fetch_data()
data = covid.data


# %%
covid.plot_cases()


# %%
covid.plot_cases_per_state()


# %%
covid.plot_cases_for_state('ANTIOQUIA')


# %%
covid.plot_cases_largest_for_state('ANTIOQUIA', 20)


# %%
covid.plot_cases_for_municipality('JARDIN')


# %%
covid.plot_incidence()


plt.show()