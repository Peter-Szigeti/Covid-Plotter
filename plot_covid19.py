import os#a mappák létrehozásához és kezeléséhez
from datetime import date #fájlok elnevezéséhez
import requests#webscraping
from bs4 import BeautifulSoup#webscraping
import pandas as pd
import urllib.request #a napi halálozásokat tartalmazó táblázathoz kell
import math
from matplotlib import pyplot as plt

'''
Dependencies: Matplotlib,BeautifulSoup, Pandas
Útmutatás a programhoz:tedd be egy mappába a .py filet és futtasd le és futtasd le:)

'''

def initFolders():
    try:
        os.mkdir('Results')
        os.mkdir('Data')
    except:
        print('"Data" folder already exists.')

def getLastPage(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    tag = soup.find('a',title='Ugrás az utolsó oldalra')
    return int(tag.get('href').split('=')[1])

def scrapeUrl(url):
    mylist = [pd.read_html(url)[0]]
    for i in range(1,getLastPage(url)):
        temp = pd.read_html((url + '?page={}').format(i))[0]
        mylist.append(temp)
    df = pd.concat(mylist)
    df.to_csv('Data/covid19Deaths_scraped_{}.csv'.format(date.today().strftime('%Y-%m-%d')))

def downloadTable(url):
    print('Beginning file download with urllib2...')
    urllib.request.urlretrieve(url, 'Data/covid19HungaryStatistics_{}.xlsx'.format(date.today().strftime('%Y-%m-%d')))

def initFoldersAndData(url):
    initFolders()
    scrapeUrl(url)
    downloadTable('https://docs.google.com/spreadsheets/d/1e4VEZL1xvsALoOIq9V2SQuICeQrT5MtWfBm32ad7i8Q/export?format=xlsx&gid=311133316')

def dateTheScrape():
    df = pd.read_csv('Data/covid19Deaths_scraped_{}.csv'.format(date.today().strftime('%Y-%m-%d')))
    dates = pd.read_excel('Data/covid19HungaryStatistics_{}.xlsx'.format(date.today().strftime('%Y-%m-%d')))
    df['Date'] = 'hi'

    c = 0
    for i in range(len(dates)):
        if not math.isnan(dates['Az új elhunytak száma naponta'][i]):
            for j in range(int(dates['Az új elhunytak száma naponta'][i])):
                df['Date'][len(df)-1-c] = dates['Dátum'][i]
                c+=1
    df.to_csv('Data/covid19Deaths_scraped_DATED_{}.csv'.format(date.today().strftime('%Y-%m-%d')))
    return df

def deathcountPerAgeGroup(step):

    '''A fügvénynek ez a fele csinál egy dataframet,melynek első oszlopában a dátumok találhatóak,
    a második oszlopban pedig a dátumhoz tartozó halottak korai korcsoportra kerekítve
    a korcsoportok szélességét a "step" paraméterrel lehet megadni'''

    df = dateTheScrape()
    age_groups = [i for i in range(15,106,step)]
    for i in range(len(df)):
        for el in age_groups:
            if df['Kor'][i] < el:
                df['Kor'][i] = el
                break

    mydict1 = {}
    for i in range(len(df)):
        if df['Date'][i] not in mydict1:
            mydict1[df['Date'][i]] = [df['Kor'][i]]
        else:
            mydict1[df['Date'][i]] += [df['Kor'][i]]

    df = pd.DataFrame(mydict1.items(),columns = ('Dátum','death_age_rounded'))
    df['Dátum']  = df['Dátum'].apply(lambda x:x.strftime('%Y_%m_%d'))
    df = df[::-1]

    '''Ez a fele a fügvénynek csinál egy oszlopot minden korcsoportnak, melynek soraiban az adott naphoz tartozó,
     halálozások száma van beírva korcsoportonként. '''

    for el in range(15,106,step):
        df[str(el)] = 0.0
        for i in range(len(df)):
            df[str(el)][i] = df['death_age_rounded'][i].count(el)
    del df['death_age_rounded']
    return df

def plot_deathcountPerAgeGroup(df):
    fig, ax = plt.subplots()
    fig.set_size_inches(18.5, 10.5)
    df.plot.area(x = 'Dátum',xlabel = 'Dátum',ylabel = 'Halálozások száma',title = 'Napi COVID19 Halálozások Korcsoportonként Magyarországon',stacked = True,ax=ax)

    plt.savefig('Results/deathcountPerAgeGroup_{}.png'.format(date.today().strftime('%Y-%m-%d')))

url = "https://koronavirus.gov.hu/elhunytak"
initFoldersAndData(url)
df = deathcountPerAgeGroup(20)
plot_deathcountPerAgeGroup(df)




