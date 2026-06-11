
# Protection

Protected by cloudflare, performs check on login
SPA application, javascript needed for rendering

## Pagination

Example list url
```
https://sirup.inaproc.id/sirup/caripaketctr/search?tahunAnggaran=2026&jenisPengadaan=&metodePengadaan=&minPagu=&maxPagu=&bulan=&lokasi=&kldi=&pdn=&ukm=&draw=1&columns%5B0%5D%5Bdata%5D=&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=false&columns%5B0%5D%5Borderable%5D=false&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=paket&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=pagu&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=jenisPengadaan&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=isPDN&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=isUMK&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=metode&columns%5B6%5D%5Bname%5D=&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B7%5D%5Bdata%5D=pemilihan&columns%5B7%5D%5Bname%5D=&columns%5B7%5D%5Bsearchable%5D=true&columns%5B7%5D%5Borderable%5D=true&columns%5B7%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B7%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B8%5D%5Bdata%5D=kldi&columns%5B8%5D%5Bname%5D=&columns%5B8%5D%5Bsearchable%5D=true&columns%5B8%5D%5Borderable%5D=true&columns%5B8%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B8%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B9%5D%5Bdata%5D=satuanKerja&columns%5B9%5D%5Bname%5D=&columns%5B9%5D%5Bsearchable%5D=true&columns%5B9%5D%5Borderable%5D=true&columns%5B9%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B9%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B10%5D%5Bdata%5D=lokasi&columns%5B10%5D%5Bname%5D=&columns%5B10%5D%5Bsearchable%5D=true&columns%5B10%5D%5Borderable%5D=true&columns%5B10%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B10%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B11%5D%5Bdata%5D=id&columns%5B11%5D%5Bname%5D=&columns%5B11%5D%5Bsearchable%5D=true&columns%5B11%5D%5Borderable%5D=true&columns%5B11%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B11%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=5&order%5B0%5D%5Bdir%5D=DESC&start=0&length=10&search%5Bvalue%5D=&search%5Bregex%5D=false&_=1781104155874
```

parsed

```python
from urllib.parse import urlsplit, parse_qsl

url = "https://sirup.inaproc.id/sirup/caripaketctr/search?tahunAnggaran=2026&jenisPengadaan=&metodePengadaan=&minPagu=&maxPagu=&bulan=&lokasi=&kldi=&pdn=&ukm=&draw=1&columns%5B0%5D%5Bdata%5D=&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=false&columns%5B0%5D%5Borderable%5D=false&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=paket&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=pagu&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=jenisPengadaan&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=isPDN&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=isUMK&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=metode&columns%5B6%5D%5Bname%5D=&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B7%5D%5Bdata%5D=pemilihan&columns%5B7%5D%5Bname%5D=&columns%5B7%5D%5Bsearchable%5D=true&columns%5B7%5D%5Borderable%5D=true&columns%5B7%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B7%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B8%5D%5Bdata%5D=kldi&columns%5B8%5D%5Bname%5D=&columns%5B8%5D%5Bsearchable%5D=true&columns%5B8%5D%5Borderable%5D=true&columns%5B8%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B8%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B9%5D%5Bdata%5D=satuanKerja&columns%5B9%5D%5Bname%5D=&columns%5B9%5D%5Bsearchable%5D=true&columns%5B9%5D%5Borderable%5D=true&columns%5B9%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B9%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B10%5D%5Bdata%5D=lokasi&columns%5B10%5D%5Bname%5D=&columns%5B10%5D%5Bsearchable%5D=true&columns%5B10%5D%5Borderable%5D=true&columns%5B10%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B10%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B11%5D%5Bdata%5D=id&columns%5B11%5D%5Bname%5D=&columns%5B11%5D%5Bsearchable%5D=true&columns%5B11%5D%5Borderable%5D=true&columns%5B11%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B11%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=5&order%5B0%5D%5Bdir%5D=DESC&start=0&length=10&search%5Bvalue%5D=&search%5Bregex%5D=false&_=1781104155874"

# --- parsed URL parts ---
parts = urlsplit(url)
scheme = parts.scheme  # "https"
netloc = parts.netloc  # "sirup.inaproc.id"
path = parts.path  # "/sirup/caripaketctr/search"
base_url = f"{scheme}://{netloc}{path}"

# --- query params, urldecoded, as a dict ---
params = dict(parse_qsl(parts.query, keep_blank_values=True))

print(params)
# expanded dict literal (same content as `params`)
```

