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
import datetime
from git import Repo  # https://gitpython.readthedocs.io/en/stable/tutorial.html
from zipfile import ZipFile

sys.path.append("../")
from config import EXFOR_ALL_URL, EXFOR_ALL_PATH



def get_local_files():
    local_files = glob.glob("EXFOR*.zip") + glob.glob("exfor*.zip")
    # check local dictionary files
    x = []
    for d in local_files:
        x += [re.split(r"\.", os.path.basename(d))[0]]

    return x # get_latest_date(x)


def get_server_files():
    x = []
    r = requests.get(EXFOR_ALL_URL)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.find_all("a", attrs={"href": re.compile(r".*(EXFOR-|exfor-)(?:19\d{2}|20\d{2})[-/.](?:0[1-9]|1[012])[-/.](?:0[1-9]|[12][0-9]|3[01]).zip")})

    for link in links:
        x += [link.get("href").split(".")[0]]
    print(x)
    return x # get_latest_date(x)


def download_master_backup_sequential():
    x = get_server_files()
    for d2 in x:
        download_backup_zip(d2)



def get_latest_date(x:list):
    if x:
        d = []
        for a in x:
            print(a.replace("EXFOR-","").replace("exfor-",""))
            d.append( convert_dtform(a.replace("EXFOR-","").replace("exfor-","")) )
        return max(d)

    else:
        return None



def convert_dtform(dtstring:str):
    # dtstring: "YYYY-MM-DD" in text format
    return datetime.date( int(dtstring.split("-")[0]), int(dtstring.split("-")[1]), int(dtstring.split("-")[2]))


def download_latest_master_from_bk():
    # get the latest dictionary from https://nds.iaea.org/exfor-master/backup/
    # filename must be in sequence e.g. trans.9124
    d1 = get_latest_date( get_local_files() )
    d2 = get_latest_date( get_server_files() )

    if d1 == d2:
        print("Local is the latest version.")
        pass

    elif d1 > d2:
        print("Something wrong") 
        pass

    else:
        download_backup_zip(d2)

    return d2



def zip_filename(date_dt):
    # latest: datatime.date(YYYY, MM, DD) format 
    if date_dt < datetime.date(2010, 7, 1):
        return "".join(["exfor-", date_dt.strftime("%Y-%m-%d"), ".zip"])
    else:
        return "".join(["EXFOR-", date_dt.strftime("%Y-%m-%d"), ".zip"])




def bck_filename(date_dt):
    # dt: datatime.date(YYYY, MM, DD) format
    if date_dt < datetime.date(2010, 7, 1):
        if os.path.exists(  "".join(["exfor-", date_dt.strftime("%Y-%m-%d"), ".bck"]) ):
            # because exfor-YYYY-MM-DD.bck and EXFOR-YYYY-MM-DD.bck are mixed
            return "".join(["exfor-", date_dt.strftime("%Y-%m-%d"), ".bck"])
    else:
        return "".join(["EXFOR-", date_dt.strftime("%Y-%m-%d"), ".bck"])



def download_backup_zip(date_dt):
    # date_dt: datatime.date(YYYY, MM, DD) format

    file = zip_filename(date_dt)

    # fetch file
    url = "".join( [EXFOR_ALL_URL, file] )
    print(url)
    r = requests.get(url, allow_redirects=True)

    if r.status_code == 404:
        print("Something wrong with retrieving new dictionary from the IAEA-NDS.")
        pass
    
    open(file, "wb").write(r.content)
    print("Downloaded", file, "from ", EXFOR_ALL_URL)



def unzip_file(filename):
    with ZipFile(filename, 'r') as zipObj:
        # Extract all the contents of zip file in current directory
        # zipObj.extractall()

        listOfFileNames = zipObj.namelist()
        for filename in listOfFileNames:
            if filename.endswith('.bck') or filename.endswith('.BCK'):
                # Extract a single file from zip
                zipObj.extract(filename)
            return filename



def split_bck_file(filename):

    with open(filename, 'r', encoding='cp1250') as infile:
        ## encoding='cp1250' is reqired to avoid encode error at A0612
        for line in infile:
            if "REQUEST" in line[0:7] or "ENDREQUEST" in line[0:10]:
                continue
            

            if "ENTRY" in line[0:5]:

                entrynum = line[17:22]
                print(entrynum)

                if os.path.exists( os.path.join(EXFOR_ALL_PATH, entrynum[0:3]) ):
                    pass
                else:
                    os.mkdir(EXFOR_ALL_PATH + "/" + entrynum[0:3])

                outfile = open ( os.path.join(EXFOR_ALL_PATH, entrynum[0:3], entrynum[0:5] + ".x4"), "w")
                outfile.write(line)

            elif "ENDENTRY" in line[0:8]:
                outfile.write(line)
                outfile.close()

            else:
                outfile.write(line)


def run_rsync():
    os.system('rsync -ar --delete exforall_py/ exforall')



repo = Repo("./")
assert not repo.bare

def git_new_branch(date_str):

    git = repo.git
    git.checkout('HEAD', b = date_str )         # create a new branch
    # git.branch('2011-01-13')
    # git.branch('-D', 'another-new-one')             # pass strings for full control over argument order
    # git.for_each_ref()                              # '-' becomes '_' when calling it



def git_push_branch(date_str):

    index = repo.index
    index.add(['exforall/']) 

    repo.commit(date_str)
    origin = repo.remote(name="origin")
    origin.push()




def test_run():
    x = get_server_files()
    
    for xx in x:
        date_str = xx.replace("EXFOR-","").replace("exfor-","")
        date_dt = convert_dtform( date_str )
        download_backup_zip(date_dt)

        git_new_branch(date_str)

        filename = unzip_file( zip_filename(date_dt) )
        split_bck_file(filename)
        run_rsync()

        git_push_branch(date_str)


    # run from list
    # x = ["EXFOR-2011-01-13"] #, "EXFOR-2011-02-16"]
    # for v in x:
    #     latest = convert_dtform(v.replace("EXFOR-",""))

    #     download_backup_zip(latest)
    #     unzip_file( zip_filename(latest) )
    #     git_new_branch( latest.strftime("%Y-%m-%d") )
    #     split_bck_file( bck_filename(latest) )
    #     run_rsync()



def main():
    get_server_files()



if __name__ == "__main__":
    # latest = download_latest_master_from_bk()

    test_run()










