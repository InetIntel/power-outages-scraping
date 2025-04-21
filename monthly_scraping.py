from scrapy import cmdline

from india.posoco.posoco import Posoco
from india.mahavitaran.mahavitaran import Mahavitaran

def scrape():

    try:
        mahadiscom = Mahavitaran()
        mahadiscom.scrape()
    except Exception as e:
        print("Failed to scrape outage data from Mahadiscom.")

    try:
        posoco = Posoco()
        posoco.scrape()
    except Exception as e:
        print("Failed to scrape outage data from POSOCO.")


    try:
        cmdline.execute("cd ukraine".split())
        cmdline.execute("sh craw_ukraine_monthly.sh".split())
    except Exception as e:
        print("Failed to scrape outage data of Ukraine")


if __name__ == "__main__":
    scrape()