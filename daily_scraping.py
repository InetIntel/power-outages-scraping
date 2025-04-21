from scrapy import cmdline

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

    # Nigeria
    try:
        ikeja = Ikeja()
        ikeja.scrape()
    except Exception as e:
        print("Failed to scrape outage data from IKEJA.")

    # Pakistan
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


    try:
        cmdline.execute("cd ukraine".split())
        cmdline.execute("sh craw_ukraine_daily.sh".split())
    except Exception as e:
        print("Failed to scrape outage data of Ukraine")


    # this is an inactive website
    # tnebnet = Tangedco()
    # tnebnet.scrape()



    print("ALL DONE")


if __name__ == "__main__":
    scrape()