```json
{
    "tahunAnggaran": "2026",
    "jenisPengadaan": "",
    "metodePengadaan": "",
    "minPagu": "",
    "maxPagu": "",
    "bulan": "",
    "lokasi": "",
    "kldi": "",
    "pdn": "",
    "ukm": "",
    "draw": "1",
    "columns[0][data]": "",
    "columns[0][name]": "",
    "columns[0][searchable]": "false",
    "columns[0][orderable]": "false",
    "columns[0][search][value]": "",
    "columns[0][search][regex]": "false",
    "columns[1][data]": "paket",
    "columns[1][name]": "",
    "columns[1][searchable]": "true",
    "columns[1][orderable]": "true",
    "columns[1][search][value]": "",
    "columns[1][search][regex]": "false",
    "columns[2][data]": "pagu",
    "columns[2][name]": "",
    "columns[2][searchable]": "true",
    "columns[2][orderable]": "true",
    "columns[2][search][value]": "",
    "columns[2][search][regex]": "false",
    "columns[3][data]": "jenisPengadaan",
    "columns[3][name]": "",
    "columns[3][searchable]": "true",
    "columns[3][orderable]": "true",
    "columns[3][search][value]": "",
    "columns[3][search][regex]": "false",
    "columns[4][data]": "isPDN",
    "columns[4][name]": "",
    "columns[4][searchable]": "true",
    "columns[4][orderable]": "true",
    "columns[4][search][value]": "",
    "columns[4][search][regex]": "false",
    "columns[5][data]": "isUMK",
    "columns[5][name]": "",
    "columns[5][searchable]": "true",
    "columns[5][orderable]": "true",
    "columns[5][search][value]": "",
    "columns[5][search][regex]": "false",
    "columns[6][data]": "metode",
    "columns[6][name]": "",
    "columns[6][searchable]": "true",
    "columns[6][orderable]": "true",
    "columns[6][search][value]": "",
    "columns[6][search][regex]": "false",
    "columns[7][data]": "pemilihan",
    "columns[7][name]": "",
    "columns[7][searchable]": "true",
    "columns[7][orderable]": "true",
    "columns[7][search][value]": "",
    "columns[7][search][regex]": "false",
    "columns[8][data]": "kldi",
    "columns[8][name]": "",
    "columns[8][searchable]": "true",
    "columns[8][orderable]": "true",
    "columns[8][search][value]": "",
    "columns[8][search][regex]": "false",
    "columns[9][data]": "satuanKerja",
    "columns[9][name]": "",
    "columns[9][searchable]": "true",
    "columns[9][orderable]": "true",
    "columns[9][search][value]": "",
    "columns[9][search][regex]": "false",
    "columns[10][data]": "lokasi",
    "columns[10][name]": "",
    "columns[10][searchable]": "true",
    "columns[10][orderable]": "true",
    "columns[10][search][value]": "",
    "columns[10][search][regex]": "false",
    "columns[11][data]": "id",
    "columns[11][name]": "",
    "columns[11][searchable]": "true",
    "columns[11][orderable]": "true",
    "columns[11][search][value]": "",
    "columns[11][search][regex]": "false",
    "order[0][column]": "5",
    "order[0][dir]": "DESC",
    "start": "0",
    "length": "10",
    "search[value]": "",
    "search[regex]": "false",
    "_": "1781104155874",
}
```

```md
Diff between the two pages — only 3 params change:

  ┌───────┬───────────────┬───────────────┬─────────────────────────┐
  │ param │    page_1     │    page_2     │         meaning         │
  ├───────┼───────────────┼───────────────┼─────────────────────────┤
  │ start │ 0             │ 10            │ row offset (pagination) │
  ├───────┼───────────────┼───────────────┼─────────────────────────┤
  │ draw  │ 1             │ 2             │ DataTables draw counter │
  ├───────┼───────────────┼───────────────┼─────────────────────────┤
  │ _     │ 1781104155874 │ 1781103529729 │ cache-bust timestamp    │
  └───────┴───────────────┴───────────────┴─────────────────────────┘

  Everything else is identical. So start is the real pagination control — page N = start = (N-1) * length (here length=10). draw just increments per request and _ is a throwaway timestamp; neither affects which rows you get, so for scraping you only need to vary start (and bump
  draw/_ to be polite/realistic).
```

Comparing to page when 100 items selected:

```
This URL differs in 4 params:

  ┌────────┬────────┬──────┬────────────────────────────────────────────────────────┐
  │ param  │ page_1 │ this │                        meaning                         │
  ├────────┼────────┼──────┼────────────────────────────────────────────────────────┤
  │ length │ 10     │ 100  │ page size → returns 100 rows                           │
  ├────────┼────────┼──────┼────────────────────────────────────────────────────────┤
  │ start  │ 0      │ 100  │ offset = skip first 100 rows (so this is rows 101–200) │
  ├────────┼────────┼──────┼────────────────────────────────────────────────────────┤
  │ draw   │ 1      │ 3    │ DataTables draw counter                                │
  ├────────┼────────┼──────┼────────────────────────────────────────────────────────┤
  │ _      │ …      │ …    │ cache-bust timestamp                                   │
  └────────┴────────┴──────┴────────────────────────────────────────────────────────┘

  So length is what controls how many rows come back — set length=100 and you get 100 per request. Note start=100 here, so it's actually fetching the second batch of 100 (rows 101–200), not the first. For the first 100 you'd use start=0&length=100.
  ```


Example response content:

```json
{
    "recordsFiltered": 3210751,
    "data": [
        {
            "idBulan": 1,
            "pagu": 45553000,
            "satuanKerja": "Badan Perencanaan Pembangunan Daerah",
            "isPDN": true,
            "idlokasi": 0,
            "idKldi": "D76",
            "metode": "Pengadaan Langsung",
            "sumberDana": "APBD",
            "kldi": "Provinsi Gorontalo",
            "isUMK": true,
            "idsLokasi": "15052",
            "id_referensi": 729,
            "lokasi": "Gorontalo, Gorontalo (Kota)",
            "jenisPengadaan": "Barang",
            "idSatker": 415091,
            "pemilihan": "January 2026",
            "idMetode": 8,
            "id": 62466015,
            "idJenisPengadaan": 1,
            "paket": "Pengadaan Bahan-Bahan Bangunan dan Konstruksi (Bahan Baku Bangunan)",
            "pds": false
        },
        {
```

It seems year in details page always 2020, `id` from list results

```
https://sirup.inaproc.id/sirup/rup/detailPaketPenyedia2020?idPaket=62466015
```
