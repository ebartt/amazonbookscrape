from datetime import datetime
from turtle import pd
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from urllib.request import urlopen
from bs4 import BeautifulSoup
from time import sleep
from random import randint
from extract_data import get_week_data, get_book_data, all_sundays_of_year
import csv

current_date = datetime.now().strftime("%Y-%m-%d")

fieldnames = ['week', 'rank', 'author', 'title', 'href', 'blurb', 'pub', 'pub_date', 'series', 'series_name', 'series_order', 'genres', 'format']

dat = [] #do not comment this out

years = [2017, 2018, 2019, 2020, 2021,2022,2023,2024,2025, 2026] #if only doing for one year, make sure this is still a list

weeks = []  #if only doing certain weeks, add them into this list in 'YYYY-MM-DD' format
#then comment out this first for loop (for year in years)
for year in years:
    weeks.extend(all_sundays_of_year(year))

dat = [] #initialize list to hold data

#create csv file we are writing to
#comment this out if you are appending to an existing csv
with open('amazon_charts.csv', 'w') as file:
    writer = csv.writer(file)
    writer.writerow(fieldnames)

with open('amazon_charts.csv', 'r') as file:
    reader = csv.DictReader(file)
    existing_weeks = {row['week'] for row in reader}

try:
    with open('amazon_charts.csv', mode='a', newline='') as file: #append to existing csv
        writer = csv.DictWriter(file, fieldnames=fieldnames)

       #get master list of books
        #indiv book data built in
        for week in weeks:
            if week > current_date:
                print(f"Week {week} is in the future. Skipping.")
                break
            elif week < '2017-05-14':
                print(f"Week {week} is before the earliest week of the charts. Skipping.")
                continue
            elif week in existing_weeks:
                print(f"Week {week} already exists in the CSV. Skipping.")
                continue
            else:
                try:
                    week_dat = get_week_data(week)
                    writer.writerows(week_dat) #write week data to csv
                    dat.extend(week_dat)
                    print(f"Finished week: {week}")
                    sleep(randint(1,4))
                except Exception as e:
                    print(f"An error occurred while processing week {week}: {e}")

except FileNotFoundError:
    print("File not found. Ensure 'amazon_charts.csv' exists.")
except Exception as e:
    print(f"An error occurred: {e}")