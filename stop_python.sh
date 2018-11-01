echo 'start kill python'
for pid in $(ps aux | grep -v 'grep' | grep python | awk '{print $2}') ;do
 sudo kill -9 $pid
 echo 'kill -9 '$pid
done
