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
import json
import shutil
import datetime
from git import (
    Git,
    Repo,
)  # GitPython https://gitpython.readthedocs.io/en/stable/tutorial.html
from zipfile import ZipFile

import logging
logging.basicConfig(filename="process.log", level=logging.DEBUG, filemode="w")

from config import EXFOR_ALL_URL, EXFOR_ALL_PATH, EXFOR_ALL_TEMP, headers,  GIT_REPO_PATH, GIT_REPO_URL


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
                r".*(EXFOR-|exfor-)(?:19\d{2}|20\d{2})[-/.](?:0[1-9]|1[012])[-/.](?:0[1-9]|[12][0-9]|3[01])([a-z]{0,1})(-{0,1}[12]{0,1}).zip"
            )
        },
    )

    for link in links:
        x += [link.get("href").split(".")[0]]

    return x  # get_latest_date(x)



def download_master_backup_sequential():
    x = get_server_files()
    for d2 in x:
        download_backup_zip(d2)



def get_latest_date(x: list):
    if x:
        d = []
        for a in x:
            d.append(convert_dtform(a.replace("EXFOR-", "").replace("exfor-", "")))
        return max(d)
    else:
        return None




def download_latest_master_from_bk():
    # get the latest dictionary from https://nds.iaea.org/exfor-master/backup/

    d1 = get_latest_date(get_local_files())
    d2 = get_latest_date(get_server_files())

    if d1 == d2:
        logging.info(f"Local is the latest version. Exit.")
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
    # EXFOR-2021-06-07-1.zip, EXFOR-2021-02-16a.zip
    date = re.sub("\D", "", dtstring.split("-")[2])
    return datetime.date(
        int(dtstring.split("-")[0]),
        int(dtstring.split("-")[1]),
        int(date),
    )




def zip_filename(date_str):
    # date_dt: datatime.date(YYYY, MM, DD) format
    date_dt = convert_dtform(date_str.replace("EXFOR-", "").replace("exfor-", ""))
    if date_dt < datetime.date(2010, 7, 1):
        return "".join(["exfor-", date_dt.strftime("%Y-%m-%d"), ".zip"])
    else:
        return "".join(["EXFOR-", date_str, ".zip"])




def bck_filename(date_dt):
    # date_dt: datatime.date(YYYY, MM, DD) format
    if date_dt < datetime.date(2010, 7, 1):
        if not os.path.exists(
            "".join(["exfor-", date_dt.strftime("%Y-%m-%d"), ".bck"])
        ):
            # because exfor-YYYY-MM-DD.bck and exfor-YYYY-MM-DD.BCK are mixed in some .zip files
            return "".join(["exfor-", date_dt.strftime("%Y-%m-%d"), ".BCK"])
    else:
        return "".join(["EXFOR-", date_dt.strftime("%Y-%m-%d"), ".bck"])




def download_backup_zip(date_str):
    zipfile = zip_filename(date_str)

    # if not isinstance(date, str):
    #     # date_dt: datatime.date(YYYY, MM, DD) format
    #     zipfile = zip_filename(date)

    # else:
    #     # date: "EXFOR-YYYY-MM-DD-1"
    #     zipfile = date + ".zip"

    if not os.path.exists(zipfile):
        url = "".join([EXFOR_ALL_URL, zipfile])

        r = requests.get(url, allow_redirects=True)

        if r.status_code == 404:
            logging.error(f"Something wrong with retrieving new dictionary from the IAEA-NDS.")
            sys.exit()

        open(zipfile, "wb").write(r.content)
        logging.info(f"zip file downloaded")
    return zipfile




def unzip_file(zipfile: str):
    with ZipFile(zipfile, "r") as zipObj:
        listOfFileNames = zipObj.namelist()
        for filename in listOfFileNames:
            if filename.endswith(".bck") or filename.endswith(".BCK"):
                zipObj.extract(filename)
                return filename
            else:
                logging.error(f"Unzip error {zipfile}")
                exit()





def split_bck_file(filename: str):
    logging.info(f"split started")
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
                    # print(entrynum[0:3])
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
    ## not used
    print("rsync")
    logging.info(f"rsync started")
    cmd = "rsync -azP --delete --ignore-times " + EXFOR_ALL_TEMP + " " + EXFOR_ALL_PATH
    os.system(cmd)
    logging.info(f"rsync finished")




def del_files(filename: str):
    if os.path.isfile(filename):
        os.remove(filename)
        logging.info(f"File has been deleted")
    else:
        logging.info(f"File does not exist")





####################################################################
# Git functions
####################################################################

repo = Repo(GIT_REPO_PATH)
assert not repo.bare


