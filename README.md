# Portscanner API

FastAPI 製ポートスキャン API  
Selenium(Chromedriver)のスクリーンショット撮影機能付き

## 使い方

- サーバーの起動

```bash
gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0
```

- `/scan`

```
GET http://(server_ip):(port)/scan?ip=(scan_ip)
```

戻り値

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

環境変数に

```bash
SCREENSHOT_SAVE_PATH="(スクリーンショット保存先)"
LOG_PATH="(ログ保存先)"
```

を登録  
どちらかが登録されていない場合は.env ファイルを読み込む

## チューニング

- オープンできるファイル数(->ソケット数)を増やす

```bash
ulimit -n 4096
```

- gunicorn の worker を増やす

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0
```

タイムアウトの恐れがあるので、改善するとは限らない

- スクリーンショット撮影に使う、Chrome の同時起動数を増やす

```bash
SCREENSHOT_THREADS_NUM=(数: デフォルトは3)
```

を環境変数に追加

- スクリーンショット撮影時の待機時間を変更

```bash
SCREENSHOT_WAIT_TIME=(秒: デフォルトは10)
```

を環境変数に追加
