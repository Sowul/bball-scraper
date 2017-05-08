#!/usr/bin/env python

import csv
import datetime
from http.client import HTTPException, IncompleteRead
import logging
import os
import re
import string
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from bs4 import BeautifulSoup
from deco import concurrent, synchronized

def get_urls(start, end):
    start = int(start.strftime("%Y%m%d"))
    end = int(end.strftime("%Y%m%d"))
    games_urls = []
    season = sys.argv[1]
    games_urls_filename = season+'_games_urls'
    if os.path.isfile(games_urls_filename):
        with open(games_urls_filename, 'r') as f:
            for line in f:
                games_urls.append(line.split('\n')[0])
        logger.info("games_urls loaded from file")
    else:
        months = ['october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']
        urls = []
        for month in months:
            urls += ['http://www.basketball-reference.com/leagues/NBA_'+\
                    str(season)+'_games-'+str(month)+'.html']
        logger.info("getting games_urls")
        for url in urls:
            try:
                f1 = urlopen(url).read().decode('utf-8')
            except HTTPError as http_err:
                continue
            
            f2 = f1.split('\n')

            for i in range(len(f2)):
                if re.search("Box Score", f2[i]):
                    #magic number: /boxscores/201704020BRK.html[11:-9] -> 20170402
                    if(start <= int(re.search('(?<=href=").{28}(?=")', f2[i]).group(0)[11:-9]) and 
                        int(re.search('(?<=href=").{28}(?=")', f2[i]).group(0)[11:-9]) <= end):
                            games_urls += ["http://www.basketball-reference.com" + re.search('(?<=href=").{28}(?=")', f2[i]).group(0)]
        #just in case
        with open(games_urls_filename, 'a+') as f:
            for line in games_urls:
                f.write(line+'\n')
        logger.info("games_urls dumped to file")
    return games_urls

@concurrent
def get_game(url):
    try:
        resp = urlopen(url).read().decode('utf-8')
    except HTTPException as http_exc_err:
        resp = urlopen(url).read().decode('utf-8')
    except IncompleteRead as ir_err:
        resp = urlopen(url).read().decode('utf-8')
    except HTTPError as http_err:
        resp = urlopen(url).read().decode('utf-8')
    except URLError as url_err:
        resp = urlopen(url).read().decode('utf-8')
    
    game_id = re.search('(?<=boxscores/).+?(?=.html)', resp).group(0)
    soup = BeautifulSoup(resp, "lxml")
    scores = soup.find("div", attrs={"id":"all_line_score"})
    scores = re.findall('<strong>(.*?)<', str(scores))
    away_pts = int(scores[0])
    home_pts = int(scores[1])

    rows = soup.find("div", attrs={"id":"all_four_factors"})
    rows = re.findall('\<tr >.*?\<\/tr>', str(rows))
    cells = re.findall('>(.*?)<', str(rows))
    cells = [item for item in cells if len(item)>1]
    #delete "', '"
    del cells[7]
    #cells = [cells[:7], cells[7:]]
    #['HOU', '90.9', '.507', '12.0', '35.9', '.466', '118.8', 'LAL', '90.9', '.373', '10.3', '25.0', '.392', '99.0']

    away = [game_id]
    for item in cells[:7]:
        away.append(item)
    away.append(away_pts)
    for item in cells[7:]:
        away.append(item)
    away.append(home_pts)
    
    home = [game_id]
    for item in cells[7:]:
        home.append(item)
    home.append(home_pts)
    for item in cells[:7]:
        home.append(item)
    home.append(away_pts)
    
    logger.info(game_id)
    return [away, home]

@synchronized
def run(games_urls):
    games = []
    for i in range(len(games_urls)):
        games.append(get_game(games_urls[i]))
    return games

def main():
    if len(sys.argv) == 2:
        start_time = time.time()

        start = datetime.datetime.strptime("25-10-2016", "%d-%m-%Y")
        end = datetime.datetime.strptime("12-04-2017", "%d-%m-%Y")

        games_urls = get_urls(start, end)
        logger.info('got {} urls'.format(len(games_urls)))
        logger.info('scraper started')
        
        games = run(games_urls)
        games = [[item for subsublist in sublist for item in subsublist] for sublist in games]
        logger.info('done scraping')

        with open('4FACTORS_'+sys.argv[1], 'w') as f:
            writer = csv.writer(f)
            half = len(games[0])//2
            for game in games:
                writer.writerow(game[:half])
                writer.writerow(game[half:])
        logger.info("4factors dumped to file")
        os.remove(sys.argv[1]+'_games_urls')
        logger.info('total running time: {} minutes'.format(round((time.time() - start_time)/60, 2)))
    else:
        print('usage: eg to scrap 03/04 stats, use 2nd year ie 2004 - python bball_scraper.py 2004')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    logger = logging.getLogger(__name__)
    main()
