import pandas as pd
import matplotlib.pyplot as plt

df1 = pd.read_html('https://www.ksh.hu/docs/hun/xstadat/xstadat_evkozi/e_wnh004e.html')[1]
cols1 = ['Év','sor-száma',	'kezdő napja',	'záró napja','0-34','35-39','40-44','45-49','50-54','55-59','60-64']
df1.columns = cols1
df1.set_index('záró napja')
df2 = pd.read_html('https://www.ksh.hu/docs/hun/xstadat/xstadat_evkozi/e_wnh004f.html')[1]
cols2 = ['Év','sor-száma',	'kezdő napja',	'záró napja','65-69','70-74','75-79','80-84','84-89','90-120',	'Összesen']
df2.columns = cols2
df2.set_index('záró napja')
df =pd.concat([df1,df2],axis=1)
df = df.loc[:,~df.columns.duplicated()]
del df['sor-száma']
del df['Év']
df.plot.area(x='záró napja',title ='Heti halálozások korcsoportonként 2015-től',xlabel = 'Dátum',ylabel ='Halálozások száma hetente',grid=True)
plt.show()
df.to_csv('Data\hetihalottak_2015_2021.csv')