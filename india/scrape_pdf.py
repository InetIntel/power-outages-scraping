import requests
from bs4 import BeautifulSoup
import os


class ScrapePDF:
    def __init__(self, url):
        self.url = url


    def fetch(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            return response
        else:
            print(f"Failed to fetch the page: {self.url}")
            exit()


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        tbody = soup.find('tbody')
        first_link = tbody.find('a', href=True)
        link = first_link['href']
        file_name = first_link.get_text(strip=True)
        return link, file_name


    def check_folder(self):
        folder_path = "./data"
        os.makedirs(folder_path, exist_ok=True)


    def download(self, file_url, filename):
        response = requests.get(file_url)
        self.check_folder()
        if response.status_code == 200:
            filename += ".pdf"
            file_path = os.path.join("./data", filename)
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"Download successful! File saved as {filename}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")


    def run(self):
        response = self.fetch()
        link, file_name = self.parse(response)
        self.download(link, file_name)


url = "https://posoco.in/en/grid-disturbancesincidence/%e0%a4%97%e0%a5%8d%e0%a4%b0%e0%a4%bf%e0%a4%a1-%e0%a4%97%e0%a4%a1%e0%a4%bc%e0%a4%ac%e0%a4%a1%e0%a4%bc%e0%a5%80-%e0%a4%98%e0%a4%9f%e0%a4%a8%e0%a4%be%e0%a4%8f%e0%a4%82-2024-25/"
scrapePDF = ScrapePDF(url)
scrapePDF.run()


