

for file in ./exforall/*/*.x4
do
    basename=`basename $file`
    count=`git log --format='%aN' $file | wc -l`
    hashobj=`git hash-object  $file`
    echo ${basename:0:5} `git log -1 --pretty=format:%s $file` $count $hashobj
done