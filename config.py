EXFOR_ALL_URL = "https://nds.iaea.org/exfor-master/backup/"
EXFOR_TRANS_URL = "https://nds.iaea.org/nrdc/exfor-master/trans/"


GIT_REPO_PATH = "./"  # here
# GIT_REPO_PATH = "/Users/sin/Documents/test/exfor_master/"  # Private Repo

GIT_REPO_URL = "https://api.github.com/repos/IAEA-NDS/exfor_master/releases"
# GIT_REPO_URL = "https://api.github.com/repos/shinokumura/exfor_master/releases" # Private Repo


"""
This is the contingency plan to use OECD/NEA Github
"""
TRANS_REPO_PATH = "../trans"
TRANS_REPO_URL = "https://git.oecd-nea.org/exfor/nrdc/trans"


TEMP_TRANS = "./trans"
EXFOR_ALL_PATH = GIT_REPO_PATH + "exforall/"


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://127.0.0.1:5000",
    "content-type": "application/vnd.github+json",
}
