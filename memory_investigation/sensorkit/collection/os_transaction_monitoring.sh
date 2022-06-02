#!/bin/sh


diagnostics_path="/var/root/diagnostics"


mkdir -p ${diagnostics_path}
mkdir -p ${diagnostics_path}/sensorkitd
cd ${diagnostics_path}

echo "cftime, physical_footprint, dirty_size, bytes_allocated, fragmentation, num_os_transactions,  pid_of_sensorkitd, uptime_sensorkitd, wall_clock_time" >> ${diagnostics_path}/sensorkitd/footprint_and_transactions.csv
	

while :
do
	wall_clock_time=`date  "+%F_%H_%M_%S"`
	
    pid_of_sensorkitd=`pidof sensorkitd`
    pid_of_maps=`pidof Maps`
	
	# ======= Track PID changes
	uptime_sensorkitd=`ps -o etime ${pid_of_sensorkitd} | tr -d "  ELAPSED" | tr -d "\n"`
	
	#===== Track os transactions
	echo "${wall_clock_time}" >> ${diagnostics_path}/sensorkitd/os_transactions.txt
	echo "Maps-PID: ${pid_of_maps} " >> ${diagnostics_path}/sensorkitd/os_transactions.txt
	echo "PID: ${pid_of_sensorkitd} , Uptime : ${uptime_sensorkitd}" >> ${diagnostics_path}/sensorkitd/os_transactions.txt
	`heap --addresses=OS_os_transaction sensorkitd | grep OS_os_transaction  >> ${diagnostics_path}/sensorkitd/os_transactions.txt`
	
	#=== Track heap
	`heap  sensorkitd  >> ${diagnostics_path}/sensorkitd/heap_${wall_clock_time}.txt`
	`footprint sensorkitd >> ${diagnostics_path}/sensorkitd/footprint_${wall_clock_time}.txt`
	`vmmap --summary sensorkitd >> ${diagnostics_path}/sensorkitd/vmmap_summary_${wall_clock_time}.txt`
	
	cftime=`timetool now | cut -f3 -d" "`
	physical_footprint=`heap sensorkitd | grep "Physical footprint:    " | cut -f2 -d":" | tr -d "M" | awk '{$1=$1;print}'`
	num_os_transactions=`heap --addresses=OS_os_transaction sensorkitd | grep OS_os_transaction | grep "]" | wc -l | tr -d " "`
	dirty_size=`vmmap --summary sensorkitd | grep DefaultMallocZone_  | awk '{ print $4}'`
	bytes_allocated=`vmmap --summary sensorkitd | grep DefaultMallocZone_  | awk '{ print $7}'`
	fragmentation=`vmmap --summary sensorkitd | grep DefaultMallocZone_  | awk '{ print $9}'`
	
	echo "${cftime}, ${physical_footprint}, ${dirty_size}, ${bytes_allocated}, ${fragmentation}, ${num_os_transactions},  ${pid_of_sensorkitd}, ${uptime_sensorkitd}, ${wall_clock_time}" >> ${diagnostics_path}/sensorkitd/footprint_and_transactions.csv
	
	printf "Sleeping 5 seconds zzzzzzzz \n"
	echo "===============================================================" >> ${diagnostics_path}/sensorkitd/os_transactions.txt
	sleep 5
done
