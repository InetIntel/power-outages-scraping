from india.scrape_pdf import ScrapePDF
from india.mahavitaran import Mahavitaran

def scrape():

    posoco = ScrapePDF()
    posoco.scrape()

    mahadiscom = Mahavitaran()
    mahadiscom.scrape()

if __name__ == "__main__":
    scrape()