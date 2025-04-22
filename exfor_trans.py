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
import os
import sys
import json
import shutil
import datetime
from git import (
    Repo,
)
import logging

logging.basicConfig(filename="process.log", level=logging.DEBUG, filemode="w")
import pandas as pd

from config import (
    EXFOR_TRANS_URL,
    EXFOR_ALL_PATH,
    TRANS_REPO_URL,
    headers,
    TEMP_TRANS,
    GIT_REPO_PATH,
    GIT_REPO_URL,
)


####################################################################
# For maintenance
####################################################################


def get_list_of_trans_files():
    """
    pd.read_html returns the list of dataframes
    groupby returns dictionary in { '2024-05-06': ['trans.1510', 'trans.1511', 'trans.c235', 'trans.c236', 'trans.l052']} format
    """
    r = requests.get(EXFOR_TRANS_URL)
    dfs = pd.read_html(r.text)
    print(r,dfs)
    df = dfs[0]
    df[["Date", "Time"]] = df["Released"].str.split(" ", expand=True)

    df = df.drop(df[df["Name"].str.contains("trans.zip")].index)
    df = df.drop(df[df["Name"].str.contains("trans.9")].index) # To skip EXFOR dictionary trans
    df = df.dropna(subset=["Released"])

    x = df.groupby("Date")["Name"].apply(list).to_dict()

    return x


def get_latest_date(x: dict):
    if x:
        d = []
        for a in x.keys():
            d.append(convert_dtform(a))
        return max(d)

    else:
        return None


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


def del_file(filename: str):
    if os.path.isfile(filename):
        os.remove(filename)
        logging.info(f"File has been deleted")
    else:
        logging.info(f"File does not exist")


def del_files(directory_path):
    shutil.rmtree(directory_path)


####################################################################
# Git functions
####################################################################

repo = Repo(GIT_REPO_PATH)
assert not repo.bare


def git_new_branch(date_str):
    repo.git.checkout("HEAD", b=date_str)  # create a new branch
    logging.info(f"repo.active_branch {repo.active_branch}")


def git_add_commit(date_str):
    repo.git.add("exforall/")
    repo.git.commit(m=date_str)
    logging.info(f"branch commit {date_str}")


def git_push_branch(date_str):
    origin = repo.remote(name="origin")
    origin.push(date_str)
    logging.info(f"origin.push {date_str}")


def git_merge_to_main(date_str):
    repo.git.checkout("main")
    repo.git.merge(date_str)
    origin = repo.remote(name="origin")
    origin.push()
    logging.info(f"repo.git.merge and origin.push master")


def git_branches():
    branches = []
    remote_refs = repo.remote().refs

    for refs in remote_refs:
        branches.append(refs.name.replace("origin/", ""))

    return branches


def git_tags():
    tags = []
    for tag in repo.tags:
        tags.append(tag.name.replace("Backup-", ""))
    return tags


def semantic_release_name(branch_name):
    name_sp = branch_name.split("-")
    if len(branch_name) == 10:
        return "v" + str(name_sp[0]) + str(name_sp[1]) + str(name_sp[2]) + ".0"
    elif branch_name.count("-") == 3:
        return (
            "v" + str(name_sp[0]) + str(name_sp[1]) + str(name_sp[2]) + "." + name_sp[3]
        )
    elif len(branch_name) == 11:
        return (
            "v"
            + str(name_sp[0])
            + str(name_sp[1])
            + str(name_sp[2])[0:2]
            + "."
            + name_sp[2][2:]
        )


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
        "generate_release_notes": False,
    }

    r = requests.post(
        GIT_REPO_URL,
        data=json.dumps(data_body),
        headers=headers,
        verify=True
    )


def git_delete_branch(date_str):
    repo.git.checkout("main")
    repo.git.branch("-d", date_str)
    origin = repo.remote(name="origin")
    origin.push()
    logging.info(f"repo.git.branch -d")


####################################################################
# Update EXFOR ENTRY based on TRANS
####################################################################


