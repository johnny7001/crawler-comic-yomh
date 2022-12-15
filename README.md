# 基本介紹
抓取  漫畫網站<br> 
# 作品應用
* requests.session 解決會員登入問題, BeautifulSoup解析Html, 抓取整個網站的目錄大綱 
* MySQL資料庫存放數據, 設定狀態欄位, 避免重複爬取資料
* 從資料庫抓取網址並requests下載圖片到指定位址的資料夾
* Multi-threading Pool 實行多執行緒, 加快下載速度

# 資料庫結構設計  
* 抓取所有書本名稱及鏈結
table_name = book   
* 抓取所有章節名稱及鏈結   
table_name = chapter    
* 抓取所有圖片鏈結  
table_name = image  
![image](https://github.com/johnny7001/crawler-comic-yomh/blob/ca954ec03d815b1a0422872b0b7e8b5adfa8a06c/yomh.jpg)

# 執行步驟

step1: get_all_book_name.py 抓取所有書本名稱及鏈結<br>
step2: get_all_json_name.py 將書本資料整理成json<br>
step3: get_all_json_name.py 抓取所有章節及圖片鏈結<br>
step4: download_img.py 下載圖片到對應名稱資料夾<br>
step5: checkIMG.py 檢查圖片是否有毀損<br>
