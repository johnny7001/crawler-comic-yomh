import os
from PIL import Image
from DB.yomhDB import DB
import time
import multiprocessing as mp

db = DB()

# 檢查圖片


def checkImg(book_id: int, chapter: int, imgPath: str):
    """
    檢查圖片檔案是否毀損, 若毀損則將 littleKorean_img 的 status = 3

    Args:
        book_id (int): 書本id
        chapter (int): 章節
        imgPath (str): 圖片路徑
    """
    try:
        # Read image
        img = Image.open(f'{imgPath}')
        # 印出 img type
        img.format
        print(f'{imgPath}, 這張圖片沒問題')
    except Exception as err:
        # print(book_id, chapter)
        sql = f"UPDATE `littleKorean_img` SET `status` = 3 WHERE `book_id` = {book_id} AND `count` = {chapter};"
        db.query(sql)
        print(f'{imgPath}, 這張圖片損毀, 錯誤碼: {err}')


def main():
    """
        讀取 yomh_comic 資料夾內的漫畫資料夾, 
        檢查是否有毀損的圖片, 若沒有毀損, 則將 littleKorean_img 的 status = 4, 表示檢查完成
    """
    # 讀出所以資料夾名稱
    folderpath = "/root/shane/yomh/yomh_comic"
    # files = os.listdir(folderpath)
    # if '.DS_Store' in files:
    #     files.remove('.DS_Store')
    # 這邊可以透過SQL指令或直接檢查指定資料夾內的圖片
    sql = "SELECT book_name FROM shane.littleKorean_book where updated_at >= '2022-12-06';"
    result = db.query(sql).fetchall()
    for i in result:
        book_name = i['book_name']
        # bookPath = f"/Users/johnny7001/yomh_git/crawl-korean-comics/yomh_comic/{i['book_name']}"
    # for book_name in files:
        bookPath = f'{folderpath}/{book_name}'
        chapters = os.listdir(bookPath)
        # if '.DS_Store' in chapters:
        #     chapters.remove('.DS_Store')

        sql = f'SELECT `id` FROM `littleKorean_book` WHERE `book_name` = "{book_name}";'
        result = db.query(sql).fetchone()
        book_id = result['id']

        for chapter in chapters:

            chapterPath = f'{bookPath}/{chapter}'
            imgs = os.listdir(chapterPath)
            # if '.DS_Store' in imgs:
            #     imgs.remove('.DS_Store')
            imgPath_list = []
            for img in imgs:
                imgPath = f'{chapterPath}/{img}'
                pool_tuple = (book_id, chapter, imgPath)
                imgPath_list.append(pool_tuple)

            start_4 = time.time()
            pool = mp.Pool(processes=10)
            pool.starmap(checkImg, imgPath_list)
            end_4 = time.time()
            print(f'{book_name}下載完成', end_4 - start_4)
            pool.terminate()  # terminate() 通常在主程序的可並行化部分完成時調用。
            pool.join()  # 調用 join() 以等待工作進程終止。

            sql = f"UPDATE `littleKorean_img` SET `status` = 4 WHERE `book_id` = {book_id} AND `count` = {chapter} AND `status` = 2;"
            db.query(sql)
            print(book_id, chapter, '執行完成')


if __name__ == '__main__':
    main()
