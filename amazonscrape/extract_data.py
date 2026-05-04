import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import time
from datetime import datetime, date, timedelta
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import urllib.parse
from time import sleep
from random import randint
import requests

root_url = 'https://www.amazon.com/'
SCRAPER_API_KEY = ##PUT IN YOUR SCRAPER API KEY HERE##

def all_sundays_of_year(year):
    """
    Generates all the dates for Sundays in a given year.
    """
    d = date(year, 1, 1) # Start with January 1st
    # Adjust d to the first Sunday of the year. 
    # weekday() returns 0 for Monday, 6 for Sunday.
    # The calculation d.weekday() gives days to add to reach Sunday.
    d += timedelta(days=6 - d.weekday())
    sundays = []
    while d.year == year:
        sundays.append(d.strftime("%Y-%m-%d"))
        d += timedelta(days=7) # Move to the next Sunday
    return sundays

def get_week_data(date):  
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

    r = requests.get('https://www.amazon.com/charts/'+ date +'/mostsold/fiction', headers=headers)
    content = r.content
    soup = BeautifulSoup(content, 'html.parser')

# //*[@id="sin-body"]/div/div/div/div[2]
    testsoup = soup.find('div', attrs={'class': 'kc-vertical-rank-container row'})
    all = []

    if testsoup is not None:
        list_items = testsoup.find_all('div', recursive=False)

        for book in list_items:
            #create tags for each element we want
            ranktag = book.find('div', attrs={'class': 'kc-rank-card-rank'}) if book.find('div', attrs={'class': 'kc-rank-card-rank'}) else None

            authtag = book.find('div', attrs={'class': 'kc-rank-card-author'}) if book.find('div', attrs={'class': 'kc-rank-card-author'}) else None

            titletag = book.find('div', attrs={'class': 'kc-rank-card-title'}) if book.find('div', attrs={'class': 'kc-rank-card-title'}) else None

            hrefs = book.find('div', attrs={'class': 'kc-book-title-img'}).find_all('a') if book.find('div', attrs={'class': 'kc-book-title-img'}) else None
            href = hrefs[0] if hrefs else None
            try:
                blurb, pub, pub_date, series, series_name, series_order, genres, format = get_book_data(href['href']) if href else (None, None, None, 0, None, None, [], None)
            except TypeError:
                blurb, pub, pub_date, series, series_name, series_order, genres, format = None, None, None, 0, None, None, [], None
                print(f"Error processing book with href, title: {titletag.get_text(strip=True) if titletag else 'N/A'}, {href['href'] if href else 'N/A'}")

            if ranktag and authtag and titletag and href:
                    all.append({
                            'week': date,
                            'rank': ranktag.get_text(strip=True) if ranktag else None,
                            'author': authtag.get_text(strip=True)[3::] if authtag else None,
                            'title': titletag.get_text(strip=True) if titletag else None,
                            'href': href['href'] if href else None,
                            'blurb': blurb,
                            'pub': pub,
                            'pub_date': pub_date,
                            'series': series,
                            'series_name': series_name,
                            'series_order': series_order,
                            'genres': genres,
                            'format': format
                    })
        sleep(randint(1,4))

    #<a class="kc-cover-link app-specific-display not_app" href="/dp/B0FJTF5MJB/ref=chrt_bk_sd_fc_1_ci_lp"> <img alt="Cover image of Dear Debbie by Freida McFadden" src="https://m.media-amazon.com/images/I/81K9E2AyfjL.jpg" title="Cover image of Dear Debbie by Freida McFadden"/>
    return all

def get_book_data(book_url):
    blurb, pub, pub_date = None, None, None
    series, series_name, series_order = 0, None, None
    genres, format = [], None
    
    book_descr_url = 'https://www.amazon.com' + book_url
    book_page = requests.get('http://api.scraperapi.com', params = {'api_key': SCRAPER_API_KEY, 'url': book_descr_url})
    book_soup = BeautifulSoup(book_page.content, 'html.parser')
    #find blurb and extract text
    blurb_tag = book_soup.find('div', attrs={'id': 'bookDescription_feature_div'})
    blurb = blurb_tag.get_text(strip=False) if blurb_tag else None

                        #find publisher and extract text
    details = book_soup.find(attrs={'class': 'a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list'})
    details_list = details.find_all('li') if details else None
#detailBullets_feature_div
    #if this doesn't work, try this other method of finding details
    if details_list is None:
        details = book_soup.find(attrs={'id': 'audibleProductDetails'})
        details_list = details.find_all('tr') if details else None

    for i, bigtag in enumerate(details_list):
        try:
            #if the details list is formatted as a table
            if bigtag.name == 'tr':
                #print(len(bigtag)) sanity check
                taglist = bigtag.find_all(recursive=False)

                taglist_label = taglist[0].get_text(strip=True) 
                taglist_value = taglist[1].get_text(strip=True)

            #if formatted in bulletpoints as list
            else:
                taglist = bigtag.find_all('span')

                taglist_label = taglist[1].get_text(strip=True) if len(taglist) > 1 else None
                taglist_value = taglist[2].get_text(strip=True) if len(taglist) > 2 else None
            if taglist_label and taglist_value:
                if 'Publisher' in taglist_label:
                    pub = taglist_value
                elif 'Publication date' in taglist_label or 'Published' in taglist_label or 'Release Date' in taglist_label:
                    pub_date = taglist_value
        except Exception as e:
            series = None
            continue

    #FOR SERIES INFO
    series_tag = book_soup.find('div', attrs={'id': 'seriesBulletWidget_feature_div'})
    if series_tag:
        series = 1
        series_info = series_tag.find('a').get_text(strip=True) if series_tag.find('a') else None
        series_info = series_info.split(':') if series_info else None
        if series_info:
            series_order = series_info[0].strip() if len(series_info) > 0 else None
            series_name = series_info[1].strip() if len(series_info) > 1 else None
    else:
        series = 0
        series_name = None
        series_order = None

                    #genre info
    genre_tag = book_soup.find('ul', attrs={'class': 'a-unordered-list a-horizontal a-size-small'}).find_all('li')
    genres = [tag.get_text(strip=True) for tag in genre_tag if len(tag.get_text(strip=True)) > 2]

                    #format
    if 'Kindle Store' in genres:
        if 'Kindle eBooks' in genres:
            format = 'eBook'
        elif 'Kindle Audiobooks' in genres:
            format = 'Audiobook'
        genres = genres[1:]
    elif 'Paperback' in genres:
        format = 'Paperback'
    elif 'Hardcover' in genres:
        format = 'Hardcover'
    elif 'Book' in genres:
        format = 'Book'
    else:
        format = None
    genres = genres[1:]
    # except:
    #     blurb = None
    #     pub = None
    #     pub_date = None
    #     series = 0
    #     series_name = None
    #     series_order = None
    #     genres = []
    #     format = None
    return blurb, pub, pub_date, series, series_name, series_order, genres, format