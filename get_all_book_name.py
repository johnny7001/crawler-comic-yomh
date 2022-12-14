from bs4 import BeautifulSoup
import requests
from pkg.message import message
import pymysql
import json
from apscheduler.schedulers.blocking import BlockingScheduler
import os
from dotenv import load_dotenv
load_dotenv()

db_host = os.getenv("db_host")
db_user = os.getenv("db_user")
db_password = os.getenv('db_password')
db_name = os.getenv('db_name')
db_charset = os.getenv('db_charset')
db_port = 8889

conn = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password,
                       database=db_name)

cursor = conn.cursor()


def format_word(word: str):
    """
    Accepts:
        word : 全部的內容
    Returns:
        回傳整理過後的內容
    """
    ans = ""
    for i in range(0, len(word)):
        if word[i] != " " and word[i] != "：" and word[i] != ":":  # 注意 這邊的冒號一個是中文輸入的冒號 一個是英文輸入的冒號
            ans = ans + word[i]
    return ans


def execute(book_url: str):
    """
    Accepts:
        book_url : 書本網址
    Returns:
        將 book_name, book_url_string, publish_status, author_name, metadata_json, status 插入 littleKorean_book 資料庫內
    """
    response = requests.get(book_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 檢查這本書是否存在
    error_content = soup.find('title')
    if error_content.text == '提示信息':
        message(f'沒有 {book_url} 這本書')
    else:
        message(f'有書 {book_url} 這本書')
        get_web = soup.find('div', class_='content clearfix')
        book_name = get_web.find('h2').text
        publish_status = get_web.find('font').text
        author_name = get_web.find('dl', class_="dl-left").find("dd").text
        # labels = get_web.find('dl', class_="dl-left").find_all('span')
        title_profile = get_web.find_all("dl", class_="dl-left")
        title_profile_dict = {}
        for i in title_profile:
            title_profile_dict[format_word(
                i.find("dt").string)] = i.find("dd").text
        metadata_json = json.dumps(title_profile_dict, ensure_ascii=False)
        status = 0
        book_url_string = f"{book_url}"
        # print(book_name, book_url_string, publish_status, author_name, metadata_json, status)
        global conn
        try:
            data = [book_name, book_url_string, publish_status,
                    author_name, metadata_json, status]
            # 下面是sql語法
            sql = "INSERT INTO `littleKorean_book` (`book_name`,book_url, `publish_status`,`author_name`,`metadata_json`,`status`) VALUES (%s, %s, %s, %s, %s, %s) "
            cursor.execute(sql, data)
            conn.commit()
            # 關閉資料庫連線
            print('成功傳入')
            conn.close()
            # 確定連線到資料庫
        except:
            data = [book_name, book_url_string, publish_status,
                    author_name, metadata_json, status]
            # 下面是sql語法
            sql = "INSERT INTO `littleKorean_book` (`book_name`,book_url, `publish_status`,`author_name`,`metadata_json`,`status`) VALUES (%s, %s, %s, %s, %s, %s) "
            conn.ping()
            cursor.execute(sql, data)
            conn.commit()
            print('重新連線並傳入')
            # 關閉資料庫連線
            conn.close()


def main():
    # 跳過259 300 352 353 518 沒有檔案
    for x in range(1, 600):
        # for x in comic_list:
        # 以下書本沒有章節
        if x == 259:
            continue
        if x == 300:
            continue
        if x == 352:
            continue
        if x == 353:
            continue
        if x == 518:
            continue
        if x == 440:
            continue
        latest_update = f"https://ydhm22.com/plus/list-{x}.html"
        execute(latest_update)


if __name__ == '__main__':
    # main()
    scheduler = BlockingScheduler(timezone="Asia/Taipei")
    # 設定每週一到日上午9:30分自動爬取並更新資料庫
    scheduler.add_job(main, 'cron', day_of_week='0-6', hour=7, minute=30)
    scheduler.start()
