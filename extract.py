from scrapy.selector import Selector
from selenium import webdriver
from tqdm import tqdm
import pandas as pd
import time
import csv
import argparse


class HLTV:
    def __init__(self, args):
        self.url = 'https://www.hltv.org'
        self.logs = args.log
        self.driver = None
        if args.driver.lower()  == 'safari': 
            self.driver = webdriver.Safari()
        elif args.driver.lower() == 'firefox':
            self.driver = webdriver.Firefox()
        else:
            self.driver = webdriver.Chrome()

    def close(self):
        if not self.driver is None: 
            self.driver.close()

    def extract(self, wait_time: int):
        self.driver.get(self.url)
        time.sleep(wait_time)
        return self.driver.page_source

    def to_csv(self, file_dir: str):
        pass 


class Ranking(HLTV):
    def __init__(self, args):
        super().__init__(args)
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
    def __init__(self, args):
        super().__init__(args)

    def to_csv(self, csv_ranking, csv_stats: str):
        fields = ['dpr', 'kast', 'impact', 'adr', 'kpr', 'rating']
        if self.logs: print("Reading csv...")
        
        df = pd.read_csv(csv_ranking, index_col=1)
        
        with open(csv_stats, 'w') as csvfile:
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
    parser = argparse.ArgumentParser('Extract ranking data from HLTV.org')

    parser.add_argument('log', help='Show logs.')
    parser.add_argument('driver', help='Webdriver: Firefox/Chrome/Safari (default=chrome)', default='chrome')

    args = parser.parse_args()
    
    print("Extracting ranking data...")
    ranking = Ranking(args)
    ranking.to_csv('data/ranking.csv')
    ranking.close()

    print("Extracting players data...")
    stats = Stats(args)
    stats.to_csv('data/stats.csv')
    stats.close()
