import os
import time
from collections import defaultdict
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime


class ScrapePowerOutageLive:

    def __init__(self, country_name, country_url):
        self.base_url = "https://poweroutage.live"
        self.country_url = country_url
        self.url = self.base_url + self.country_url
        self.country = country_name
        self.states = {}


    def fetch(self):
        response = requests.get(self.url)
        if response.status_code != 200:
            print(f"Failed to access {self.url}")
            exit()
        else:
            return response

    def get_links(self, response):
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = [a['href'] for a in soup.select('.links-list a')]
            return links
        else:
            print(f"Failed to fetch the page. Status Code: {response.status_code}")
            exit()

    def scrape(self):
        response = self.fetch()
        links = self.get_links(response)
        for link in links:
            url = self.base_url + link
            data = self.process(url)
            times, state = self.find_outage_times(data)
            self.states[state] = times



    def find_outage_times(self, data):
        times = dict()
        date, state = data
        for day in date.keys():
            times[day] = dict()
            times[day]["power_present"] = []
            times[day]["no_power"] = []
            times[day]["possible_shutdown"] = []
            times[day]["no_info"] = []
            hours, outages = date[day]
            for i, outage in enumerate(outages):
                if outage == "●":
                    times[day]["power_present"].append(hours[i])
                elif outage == "✕":
                    times[day]["no_power"].append(hours[i])
                if outage == "±":
                    times[day]["possible_shutdown"].append(hours[i])
                if outage == "-":
                    times[day]["no_info"].append(hours[i])
        return times, state

    def process(self, url):
        response = requests.get(url)
        state = url.split("/")[-1][:-1]
        data = defaultdict(tuple)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            schedule_for_today = soup.find('h2', string="Schedule for today")
            if schedule_for_today:
                table_today = schedule_for_today.find_next('table')
                if table_today:
                    rows = table_today.find_all('tr')
                    today_time = rows[0]
                    if today_time:
                        today_times = [td.get_text(strip=True) for td in today_time.find_all('td')]
                    else:
                        print("No <tr> found in the table.")
                    today_outage = rows[1]
                    if today_outage:
                        today_outage_marks = [td.get_text(strip=True) for td in today_outage.find_all('td')]
                    else:
                        print("No <tr> found in the table.")
                    data[today_times[0]] = (today_times[1:], today_outage_marks[1:])
                else:
                    print("No table found after the H2 tag.")
            else:
                print("No H2 tag with 'Schedule for today' found.")
            schedule_for_tomorrow = soup.find('h2', string="Schedule for tomorrow")
            if schedule_for_tomorrow:
                table_tomorrow = schedule_for_tomorrow.find_next('table')
                if table_tomorrow:
                    rows = table_tomorrow.find_all('tr')
                    tomorrow_time = rows[0]
                    if tomorrow_time:
                        tomorrow_times = [td.get_text(strip=True) for td in tomorrow_time.find_all('td')]
                    else:
                        print("No <tr> found in the table.")
                    tomorrow_outage = rows[1]
                    if tomorrow_outage:
                        tomorrow_outage_marks = [td.get_text(strip=True) for td in tomorrow_outage.find_all('td')]
                    else:
                        print("No <tr> found in the table.")
                    data[tomorrow_times[0]] = (tomorrow_times[1:], tomorrow_outage_marks[1:])
                else:
                    print("No table found after the H2 tag.")
            else:
                print("No H2 tag with 'Schedule for tomorrow' found.")
            return data, state
        else:
            print(f"Failed to fetch the page. Status Code: {response.status_code}")

def save_json(data):

    file_path = os.path.join("./worldwide/data", "outage_" + datetime.today().strftime("%Y-%m-%d") + ".json")
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def get_countries():
    url = "https://poweroutage.live/"
    response = requests.get(url)
    res = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        countries = [a for a in soup.select('.links-list li a')]
        for c in countries:
            link = "/" + c['href']
            country = c.get_text(strip=True)
            res.append((link, country))
    return res

# countries = get_countries()

outage_schedule = {}

countries = [("/pk", "Pakistan")]
for country_url, country_name in countries:

    scrapePowerOutageLive = ScrapePowerOutageLive(country_name, country_url)
    scrapePowerOutageLive.scrape()
    outage_schedule[country_name] = scrapePowerOutageLive.states
    save_json(outage_schedule)
    time.sleep(1)





