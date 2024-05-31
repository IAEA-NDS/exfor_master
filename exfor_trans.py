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
)
from zipfile import ZipFile
from bs4 import BeautifulSoup

import logging
logging.basicConfig(filename="process.log", level=logging.DEBUG, filemode="w")
import pandas as pd

from config import EXFOR_TRANS_URL, EXFOR_ALL_PATH, TRANS_REPO_URL, headers, TEMP_TRANS, GIT_REPO_PATH, GIT_REPO_URL


####################################################################
# For maintenance
####################################################################

def get_list_of_trans_files():
    ''' 
    pd.read_html returns the list of dataframes
    groupby returns dictionary in { '2024-05-06': ['trans.1510', 'trans.1511', 'trans.c235', 'trans.c236', 'trans.l052']} format
    '''
    dfs = pd.read_html(EXFOR_TRANS_URL)
    df = dfs[0]
    df[["Date", "Time"]] = df['Last modified'].str.split(' ', expand=True)

    df = df.drop(df[df['Name'].str.contains("trans.zip")].index)
    df = df.drop(df[df['Name'].str.contains("trans.99")].index)
    df = df.dropna(subset=["Last modified"])

    x = df.groupby("Date")["Name"].apply(list).to_dict()

    # x = {'2015-03-13': ['trans.l025'], '2015-04-08': ['trans.c146'], '2015-04-10': ['trans.4167'], '2015-04-13': ['trans.m077'], '2015-04-20': ['trans.c147'], '2015-04-28': ['trans.l026'], '2015-04-29': ['trans.d098', 'trans.e095', 'trans.e096', 'trans.g032', 'trans.r028'], '2015-05-12': ['trans.4168'], '2015-05-18': ['trans.2241', 'trans.3169'], '2015-05-19': ['trans.m078'], '2015-05-28': ['trans.a083'], '2015-06-05': ['trans.1405'], '2015-06-16': ['trans.c148'], '2015-06-22': ['trans.m079'], '2015-06-24': ['trans.k015'], '2015-06-25': ['trans.e097'], '2015-07-06': ['trans.3170'], '2015-07-09': ['trans.o054'], '2015-07-15': ['trans.d099'], '2015-07-20': ['trans.1406'], '2015-07-23': ['trans.l027'], '2015-07-24': ['trans.c149'], '2015-08-07': ['trans.g033'], '2015-08-11': ['trans.4169', 'trans.f058'], '2015-08-13': ['trans.v033'], '2015-08-27': ['trans.1407'], '2015-09-25': ['trans.3171', 'trans.3172', 'trans.e098', 'trans.e099'], '2015-09-28': ['trans.c150', 'trans.d100', 'trans.g034'], '2015-09-29': ['trans.m080'], '2015-10-05': ['trans.c151'], '2015-10-09': ['trans.c152'], '2015-11-09': ['trans.d101'], '2015-11-13': ['trans.4170'], '2015-11-16': ['trans.2242', 'trans.4171'], '2016-01-20': ['trans.c153'], '2016-01-21': ['trans.1408'], '2016-01-22': ['trans.c154'], '2016-02-02': ['trans.d102'], '2016-02-04': ['trans.1409', 'trans.1410'], '2016-02-05': ['trans.e100'], '2016-02-09': ['trans.2243', 'trans.2244'], '2016-02-15': ['trans.f059'], '2016-02-16': ['trans.4172', 'trans.4173'], '2016-02-23': ['trans.1411', 'trans.l028', 'trans.s019'], '2016-03-11': ['trans.f060'], '2016-03-14': ['trans.m081'], '2016-03-30': ['trans.c155'], '2016-04-08': ['trans.3173'], '2016-04-12': ['trans.1412'], '2016-04-15': ['trans.1413'], '2016-04-29': ['trans.e101'], '2016-05-02': ['trans.d103', 'trans.m082'], '2016-05-03': ['trans.1414'], '2016-05-05': ['trans.v034'], '2016-05-10': ['trans.e102'], '2016-05-11': ['trans.f061'], '2016-05-23': ['trans.o055', 'trans.o056'], '2016-05-24': ['trans.2245', 'trans.2246', 'trans.2247', 'trans.o057'], '2016-05-25': ['trans.1415', 'trans.2248'], '2016-05-27': ['trans.c156'], '2016-06-15': ['trans.1416', 'trans.m083'], '2016-06-21': ['trans.a084'], '2016-06-26': ['trans.e103'], '2016-06-28': ['trans.g035'], '2016-06-29': ['trans.d104'], '2016-07-12': ['trans.f062'], '2016-07-27': ['trans.c157'], '2016-08-12': ['trans.k016', 'trans.l029'], '2016-08-18': ['trans.2249', 'trans.c158'], '2016-08-24': ['trans.1417'], '2016-08-25': ['trans.1418'], '2016-08-29': ['trans.2250'], '2016-09-05': ['trans.3174', 'trans.d105'], '2016-09-09': ['trans.a085'], '2016-09-21': ['trans.c159'], '2016-09-27': ['trans.c160'], '2016-09-29': ['trans.2251', 'trans.b025'], '2016-10-06': ['trans.o058'], '2016-10-13': ['trans.l030'], '2016-10-14': ['trans.1419'], '2016-10-17': ['trans.c161'], '2016-11-14': ['trans.m084'], '2016-11-15': ['trans.c162'], '2016-11-16': ['trans.3175'], '2016-11-21': ['trans.d106'], '2016-11-23': ['trans.k017'], '2017-01-16': ['trans.c163', 'trans.l031', 'trans.m085'], '2017-01-17': ['trans.3176', 'trans.g036'], '2017-01-19': ['trans.4174', 'trans.f063', 'trans.s020'], '2017-01-24': ['trans.2252', 'trans.2253'], '2017-01-26': ['trans.o059'], '2017-01-31': ['trans.d107'], '2017-02-15': ['trans.2254', 'trans.2255'], '2017-02-17': ['trans.e104'], '2017-02-22': ['trans.m086'], '2017-03-03': ['trans.e105', 'trans.e106'], '2017-03-20': ['trans.2256'], '2017-03-28': ['trans.2257'], '2017-03-30': ['trans.c164'], '2017-03-31': ['trans.d108'], '2017-04-06': ['trans.a086', 'trans.a087'], '2017-04-11': ['trans.f064'], '2017-05-02': ['trans.g037'], '2017-05-03': ['trans.1420', 'trans.1421', 'trans.1422', 'trans.m087'], '2017-05-04': ['trans.1423'], '2017-05-08': ['trans.e107'], '2017-05-15': ['trans.1424', 'trans.2258'], '2017-05-26': ['trans.s021'], '2017-05-29': ['trans.3177', 'trans.e108'], '2017-06-06': ['trans.1425'], '2017-06-07': ['trans.m088'], '2017-06-08': ['trans.o060', 'trans.o061'], '2017-06-13': ['trans.2259'], '2017-06-21': ['trans.c165'], '2017-06-27': ['trans.1426'], '2017-06-28': ['trans.j010'], '2017-06-30': ['trans.3178', 'trans.4175', 'trans.d109', 'trans.d110'], '2017-07-12': ['trans.b026', 'trans.v035'], '2017-07-18': ['trans.m089'], '2017-07-24': ['trans.1427'], '2017-07-25': ['trans.c166'], '2017-08-08': ['trans.l032'], '2017-09-18': ['trans.1428', 'trans.1429', 'trans.3179', 'trans.d111', 'trans.g038', 'trans.s022'], '2017-09-25': ['trans.m090'], '2017-09-26': ['trans.c167'], '2017-10-03': ['trans.f065'], '2017-10-24': ['trans.1430', 'trans.1431'], '2017-11-08': ['trans.1432'], '2017-11-16': ['trans.m091'], '2017-11-22': ['trans.3180', 'trans.d112', 'trans.g039'], '2017-12-07': ['trans.c168'], '2017-12-22': ['trans.1433'], '2017-12-27': ['trans.c169'], '2018-01-08': ['trans.1434'], '2018-01-09': ['trans.m092'], '2018-01-15': ['trans.f066'], '2018-01-17': ['trans.e109'], '2018-01-19': ['trans.4176'], '2018-01-22': ['trans.2260', 'trans.c170'], '2018-01-23': ['trans.1435', 'trans.1436', 'trans.2261', 'trans.2262', 'trans.e110'], '2018-01-24': ['trans.2263', 'trans.2264', 'trans.o062'], '2018-01-29': ['trans.2265', 'trans.o063'], '2018-02-02': ['trans.l033'], '2018-02-08': ['trans.1437'], '2018-02-09': ['trans.3181', 'trans.s023'], '2018-02-16': ['trans.c171'], '2018-02-23': ['trans.e111', 'trans.l034', 'trans.m093'], '2018-03-09': ['trans.c172'], '2018-03-15': ['trans.d113', 'trans.g040'], '2018-03-16': ['trans.d114'], '2018-03-19': ['trans.4177'], '2018-03-29': ['trans.1438'], '2018-04-06': ['trans.m094'], '2018-04-09': ['trans.f067'], '2018-04-10': ['trans.c173'], '2018-04-20': ['trans.3182', 'trans.d115'], '2018-04-23': ['trans.a088'], '2018-04-24': ['trans.e112', 'trans.e113', 'trans.e114'], '2018-04-26': ['trans.3183', 'trans.e115'], '2018-05-14': ['trans.l035'], '2018-05-16': ['trans.m095'], '2018-05-25': ['trans.4178'], '2018-06-04': ['trans.4179'], '2018-06-20': ['trans.1439'], '2018-06-25': ['trans.b027', 'trans.v036'], '2018-06-29': ['trans.3184', 'trans.3185', 'trans.b028', 'trans.d116', 'trans.d117', 'trans.g041', 'trans.s024'], '2018-08-08': ['trans.1440', 'trans.m096'], '2018-08-09': ['trans.2266'], '2018-08-14': ['trans.c174'], '2018-09-17': ['trans.2267'], '2018-09-18': ['trans.1441'], '2018-09-19': ['trans.a089', 'trans.a090', 'trans.c175'], '2018-09-26': ['trans.l036'], '2018-09-27': ['trans.f068', 'trans.o064'], '2018-10-04': ['trans.e116'], '2018-10-10': ['trans.m097'], '2018-10-12': ['trans.1442', 'trans.c176'], '2018-10-30': ['trans.1443'], '2018-11-27': ['trans.e117'], '2018-11-29': ['trans.f069'], '2018-12-04': ['trans.3186', 'trans.d118'], '2018-12-06': ['trans.g042'], '2018-12-07': ['trans.m098'], '2018-12-29': ['trans.4180'], '2019-01-08': ['trans.e118'], '2019-01-09': ['trans.1444', 'trans.c177'], '2019-01-18': ['trans.e119'], '2019-01-19': ['trans.c178', 'trans.c179'], '2019-01-21': ['trans.c180'], '2019-01-22': ['trans.c181', 'trans.e120'], '2019-01-31': ['trans.e121'], '2019-02-06': ['trans.o065', 'trans.o066'], '2019-02-15': ['trans.f070'], '2019-02-19': ['trans.2268'], '2019-02-20': ['trans.l037'], '2019-02-21': ['trans.2269', 'trans.2270'], '2019-02-22': ['trans.2271', 'trans.3187', 'trans.k018', 'trans.r029', 'trans.s025'], '2019-02-28': ['trans.1445'], '2019-03-15': ['trans.m099'], '2019-03-18': ['trans.e122'], '2019-03-22': ['trans.1446', 'trans.d119'], '2019-03-26': ['trans.4181', 'trans.c182'], '2019-04-05': ['trans.2272'], '2019-04-23': ['trans.2273', 'trans.2274'], '2019-04-24': ['trans.2275', 'trans.2276'], '2019-04-26': ['trans.c183'], '2019-04-30': ['trans.1447'], '2019-05-07': ['trans.b029'], '2019-05-14': ['trans.f071'], '2019-06-03': ['trans.l038'], '2019-06-06': ['trans.c184'], '2019-06-12': ['trans.l039'], '2019-06-13': ['trans.l040'], '2019-06-17': ['trans.2277'], '2019-06-18': ['trans.3188'], '2019-06-19': ['trans.d120'], '2019-07-01': ['trans.1448'], '2019-07-12': ['trans.o067'], '2019-07-13': ['trans.o068', 'trans.o069'], '2019-07-17': ['trans.4182'], '2019-07-20': ['trans.g043', 'trans.l041'], '2019-07-22': ['trans.e123'], '2019-07-25': ['trans.m100'], '2019-08-13': ['trans.1449'], '2019-08-19': ['trans.1450'], '2019-08-21': ['trans.m101'], '2019-08-22': ['trans.a091'], '2019-08-28': ['trans.2278', 'trans.2279'], '2019-09-13': ['trans.2280'], '2019-09-14': ['trans.1451'], '2019-09-18': ['trans.1452'], '2019-09-19': ['trans.l042'], '2019-09-24': ['trans.c185'], '2019-09-27': ['trans.1453'], '2019-10-01': ['trans.2281'], '2019-10-03': ['trans.1454'], '2019-10-04': ['trans.a092', 'trans.f072', 'trans.k019'], '2019-10-09': ['trans.d121', 'trans.d122'], '2019-10-11': ['trans.o070'], '2019-10-14': ['trans.4183'], '2019-10-22': ['trans.1455'], '2019-10-23': ['trans.3189', 'trans.3190'], '2019-11-20': ['trans.m102'], '2019-11-22': ['trans.c186'], '2019-11-24': ['trans.1456'], '2019-12-09': ['trans.3191'], '2019-12-16': ['trans.1457', 'trans.2282', 'trans.d123', 'trans.s026'], '2019-12-17': ['trans.3192', 'trans.o071', 'trans.o072'], '2019-12-28': ['trans.m103'], '2020-01-09': ['trans.f073'], '2020-01-10': ['trans.1458', 'trans.1459'], '2020-01-13': ['trans.3193', 'trans.4184'], '2020-01-20': ['trans.e124'], '2020-01-21': ['trans.e125', 'trans.k020'], '2020-01-23': ['trans.d124'], '2020-01-27': ['trans.2283'], '2020-02-04': ['trans.r030'], '2020-02-07': ['trans.1460', 'trans.l043'], '2020-02-17': ['trans.4185'], '2020-02-18': ['trans.m104', 'trans.m105'], '2020-03-02': ['trans.2284', 'trans.3194', 'trans.o073'], '2020-03-04': ['trans.o074'], '2020-03-05': ['trans.2285'], '2020-03-09': ['trans.1461'], '2020-03-12': ['trans.1462'], '2020-03-27': ['trans.f074'], '2020-04-10': ['trans.c187'], '2020-04-11': ['trans.a093'], '2020-04-14': ['trans.1463'], '2020-04-16': ['trans.3195', 'trans.d125'], '2020-04-21': ['trans.g044', 'trans.s027', 'trans.v037'], '2020-04-23': ['trans.m106'], '2020-04-30': ['trans.1464'], '2020-05-14': ['trans.4186'], '2020-05-28': ['trans.d126', 'trans.o075'], '2020-05-31': ['trans.1465'], '2020-06-09': ['trans.f075'], '2020-06-17': ['trans.c188', 'trans.c189'], '2020-06-22': ['trans.2286', 'trans.4187'], '2020-06-23': ['trans.a094', 'trans.o076'], '2020-06-26': ['trans.f076'], '2020-06-29': ['trans.f077'], '2020-07-02': ['trans.e126'], '2020-07-08': ['trans.1466'], '2020-07-17': ['trans.a095', 'trans.g045'], '2020-07-24': ['trans.c190'], '2020-07-28': ['trans.o077'], '2020-08-03': ['trans.2287'], '2020-08-06': ['trans.3196', 'trans.d127', 'trans.m107', 'trans.s028'], '2020-08-11': ['trans.e127'], '2020-08-13': ['trans.1467'], '2020-08-18': ['trans.e128', 'trans.f078', 'trans.f079'], '2020-08-24': ['trans.c191'], '2020-08-27': ['trans.4188'], '2020-09-01': ['trans.1468'], '2020-09-10': ['trans.c192', 'trans.f080'], '2020-09-17': ['trans.c193'], '2020-09-25': ['trans.1469', 'trans.c194'], '2020-10-07': ['trans.2288', 'trans.2289'], '2020-10-08': ['trans.2290', 'trans.o078'], '2020-10-13': ['trans.f081'], '2020-10-14': ['trans.e129'], '2020-10-19': ['trans.1470'], '2020-10-27': ['trans.e130'], '2020-10-28': ['trans.c195'], '2020-11-12': ['trans.4189'], '2020-11-19': ['trans.d128'], '2020-11-24': ['trans.1471'], '2020-12-01': ['trans.4190'], '2020-12-03': ['trans.3197', 'trans.m108'], '2020-12-18': ['trans.m109'], '2021-01-04': ['trans.o079'], '2021-01-05': ['trans.2291', 'trans.2292'], '2021-01-06': ['trans.2293', 'trans.2294', 'trans.2295'], '2021-01-12': ['trans.o080'], '2021-01-17': ['trans.c196'], '2021-01-18': ['trans.m110'], '2021-01-20': ['trans.4191'], '2021-01-28': ['trans.1472'], '2021-01-30': ['trans.c197'], '2021-02-15': ['trans.b030', 'trans.c198'], '2021-02-16': ['trans.v038'], '2021-02-17': ['trans.g046'], '2021-02-19': ['trans.d129'], '2021-02-20': ['trans.3198'], '2021-02-24': ['trans.1473'], '2021-03-03': ['trans.2296'], '2021-03-05': ['trans.o081', 'trans.s029'], '2021-03-15': ['trans.4192'], '2021-03-19': ['trans.4193'], '2021-03-21': ['trans.l044'], '2021-04-06': ['trans.a096'], '2021-04-15': ['trans.f082'], '2021-04-21': ['trans.1474'], '2021-04-22': ['trans.2297'], '2021-04-23': ['trans.o082'], '2021-04-27': ['trans.1475'], '2021-05-18': ['trans.2298', 'trans.m111', 'trans.o083'], '2021-05-21': ['trans.3199', 'trans.v039'], '2021-05-23': ['trans.c199'], '2021-05-25': ['trans.1476'], '2021-06-01': ['trans.a097'], '2021-06-07': ['trans.1477', 'trans.4194', 'trans.e131'], '2021-06-15': ['trans.3200', 'trans.d130'], '2021-06-22': ['trans.e132'], '2021-06-25': ['trans.2299'], '2021-06-28': ['trans.l045', 'trans.m112'], '2021-08-09': ['trans.1478'], '2021-08-10': ['trans.4195', 'trans.4196', 'trans.m113'], '2021-08-12': ['trans.f083'], '2021-08-17': ['trans.f084'], '2021-08-19': ['trans.f085'], '2021-08-20': ['trans.1479', 'trans.c200'], '2021-08-23': ['trans.1480'], '2021-08-24': ['trans.2300'], '2021-09-07': ['trans.c201'], '2021-09-14': ['trans.1481', 'trans.4197'], '2021-09-15': ['trans.4198'], '2021-09-21': ['trans.a098'], '2021-09-29': ['trans.3201', 'trans.d131', 'trans.g047'], '2021-10-01': ['trans.4199', 'trans.m114'], '2021-10-05': ['trans.f086'], '2021-10-22': ['trans.c202'], '2021-11-08': ['trans.1482', 'trans.1483'], '2021-11-12': ['trans.4200'], '2021-11-17': ['trans.3202', 'trans.d132'], '2021-11-22': ['trans.m115'], '2021-11-23': ['trans.c203', 'trans.l046'], '2021-12-01': ['trans.2301', 'trans.l047'], '2021-12-02': ['trans.2302'], '2021-12-06': ['trans.1484'], '2021-12-08': ['trans.1485'], '2021-12-15': ['trans.c204', 'trans.f087'], '2021-12-21': ['trans.3203'], '2022-01-04': ['trans.o084'], '2022-01-12': ['trans.3204', 'trans.d133', 'trans.o085'], '2022-01-13': ['trans.4201', 'trans.m116'], '2022-01-17': ['trans.2303'], '2022-01-19': ['trans.c205'], '2022-01-24': ['trans.3205', 'trans.b031', 'trans.d134'], '2022-01-26': ['trans.1486'], '2022-01-27': ['trans.c206'], '2022-01-31': ['trans.4202', 'trans.b032'], '2022-02-14': ['trans.1487', 'trans.c207'], '2022-02-17': ['trans.c208'], '2022-03-01': ['trans.1488'], '2022-03-03': ['trans.3206'], '2022-03-05': ['trans.4203'], '2022-03-07': ['trans.1489'], '2022-03-17': ['trans.2304', 'trans.2305', 'trans.2306'], '2022-03-18': ['trans.2307'], '2022-03-21': ['trans.d135', 'trans.g048'], '2022-03-23': ['trans.s030'], '2022-03-28': ['trans.1490', 'trans.c209'], '2022-04-01': ['trans.m117'], '2022-04-19': ['trans.1491'], '2022-05-04': ['trans.1492'], '2022-05-23': ['trans.c210'], '2022-05-30': ['trans.3207', 'trans.b033', 'trans.d136'], '2022-05-31': ['trans.l048'], '2022-06-07': ['trans.o086', 'trans.o087'], '2022-06-09': ['trans.1493'], '2022-06-10': ['trans.4204', 'trans.4205'], '2022-06-13': ['trans.e133', 'trans.e134'], '2022-06-27': ['trans.v040'], '2022-06-28': ['trans.4206', 'trans.m118'], '2022-07-04': ['trans.a099', 'trans.f088'], '2022-07-20': ['trans.1494', 'trans.2308', 'trans.c211', 'trans.o088'], '2022-08-02': ['trans.1495', 'trans.c212'], '2022-08-12': ['trans.s031'], '2022-08-16': ['trans.m119'], '2022-08-18': ['trans.e135', 'trans.j011', 'trans.k021'], '2022-08-22': ['trans.2309', 'trans.2310', 'trans.2311'], '2022-08-23': ['trans.c213', 'trans.l049', 'trans.o089'], '2022-08-29': ['trans.c214'], '2022-09-14': ['trans.f089'], '2022-09-16': ['trans.a100'], '2022-09-26': ['trans.1496', 'trans.1497'], '2022-09-28': ['trans.1498'], '2022-10-05': ['trans.o090'], '2022-10-11': ['trans.l050'], '2022-10-13': ['trans.4207'], '2022-10-17': ['trans.f090', 'trans.f091'], '2022-10-18': ['trans.1499'], '2022-10-21': ['trans.f092'], '2022-11-07': ['trans.m120'], '2022-11-28': ['trans.c215'], '2022-12-22': ['trans.f093'], '2022-12-23': ['trans.a101', 'trans.a102'], '2022-12-26': ['trans.a103'], '2023-01-04': ['trans.c216'], '2023-01-12': ['trans.1500', 'trans.c217'], '2023-01-16': ['trans.b034', 'trans.d137', 'trans.g049'], '2023-01-18': ['trans.4208', 'trans.m121', 'trans.s032', 'trans.v041'], '2023-01-19': ['trans.3208'], '2023-02-13': ['trans.c218'], '2023-02-27': ['trans.4209', 'trans.4210'], '2023-03-02': ['trans.1501'], '2023-03-04': ['trans.1502'], '2023-03-06': ['trans.c219'], '2023-03-07': ['trans.e136', 'trans.m122'], '2023-03-14': ['trans.f094'], '2023-03-15': ['trans.c220'], '2023-03-31': ['trans.2312', 'trans.o091'], '2023-04-03': ['trans.o092'], '2023-04-11': ['trans.1503'], '2023-04-18': ['trans.4211'], '2023-04-28': ['trans.c221'], '2023-05-15': ['trans.c222'], '2023-05-23': ['trans.2313', 'trans.2314', 'trans.o093', 'trans.o094'], '2023-05-29': ['trans.3209', 'trans.b035', 'trans.d138', 'trans.g050'], '2023-05-31': ['trans.1504'], '2023-06-12': ['trans.m123', 'trans.m124'], '2023-06-15': ['trans.4212'], '2023-06-23': ['trans.c223'], '2023-06-26': ['trans.c224'], '2023-06-29': ['trans.e137'], '2023-07-13': ['trans.c225'], '2023-07-18': ['trans.o095'], '2023-08-15': ['trans.c226'], '2023-09-07': ['trans.2315'], '2023-09-08': ['trans.4213'], '2023-09-11': ['trans.m125'], '2023-09-12': ['trans.1505'], '2023-09-25': ['trans.1506'], '2023-09-27': ['trans.2316', 'trans.2317'], '2023-10-03': ['trans.e138'], '2023-10-15': ['trans.9911', 'trans.9912', 'trans.9913', 'trans.9914', 'trans.9915', 'trans.9916', 'trans.9917', 'trans.9918', 'trans.9919', 'trans.9920', 'trans.9921', 'trans.9922', 'trans.9923', 'trans.9924', 'trans.9925', 'trans.9926', 'trans.9927', 'trans.9928'], '2023-10-25': ['trans.o096'], '2023-10-26': ['trans.o097'], '2023-11-02': ['trans.m126'], '2023-11-08': ['trans.e139'], '2023-11-09': ['trans.4214'], '2023-11-13': ['trans.e140'], '2023-12-18': ['trans.c227', 'trans.c228'], '2023-12-22': ['trans.9929'], '2024-02-01': ['trans.2318', 'trans.o098'], '2024-02-02': ['trans.4215'], '2024-02-15': ['trans.g051'], '2024-03-05': ['trans.k022'], '2024-03-12': ['trans.m127'], '2024-03-13': ['trans.3210', 'trans.a104', 'trans.a105', 'trans.a106', 'trans.d139', 'trans.f095', 'trans.v042'], '2024-03-14': ['trans.s033'], '2024-03-15': ['trans.1507', 'trans.1508', 'trans.1509', 'trans.c229', 'trans.e141'], '2024-03-31': ['trans.3211', 'trans.3212', 'trans.4216', 'trans.d140', 'trans.d141', 'trans.g052'], '2024-04-05': ['trans.c230', 'trans.c231', 'trans.c232', 'trans.c233', 'trans.c234'], '2024-04-08': ['trans.m128', 'trans.m129'], '2024-04-11': ['trans.a107', 'trans.a108', 'trans.l051'], '2024-04-12': ['trans.f096', 'trans.f097'], '2024-04-15': ['trans.a109'], '2024-04-16': ['trans.f098'], '2024-04-17': ['trans.d142'], '2024-05-02': ['trans.a110'], '2024-05-03': ['trans.e142'], '2024-05-05': ['trans.e143', 'trans.e144'], '2024-05-06': ['trans.1510', 'trans.1511', 'trans.c235', 'trans.c236', 'trans.l052']}

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
            logging.error(f"Something wrong with retrieving trans list from both IAEA-NDS Web and Databank Gitlab.")
            sys.exit()

        else:
            # TEMP_TRANS
            if not os.path.exists(TEMP_TRANS):
                os.mkdir(TEMP_TRANS)

            open(f"{TEMP_TRANS}/{trans}", "wb").write(r.content)
            # with open(file_path, 'wb') as file:
            #     file.write(r.content)

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
            content_indexes[entry_num] = { "ENTRY":{}, "SUBENTRIES":{} }

        elif "SUBENT" in line[0:6]:
            subnet_num = line[14:22]
            subent_start_index = i

        elif "ENDSUBENT" in line[0:9]:
            subent_end_index = i
            content_indexes[entry_num]["SUBENTRIES"][subnet_num] = {"start":subent_start_index ,"end": subent_end_index}

        elif "NOSUBENT" in line[0:8]:
            subnet_num = line[14:22]
            content_indexes[entry_num]["SUBENTRIES"][subnet_num] = {"start":i ,"end": i}

        elif "ENDENTRY" in line[0:8]:
            ent_end_index = i
            content_indexes[entry_num]["ENTRY"] = {"start":ent_start_index ,"end": ent_end_index} 


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
        return '{:11}{:>11}{:>11}{:>11}{:>11}{:>11}'.format('ENTRY', entry_num.upper(), ent_date, trans_date, trans_date, trans.split(".")[1].upper())
    
    if len(entry_num) == 8: 
        ## SUBENT        M1040001   20221223   20230307   20230307       M122
        return '{:11}{:>11}{:>11}{:>11}{:>11}{:>11}\n'.format('SUBENT', entry_num.upper(), ent_date, trans_date, trans_date, trans.split(".")[1].upper())
    
    else:
        return None

    




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
    with open(trans_file_path, 'r') as trans_file:
        for line in trans_file:
            if line.startswith("END"):
                trans_lines += [ line[0:22].rstrip() ]
            else:
               trans_lines += [ line[0:66].rstrip() ]
        trans_indexes = get_subent_index(trans_lines)
        # print("trans_indexes", trans_indexes)       


    for entry_num in trans_indexes.keys():
        print(trans, entry_num)
        if entry_num != "D0208":
            continue

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
            with open(ent_file_name, 'r') as e:
                ent_lines = e.readlines()
            ent_indexes = get_subent_index(ent_lines)

            subents = sorted( set ( list( ent_indexes[entry_num]['SUBENTRIES'].keys() ) + list( trans_indexes[entry_num]['SUBENTRIES'].keys() ) ) )

        else:
            """
            Create new file
            """
            subents = sorted( list( trans_indexes[entry_num]['SUBENTRIES'].keys() ) ) 

        print(subents)
        trans_date = trans_lines[0][22:33]
        ent_date = trans_lines[ trans_indexes[entry_num]['ENTRY']["start"] ][22:33]

        ## create ENTRY in the list
        new_subent_lines = []
        # new_subent_lines += trans_lines[ trans_indexes[entry_num]['ENTRY']["start"] ]
        new_subent_lines += ent_header(trans, entry_num, ent_date, trans_date)

        for subent in subents:
            """
            {'M0538': {'ENTRY': {'start': 0, 'end': 433}, 
                        'SUBENTRIES': {'M0538001': {'start': 1, 'end': 33}, 
                                        'M0538002': {'start': 34, 'end': 212}...
            """
            if trans_indexes[entry_num]['SUBENTRIES'].get(subent):
                src_start = trans_indexes[entry_num]['SUBENTRIES'][subent]["start"]
                src_end = trans_indexes[entry_num]['SUBENTRIES'][subent]["end"]
                new_subent_lines += ["\n"]
                new_subent_lines += ent_header(trans, subent, ent_date, trans_date)
                new_subent_lines += "\n".join( trans_lines[src_start+1:src_end+1] )
                new_subent_lines += ["\n"]

            else:
                dest_start = ent_indexes[entry_num]['SUBENTRIES'][subent]["start"]
                dest_end = ent_indexes[entry_num]['SUBENTRIES'][subent]["end"]

                if dest_start == dest_end:
                    new_subent_lines += [ ent_lines[dest_start] ]

                else:
                    # new_subent_lines += ["\n"]
                    new_subent_lines += "\n".join( ent_lines[ dest_start : dest_end+1 ] )

        ## end ENTRY
        # new_subent_lines += ["\n"]
        new_subent_lines += trans_lines[ trans_indexes[entry_num]['ENTRY']["end"] ]

        with open(ent_file_name, 'w') as e:
            new_subent_lines += ["\n"]
            for line in new_subent_lines:
                e.write(line)

        logging.info(f"end: {trans} {entry_num}")

    logging.info(f"end: {trans}")




