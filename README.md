# Rakuten Ranking System

Rakuten Ranking API crawler for `genreId=100371`. It can run locally on Windows, and the GitHub Actions workflow is kept as a backup because Rakuten currently blocks GitHub-hosted runner IPs.

## Current Recommended Plan

Use the local Windows/browser workflow. This does not require Python network requests:

1. Open `browser_test.html` in your browser.
2. Fill `applicationId`, `accessKey`, and optional `affiliateId`.
3. Click `Save and Fetch`.
4. View product name, price, shop, and image directly in the page.
5. Click `Download JSON` or `Export CSV`.

Alternative manual flow:

1. Generate a browser API URL with `debug_url.py`.
2. Open the URL in your browser.
3. If the browser returns JSON, save it as `downloaded_rakuten.json`.
4. Run `import_json.py` to convert the JSON into CSV and Excel.

GitHub Actions is still in `.github/workflows/rakuten-ranking.yml`, but treat it as backup only. Rakuten returned:

```text
Access from this IP address is not allowed for webservice.rakuten.co.jp
```

for GitHub-hosted runner IPs.

## Install

```bash
pip install -r requirements.txt
```

Create `.env`:

```bash
copy .env.example .env
```

Fill these values in `.env`:

```env
RAKUTEN_APPLICATION_ID=your_rakuten_application_id
RAKUTEN_ACCESS_KEY=your_rakuten_access_key
RAKUTEN_AFFILIATE_ID=
OUTPUT_DIR=output
DEFAULT_GENRE_IDS=100371
DAILY_RUN_TIME=02:00
RAKUTEN_USE_SYSTEM_PROXY=false
RAKUTEN_REQUEST_TIMEOUT=60
HTTP_PROXY=
HTTPS_PROXY=
```

## Local Windows Run

If your local network can access Rakuten API:

```bash
python main.py --genre-id 100371
```

Output:

```text
output/ranking_100371_YYYYMMDD.csv
output/ranking_100371_YYYYMMDD.xlsx
```

## Browser Manual URL Test

### Pure Browser Page

Open this file directly in your browser:

```text
browser_test.html
```

The page uses browser JavaScript `fetch()` to call Rakuten API and renders:

- 商品名
- 价格
- 店铺
- 图片

It can also download:

- `downloaded_rakuten.json`
- `ranking_100371_YYYYMMDD.csv`

Browser note: JavaScript cannot truly override protected request headers such as `Origin` and `User-Agent`. The page includes the requested header object where browsers allow it and uses the `referrer` option for Referer.

### URL Generator

Print a masked URL:

```bash
python debug_url.py --genre-id 100371
```

Print the real URL for browser copy/paste:

```bash
python debug_url.py --genre-id 100371 --show-secret
```

Copy the real URL into your browser. If it opens JSON successfully, save the page as:

```text
downloaded_rakuten.json
```

## Import Browser-Downloaded JSON

Convert `downloaded_rakuten.json` into CSV and Excel:

```bash
python import_json.py --input downloaded_rakuten.json --genre-id 100371
```

Output:

```text
output/ranking_100371_YYYYMMDD.csv
output/ranking_100371_YYYYMMDD.xlsx
```

## GitHub Actions Backup

The workflow remains available:

```text
.github/workflows/rakuten-ranking.yml
```

It supports:

- Daily scheduled run
- Manual `workflow_dispatch`
- Python 3.11
- CSV and Excel output under `output/`
- Auto commit of output files

Required GitHub Secrets:

```text
RAKUTEN_APPLICATION_ID
RAKUTEN_ACCESS_KEY
RAKUTEN_AFFILIATE_ID
```

However, GitHub-hosted runner IPs may be blocked by Rakuten. Use this workflow only as a backup.

## Output Fields

- 商品名
- 商品价格
- 店铺名
- 评论数
- 评分
- 商品URL
- 主图URL
- 排名
- 类目ID
- 抓取时间

## Common genreId Examples

| genreId | Category |
| --- | --- |
| `0` | All categories |
| `100371` | Ladies fashion |
| `551177` | Mens fashion |
| `216131` | Bags, accessories, brand goods |
| `558885` | Shoes |
| `100227` | Food |
| `551167` | Sweets |
| `100316` | Water and soft drinks |
| `100804` | Interior, bedding, storage |
| `215783` | Daily goods, stationery, crafts |
| `100939` | Beauty, cosmetics, perfume |
| `100938` | Diet, health |
| `562637` | Home appliances |
| `211742` | TV, audio, camera |
| `200162` | Books, magazines, comics |
| `101164` | Toys |
| `101070` | Sports, outdoor |
| `101213` | Pet goods |