def download_trans_files(trans_list: list):
    for trans in trans_list:
        try:
            url = "".join([EXFOR_TRANS_URL, trans])
            r = requests.get(url, allow_redirects=True)

        except:
            url = "".join([TRANS_REPO_URL, "-/tree/main/trans_files", trans])
            r = requests.get(url, allow_redirects=True)

        if r.status_code == 404:
            logging.error(
                f"Something wrong with retrieving trans list from both IAEA-NDS Web and Databank Gitlab."
            )
            sys.exit()

        else:
            if not os.path.exists(TEMP_TRANS):
                os.mkdir(TEMP_TRANS)

            open(f"{TEMP_TRANS}/{trans}", "wb").write(r.content)

        logging.info(f"{trans} file downloaded")

    return


def get_subent_index(lines):
    content_indexes = {}
    for i, line in enumerate(lines):
        if "TRANS" in line[0:5] or "ENDTRANS" in line[0:8]:
            continue

        if "ENTRY" in line[0:5]:
            entry_num = line[17:22]
            ent_start_index = i
            content_indexes[entry_num] = {"ENTRY": {}, "SUBENTRIES": {}}

        elif "SUBENT" in line[0:6]:
            subnet_num = line[14:22]
            subent_start_index = i

        elif "ENDSUBENT" in line[0:9]:
            subent_end_index = i
            content_indexes[entry_num]["SUBENTRIES"][subnet_num] = {
                "start": subent_start_index,
                "end": subent_end_index,
            }

        elif "NOSUBENT" in line[0:8]:
            subnet_num = line[14:22]
            content_indexes[entry_num]["SUBENTRIES"][subnet_num] = {
                "start": i,
                "end": i,
            }

        elif "ENDENTRY" in line[0:8]:
            ent_end_index = i
            content_indexes[entry_num]["ENTRY"] = {
                "start": ent_start_index,
                "end": ent_end_index,
            }

            """
            {'M0538': {
                'ENTRY': {'start': 1, 'end': 454}, 
                'SUBENTRIES': 
                    {'M0538001': {'start': 2, 'end': 34}, 'M0538002': {'start': 35, 'end': 220}, 'M0538003': {'start': 221, 'end': 419}, 'M0538004': {'start': 420, 'end': 436}, 'M0538005': {'start': 437, 'end': 453}}}, 
            'M0702': {
                'ENTRY': {'start': 455, 'end': 1197}, 
                'SUBENTRIES': {'M0702001': {'start': 456, 'end': 493}, 'M0702002': {'start': 494, 'end': 698}, 'M0702003': {'start': 699, 'end': 993}, 'M0702004': {'start': 994, 'end': 1196}}},
            """
    return content_indexes


def ent_header(trans, entry_num, ent_date, trans_date):
    if len(entry_num) == 5:
        ## ENTRY            M0538   20230918   20231102   20231102       M126
        return "{:11}{:>11}{:>11}{:>11}{:>11}{:>11}\n".format(
            "ENTRY",
            entry_num.upper(),
            ent_date,
            trans_date,
            trans_date,
            trans.split(".")[1].upper(),
        )

    if len(entry_num) == 8:
        ## SUBENT        M1040001   20221223   20230307   20230307       M122
        return "{:11}{:>11}{:>11}{:>11}{:>11}{:>11}\n".format(
            "SUBENT",
            entry_num.upper(),
            ent_date,
            trans_date,
            trans_date,
            trans.split(".")[1].upper(),
        )

    else:
        return None



def ent_footer(num):
    return "{:11}{:>11}\n".format("ENDENTRY", num)



