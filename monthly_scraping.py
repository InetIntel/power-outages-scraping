from scrapy.crawler import CrawlerProcess

# from india.posoco.posoco import Posoco
# from india.mahavitaran.mahavitaran import Mahavitaran
from ukraine.vinnytsia.crawler import VinnytsiaSpider
from ukraine.vinnytsia.utils import mk_dir as mk_dir_for_vinnytsia
from ukraine.vinnytsia.post_processor import post_process_vinnytsia


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

    # Ukraine Vinnytsia
    process = CrawlerProcess()
    try:
        mk_dir_for_vinnytsia()
        process.crawl(VinnytsiaSpider)
        process.start()
    except Exception as e:
        print("Failed to scrape outage data of Ukraine Vinnytsia")
    try:
        post_process_vinnytsia()
    except Exception as e:
        print("Failed to cope with Ukraine Vinnytsia")


if __name__ == "__main__":
    scrape()