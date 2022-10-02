####################################################################
#
# This file is part of exfor-parser.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Disclaimer: The code is still under developments and not ready
#             to use. It has been made public to share the progress
#             among collaborators.
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import requests
from bs4 import BeautifulSoup
import glob
import re
import os
import sys
import shutil
import datetime
from git import (
    Git,
    Repo,
)  # GitPython https://gitpython.readthedocs.io/en/stable/tutorial.html
from zipfile import ZipFile
import logging

logging.basicConfig(filename="process.log", level=logging.DEBUG, filemode="w")

# sys.path.append("../")
from config import EXFOR_ALL_URL, EXFOR_ALL_PATH, EXFOR_ALL_TEMP
from gitconf import repo_path



####################################################################
# For maintenance
####################################################################

def get_local_files():
    local_files = glob.glob("EXFOR*.zip") + glob.glob("exfor*.zip")
    # check local dictionary files
    x = []
    for d in local_files:
        x += [re.split(r"\.", os.path.basename(d))[0]]

    return x  # get_latest_date(x)



def get_server_files():
    x = []
    r = requests.get(EXFOR_ALL_URL)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.find_all(
        "a",
        attrs={
            "href": re.compile(
                r".*(EXFOR-|exfor-)(?:19\d{2}|20\d{2})[-/.](?:0[1-9]|1[012])[-/.](?:0[1-9]|[12][0-9]|3[01]).zip"
            )
        },
    )

    for link in links:
        x += [link.get("href").split(".")[0]]
    print(x)
    return x  # get_latest_date(x)



def download_master_backup_sequential():
    x = get_server_files()
    for d2 in x:
        download_backup_zip(d2)



def get_latest_date(x: list):
    if x:
        d = []
        for a in x:
            print(a.replace("EXFOR-", "").replace("exfor-", ""))
            d.append(convert_dtform(a.replace("EXFOR-", "").replace("exfor-", "")))
        return max(d)
    else:
        return None



def download_latest_master_from_bk():
    # get the latest dictionary from https://nds.iaea.org/exfor-master/backup/

    d1 = get_latest_date(get_local_files())
    d2 = get_latest_date(get_server_files())

    if d1 == d2:
        print("Local is the latest version. Exit.")
        pass

    elif d1 > d2:
        logging.error(f"Local file is newer than the server file.")
        pass

    else:
        download_backup_zip(d2)
        logging.info(f"zip file downloaded")

    return d2



####################################################################
# General functions
####################################################################

def convert_dtform(dtstring: str):
    # dtstring: "YYYY-MM-DD" in text format
    return datetime.date(
        int(dtstring.split("-")[0]),
        int(dtstring.split("-")[1]),
        int(dtstring.split("-")[2]),
    )


def zip_filename(date_dt):
    # date_dt: datatime.date(YYYY, MM, DD) format
    if date_dt < datetime.date(2010, 7, 1):
        return "".join(["exfor-", date_dt.strftime("%Y-%m-%d"), ".zip"])
    else:
        return "".join(["EXFOR-", date_dt.strftime("%Y-%m-%d"), ".zip"])



def bck_filename(date_dt):
    # date_dt: datatime.date(YYYY, MM, DD) format
    if date_dt < datetime.date(2010, 7, 1):
        if not os.path.exists(
            "".join(["exfor-", date_dt.strftime("%Y-%m-%d"), ".bck"])
        ):
            # because exfor-YYYY-MM-DD.bck and exfor-YYYY-MM-DD.BCK are mixed
            return "".join(["exfor-", date_dt.strftime("%Y-%m-%d"), ".BCK"])
    else:
        return "".join(["EXFOR-", date_dt.strftime("%Y-%m-%d"), ".bck"])



def download_backup_zip(date_dt):
    # date_dt: datatime.date(YYYY, MM, DD) format

    zipfile = zip_filename(date_dt)

    if not os.path.exists(zipfile):
        url = "".join([EXFOR_ALL_URL, zipfile])

        r = requests.get(url, allow_redirects=True)

        if r.status_code == 404:
            print("Something wrong with retrieving new dictionary from the IAEA-NDS.")
            pass

        open(zipfile, "wb").write(r.content)

        logging.info(f"zip file downloaded")
    return zipfile



