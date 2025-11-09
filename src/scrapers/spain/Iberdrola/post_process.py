# parse_ide_planned_outages.py
from pathlib import Path
import re
import pandas as pd
import pdfplumber
from pathlib import Path
from datetime import datetime, date, time
import json
import os
from utils import Uploader

# Data in table formatted like:
# <MUNICIPIO> <DD/MM/YYYY> <HH:MM> <HH:MM> [optional address chunk]
ROW_START = re.compile(
    r"^(?P<municipio>[A-ZÁÉÍÓÚÜÑ/ \-]+?)\s+"
    r"(?P<fecha>\d{2}/\d{2}/\d{4})\s+"
    r"(?P<hora_inicio>\d{2}:\d{2})\s+"
    r"(?P<hora_fin>\d{2}:\d{2})(?:\s+(?P<direccion>.+))?$"
)

# Common street prefixes to catch wrapped address lines
ADDR_PREFIX = re.compile(
    r"^(?:Cl|Calle|Av|Avenida|Ps|Paseo|Pl|Plaza|Cr|Carretera|Ctra|Cam|Camino|Tr|Traves[ií]a|Pz|Pi|B[ºo]|Barrio)\b",
    re.IGNORECASE,
)

def extract_lines(pdf_path: Path):
    """
    Convert PDF to text for parsing.
    """
    lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            for line in txt.splitlines():
                line = line.strip()
                if not line:
                    continue
                # Skip page numbers between tables that span multiple pages
                if line.startswith("Página "):
                    continue
                lines.append(line)
    return lines

def province_from(lines, fallback_province: str) -> str:
    """
    Pulls province name from top of pdf

    Example:
        Zonas Afectodas: <Province Name>
    """
    # iterate through first 20 lines of pdf text looking for province name
    for ln in lines[:20]:
        province = re.search(r"Zonas Afectadas:\s*(.+)", ln, re.IGNORECASE)
        if province:
            return province.group(1).strip()
    # if not found, default to pdf file name
    return fallback_province

def parse_pdf(pdf_path: Path) -> pd.DataFrame:

    # get text data from pdf
    lines = extract_lines(pdf_path)

    # get province name from top of the file
    province = province_from(lines, pdf_path.stem)

    # collect completed rows as we read them
    rows = []
    # current row we're reading
    curr_row = None

    # iterate through each line of text
    for ln in lines:

        # if current line is part of table, collect the data
        table = ROW_START.match(ln)

        # if we're in a table
        if table:
            # finalize previous row
            if curr_row:
                curr_row["direccion"] = " | ".join(curr_row["direccion"]).strip()
                rows.append(curr_row)

            # build new outage record
            curr_row = {
                "province": province,
                "municipio": table.group("municipio").strip(),
                "fecha": table.group("fecha"),
                "hora_inicio": table.group("hora_inicio"),
                "hora_fin": table.group("hora_fin"),
                "direccion": [],
                "dso": "i-DE",
                "source_file": pdf_path.name,
            }

            # store addresses
            if table.group("direccion"):
                curr_row["direccion"].append(table.group("direccion").strip())

            # move to next line
            continue

        # If wrapped address lines, append them
        #if curr_row and (ADDR_PREFIX.match(ln) or (curr_row["direccion"] and ("," in ln or ":" in ln))):##########################
        if curr_row and (ADDR_PREFIX.match(ln) or (curr_row["direccion"] and (ln[0] == ',' or ln[0] == ':'))):
            curr_row["direccion"].append(ln)
            continue

    # finalize last open record if more addresses listed
    if curr_row:
        curr_row["direccion"] = " | ".join(curr_row["direccion"]).strip()
        rows.append(curr_row)

    # convert parsed records into a dataframe
    df = pd.DataFrame(rows, columns=[
        "province", "municipio", "fecha", "hora_inicio", "hora_fin", "direccion", "dso", "source_file"
    ])

    # Convert start and end times to Python time objects
    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"], format="%d/%m/%Y", errors="coerce")
        df["hora_inicio"] = pd.to_datetime(df["hora_inicio"], format="%H:%M", errors="coerce").dt.time
        df["hora_fin"] = pd.to_datetime(df["hora_fin"], format="%H:%M", errors="coerce").dt.time

    # return dataframe of outage data
    return df

