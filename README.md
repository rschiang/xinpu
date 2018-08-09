Xinpu
=====

<ruby>新<rp>(</rp><rt>sìn</rt><rp>)</rp>埔<rp>(</rp><rt>bù</rt><rp>)</rp>是套會自動轉發新聞到噗浪河道的小程式。

安裝
----

(1) 將套件拷貝至本機。

    git clone https://github.com/rschiang/xinpu.git && cd xinpu
    pip install .

(2) 將噗浪的 OAuth token 寫入 `plurk.json` 設定檔中。（可以參考[範例](plurk.json.example)）

(3) 依照需求修改 `config.json`。

* `format`: 發佈噗浪內容時使用的格式。
* `throttle`: 為了避免進展太快造成眾人不便的防洪緩速時間。（秒）
* `backtrack`: 當沒有最近一次的更新紀錄時，從現在往前回溯的最長期限。（秒）
* `feeds`: 要同步的 RSS 動態。
  - `name`: 新聞來源的名稱。
  - `url`: RSS 連結網址。
  - `interval`: 擷取更新的時間間隔。（秒）
  - `options`: 擷取時的額外選項。
    + `link`: 設定為 `follow` 時，會自動解析並展開轉址過的新聞網址。
    + `extract`: 由頁面上的中繼資料擷取、而非仰賴 RSS 所提供的欄位陣列，支援 `image` 與 `description`。
    + `content_filter`: 要從新聞摘要中過濾的字串，以正規表達式表示。
    + `image_exclude`: 要排除的影像網址清單，用以去除新聞網站顯示之預設影像。
    + `image_selector`: 解析文章影像 `<img>` 所使用的選擇子，如未指定，則僅會搜尋 `<meta property="og:image">` 的值。

(4) 透過 `crontab` 或是其他方式，將套件排入背景執行。

    * * * * * python -m xinpu.crawler
    * * * * * python -m xinpu.poster

授權
----

以 [BSD License](LICENSE.md) 釋出予公眾利用。

---

![Photo by Willie Chen on Flickr, CC BY-NC-ND 2.0](https://farm1.staticflickr.com/108/302535466_f650b10a42_b.jpg)

Xinpu (Sìnbù) publishes news feeds on [Plurk](https://www.plurk.com) accordingly. Its naming comes from the hakka village [Xinpu](https://en.wikipedia.org/wiki/Xinpu,_Hsinchu), located in northern Taiwan, while also the starting words of Sìnvun (news) and Plurk.
