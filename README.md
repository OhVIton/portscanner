# Portscanner API

FastAPI 製ポートスキャン API  
Selenium(Chromedriver)のスクリーンショット撮影機能付き

## 使い方

- サーバーの起動
ワーカー数は増やさないこと！  
```bash
gunicorn main:app -k uvicorn.workers.UvicornWorker
```

- `/register`
  
```
GET http://(server_ip):(port)/register?ip=(scan_ip)
```
  
戻り値
```json
  {"job_uuid": job_uuid}
```
  
- `/get_result`
  
```
GET http://(server_ip):(port)/get_result?job_uuid=(scan_ip)
```
  
戻り値
  
取得成功時  
status_code = 404
```
[
    {
        "@protocol": "tcp",
        "@portid": "80",
        "state": {
            "@state": "open",
            "@reason": "syn-ack",
            "@reason_ttl": "0"
        },
        "service": {
            "@name": "http",
            "@method": "table",
            "@conf": "3"
        },
        "screenshot_uuid": "88fdbf9e-c0f0-4140-bc59-2b7a03a81f76"
    }...
]
```
  
処理中  
status_code = 202  
```
{job_uuid} is now processing
```  
  
job_uuidがない  
status_code = 404  
```
{job_uuid} was not found
```

- `/getimg`

```
GET http://(ip):(port)/getimg?img_uuid=(screenshot_uuid)
```

戻り値  
スクリーンショットのデータ

## インストール

```bash
pip3 install -r requirements.txt
```

環境変数に以下を登録(.env ファイルでも可。どちらかが登録されていない場合は.env ファイルを読み込む)

```bash
SCREENSHOT_SAVE_PATH="(スクリーンショット保存先)"
LOG_PATH="(ログ保存先)"
```

## チューニング

- オープンできるファイル数(->ソケット数)を増やす

```bash
ulimit -n 4096
```

- gunicorn の thread を増やす

```bash
gunicorn main:app --threads 4 -k uvicorn.workers.UvicornWorker
```

- スクリーンショット撮影に使う、Chrome の同時起動数を増やす
  環境変数に以下を追加  
  
```bash
SCREENSHOT_THREADS_NUM=(数: デフォルトは3)
```

- スクリーンショット撮影時の待機時間を変更
  環境変数に以下を追加  
  
```bash
SCREENSHOT_WAIT_TIME=(秒: デフォルトは10)
```
