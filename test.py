import fetchdata.costa_rica as fcosta
import matplotlib.pyplot as plt

covid = fcosta.CovidCR()
covid.read_data()
covid.plot_dashboard(state='Limón', municipality='Talamanca')
plt.show()