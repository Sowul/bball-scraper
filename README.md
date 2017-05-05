# bball_scraper
It takes about 20 minutes to scrap one regular season.

## Requirements
```
$ pip install -r requirements.txt
```
## Usage
Edit dates in main function, e.g. to get all regular season games from 2016–17 season set dates as follows:
```python
start = datetime.datetime.strptime("25-10-2016", "%d-%m-%Y")
end = datetime.datetime.strptime("12-04-2017", "%d-%m-%Y")
```
Run script:
```
$ python bball_scraper.py
usage: eg to scrap 03/04 stats, use 2nd year ie 2004 - python bball_scraper.py 2004
$ python bball_scraper.py 2017
```
## Sample output
```
$ head -n 5 4FACTORS_2017
201610250CLE,NYK,99.9,.420,15.8,24.5,.172,88.1,88,CLE,99.9,.548,12.0,27.5,.149,117.1,117
201610250CLE,CLE,99.9,.548,12.0,27.5,.149,117.1,117,NYK,99.9,.420,15.8,24.5,.172,88.1,88
201610250GSW,SAS,98.3,.541,10.6,43.8,.235,131.3,129,GSW,98.3,.512,14.7,19.0,.153,101.8,100
201610250GSW,GSW,98.3,.512,14.7,19.0,.153,101.8,100,SAS,98.3,.541,10.6,43.8,.235,131.3,129
201610250POR,UTA,90.5,.537,11.0,17.1,.195,114.9,104,POR,90.5,.607,12.4,16.7,.293,124.8,113
```