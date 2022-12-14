import urllib3
from DB.yomhDB import DB
import os
import time
import requests
import json
from pkg.message import message
import multiprocessing as mp

db = DB()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def downloadImg(book_name: str, imgsql: dict, folderpath: str):
    '''
    Accepts:
        book_name : 書本名稱
        imgsql : 該本書所有章節:圖片網址array
        folderpath : 下載的書本路徑
    Returns:
        執行圖片下載
    '''
    # chapter_num = 第幾話
    chapter_num = imgsql['count']

    # book_id = 書本id
    book_id = imgsql['id']

    # 用來計算圖片的檔名
    count = 1

    try:
        # 戳到先改狀態, status = 1
        sql = f"UPDATE `littleKorean_img` SET `status` = 1 WHERE `book_id` = {book_id} AND `count` = {chapter_num};"
        db.query(sql)

        # 拿到圖片網址
        for imgUrl in json.loads(imgsql['imgUrl_array'])['img_array']:
            # print(count, imgUrl)

            #  判斷漫畫資料夾存在
            if os.path.isdir(folderpath):
                # 判斷章節資料夾是否存在
                if os.path.isdir(f'{folderpath}/{chapter_num}'):
                    urllib3.disable_warnings(
                        urllib3.exceptions.InsecureRequestWarning)
                    headers = {'referer': 'https://www.ydhm22.com/'}
                    img = requests.get(url=imgUrl, stream=True,
                                       verify=False, headers=headers)
                    with open(f"{folderpath}/{chapter_num}/{count}.jpg", "wb") as file:
                        file.write(img.content)
                    print(book_name, chapter_num, count, imgUrl)
                else:
                    os.mkdir(f'{folderpath}/{chapter_num}')
                    headers = {'referer': 'https://www.ydhm22.com/'}
                    img = requests.get(url=imgUrl, stream=True,
                                       verify=False, headers=headers)
                    with open(f"{folderpath}/{chapter_num}/{count}.jpg", "wb") as file:
                        file.write(img.content)
                    print(book_name, chapter_num, count, imgUrl)
            else:
                os.mkdir(folderpath)
                if os.path.isdir(f'{folderpath}/{chapter_num}'):
                    urllib3.disable_warnings(
                        urllib3.exceptions.InsecureRequestWarning)
                    headers = {'referer': 'https://www.ydhm22.com/'}
                    img = requests.get(url=imgUrl, stream=True,
                                       verify=False, headers=headers)
                    with open(f"{folderpath}/{chapter_num}/{count}.jpg", "wb") as file:
                        file.write(img.content)
                    print(book_name, chapter_num, count, imgUrl)
                else:
                    os.mkdir(f'{folderpath}/{chapter_num}')
                    urllib3.disable_warnings(
                        urllib3.exceptions.InsecureRequestWarning)
                    headers = {'referer': 'https://www.ydhm22.com/'}
                    img = requests.get(url=imgUrl, stream=True,
                                       verify=False, headers=headers)
                    with open(f"{folderpath}/{chapter_num}/{count}.jpg", "wb") as file:
                        file.write(img.content)
                    print(book_name, chapter_num, count, imgUrl)
            time.sleep(3)
            count += 1
        # 成功下載完一個章節, 將狀態改為2
        sql = f"UPDATE `littleKorean_img` SET `status` = 2 WHERE `book_id` = {book_id} AND `count` = {chapter_num};"
        db.query(sql)
    except Exception as err:
        message(err)
        # 若下載失敗, 則將狀態改為3
        sql = f"UPDATE `littleKorean_img` SET `status` = 3 WHERE `book_id` = {book_id} AND `count` = {chapter_num};"
        db.query(sql)


if __name__ == '__main__':

    # 篩選目前沒有抓取過的章節, status = 0
    sql = f"SELECT b.id, b.book_name, i.count, i.imgUrl_array FROM littleKorean_img as i left join littleKorean_book as b on i.book_id = b.id WHERE i.status = 0;"

    result = db.query(sql).fetchall()  # type = list

    img_list = []

    for imgsql in result:
        book_name = imgsql['book_name']
        # 漫畫資料夾
        folderpath = f"yomh_comic/{book_name}"
        pool_tuble = (book_name, imgsql, folderpath)
        img_list.append(pool_tuble)

    try:
        # 一次10本書下載
        start_4 = time.time()
        pool = mp.Pool(processes=10)
        pool.starmap(downloadImg, img_list)
        end_4 = time.time()
        print(f'{book_name}下載完成', end_4 - start_4)
        pool.terminate()  # terminate() 通常在主程序的可並行化部分完成時調用。
        pool.join()  # 調用 join() 以等待工作進程終止。

    except Exception as err:
        message(err)