def git_new_branch(date_str):
    repo.git.checkout("HEAD", b=date_str)  # create a new branch
    logging.info(f"repo.active_branch {repo.active_branch}")
    print("create new branch:", date_str)




def git_add_commit(date_str):
    repo.git.add("exforall/")
    repo.git.commit(m=date_str)
    logging.info(f"branch commit {date_str}")
    print("add and commit to branch:", date_str)




def git_push_branch(date_str):
    origin = repo.remote(name="origin")
    origin.push(date_str)
    # logging.info(f"origin.push {date_str}")
    print("branch push:", date_str)




def git_merge_to_main(date_str):
    repo.git.checkout("main")
    repo.git.merge(date_str)
    origin = repo.remote(name="origin")
    origin.push()
    # logging.info(f"repo.git.merge and origin.push master")
    print("branch merged to main:", date_str)



def git_branches():
    branches = []
    remote_refs = repo.remote().refs

    for refs in remote_refs:
        branches.append(refs.name.replace("origin/",""))

    return branches




def git_tags():
    tags = []
    for tag in repo.tags:
        tags.append(tag.name.replace("Backup-",""))
    return tags





def semantic_release_name(branch_name):
    name_sp = branch_name.split("-")
    if len(branch_name) == 10:
        return "v" + str(name_sp[0]) + str(name_sp[1])+ str(name_sp[2]) + ".0"
    elif branch_name.count("-") == 3:
        return "v" + str(name_sp[0]) + str(name_sp[1])+ str(name_sp[2]) + "." + name_sp[3]
    elif len(branch_name) == 11:
        return "v" + str(name_sp[0]) + str(name_sp[1])+ str(name_sp[2])[0:2] + "." + name_sp[2][2:]




def git_log():
    return repo.git.log("--name-status", "--no-merges", "-n1", "--pretty=oneline")




def git_tagging(branch_name):
    repo.git.checkout(branch_name)
    repo.git.pull("origin", branch_name)
    repo.git.fetch("origin")

    msg = git_log()
    repo.create_tag("Backup-" + branch_name, ref=branch_name, message=msg)
    
    origin = repo.remote(name="origin")
    origin.push("Backup-" + branch_name)
    logging.info(f"tagging branch_name: {branch_name}")




def git_release(branch_name):
    data_body = {
        "tag_name": "Backup-" + branch_name,
        "name": semantic_release_name(branch_name),
        "draft": False,
        "prerelease": False,
        "generate_release_notes": False
        }

    r = requests.post(
        GIT_REPO_URL, 
        data=json.dumps(data_body), 
        headers=headers, 
        verify=False,
    )



def git_delete_branch(date_str):
    repo.git.checkout("main")
    repo.git.branch("-d", date_str)
    origin = repo.remote(name="origin")
    origin.push()
    # logging.info(f"repo.git.branch -d")
    print("branch deleted:", date_str)




def process_zip_file(date_str):
    print(date_str)
    ## download and unzip .zip file
    download_backup_zip(date_str)
    bck_filename = unzip_file(zip_filename(date_str))

    ## create new branch and extract master file and split into exntry
    git_new_branch(date_str)
    split_bck_file(bck_filename)

    ## git commit, push, merge
    git_add_commit(date_str)
    git_push_branch(date_str)
    git_merge_to_main(date_str)

    ## create Release in Github
    git_tagging(date_str)

    ## release does not work from the CLI from Github/Actions, 
    ## it needs curl to post to REST API 
    ## (see .github/workflows/manual.yaml)
    # git_release(date_str)

    ## delete branch
    git_delete_branch(date_str)

    ## delete donwnloaded .zip and .bck files
    del_files(zip_filename(date_str))
    del_files(bck_filename)


####################################################################
# This is the process to run through all server files.
# Some of the zip file cannot be proecssed. (e.g.
# EXFOR-2010-07-12.zip seems to be broken or not a zip format.)
####################################################################


def runall():
    x = get_server_files()

    for xx in x:
        date_str = xx.replace("EXFOR-", "").replace("exfor-", "")
        process_zip_file(date_str)



####################################################################
# This is the process to update the repository.
####################################################################


def update():
    x = get_server_files()
    tags = git_tags()

    processed = []
    not_processed = []

    ## check if there is unprocessed zip file or not
    for xx in x:
        date_str = xx.replace("EXFOR-", "").replace("exfor-", "")

        if date_str in tags:
            processed.append(date_str)

        else:
            not_processed.append(date_str)


    ## because exfor-2010-07-12.zip is broken
    not_processed.remove('2010-07-12')
    logging.info(f"process starts for {not_processed}")

    if not_processed:
        for date_str_np in not_processed:
            process_zip_file(date_str_np)

    else:
        logging.info(f"repository is up-to-date")


    return " ".join(not_processed)



if __name__ == "__main__":

    print(update())


