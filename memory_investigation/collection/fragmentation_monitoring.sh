#!/bin/sh


diagnostics_path="/var/root/diagnostics"


mkdir -p ${diagnostics_path}
mkdir -p ${diagnostics_path}/locationd
cd ${diagnostics_path}


while :
do
	wall_clock_time=`date  "+%F_%H_%M_%S"`
	
    pid_of_locationd=`pidof locationd`
	
	# ======= Track PID changes
	uptime_locationd=`ps -o etime ${pid_of_locationd} | tr -d "  ELAPSED" | tr -d "\n"`
	
	#===== Track os transactions
	echo "${wall_clock_time}" >> ${diagnostics_path}/locationd/fragmentation.txt
	echo "PID: ${pid_of_locationd} , Uptime : ${uptime_locationd}" >> ${diagnostics_path}/locationd/fragmentation.txt
	
	
	cftime=`timetool now | cut -f3 -d" "`
	physical_footprint=`heap locationd | grep "Physical footprint:    " | cut -f2 -d":" | tr -d "M" | awk '{$1=$1;print}'`
	fragmentation=`vmmap locationd | grep -A 2 "% FRAG" | grep -v "FRAG" | grep -v "=="  | grep -o "\w*%\w*" `
	num_os_transactions=`heap --addresses=OS_os_transaction locationd | grep OS_os_transaction | grep "]" | wc -l | tr -d " "`
	
	echo "${wall_clock_time}, ${cftime},  ${uptime_locationd}, ${physical_footprint}, ${fragmentation}, ${num_os_transactions},  ${pid_of_locationd}," >> ${diagnostics_path}/locationd/fragmentation.csv
	
	printf "Sleeping 5 seconds zzzzzzzz \n"
	sleep 5
done