def process_trans_file(trans: str):
    logging.info(f"process: {trans} file started")
    """
    trans_lines:    all lines in the TRANS
    trans_indexes:  line numbers of start and end of ENTRY and SUBENT in the TRANS
    ent_lines:      all lines in the current ENTRY
    ent_indexes:    line numbers of start and end of SUBENT in the ENTRY
    """

    ## Read the source file
    trans_file_path = os.path.join(TEMP_TRANS, trans)
    trans_lines = []
    with open(trans_file_path, "r") as trans_file:
        for line in trans_file:
            if line.startswith("END"):
                trans_lines += [line[0:22].rstrip() + "\n"]
            else:
                trans_lines += [line[0:66].rstrip() + "\n"]
        trans_indexes = get_subent_index(trans_lines)
    

    for entry_num in trans_indexes.keys():
        entry_dir = os.path.join(EXFOR_ALL_PATH, entry_num[0:3])
        ## Check if the entry dir exist
        if not os.path.exists(entry_dir):
            os.mkdir(entry_dir)



        ent_file_name = os.path.join(entry_dir, entry_num[0:5] + ".x4")
        ## Check if the entry file exist, else create a new one
        if os.path.exists(ent_file_name):
            """
            Update existing entry file
            """
            with open(ent_file_name, "r") as e:
                ent_lines = e.readlines()

            ent_indexes = get_subent_index(ent_lines)

            subents = sorted(
                set(
                    list(ent_indexes[entry_num]["SUBENTRIES"].keys())
                    + list(trans_indexes[entry_num]["SUBENTRIES"].keys())
                )
            )

        else:
            """
            Create new file
            """
            subents = sorted(list(trans_indexes[entry_num]["SUBENTRIES"].keys()))

        trans_date = trans_lines[0][22:33]
        ent_date = trans_lines[ trans_indexes[entry_num]["ENTRY"]["start"] ][22:33]

        ## create ENTRY in the list
        new_subent_lines = []
        new_subent_lines += [ ent_header(trans, entry_num, ent_date, trans_date) ]


        for subent in subents:
            """
            {'M0538': {'ENTRY': {'start': 0, 'end': 433},
                        'SUBENTRIES': {'M0538001': {'start': 1, 'end': 33},
                                        'M0538002': {'start': 34, 'end': 212}...
            """
            if trans_indexes[entry_num]["SUBENTRIES"].get(subent):
                src_start = trans_indexes[entry_num]["SUBENTRIES"][subent]["start"]
                src_end = trans_indexes[entry_num]["SUBENTRIES"][subent]["end"]

                new_subent_lines += [ ent_header(trans, subent, ent_date, trans_date) ]
                new_subent_lines +=  trans_lines[src_start + 1 : src_end + 1] # already a list


            else:
                dest_start = ent_indexes[entry_num]["SUBENTRIES"][subent]["start"]
                dest_end = ent_indexes[entry_num]["SUBENTRIES"][subent]["end"]

                if dest_start == dest_end:

                    new_subent_lines +=   ent_lines[dest_start : dest_end] 

                else:

                    new_subent_lines +=  ent_lines[dest_start : dest_end + 1] # already a list

        ## end ENTRY
        new_subent_lines += [ ent_footer(len(subents)) ]

        with open(ent_file_name, "w") as e:
            for line in new_subent_lines:
                e.write(line)

        logging.info(f"end: {trans} {entry_num}")

    logging.info(f"end: {trans}")


def process_release(date_str, trans_list):
    ## create new branch and extract master file and split into exntry
    git_new_branch(date_str)

    for trans in trans_list:
        logging.info(f"start processing of {trans} in {date_str}")
        process_trans_file(trans)

    ## git commit, push, merge
    git_add_commit(date_str)
    git_push_branch(date_str)
    git_merge_to_main(date_str)

    ## create Release in Github
    git_tagging(date_str)

    ## release does not work from the CLI from Github/Actions,
    ## it needs curl to post to REST API
    ## (see .github/workflows/manual.yaml)
    git_release(date_str)

    ## delete branch
    git_delete_branch(date_str)

    ## delete donwnloaded files
    del_files(TEMP_TRANS)


####################################################################
# This is the process to update the repository.
####################################################################


def update():
    x = get_list_of_trans_files()
    tags = git_tags()

    processed = []
    not_processed = []

    ## check if there are any unprocessed trans file
    for date_str in x.keys():
        date_dt = convert_dtform(date_str)
        if date_dt < datetime.date(2023, 11, 2):
            """
            Since the production of EXFOR backup files are suspended by NRDC after the final backup file, 
            which corresponds to the 2023-10-27 database version and contains trans.o097, 
            https://github.com/IAEA-NDS/exfor_master/releases/tag/Backup-2023-10-27), 
            the master file will be updated based on  TRANS files.
            """
            continue

        if date_str in tags:
            processed.append(date_str)

        else:
            not_processed.append(date_str)

    logging.info(f"process starts for {not_processed}")

    if not_processed:

        """
        After the TRANS files have been back public in May 2024, the name of the 'release' 
        will be the date of the TRANS file. If more than one TRANS files exist, all TRANS are 
        included in one 'release'.
        """
        for date_str in not_processed:
            download_trans_files(x[date_str])
            process_release(date_str, x[date_str])

    else:
        logging.info(f"repository is up-to-date")

    return " ".join(not_processed)


if __name__ == "__main__":
    print(update())

