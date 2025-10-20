# X(Twitter) Media Downloader
X(Twitter)の特定のユーザーのメディアを全てダウンロードするツールです。  
gallery-dlに依存しているためgallery-dlが整備されなくなる、またはX(Twitter)側の設計変更によって機能しなくなる場合があります。

# 使い方
## cookieの取得
このツールを使うにはcookieの取得が必要です。  
以下のchrome拡張機能を使ってX(Twitter)のcookieを取得してください。  
[Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)

## .pyファイルを使う場合
仮想環境を作成して有効化しライブラリをダウンロード
```
python -m venv venv
./venv/scripts/activate
pip install -r requirements.txt
python x_media_downloader.py
```