import json
import pymysql
import requests
from bs4 import BeautifulSoup
from DB.yomhDB import DB
import os
from dotenv import load_dotenv
load_dotenv()

db_host = os.getenv("db_host")
db_user = os.getenv("db_user")
db_password = os.getenv('db_password')
db_name = os.getenv('db_name')
db_charset = os.getenv('db_charset')
db_port = 8889

userid = os.getenv("userid")
pwd = os.getenv("pwd")

conn = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password,
                       database=db_name)
cursor = conn.cursor()

db = DB()


def login_url(chapter_url: str):
    """
    該網站有需要登入會員的時候,因此在前面先登入,讓後續爬蟲的時候更順利
    Accepts:
        chapter_url : 每一本章節的網址
    Returns:
        將 BeautifulSoup 整理過後的結果回傳
    """

    lo = "https://www.ydhm22.com/member/index.php"
    payload = {
        'userid': userid,
        'pwd': pwd,
        'fmdo': "login",
        'dopost': "login",
        'keeptime': "6048000",
        'gourl': '/plus/view-54052-1.html'
    }

    session_requests = requests.session()

    # session_requests.get(lo)
    session_requests.post(lo, data=payload, headers=dict(referer=lo))
    header = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
        'cookie': 'PHPSESSID=bfgtsunpshmg1b3r5lf0ghg57l; _fw_crm_v=85de975c-a4e6-4080-d3df-17a66a290e10; _fw_crm_v=85de975c-a4e6-4080-d3df-17a66a290e10; DedeUserID=11702; DedeUserID__ckMd5=3053eb21344c6e4a; dede_csrf_token=9388c1bb2454b828b19d6fc9c640acf6; dede_csrf_token__ckMd5=e5afc35d3c30a430; DedeLoginTime=1651808496; DedeLoginTime__ckMd5=892dcfda88cf9465; ENV_GOBACK_URL=%2Fmember%2Fhistory.php'}
    resp = requests.get(chapter_url, headers=header)
    soup = BeautifulSoup(resp.content, "html.parser")
    return soup


def get_chapter_image_list(chapter_url: str):
    """
    拿到每一個章節的所有圖片,並整理成json 的格式
    Accepts:
        chapter_url : 每一本章節的網址
    Returns:
        將 img_array 從list 調整為 json 格式後回傳
    """
    img_array = []
    soup = login_url(chapter_url)
    for img in soup.find_all('img'):
        if 'img.pic-server.com' in img.get('src') or 'vip.server-pic.com' in img.get('src'):
            imgUrl = img.get('src')
            img_array.append(imgUrl)
    chapter_json = {
        "img_array": img_array,
    }
    json_object = json.dumps(chapter_json, indent=4, ensure_ascii=False)
    return json_object


def get_book_list():
    """
    找尋littleKorean_book_chapter 內 所有 status是0 的 來拿他們的資料
    Returns:
        所有需要的值
    """
    all_data = []
    # with open('noIMG.txt', 'r', encoding='utf-8') as file:
    #     content = file.readlines() # type = content

    sql = f"SELECT `book_name` FROM `littleKorean_book_chapter` WHERE `status` = 0 group by `book_name`;"
    result = db.query(sql).fetchall()
    for i in result:
        bookname = i['book_name'].replace('\n', '')
        sql = f"SELECT `book_id`,`count`,`chapter_url` FROM `littleKorean_book_chapter` WHERE `status` = 0 AND `book_name` = '{bookname}';"
        result = db.query(sql).fetchall()
        for one_ans in result:
            all_data.append(one_ans)

    return all_data


def main():
    """
    執行所有的func 並將結果傳回 littleKorean_img 內
    Returns:
        將所有結果 傳進littleKorean_img 內
    """
    global conn
    a = get_book_list()
    # 計算有幾個a
    for num in range(len(a)):
        book_id = int(a[num]["book_id"])
        count = int(a[num]["count"])
        chapter_url = a[num]["chapter_url"]
        image_list = get_chapter_image_list(chapter_url)
        status = 0
        try:
            data = [book_id, count, image_list, status]
            # 下面是sql語法
            sql = "INSERT INTO `littleKorean_img` (`book_id`,`count`, `imgUrl_array`,`status`) VALUES (%s, %s, %s, %s) "
            sql2 = f"UPDATE `littleKorean_book_chapter`set `status` = 1 where `book_id` = '{book_id} '&& `count`={count};"
            cursor.execute(sql, data)
            cursor.execute(sql2)
            conn.commit()
            print('成功傳入')

        except:
            data = [book_id, count, image_list, status]
            # 下面是sql語法
            sql = "INSERT INTO `littleKorean_img` (`book_id`,`count`, `imgUrl_array`,`status`) VALUES (%s, %s, %s, %s) "
            sql2 = f"UPDATE `littleKorean_book_chapter`set `status` = 1 where `book_id` = '{book_id} '&& `count`={count};"
            conn.ping()
            cursor.execute(sql, data)
            cursor.execute(sql2)
            conn.commit()
            print('重新連線並傳入')


if __name__ == '__main__':
    main()
