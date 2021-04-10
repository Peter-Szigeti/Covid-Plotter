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
    urllib.request.urlretrieve(url, 'Data/covid19HungaryStatistics_{}.xlsx'.format(date.today().strftime('%Y-%m-%d')))

def initFoldersAndData():
    url = "https://koronavirus.gov.hu/elhunytak"
    print('Trying to create folders...')
    initFolders()
    print('Beginning scraping tables with Pandas...')
    scrapeUrl(url)
    print('Beginning file download...')
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

def deathcountPerAgeGroup(weighted):

    '''
    A fügvénynek ez a fele csinál egy dataframet,melynek első oszlopában a dátumok találhatóak,
    a második oszlopban pedig a dátumhoz tartozó halottak korai korcsoportra kerekítve
    weighted = bool
    '''
    print('Processing data...')
    df = dateTheScrape()
    age_groups = ['0-34','35-39','40-44','45-49','50-54','55-59','60-64','65-69','70-74','75-79','80-84','84-89','90-120' ]
    mydict1 = {}
    for i in range(len(df)):
        for el in age_groups:
            splat = el.split('-')
            if int(splat[0]) <= int(df['Kor'][i]) and int(splat[1]) >= int(df['Kor'][i]):
                df['Kor'][i] = el
                break
        if df['Date'][i] not in mydict1:
            mydict1[df['Date'][i]] = [df['Kor'][i]]
        else:
            mydict1[df['Date'][i]] += [df['Kor'][i]]

    df = pd.DataFrame(mydict1.items(),columns = ('Dátum','death_age_rounded'))
    df['Dátum']  = df['Dátum'].apply(lambda x:x.strftime('%Y_%m_%d'))
    df = df[::-1]

    '''
    Ez a fele a fügvénynek csinál egy oszlopot minden korcsoportnak, melynek soraiban az adott naphoz tartozó,
     halálozások száma van beírva korcsoportonként.
    '''
    if weighted:
        age_groups_weights = [3700000,652000,838000,750000,663000,572000,651000,643000,482000,377000,240000,134000,65245]
    else:
        age_groups_weights = [1 for x in range(len(age_groups))]
    j = 0
    for el in age_groups:
        df[el] = 0.0
        for i in range(len(df)):
            df[str(el)][i] = df['death_age_rounded'][i].count(el)/age_groups_weights[j]
        j+=1
    del df['death_age_rounded']
    return df

def plot_deathcountPerAgeGroup(df,weighted):
    print('Creating the plots...')
    fig, ax = plt.subplots()
    fig.set_size_inches(18.5, 10.5)
    df.plot.area(x = 'Dátum',xlabel = 'Dátum',ylabel = 'Halálozások száma',title = 'Napi COVID19 Halálozások Korcsoportonként Magyarországon',stacked = True,ax=ax,grid=True)
    plt.savefig('Results/deathcountPerAgeGroup_{}_wstep_{}.png'.format(str(weighted),date.today().strftime('%Y-%m-%d')))
    plt.show()
    print('Done.')

weighted = input("Weighted? : ")
initFoldersAndData()
df = deathcountPerAgeGroup(weighted)
plot_deathcountPerAgeGroup(df,weighted)
