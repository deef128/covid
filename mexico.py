# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import matplotlib.pyplot as plt
import fetchdata.mexico as fmexico

covid = fmexico.CovidMexico()

# %%
covid.fetch_data()

# %%
covid.plot_cases()


# %%
covid.plot_cases_per_state()


# %%
covid.plot_incidence()

plt.show()
# %%
