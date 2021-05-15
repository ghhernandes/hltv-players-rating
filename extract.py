from scrapy.selector import Selector
from selenium import webdriver
from tqdm import tqdm
import pandas as pd
import time
import csv

class HLTV:
    def __init__(self, logs=False):
        self.url = 'https://www.hltv.org'
        self.logs = logs 
        self.driver = webdriver.Safari()

    def __del__(self):
        self.driver.close()

    def extract(self, wait_time: int):
        self.driver.get(self.url)
        time.sleep(wait_time)
        return self.driver.page_source

    def to_csv(self, file_dir: str):
        pass 


class Ranking(HLTV):
    def __init__(self, logs=False):
        super().__init__(logs)
        self.url = 'https://www.hltv.org/stats/players?startDate=2020-05-13&endDate=2021-05-13&rankingFilter=Top50'

    def to_csv(self, csv_file: str):
        response = self.extract(2)

        players = {
            'name': [],
            'url': [],
            'country': [],
        }

        tr = Selector(text=response).xpath('/html/body/div/div/div/div/div/table/tbody/tr')
        for player in tr:
            players['name'].append(player.css('a::text').get())
            players['url'].append(player.css('a').attrib['href'])
            players['country'].append(player.css('img').attrib['title'])
            if self.logs:
                print("player: {} country: {}".format(players['name'][-1], players['country']))

        df = pd.DataFrame(data=players)
        df.to_csv(csv_file)


class Stats(HLTV):
    def __init__(self, logs=False):
        super().__init__(logs)

    def to_csv(self, csv_file: str):
        fields = ['dpr', 'kast', 'impact', 'adr', 'kpr', 'rating']
        if self.logs: print("Reading csv...")

        df = pd.read_csv(csv_file, index_col=0)

        with open('stats.csv', 'w') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csvwriter.writerow(fields)
        
            if self.logs: print("Extracting data...") 

            for url in tqdm(df['url']):
                self.driver.get(self.url+url)
                time.sleep(.5)
                
                r = Selector(text=str(self.driver.page_source))
                
                rating = r.xpath('/html/body/div[2]/div/div[2]/div[1]/div[2]/div[5]/div[2]/div[2]/div[1]/div[2]/div[1]/text()').get()
                
                dpr = r.xpath('/html/body/div[2]/div/div[2]/div[1]/div[2]/div[5]/div[2]/div[2]/div[2]/div[2]/div[1]/text()').get()
               
                kast = r.xpath('/html/body/div[2]/div/div[2]/div[1]/div[2]/div[5]/div[2]/div[2]/div[3]/div[2]/div[1]/text()').get()
               
                impact = r.xpath('/html/body/div[2]/div/div[2]/div[1]/div[2]/div[5]/div[2]/div[3]/div[1]/div[2]/div[1]/text()').get()
               
                adr = r.xpath('/html/body/div[2]/div/div[2]/div[1]/div[2]/div[5]/div[2]/div[3]/div[2]/div[2]/div[1]/text()').get()
               
                kpr = r.xpath('/html/body/div[2]/div/div[2]/div[1]/div[2]/div[5]/div[2]/div[3]/div[3]/div[2]/div[1]/text()').get()

                csvwriter.writerow([dpr, kast, impact, adr, kpr, rating])
           
            if self.logs:   
                print(f"{rating} - {dpr} {kast} {impact} {adr} {kpr}")

if __name__ == '__main__':
    ranking = Ranking(logs=True)
    ranking.to_csv('ranking.csv')

    stats = Stats(logs=True)
    stats.to_csv('ranking.csv')