def process_release(date_str, trans_list):
    ## create new branch and extract master file and split into exntry
    # git_new_branch(date_str)

    for trans in trans_list:
        print(date_str, trans)
        logging.info(f"start processing of {trans} in {date_str}")
        process_trans_file(trans)

    # ## git commit, push, merge
    # git_add_commit(date_str)
    # git_push_branch(date_str)
    # git_merge_to_main(date_str)

    # ## create Release in Github
    # git_tagging(date_str)

    # ## release does not work from the CLI from Github/Actions, 
    # ## it needs curl to post to REST API 
    # ## (see .github/workflows/manual.yaml)
    # git_release(date_str)

    # ## delete branch
    # git_delete_branch(date_str)

    # ## delete donwnloaded files
    # del_files(TEMP_TRANS)



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
            '''
            Since the production of EXFOR backup files are suspended by NRDC after the final backup file, which corresponds to the 2023-10-27 database version and contains trans.o097, https://github.com/IAEA-NDS/exfor_master/releases/tag/Backup-2023-10-27), the master file will be updated based on  TRANS files. 
            '''
            continue

        if date_str in tags:
            processed.append(date_str)

        else:
            not_processed.append(date_str)

    logging.info(f"process starts for {not_processed}")

    not_processed = ["2024-04-17"]
    if not_processed:
        '''
        After the TRANS files have been back public in May 2024, the name of the 'release' will be the date of the TRANS file. If more than one TRANS files exist, all TRANS are included in one 'release'.
        '''
        print(not_processed)
        for date_str in not_processed:
            download_trans_files(x[date_str])
            process_release(date_str, x[date_str])

    else:
        logging.info(f"repository is up-to-date")


    return " ".join(not_processed)



if __name__ == "__main__":
    # get_list_of_trans_files()
    update()
    # print(update())


