
pid_of_locationd=`pidof locationd`

uptime_locationd=`ps -o etime ${pid_of_locationd} | tr -d "  ELAPSED" | tr -d "\n"`
echo ${uptime_locationd}
