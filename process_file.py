from nigeria.ikeja.process_Ikeja import Process_Ikeja
from pakistan.quetta.process_quetta import Process_quetta
from india.goa.process_GOA import Process_GOA
from india.rajdhani_weekly.process_rajdhani_weekly import Process_rajdhani_weekly
from india.tnpdcl.process_tnpdcl import Process_tnpdcl
from india.npp.process_npp import Process_Npp
from india.bses_rajdhani.process_rajdhani import Process_Rajdhani
from india.bses_yamuna.process_yamuna import Process_Yamuna
from india.tata.process_tata import Process_tata
import os
import argparse
from datetime import datetime, timedelta


countries = {"india": "IND", "nigeria": "NG", "pakistan": "PK"}
india_providers = ["goa", "npp", "rajdhani_weekly", "tata", "tnpdcl", "bses_rajdhani", "bses_yamuna"]
nigeria_providers = ["ikeja"]
pakistan_providers = ["quetta"]


def date_validate(date):
    validate = True
    date_list = date.split("-")
    if len(date_list) != 3:
        print("Date format is invalid.")
        return False
    year = date_list[0]
    if not (2000 <= int(year) <= 2100):
        print("Year is invalid.")
        validate = False
    month = date_list[1]
    if not (1 <= int(month) <= 12):
        print("Month is invalid.")
        validate = False
    day = date_list[2]
    if not (1 <= int(day) <= 31):
        print("Day is invalid.")
        validate = False
    return validate


def provider_validate(provider, country):
    validate = True
    if country == "india" and provider not in india_providers:
        print("Provider does not exist in the provider list for India.")
        validate = False
    elif country == "pakistan" and provider not in pakistan_providers:
        print("Provider does not exist in the provider list for Pakistan.")
        validate = False
    elif country == "nigeria" and provider not in nigeria_providers:
        print("Provider does not exist in the provider list for Nigeria.")
        validate = False
    return validate


def validate(args):
    validate = True
    country = args.country.lower()
    if country not in countries:
        print("Please enter country name from india, nigeria, pakistan.")
        validate = False
    provider = args.provider.lower()
    if not provider_validate(provider, country):
        validate = False
    start_date = args.start_date
    if not date_validate(start_date):
        validate = False
    end_date = args.end_date
    if not date_validate(end_date):
        validate = False
    if start_date > end_date:
        print("end date cannot be earlier than start date")
        return False
    return validate


def main(args):
    country = args.country.lower()
    provider = args.provider.lower()
    country_code = countries[country]
    start_date = args.start_date
    end_date = args.end_date
    while end_date >= start_date:
        date = start_date
        date_list = date.split("-")
        year = date_list[0]
        month = date_list[1]

        folder = country + "/" + provider + "/raw/" + year + "/" + month + "/"
        file_name = "power_outages." + country_code + "." + provider + ".raw." + date + "."

        if provider == "tnpdcl":
            file_name += "xlsx"
        elif provider != "npp":
            file_name += "html"

        file_path = folder + file_name
        if provider == "npp":
            file_path = folder + file_name + "dgr10-" + date + ".xls"
            report_name = "dgr10-" + date
            process_npp(year, month, date, file_path, report_name)
            file_path = folder + file_name + "dgr11-" + date + ".xls"
            report_name = "dgr11-" + date
            process_npp(year, month, date, file_path, report_name)
        else:
            file_processor(provider, year, month, date, file_path)
        start_date = increase_one_day(start_date)


def increase_one_day(date):
    next_day = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    return next_day



def process_npp(year, month, date, file_path, report_name):
    if not os.path.exists(file_path):
        print(f"File {file_path} dose not exist!")
        return None
    process = Process_Npp(year, month, date, file_path, report_name)
    process.run()


def file_processor(provider, year, month, date, file_path):

    if not os.path.exists(file_path):
        print(f"File {file_path} dose not exist!")
        return None

    if provider == "goa":
        process = Process_GOA(year, month, date, file_path)
        process.run()

    elif provider == "rajdhani_weekly":
        process = Process_rajdhani_weekly(year, month, date, file_path)
        process.run()

    elif provider == "tata":
        process = Process_tata(year, month, date, file_path)
        process.run()

    elif provider == "tnpdcl":
        process = Process_tnpdcl(year, month, date, file_path)
        process.run()

    elif provider == "bses_rajdhani":
        process = Process_Rajdhani(year, month, date, file_path)
        process.run(provider)

    elif provider == "bses_yamuna":
        process = Process_Yamuna(year, month, date, file_path)
        process.run(provider)

    elif provider == "ikeja":
        process = Process_Ikeja(year, month, date, file_path)
        process.run()

    elif provider == "quetta":
        process = Process_quetta(year, month, date, file_path)
        process.run()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Process raw outage data files with a date range.')

    parser.add_argument("--country", type=str, required=True, help="enter a country from india, nigeria, pakistan")
    parser.add_argument("--provider", type=str, required=True, help="enter a power provider")
    parser.add_argument("--start_date", type=str, required=True, help="enter a start date in format xxxx-xx-xx")
    parser.add_argument("--end_date", type=str, required=True, help="enter a end date in format xxxx-xx-xx")
    args = parser.parse_args()

    if validate(args):
        main(args)












