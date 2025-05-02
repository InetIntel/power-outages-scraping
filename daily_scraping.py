
from india.bses_rajdhani.rajdhani import Rajdhani
from india.bses_yamuna.yamuna import Yamuna
from scrapy.crawler import CrawlerProcess

from cameroon.Adamaoua.crawler import crawl_adamaoua
from cameroon.Centre.crawler import crawl_centre
from cameroon.Douala.crawler import crawl_douala
from cameroon.Est.crawler import crawl_est
from cameroon.Littoral.crawler import crawl_littoral
from cameroon.Nord.crawler import crawl_nord
from cameroon.Ouest.crawler import crawl_ouest
from cameroon.Sud.crawler import crawl_sud
from cameroon.Sud_Ouest.crawler import crawl_sud_ouest
from cameroon.Nord_Ouest.crawler import crawl_nord_ouest
from cameroon.Yaoundé.crawler import crawl_yaounde
from india.goa.goa import Goa
from india.npp.npp import Npp
from india.rajdhani_weekly.rajdhani_weekly import RajdhaniWeekly
from india.tata.tata import Tata
from india.tnpdcl.tnpdcl import Tnpdcl
from nigeria.ikeja.Ikeja import Ikeja
from pakistan.fesco.fesco import Fesco
from pakistan.hyderabad.hyderabad import Hyderabad
from pakistan.iesco.iesco import Iesco
from pakistan.quetta.quetta import Quetta
from ukraine.cherkasy.crawler import CherkasySpider
from ukraine.cherkasy.post_processor import post_process_cherkasy
from ukraine.cherkasy.utils import mk_dir as mk_dir_for_cherkasy
from ukraine.khmelnytsky.crawler import KhmelnytskySpider
from ukraine.khmelnytsky.post_processor import post_process_khmelnytsky
from ukraine.khmelnytsky.utils import mk_dir as mk_dir_for_khmelnytsky
from ukraine.mykolaiv.crawler import MykolaivSpider
from ukraine.mykolaiv.post_processor import post_process_mykolaiv
from ukraine.mykolaiv.utils import mk_dir as mk_dir_for_mykolaiv
from ukraine.sumy.crawler import SumySpider
from ukraine.sumy.utils import mk_dir as mk_dir_for_sumy
from ukraine.zhytomyr.crawler import crawl_zhytomyr
from ukraine.zhytomyr.utils import mk_dir as mk_dir_for_zhytomyr
#
#
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
        post_process_cherkasy()
    except Exception as e:
        print('error while processing raw cherkasy files')
        print(e)

    try:
        post_process_mykolaiv()
    except Exception as e:
        print('error while processing raw mykolaiv files')
        print(e)

    try:
        post_process_khmelnytsky()
    except Exception as e:
        print("error while processing raw khmelnytsky files")
        print(e)

    try:
        mk_dir_for_zhytomyr()
        crawl_zhytomyr()
    except Exception as e:
        print("Failed to scrape outage data of Ukraine Zhytomyr because")
        print(e)

    try:
        crawl_adamaoua()
        crawl_centre()
        crawl_littoral()
        crawl_douala()
        crawl_ouest()
        crawl_nord()
        crawl_nord_ouest()
        crawl_sud()
        crawl_est()
        crawl_yaounde()
        crawl_sud_ouest()
    except Exception as e:
        print("Failed to scrape outage data of Cameroon because")
        print(e)


    # this is an inactive website
    # tnebnet = Tangedco()
    # tnebnet.scrape()



    print("ALL DONE")


if __name__ == "__main__":
    scrape()
