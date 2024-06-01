#!/bin/sh
# dir="/Users/sin/Downloads/entry"

# cd $dir
# mkdir exforall

# for d in `ls $dir`; do
#     cd $d
#     for f in `ls *.txt`; do
#         ff=`echo $f | tr 'a-z' 'A-Z'`
#         entdir=${ff:0:3}
        
#         if [ ! -d ../exforall/$entdir ]; then
#             mkdir "../exforall/$entdir"
#         fi

#         mv $f ../exforall/$entdir/${ff%.*}.x4
#     done
#     cd ../
# done

dir="/Users/sin/Downloads/EXFOR-masterfiles-20243105"

cd $dir
# for t in *.tar.gz; do
#     td=`echo $t | cut -f1 -d'.'`
#     mkdir $td
#     tar zxf $t -C $td
#     rm $t
# done


mkdir exforall
for d in `ls $dir`; do
    cd $d
    for f in `ls *.txt`; do
        ff=`echo $f | sed 's/entry\_//g' | tr 'a-z' 'A-Z'`
        entdir=${ff:0:3}
        echo $ff $entdir
        
        if [ ! -d ../exforall/$entdir ]; then
            mkdir "../exforall/$entdir"
        fi

        mv $f ../exforall/$entdir/${ff%.*}.x4
    done
    cd ../
done


