# Rakuten Ranking System

This project converts Rakuten Ichiba Ranking API JSON into CSV and Excel.

Current recommended workflow:

1. Use Rakuten official API Test Form to request Ranking API.
2. Save the returned JSON as `downloaded_rakuten.json`.
3. Run `paste_json_to_excel.py`.
4. Read the generated files in `output/`.

The browser JavaScript page is no longer maintained because browser JavaScript cannot override protected headers such as `Referer`, `Origin`, and `User-Agent`.

## Install

```bash
pip install -r requirements.txt
```

## Official Test Form Workflow

Open the Rakuten official API documentation/Test Form:

```text
https://webservice.rakuten.co.jp/documentation/ichiba-item-ranking
```

Use the official Test Form on that page.

Recommended parameters:

```text
endpoint=https://app.rakuten.co.jp/services/api/IchibaItem/Ranking/20220601
genreId=100371
page=1
format=json
formatVersion=2
```

Use your Rakuten Web Service app credentials from the official dashboard:

```text
applicationId
affiliateId optional
```

Run the test in the official page. If it returns JSON successfully, save the full JSON response into this project folder as:

```text
downloaded_rakuten.json
```

Then convert it:

```bash
python paste_json_to_excel.py --input downloaded_rakuten.json --genre-id 100371
```

Output:

```text
output/ranking_100371_YYYYMMDD.csv
output/ranking_100371_YYYYMMDD.xlsx
```

## Local JSON Conversion

Default command:

```bash
python paste_json_to_excel.py
```

Custom input:

```bash
python paste_json_to_excel.py --input downloaded_rakuten.json --genre-id 100371 --output-dir output
```

The converter reads `Items` from Rakuten JSON and exports:

- CSV with UTF-8 BOM
- Excel `.xlsx`

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

## GitHub Actions Backup

The GitHub Actions workflow is kept only as backup:

```text
.github/workflows/rakuten-ranking.yml
```

Rakuten currently blocks GitHub-hosted runner IPs with:

```text
Access from this IP address is not allowed for webservice.rakuten.co.jp
```

So the official Test Form plus local JSON conversion is the safer workflow.

## Local API Scripts

The older local Python API crawler remains in the repository:

```bash
python main.py --genre-id 100371
```

It now tries endpoints in this order:

1. `https://app.rakuten.co.jp/services/api/IchibaItem/Ranking/20220601`
2. `https://openapi.rakuten.co.jp/ichibaranking/api/IchibaItem/Ranking/20220601`

The default app endpoint sends only `applicationId`, optional `affiliateId`, `genreId`, `page`, `format=json`, and `formatVersion=2`. It does not require `accessKey` or `Referer`.

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
