

!pip install bt

!pip install yfinance

# Commented out IPython magic to ensure Python compatibility.
import bt
import yfinance as yf

import pandas as pd
import matplotlib
matplotlib.style.use('seaborn-darkgrid')
# %matplotlib inline

"""##Funções"""

def consulta_bc(codigo_bcb):
  url = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados?formato=json'.format(codigo_bcb)
  df = pd.read_json(url)
  df['data'] = pd.to_datetime(df['data'], dayfirst=True)
  df.set_index('data', inplace=True)
  return df

def cdi_acumulado(data_inicio, data_fim):
  cdi = consulta_bc(12)
  cdi_acumulado = (1 + cdi[data_inicio : data_fim] / 100).cumprod()
  cdi_acumulado.iloc[0] = 1
  return cdi_acumulado

"""##Obtendo e tratando os dados"""

data_inicio = "2021-07-01"
data_fim    = "2022-07-01"

cdi = cdi_acumulado(data_inicio=data_inicio, data_fim=data_fim)

tickers_carteira = ['BOVA11.SA', 'TEND3.SA']

carteira = yf.download(tickers_carteira, start=data_inicio, end=data_fim)['Adj Close']

carteira

carteira['renda_fixa'] = cdi
carteira.dropna(inplace=True)

carteira

"""##Backtesting"""

rebalanceamento = bt.Strategy('rebalanceamento', 
                [bt.algos.RunMonthly(run_on_end_of_period=True),
                 bt.algos.SelectAll(),
                 bt.algos.WeighEqually(),
                 bt.algos.Rebalance()])

buy_hold = bt.Strategy('Buy&Hold', 
                   [ bt.algos.RunOnce(),
                     bt.algos.SelectAll(),
                     bt.algos.WeighEqually(),
                     bt.algos.Rebalance()]
                    )

bt1 = bt.Backtest(rebalanceamento, carteira)
bt2 = bt.Backtest(buy_hold, carteira[["TEND3.SA",'BOVA11.SA']])

resultados = bt.run(bt1, bt2)

"""#Resultados"""

resultados.display()

resultados.plot();

"""###Operações"""

resultados.get_transactions()

"""###Pesos"""

resultados.get_security_weights()

resultados.plot_security_weights()

