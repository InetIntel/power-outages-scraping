from nigeria.ikeja.Ikeja import Ikeja
from pakistan.fesco.fesco import Fesco
from pakistan.hyderabad.hyderabad import Hyderabad
from pakistan.iesco.iesco import Iesco
from pakistan.quetta.quetta import Quetta
from india.goa.goa import Goa
from india.rajdhani_weekly.rajdhani_weekly import RajdhaniWeekly
from india.tangedco.tangedco import Tangedco
from india.tnpdcl.tnpdcl import Tnpdcl
from india.npp.npp import Npp
from india.bses_rajdhani.rajdhani import Rajdhani
from india.bses_yamuna.yamuna import Yamuna
from india.tata.tata import Tata
from scrapy.crawler import CrawlerProcess
from ukraine.khmelnytsky.utils import mk_dir as mk_dir_for_khmelnytsky
from ukraine.khmelnytsky.crawler import KhmelnytskySpider
from ukraine.cherkasy.utils import mk_dir as mk_dir_for_cherkasy
from ukraine.cherkasy.crawler import CherkasySpider
from ukraine.mykolaiv.utils import mk_dir as mk_dir_for_mykolaiv
from ukraine.mykolaiv.crawler import MykolaivSpider
from ukraine.sumy.utils import mk_dir as mk_dir_for_sumy
from ukraine.sumy.crawler import SumySpider
from ukraine.zhytomyr.crawler import crawl_zhytomyr
from ukraine.zhytomyr.utils import mk_dir as mk_dir_for_zhytomyr


def scrape():

    # India
    try:
        tnebltd = Tnpdcl()
        tnebltd.scrape()
    except Exception as e:
        print("Failed to scrape outage data from TNEBLTD.")

    try:
        rajdhani_weekly = RajdhaniWeekly()
        rajdhani_weekly.scrape()
    except Exception as e:
        print("Failed to scrape outage data for Rajdhani Weekly.")

    try:
        tatapower = Tata()
        tatapower.scrape()
    except Exception as e:
        print("Failed to scrape outage data from TATA.")

    try:
        goaelectricity = Goa()
        goaelectricity.scrape()
    except Exception as e:
        print("Failed to scrape outage data from GOA.")

    try:
        npp = Npp()
        npp.scrape()
    except Exception as e:
        print("Failed to scrape outage data from NPP.")

    try:
        rajdhani = Rajdhani()
        rajdhani.scrape()
    except Exception as e:
        print("Failed to scrape outage data from Rajdhani.")

    try:
        yamuna = Yamuna()
        yamuna.scrape()
    except Exception as e:
        print("Failed to scrape outage data from Yamuna.")

    # # Nigeria
    try:
        ikeja = Ikeja()
        ikeja.scrape()
    except Exception as e:
        print("Failed to scrape outage data from IKEJA.")

    # # Pakistan
    try:
        fesco = Fesco()
        fesco.scrape()
    except Exception as e:
        print("Failed to scrape outage data from FESCO.")

    try:
        hesco = Hyderabad()
        hesco.scrape()
    except Exception as e:
        print("Failed to scrape outage data from Hyderabad.")

    try:
        iesco = Iesco()
        iesco.scrape()
    except Exception as e:
        print("Failed to scrape outage data from IESCO.")

    try:
        qesco = Quetta()
        qesco.scrape()
    except Exception as e:
        print("Failed to scrape outage data from Quetta.")


    # Ukraine
    process = CrawlerProcess()

    try:
        mk_dir_for_khmelnytsky()
        process.crawl(KhmelnytskySpider)
    except Exception as e:
        print("Failed to scrape outage data of Ukraine Khmelnytsky because ")
        print(e)

    try:
        mk_dir_for_cherkasy()
        process.crawl(CherkasySpider)
    except Exception as e:
        print("Failed to scrape outage data of Ukraine Cherkasy because")
        print(e)

    try:
        mk_dir_for_mykolaiv()
        process.crawl(MykolaivSpider)
    except Exception as e:
        print("Failed to scrape outage data of Ukraine Mykolaiv because")
        print(e)

    try:
        mk_dir_for_sumy()
        process.crawl(SumySpider)
    except Exception as e:
        print("Failed to scrape outage data of Ukraine Sumy because")
        print(e)

    try:
        process.start()
    except Exception as e:
        print(e)

    try:
        mk_dir_for_zhytomyr()
        crawl_zhytomyr()
    except Exception as e:
        print("Failed to scrape outage data of Ukraine Zhytomyr because")
        print(e)


    # this is an inactive website
    # tnebnet = Tangedco()
    # tnebnet.scrape()



    print("ALL DONE")


if __name__ == "__main__":
    scrape()