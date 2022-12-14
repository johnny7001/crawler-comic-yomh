import pymysql
import requests
from bs4 import BeautifulSoup
from DB.yomhDB import DB
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

db = DB()

conn = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password,
                       database=db_name)

cursor = conn.cursor()


def get_data(book_id):
    all_book_name = []
    all_book_url = []
    # 根據書本id篩選出book_name, book_url
    sql = f'SELECT `book_name`,`book_url` FROM `littleKorean_book` where `id`= {book_id};'

    result = db.query(sql).fetchall()

    for all_name in result:
        book_name = all_name['book_name']
        book_url = all_name['book_url']
        all_book_name.append(book_name)
        all_book_url.append(book_url)

    return all_book_name, all_book_url


def get_book_id(book_name: str):
    """
    Accepts:
        book_name : 書名
    Returns:
        回傳那本書的id
    """

    sql = f'SELECT `id` FROM `littleKorean_book` WHERE `book_name` = "{book_name}";'
    result = db.query(sql).fetchone()
    book = result['id']
    return book


def get_all_chapter(book_url):
    response = requests.get(book_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    all_chapters = soup.find("div", class_="stab_list")
    chapters = all_chapters.find_all("li")
    all_chapters = []
    all_chapter_title = []
    for one_chapter in chapters:
        chapter_title = one_chapter.find("a").text
        all_chapter_title.append(chapter_title.replace("\xa0", ''))
        chapter = "https://ydhm22.com/" + one_chapter.find("a").get('href')
        all_chapters.append(chapter)

    return all_chapter_title, all_chapters


def get_all_need(book_id):
    book_name, book_urls = get_data(book_id)
    for book_url in book_urls:
        all_chapter_title, all_chapter_list = get_all_chapter(book_url)
        return book_name, all_chapter_list, all_chapter_title


def execute(book_id):
    book_name, all_chapter_list, all_chapter_title = get_all_need(book_id)
    # 判斷書本是否有最新的章節可以下載

    # 撈出資料庫該本書的最新章節
    sql = f"SELECT * FROM shane.littleKorean_book_chapter where book_id = {book_id} order by count desc limit 1;"
    result = db.query(sql).fetchone()
    if result != None and len(all_chapter_list) > result['count']:
        for canDownload in range(result['count']+1, len(all_chapter_list)+1):
            # 拿到要更新的chapter_url網址
            chapter_url = all_chapter_list[canDownload-1:canDownload]

            data = [book_name, book_id, result['chapter'],
                    chapter_url, 0, canDownload]
            sql = "INSERT INTO `littleKorean_book_chapter` (`book_name`,`book_id`, `chapter`,`chapter_url`,`status`,`count`) VALUES (%s, %s, %s, %s, %s, %s) "
            cursor.execute(sql, data)
            conn.commit()
            # 關閉資料庫連線
            print('成功傳入')
            conn.close()
            # '17666','姐姐的私密日记','341','32','https://ydhm22.com//plus/view-45842-1.html','第32话','2022-11-22 11:14:53','1'
    elif result == None:
        # print(all_chapter_title)
        diction = dict(zip(all_chapter_title, all_chapter_list))
        id = f"{book_id}"
        status = 0
        count = 0
        for chapter_title, chapter_url in diction.items():
            print(chapter_title, chapter_url)
            count += 1
            # print(book_id, book_name[0], chapter)
            try:
                data = [book_name[0], id, chapter_title,
                        chapter_url, status, count]
                # 下面是sql語法
                sql = "INSERT INTO `littleKorean_book_chapter` (`book_name`,`book_id`, `chapter`,`chapter_url`,`status`,`count`) VALUES (%s, %s, %s, %s, %s, %s) "
                cursor.execute(sql, data)
                conn.commit()
                # 關閉資料庫連線
                print('成功傳入')
                conn.close()
                # 確定連線到資料庫
            except:
                data = [book_name[0], id, chapter_title,
                        chapter_url, status, count]
                # 下面是sql語法
                sql = "INSERT INTO `littleKorean_book_chapter` (`book_name`,`book_id`, `chapter`,`chapter_url`,`status`,`count`) VALUES (%s, %s, %s, %s, %s, %s) "
                conn.ping()
                crs = conn.cursor()
                cursor.execute(sql, data)
                conn.commit()
                print('重新連線並傳入')
                # 關閉資料庫連線
                conn.close()
    else:
        print(f"{result['book_id']}, {result['count']} 已經下載過了")


def update_data(book_id):
    sql = f"UPDATE `littleKorean_book`set `status` = 1 where `id` = {book_id};"
    cursor.execute(sql)
    conn.commit()


def main():
    # 選出還沒有insert chapter json 的資料
    # sql = "SELECT `id` FROM `littleKorean_book` ORDER BY `id`;"
    sql = "SELECT `id` FROM `littleKorean_book` WHERE `status` = 0;"
    result = db.query(sql).fetchall()
    for i in result:
        # print(i['id'])
        execute(i['id'])
        update_data(i['id'])


if __name__ == '__main__':
    # main()
    scheduler = BlockingScheduler(timezone="Asia/Taipei")
    # 設定每週一到日上午9:30分自動爬取並更新資料庫
    scheduler.add_job(main, 'cron', day_of_week='0-6', hour=9, minute=30)
    scheduler.start()

    get_all_chapter("https://ydhm22.com/plus/list-101.html")
