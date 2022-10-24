#!/bin/bash

not_processed=$1
n=${#not_processed}


if [ $n -eq 10 ];
then
    semantic_release_name=v${not_processed:0:4}${not_processed:5:2}${not_processed:8:2}.0
    echo $semantic_release_name

elif [ $n -eq 12 ];
then
    semantic_release_name=v${not_processed:0:4}${not_processed:5:2}${not_processed:8:2}.${not_processed:11:1}
    echo $semantic_release_name


elif [ $n -eq 11 ];
then
    semantic_release_name=v${not_processed:0:4}${not_processed:5:2}${not_processed:8:2}.${not_processed:10:1}
    echo $semantic_release_name
fi
