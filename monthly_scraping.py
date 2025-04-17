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


if __name__ == "__main__":
    scrape()