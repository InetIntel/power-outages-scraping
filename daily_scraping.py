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
from india.bses.bses import Bses
from india.tata.tata import Tata


def scrape():

    # India
    tnebltd = Tnpdcl()
    tnebltd.scrape()

    rajdhani_weekly = RajdhaniWeekly()
    rajdhani_weekly.scrape()

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