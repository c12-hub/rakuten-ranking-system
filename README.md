# 日本乐天排行榜抓取系统

基于 Rakuten Ichiba Ranking API 抓取指定 `genreId` 的 Top100 排行榜，并导出 CSV 和 Excel。

## 功能

- 使用 Rakuten Ichiba Ranking API
- 默认抓取 `genreId=100371`
- 支持分页、自动重试、自动去重
- 自动生成 CSV 和 Excel
- 输出到 `output/`
- 支持 GitHub Actions 每天云端自动抓取并提交结果
- 本地仍可用 `main.py` 手动运行

## GitHub Actions 云端自动抓取

项目已包含 workflow：

```text
.github/workflows/rakuten-ranking.yml
```

它会使用 Python 3.11，在 GitHub 云端每天自动运行：

```bash
python main.py --genre-id 100371
```

输出文件会保存到：

```text
output/
```

生成示例：

```text
output/ranking_100371_20260524.csv
output/ranking_100371_20260524.xlsx
```

workflow 成功后会自动 commit `output/*.csv` 和 `output/*.xlsx` 到 GitHub 仓库。

## 设置 GitHub Secrets

进入你的 GitHub 仓库页面：

1. 打开 `Settings`
2. 打开 `Secrets and variables`
3. 点击 `Actions`
4. 点击 `New repository secret`
5. 添加以下两个 Secrets：

```text
RAKUTEN_APPLICATION_ID
RAKUTEN_AFFILIATE_ID
```

说明：

- `RAKUTEN_APPLICATION_ID`：必填，Rakuten Developers 后台申请的 applicationId。
- `RAKUTEN_AFFILIATE_ID`：选填，如果没有 affiliateId，可以创建为空值或不配置；程序会自动跳过。

## 开启自动提交权限

如果 workflow 提交失败，请检查仓库权限：

1. 打开 `Settings`
2. 打开 `Actions`
3. 打开 `General`
4. 找到 `Workflow permissions`
5. 选择 `Read and write permissions`
6. 保存设置

workflow 文件里已经配置：

```yaml
permissions:
  contents: write
```

## 手动运行 Workflow

进入 GitHub 仓库：

1. 打开 `Actions`
2. 选择 `Rakuten Ranking`
3. 点击 `Run workflow`
4. 选择分支
5. 再次点击 `Run workflow`

运行完成后，查看仓库里的 `output/` 文件夹。

## 本地运行

本地运行仍然兼容。先安装依赖：

```bash
pip install -r requirements.txt
```

复制配置模板：

```bash
copy .env.example .env
```

编辑 `.env`：

```env
RAKUTEN_APPLICATION_ID=你的Rakuten applicationId
RAKUTEN_AFFILIATE_ID=
OUTPUT_DIR=output
DEFAULT_GENRE_IDS=100371
DAILY_RUN_TIME=02:00
RAKUTEN_USE_SYSTEM_PROXY=false
RAKUTEN_REQUEST_TIMEOUT=60
HTTP_PROXY=
HTTPS_PROXY=
```

手动抓取：

```bash
python main.py --genre-id 100371
```

如果不传 `--genre-id`，程序会读取 `.env` 里的 `DEFAULT_GENRE_IDS`：

```bash
python main.py
```

## 换 genreId

本地换类目：

```bash
python main.py --genre-id 551167
```

GitHub Actions 换类目时，修改 `.github/workflows/rakuten-ranking.yml` 中的两处 `100371`：

```yaml
DEFAULT_GENRE_IDS: "100371"
run: python main.py --genre-id 100371
```

## 常用类目 genreId 示例

| genreId | 类目 |
| --- | --- |
| `0` | 全部类目 |
| `100371` | レディースファッション / 女装 |
| `551177` | メンズファッション / 男装 |
| `216131` | バッグ・小物・ブランド雑貨 |
| `558885` | 靴 |
| `100227` | 食品 |
| `551167` | スイーツ・お菓子 |
| `100316` | 水・ソフトドリンク |
| `100804` | インテリア・寝具・収納 |
| `215783` | 日用品雑貨・文房具・手芸 |
| `100939` | 美容・コスメ・香水 |
| `100938` | ダイエット・健康 |
| `562637` | 家電 |
| `211742` | TV・オーディオ・カメラ |
| `200162` | 本・雑誌・コミック |
| `101164` | おもちゃ |
| `101070` | スポーツ・アウトドア |
| `101213` | ペット・ペットグッズ |

## 输出字段

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

## API Endpoint

程序优先使用新版 endpoint：

```text
https://openapi.rakuten.co.jp/ichibaranking/api/IchibaItem/Ranking/20220601
```

如果新版 endpoint 超时，会自动尝试旧 endpoint：

```text
https://app.rakuten.co.jp/services/api/IchibaItem/Ranking/20220601
```
