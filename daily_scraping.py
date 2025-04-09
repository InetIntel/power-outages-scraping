from nigeria.Ikeja import Ikeja
from pakistan.fesco import Fesco
from pakistan.hyderabad import Hyderabad
from pakistan.iesco import Iesco
from pakistan.quetta import Quetta
from india.goa import Goa
from india.bses_weekly import BsesWeekly
from india.tangedco import Tangedco
from india.tnpdcl import Tnpdcl
from india.npp import Npp
from india.bses import Bses
from india.tata import Tata


def scrape():

    # India
    tnebltd = Tnpdcl()
    tnebltd.scrape()

    bses_weekly = BsesWeekly()
    bses_weekly.scrape()

    tatapower = Tata()
    tatapower.scrape()

    goaelectricity = Goa()
    goaelectricity.scrape()

    npp = Npp()
    npp.scrape()

    bses = Bses()
    bses.scrape()

    # Nigeria
    ikeja = Ikeja()
    ikeja.scrape()

    #Pakistan
    fesco = Fesco()
    fesco.scrape()

    hesco = Hyderabad()
    hesco.scrape()

    iesco = Iesco()
    iesco.scrape()

    qesco = Quetta()
    qesco.scrape()


    # this is an inactive website
    # tnebnet = Tangedco()
    # tnebnet.scrape()



    print("ALL DONE")


if __name__ == "__main__":
    scrape()