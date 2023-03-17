#!/bin/sh
bckfile="EXFOR-2010-09-17.bck"

dos2unix $bckfile
#rm -r exforall
mkdir exforall
while IFS= read line;
do

if [ "${line:0:5}" = ENTRY ]; then
    entrynum=${line:17:5}
    
    echo $entrynum
    
    if [ ! -d "exforall/${entrynum:0:3}" ]; then
	mkdir exforall/${entrynum:0:3}
    fi
    if [ -f "exforall/${entrynum:0:3}/$entrynum.x4" ]; then
	rm exforall/${entrynum:0:3}/$entrynum.x4
    fi
    
    printf "%s\n" "$line" > exforall/${entrynum:0:3}/$entrynum.x4    
fi

printf "%s\n" "$line" >> exforall/${entrynum:0:3}/$entrynum.x4 

done < $bckfile

