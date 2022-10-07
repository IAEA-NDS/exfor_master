EXFOR_ALL_URL = "https://nds.iaea.org/exfor-master/backup/"


EXFOR_ALL_TEMP = "/Users/sin/Desktop/exforall/"  # do not remove for rsync "/"
EXFOR_ALL_PATH = "history_test_from_backup/exforall"

headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://127.0.0.1:5000",
            'content-type': 'application/vnd.github+json',
        }
