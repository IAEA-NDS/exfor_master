 -----------------------------------------------------------------------------
                           Nuclear Data Section
                     International Atomic Energy Agency

                                2005-2022
 -----------------------------------------------------------------------------

### EXFOR Master Files Backup Test Repository
This repository contains the all EXFOR Master files restored from backup zip files maintained in the IAEA Nuclear Data Section. All data have been compiled by International Network of Nuclear Reaction Data Centres (NRDC).

See details in: [https://nds.iaea.org/nrdc/](https://nds.iaea.org/nrdc/)

Data retrieval system is avaialbe at: [https://nds.iaea.org/exfor/](https://nds.iaea.org/exfor/)


Please note that this is a test repository.


#### Download
You can download the repository from a terminal using:
```
git clone https://github.com/shinokumura/exfor_master.git
```

#### Check modification history
You can check the updates for the specific entry as follows.
```
git log -p exforall/224/22449.x4
```


#### Run locally
```
pip install -r requirements.txt
python exfor_backups.py
```
