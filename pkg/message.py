from datetime import datetime, timezone, timedelta


def message(msg):
    # - |2017-04-09 02:08:55.764256 | 訊息，顯示在這邊
    current = '{0:%Y-%m-%d %H:%M:%S.%f}'.format(datetime.now(timezone.utc) + timedelta(hours=8))
    log = "- |" + current + " | " + ": " + str(msg)
    print(log)
    return log
