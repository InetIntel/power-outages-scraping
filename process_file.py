from nigeria.ikeja.process_Ikeja import Process_Ikeja
from pakistan.quetta.process_quetta import Process_quetta
from india.goa.process_GOA import Process_GOA
from india.rajdhani_weekly.process_rajdhani_weekly import Process_rajdhani_weekly
from india.tnpdcl.process_tnpdcl import Process_tnpdcl
from india.npp.process_npp import Process_Npp
from india.bses_rajdhani.process_rajdhani import Process_Rajdhani
from india.bses_yamuna.process_yamuna import Process_Yamuna
from india.tata.process_tata import Process_tata

def input_country():
    country_input = False
    country_dict = {"india": "IND", "nigeria": "NG", "pakistan": "PK"}
    while not country_input:
        country = input("Please enter country name from [india, nigeria, pakistan]: ").lower()
        if country in country_dict:
            country_input = True
            country_code = country_dict[country]
    return country, country_code

def input_year():
    year_input = False
    while not year_input:
        year = input("Enter a year: ")
        if 2000 <= int(year) <= 2100:
            year_input = True
    return year


def input_month():
    month_input = False
    while not month_input:
        month = input("Enter a month: ")
        if 1 <= int(month) <= 12:
            month_input = True
            month = month.zfill(2)
    return month


def input_day():
    day_input = False
    while not day_input:
        day = input("Enter a day: ")
        if 1 <= int(day) <= 31:
            day_input = True
            day = day.zfill(2)
    return day


def india_provider():
    provider_input = False
    provider_list = ["goa", "npp", "rajdhani_weekly", "tata", "tnpdcl", "bses_rajdhani", "bses_yamuna"]
    while not provider_input:
        provider = input("Please enter a provider from [goa, npp, rajdhani_weekly, tata, tnpdcl, bses_rajdhani, bses_yamuna]: ").lower()
        if provider in provider_list:
            provider_input = True
    return provider


def nigeria_provider():
    provider_input = False
    provider_list = ["ikeja"]
    while not provider_input:
        provider = input("Please enter a provider from [ikeja]: ").lower()
        if provider in provider_list:
            provider_input = True
    return provider


def pakistan_provider():
    provider_input = False
    provider_list = ["quetta"]
    while not provider_input:
        provider = input("Please enter a provider from [quetta]: ").lower()
        if provider in provider_list:
            provider_input = True
    return provider


def report_name():
    report_input = False
    report_dic = {"1": "dgr10", "2": "dgr11"}
    while not report_input:
        report_num = input("Please enter a number to select a report from [1. dgr10, 2. dgr11]: ")
        if report_num == "1" or report_num == "2":
            report = report_dic[report_num]
            report_input = True
    return report



if __name__ == "__main__":

    country, country_code = input_country()

    if country == "india":
        provider = india_provider()
    elif country == "nigeria":
        provider = nigeria_provider()
    elif country == "pakistan":
        provider = pakistan_provider()

    if provider == "npp":
        report = report_name()

    year = input_year()
    month = input_month()
    day = input_day()
    date = year + "-" + month + "-" + day

    file_path = country + "/" + provider + "/raw/" + year + "/" + month + "/"
    file_name = "power_outages." + country_code + "." + provider + ".raw." + date + "."
    # save_path = country + "/" + provider + "/processed/" + year + "/" + month + "/"
    # save_file_name = "power_outages." + country_code + "." + provider + ".processed." + date + "."
    if provider == "npp":
        file_name += report + "-" + date + ".xls"
    elif provider == "tnpdcl":
        file_name += "xlsx"
    else:
        file_name += "html"

    if provider == "goa":
        process = Process_GOA(year, month, date, file_path + file_name)
        process.run()

    elif provider == "npp":
        process = Process_Npp(year, month, date, file_path + file_name, report + "-" + date)
        process.run()

    elif provider == "rajdhani_weekly":
        process = Process_rajdhani_weekly(year, month, date, file_path + file_name)
        process.run()

    elif provider == "tata":
        process = Process_tata(year, month, date, file_path + file_name)
        process.run()

    elif provider == "tnpdcl":
        process = Process_tnpdcl(year, month, date, file_path + file_name)
        process.run()

    elif provider == "bses_rajdhani":
        process = Process_Rajdhani(year, month, date, file_path + file_name)
        process.run(provider)

    elif provider == "bses_yamuna":
        process = Process_Yamuna(year, month, date, file_path + file_name)
        process.run(provider)

    elif provider == "ikeja":
        process = Process_Ikeja(year, month, date, file_path + file_name)
        process.run()

    elif provider == "quetta":
        process = Process_quetta(year, month, date, file_path + file_name)
        process.run()