def parse_folder(folder: Path) -> pd.DataFrame:
    """
    Takes the directory with the PDF's and returns a dataframe with all the outage data.
    """
    pdfs = sorted(Path(folder).glob("*.pdf"))
    frames = [parse_pdf(p) for p in pdfs]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

def df_to_json(df, filename="processed_output.json"):
    """
    Build the JSON list of outage records AND write it
    to the same directory as this script. Returns (records, out_path).
    """

    # store outage records as they're built
    records = []

    for _, row in df.iterrows():
        # ---- date/time assembly ----
        # fecha(date) -> date
        if isinstance(row["fecha"], (pd.Timestamp, datetime)):
            d = row["fecha"].date()
        else:
            d = pd.to_datetime(str(row["fecha"]), errors="coerce").date()

        # hora_inicio(start time) -> time
        if isinstance(row["hora_inicio"], time):
            t_start = row["hora_inicio"]
        else:
            t_start = pd.to_datetime(str(row["hora_inicio"]), format="%H:%M", errors="coerce").time()

        # hora_fin(end time) -> time
        if isinstance(row["hora_fin"], time):
            t_end = row["hora_fin"]
        else:
            t_end = pd.to_datetime(str(row["hora_fin"]), format="%H:%M", errors="coerce").time()

        # combine to datetimes
        start_dt = datetime.combine(d, t_start)
        end_dt = datetime.combine(d, t_end)

        # handle overnight windows (rare)
        if end_dt < start_dt:
            from datetime import timedelta
            end_dt = end_dt + timedelta(days=1)

        duration = (end_dt - start_dt).total_seconds() / 3600.0

        # ---- areas_affected ----
        # Currently addresses are being ignored, could not consistently parse from PDFs.
        # Would be good for future, can get household count from this data.
        parts = []
        if pd.notna(row.get("direccion", None)):
            parts = [p.strip() for p in str(row["direccion"]).split("|")]
            parts = [p for p in parts if p]  # drop empties

        areas = [f"{row['municipio']}"]

        line = {
            "start": str(start_dt),
            "end": str(end_dt),
            "duration_(hours)": f"{duration:.2f}",
            "event_category": "Planned",
            "country": "spain",
            "areas_affected": areas
        }
        records.append(line)

    # write json file to same directory as this script
    script_dir = Path(__file__).resolve().parent
    out_path = script_dir / filename
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)

    return records, str(out_path)

def upload():
    """
    Upload json to minio storage.
    """
    uploader = Uploader("spain") # create uploader to upload data to minio
    base = os.path.dirname(os.path.abspath(__file__))
    for root, _, files in os.walk(base):
        for file in files:
            if not file.lower().endswith(".json"):
                continue
            local_path = os.path.join(root, file)
            rel_path = os.path.relpath(local_path, base).replace("\\", "/")
            s3_path = f"iberdrola_planned/processed/{current_year}/{current_month}/{rel_path}"
            uploader.upload_file(local_path, s3_path)

if __name__ == "__main__":

    # Point this at folder of downloaded PDFs for parsing
    folder = Path("planned_outage_pdfs")

    # Parse the data from the PDFs
    if folder.exists():
        df = parse_folder(folder)
    else:
        print("PDF directory not found.")
        df = pd.DataFrame()

    # If data was parsed, save as json
    if df.empty:
        print("No data parsed.")
    else:

        # date for file name
        now = datetime.now()
        current_year = f"{now.year}"
        current_month = f"{now.month:02d}"
        current_day = f"{now.day:02d}"

        # save json to same directory as script
        filename = f"iberdrola_planned_processed_output_{current_month}_{current_day}_{current_year}.json"
        records, out_path = df_to_json(df, filename)
        print(f"JSON written to {out_path}")

        # upload json to minio
        upload()


