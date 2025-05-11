from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import time

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)

url = 'https://pokemon.fandom.com/ru/wiki/Категория:Покемоны'
driver.get(url)

time.sleep(3)

html = driver.page_source
driver.quit()

soup = BeautifulSoup(html, 'html.parser')
items = soup.select('.category-page__member-link')

pokemons = []
for item in items:
    name = item.text.strip()
    link = 'https://pokemon.fandom.com' + item['href']
    pokemons.append({'name': name, 'link': link})

df = pd.DataFrame(pokemons)

df = df[~df['name'].str.contains('Категория:')]
df = df[~df['name'].isin(['Эволюция'])]
df.reset_index(drop=True, inplace=True)

df.to_csv('pokemons.csv', index=False)
print(df.head())

