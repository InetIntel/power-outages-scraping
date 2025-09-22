import os
from datetime import datetime
import requests
import urllib3


class Tangedco:

    def __init__(self):
        self.url = "https://tneb.tnebnet.org/cpro/today.html"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None

    def check_folder(self):
        self.folder_path = "./data/" + self.today
        os.makedirs(self.folder_path, exist_ok=True)

    def scrape(self):
        """Scrape the webpage and save the content to a file."""
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # Disable SSL warnings

        try:
            # Send a GET request to the URL
            response = requests.get(self.url, verify=False, timeout=10)  # Added timeout
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx, 5xx)

            # Create the folder if it doesn't exist
            self.check_folder()

            # Save the response content to a file
            path = os.path.join(self.folder_path, self.today + "_power_shutdown.html")
            with open(path, "w", encoding="utf-8") as file:
                file.write(response.text)

            print("Scraping is done for tnebnet. File saved at:", path)

        except requests.exceptions.ConnectionError as e:
            print(
                "Connection error: Failed to connect to the server. Please check your internet connection or the server status.")
        except requests.exceptions.Timeout as e:
            print("Request timed out: The server did not respond in time.")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")



if __name__ == "__main__":
    tnebnet = Tangedco()
    tnebnet.scrape()