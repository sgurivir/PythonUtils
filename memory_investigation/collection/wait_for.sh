#!/bin/sh


diagnostics_path="/var/root/diagnostics"


mkdir -p ${diagnostics_path}
mkdir -p ${diagnostics_path}/locationd
cd ${diagnostics_path}

rm -f ${diagnostics_path}/locationd/footprint_and_transactions.csv


echo "cftime, physical_footprint, dirty_size, bytes_allocated, allocation_count, fragmentation, bytes_lost_to_fragmentation, non_malloc_section, num_os_transactions,  pid_of_locationd, uptime_locationd, wall_clock_time" >> ${diagnostics_path}/locationd/footprint_and_transactions.csv
	

while :
do
	wall_clock_time=`date  "+%F_%H_%M_%S"`
	
    pid_of_locationd=`pidof locationd`
    pid_of_maps=`pidof Maps`
	
	# ======= Track PID changes
	uptime_locationd=`ps -o etime ${pid_of_locationd} | tr -d "  ELAPSED" | tr -d "\n"`
	
	#===== Track os transactions
	num_os_transactions=`heap --addresses=OS_os_transaction locationd | grep OS_os_transaction | grep "]" | wc -l | tr -d " " | tr -d "\n"`
	num_os_transactions= expr ${num_os_transactions}
	if [ ${num_os_transactions} -gt 3 ]; then
		printf "Locationd is not clean at ${wall_clock_time} with ${num_os_transactions} transcations\n"
		sleep 15
    	continue
	fi
	
	#===== Track heap
	
	echo "${wall_clock_time}" >> ${diagnostics_path}/locationd/os_transactions.txt
	echo "Maps-PID: ${pid_of_maps} " >> ${diagnostics_path}/locationd/os_transactions.txt
	echo "PID: ${pid_of_locationd} , Uptime : ${uptime_locationd}" >> ${diagnostics_path}/locationd/os_transactions.txt
	`heap --addresses=OS_os_transaction locationd | grep OS_os_transaction  >> ${diagnostics_path}/locationd/os_transactions.txt`
	
	#=== Track heap
	`heap  locationd  >> ${diagnostics_path}/locationd/heap_${wall_clock_time}.txt`
	`footprint locationd >> ${diagnostics_path}/locationd/footprint_${wall_clock_time}.txt`
	`vmmap --summary locationd >> ${diagnostics_path}/locationd/vmmap_summary_${wall_clock_time}.txt`
	
	cftime=`timetool now | cut -f3 -d" "`
	physical_footprint=`heap locationd | grep "Physical footprint:    " | cut -f2 -d":" | tr -d "M" | awk '{$1=$1;print}'`
	dirty_size=`vmmap --summary locationd | grep DefaultMallocZone_  | awk '{ print $4}'`
	bytes_allocated=`vmmap --summary locationd | grep DefaultMallocZone_  | awk '{ print $7}'`
	allocation_count=`vmmap --summary locationd | grep DefaultMallocZone_  | awk '{ print $6}'`
    bytes_lost_to_fragmentation=`vmmap --summary locationd | grep DefaultMallocZone_  | awk '{ print $8}'`
    non_malloc_section=`footprint locationd | grep KB | grep -v MALLOC | awk '{print $1;}' | awk '{ sum += $1 } END { print sum }'`
	fragmentation=`vmmap --summary locationd | grep DefaultMallocZone_  | awk '{ print $9}'`
	
	echo "${cftime}, ${physical_footprint}, ${dirty_size}, ${bytes_allocated}, ${allocation_count}, ${fragmentation}, ${bytes_lost_to_fragmentation}, ${non_malloc_section}, ${num_os_transactions},  ${pid_of_locationd}, ${uptime_locationd}, ${wall_clock_time}" >> ${diagnostics_path}/locationd/footprint_and_transactions.csv
	
	printf "Sleeping 30 seconds zzzzzzzz \n"
	echo "===============================================================" >> ${diagnostics_path}/locationd/os_transactions.txt
	sleep 30 
done
