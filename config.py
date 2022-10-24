EXFOR_ALL_URL = "https://nds.iaea.org/exfor-master/backup/"


# GIT_REPO_PATH = "/Users/okumuras/Documents/nucleardata/EXFOR/exfor_master_soku/"  # private repo
GIT_REPO_PATH = "./"  # here
GIT_REPO_URL = "https://api.github.com/repos/IAEA-NDS/exfor_master/releases"

EXFOR_ALL_TEMP = "exforall_tmp/"  # do not remove for rsync "/"
EXFOR_ALL_PATH = GIT_REPO_PATH + "exforall/"


headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://127.0.0.1:5000",
            'content-type': 'application/vnd.github+json',
        }
