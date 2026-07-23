# Romania Power Outage Data (Retele Electrice)

> Note: this file previously contained a copy of the Germany (Störungsauskunft) documentation, which wrongly implied Romania uses that platform. The actual backend is an Esri ArcGIS FeatureServer. Rewritten from code evidence 2026-07-16.

## Source

Retele Electrice (part of the PPC group, formerly Enel Romania) publishes outages on an interactive map:

🔗 https://www.reteleelectrice.ro/en/outages/

The map is backed by an Esri ArcGIS FeatureServer, identified through browser developer tools:

```
https://services-eu1.arcgis.com/ZugzWQbNk6XT3BMo/arcgis/rest/services/OutagesMapViewLayer/FeatureServer/0/query
```

This is the same Esri ArcGIS platform pattern used by the Spain (edistribucion, naturgy) and Italy (edistribuzione) scrapers — Enel runs Spain and Italy off a shared instance, and the query shape here matches that family.

## Data Retrieval

`scrape.py` queries the FeatureServer layer with `f=json`, `outFields=*`, `returnGeometry=false`, filtering on the `causa_disa_en` attribute:

- `causa_disa_en = 'Accidental'` — unplanned outages
- `causa_disa_en = 'Planned'` — planned outages

Both types are fetched on every run. Results are paginated 1000 records at a time via `resultOffset` / `resultRecordCount`, with a random 0.5–1.5s delay between pages. Pagination stops when a page returns no features or fewer than 1000.

No authentication is required.

## Output Behavior

- **Raw** (`scrape.py`): the concatenated `attributes` objects of all features, written as `power_outages.RO.retele_electric.raw.<YYYY-MM-DD>.json` and uploaded via the shared `Uploader` to `retele_electric/raw/<year>/<month>/`.
- **Processed** (`post_process.py`): downloads the same-day raw file, deduplicates records on the `fid0` attribute (last occurrence wins; records without `fid0` are kept), and uploads `power_outages.RO.retele_electric.processed.<YYYY-MM-DD>.json` to `retele_electric/processed/<year>/<month>/`.
- `post_process.py` accepts an optional `YYYY-MM-DD` argument to reprocess a past date.

## Notable Fields

Records carry the layer's full attribute set (`outFields=*`). Fields observed in use by the code:

- `fid0` – unique record identifier, used for deduplication.
- `causa_disa_en` – outage cause in English; the scraper filters on `Accidental` and `Planned`.
- `num_cli_di` – used as the API sort key (`orderByFields=num_cli_di DESC`); appears to be the number of affected clients.

For the complete current attribute list, inspect a raw output file or query the FeatureServer layer metadata.

## Other Notes

- `crawler.py` is an earlier standalone version of the fetch logic (CSV/pandas based, unplanned outages only). The production path is `scrape.py` → `post_process.py`; the Airflow DAG (`romania_retele_electric`, every 4 hours) does not run `crawler.py`.
- The `where` filter means records with other `causa_disa_en` values (if any exist) are not collected.
- Timestamps in attributes are as provided by the ArcGIS layer; verify timezone semantics before analysis.
