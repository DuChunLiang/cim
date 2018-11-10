if [ ! -n "$1" ]; then
  echo 'not set can channel'
  echo 'examples: ./start_monitor.sh can0'
  exit 0
fi

sudo nohup python3 monitor_can_info.py $1> /dev/null 2>&1 &
echo 'start monitor_can_info.py success'
