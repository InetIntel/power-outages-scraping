from nigeria.scrape_webpage import ScrapeWebpage
from pakistan.fesco import Fesco
from pakistan.hyderabad import Hyderabad
from pakistan.islamabad_xls import IslamabadXls
from pakistan.quetta import Quetta
from india.goa import Goa
from india.scrape_Rajdhani_weekly import ScrapeRajdhaniWeekly
from india.tangedco import Tangedco
from india.tnpdcl import Tnpdcl
from india.npp import Npp
from india.scrape_Rajdhani import ScrapeRajdhani
from india.tata import Tata


def scrape():

    tnebltd = Tnpdcl()
    tnebltd.scrape()



    bsesdelhi_weekly = ScrapeRajdhaniWeekly()
    bsesdelhi_weekly.scrape()

    tatapower = Tata()
    tatapower.scrape()

    goaelectricity = Goa()
    goaelectricity.scrape()

    npp = Npp()
    npp.scrape()

    bsesdelhi = ScrapeRajdhani()
    bsesdelhi.scrape()
    #
    # ikejaelectric = ScrapeWebpage()
    # ikejaelectric.scrape()
    #
    # fesco = Fesco()
    # fesco.scrape()
    #
    # hesco = Hyderabad()
    # hesco.scrape()
    #
    # iesco = IslamabadXls()
    # iesco.scrape()
    #
    # qesco = Quetta()
    # qesco.scrape()
    #

    # this is an inactive website
    # tnebnet = Tangedco()
    # tnebnet.scrape()



    print("ALL DONE")


if __name__ == "__main__":
    scrape()