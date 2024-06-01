# EXFOR Master Files Repository

This repository contains all EXFOR Master Files restored from backup zip files maintained by the IAEA Nuclear Data Section (until October 2023) and updated from TRANS files finalized by the [Nuclear Reaction Data Centres (NRDC)](https://nds.iaea.org/nrdc/) (since June 2024). The EXFOR Master Files serve as an input for the [IAEA Nuclear Reaction Data Explorer](https://nds.iaea.org/dataexplorer/). The JSON formatted EXFOR entries are available in the [EXFOR_JSON repository](https://github.com/IAEA-NDS/exfor_json).

## Download
Clone the repository from a terminal using:
```sh
git clone https://github.com/IAEA-NDS/exfor_master.git
```

### Pull the Updates
The latest release version of the EXFOR Master can always be found at the head of the [main](https://github.com/IAEA-NDS/exfor_master) branch. This repository is updated automatically when the NRDC finalizes and releases TRANS (final transmission) files. Updates are made irregularly. To update the repository after cloning, pull the updates from the terminal:
```sh
git pull origin main
```

### Download as Zip File
Zip files for each release can be found in the [releases](https://github.com/IAEA-NDS/exfor_master/releases) section, tagged by the update date. Note that tags up to [v20231027.0](https://github.com/IAEA-NDS/exfor_master/releases/tag/Backup-2023-10-27) were based on EXFOR database updates. Tags from [v20231108.0](https://github.com/IAEA-NDS/exfor_master/releases/tag/Backup-2023-11-08) onward are based on the update date of the [TRANS](https://www-nds.iaea.org/nrdc/exfor-master/trans/) files.

## Usage
### Check All Branches
Branch names are based on the timestamp (filename) of the backup zip file:
```sh
git log --all --decorate --oneline --graph
```

### Check Modification History
You can check the updates for a specific entry as follows:
```sh
git log -p exforall/224/22449.x4
```

## Access EXFOR Entries 
Several web interfaces are available from the IAEA website:
- Reaction Based Data Plotter: [IAEA Nuclear Reaction Data Explorer](https://nds.iaea.org/dataexplorer/)
- EXFOR Entry Search: [IAEA Nuclear Reaction Data Explorer](https://nds.iaea.org/dataexplorer/exfor/search)
- Search and Data Retrievals: [EXFOR Data Retrieval System](https://nds.iaea.org/exfor/)

## Master File Distribution from NRDC
All data have been compiled through the International Network of Nuclear Reaction Data Centres (NRDC) network activities.
- [NRDC Homepage](https://www-nds.iaea.org/nrdc/exfor-master/)