def unzip_file(zipfile:str):
    with ZipFile(zipfile, "r") as zipObj:
        listOfFileNames = zipObj.namelist()
        for filename in listOfFileNames:
            if filename.endswith(".bck") or filename.endswith(".BCK"):
                zipObj.extract(filename)
                return filename
            else:
                exit()



def split_bck_file(filename:str):
    logging.info(f"split started")
    print("split into ENTRY number")
    with open(filename, "r", encoding="cp1250") as infile:
        shutil.rmtree(EXFOR_ALL_PATH + "/")
        os.mkdir(EXFOR_ALL_PATH)
        ## encoding='cp1250' is reqired to avoid encode error at A0612
        for line in infile:
            if "REQUEST" in line[0:7] or "ENDREQUEST" in line[0:10]:
                continue

            if "ENTRY" in line[0:5]:
                entrynum = line[17:22]

                if os.path.exists(os.path.join(EXFOR_ALL_PATH, entrynum[0:3])):
                    pass
                else:
                    print(entrynum[0:3])
                    os.mkdir(EXFOR_ALL_PATH + "/" + entrynum[0:3])

                outfile = open(
                    os.path.join(EXFOR_ALL_PATH, entrynum[0:3], entrynum[0:5] + ".x4"),
                    "w",
                )
                outfile.write(line)

            elif "ENDENTRY" in line[0:8]:
                outfile.write(line)
                outfile.close()

            else:
                outfile.write(line)

    logging.info(f"split finished")


def run_rsync():
    # --ignore-times does more than its name implies. It ignores both the time and size. 
    # In contrast, --size-only does exactly what it says.
    print("rsync")
    logging.info(f"rsync started")
    cmd = "rsync -azP --delete --ignore-times " + EXFOR_ALL_TEMP + " " + EXFOR_ALL_PATH
    os.system(cmd)
    logging.info(f"rsync finished")



def del_files(filename:str):
    if os.path.isfile(filename):
        os.remove(filename)
        print("File has been deleted")
    else:
        print("File does not exist")


####################################################################
# Git functions
####################################################################

repo = Repo(repo_path)
# Repo.clone_from("git@github.com:shinokumura/exfor_master.git" , repo_path, branch="main")
assert not repo.bare


def git_new_branch(date_str):
    # for remote in repo.remotes:
    #     print('Remote named "{}" with URL "{}"'.format(remote, remote.url))
    repo.git.checkout("HEAD", b=date_str)  # create a new branch
    # print("Repo active branch is {}".format(repo.active_branch))
    logging.info(f"repo.active_branch {repo.active_branch}")



def git_add_commit(date_str):
    # print("Repo active branch is {}".format(repo.active_branch))
    repo.git.add("exforall/")
    repo.git.commit(m=date_str)
    logging.info(f"branch commit {date_str}")



def git_push_branch(date_str):
    # print(repo.git.status())
    origin = repo.remote(name="origin")
    origin.push(date_str)
    logging.info(f"origin.push {date_str}")



def git_merge_to_main(date_str):
    repo.git.checkout("main")
    repo.git.merge(date_str)
    origin = repo.remote(name="origin")
    origin.push()
    logging.info(f"repo.git.merge and origin.push master")



####################################################################
# This is the process to run through all server files
# Note that some of the zip file cannot be proecssed.
# (e.g. EXFOR-2010-07-12.zip seems to be broken or not in zip format)
####################################################################

def run():
    x = get_server_files()

    for xx in x:
        date_str = xx.replace("EXFOR-", "").replace("exfor-", "")
        date_dt = convert_dtform(date_str)

        download_backup_zip(date_dt)
        filename = unzip_file(zip_filename(date_dt))

        git_new_branch(date_str)
        split_bck_file(filename)

        # run_rsync()

        git_add_commit(date_str)
        git_push_branch(date_str)
        git_merge_to_main(date_str)

        del_files(zip_filename(date_dt))
        del_files(filename)



if __name__ == "__main__":
    # latest = download_latest_master_from_bk()
    run()
