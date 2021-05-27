import fetchdata.colombia as fcolombia
import fetchdata.costa_rica as fcosta
import fetchdata.germany as fgermany
import fetchdata.mexico as fmexico
import matplotlib.pyplot as plt

mexico = fmexico.CovidMexico()
mexico.fetch_data()
mexico.plot_dashboard(state=['YUCATAN', 'QUINTANA ROO'])

costa = fcosta.CovidCR()
costa.fetch_data()
# costa.read_data()
costa.plot_dashboard(state=['Guanacaste'])

colombia = fcolombia.CovidColombia()
colombia.fetch_data()
# colombia.read_data()
colombia.plot_dashboard(state=['BOGOTA', 'ANTIOQUIA'])

germany = fgermany.CovidGermany()
germany.fetch_data()
# germany.read_data()
germany.plot_cases()

plt.show()
