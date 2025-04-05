from india.posoco import Posoco
from india.mahavitaran import Mahavitaran

def scrape():

    mahadiscom = Mahavitaran()
    mahadiscom.scrape()

    posoco = Posoco()
    posoco.scrape()


if __name__ == "__main__":
    scrape()