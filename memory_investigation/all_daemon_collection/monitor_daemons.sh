#!/bin/sh


diagnostics_path="/var/root/lomo_daemmon_diagnostics"

# Cleanup
rm -rf ${diagnostics_path}
mkdir -p ${diagnostics_path}

daemons=("locationd" "airportd" "bluetoothd" "bluetoothaudiod" "cloudpaird" "gpsd" "nearbyd" "pipelined" "relatived" "routined" "sensorkitd" "timed" "wifid" "wifivelocityd" "WirelessRadioManagerd")
daemons_with_more_than_one_zone=("locationd" "bluetoothd" "wifid")

# Create necessary directories and header for CSV
for daemon_name in "${daemons[@]}"
do
  	mkdir -p ${diagnostics_path}/${daemon_name}
	echo "cftime, physical_footprint, dirty_size, bytes_allocated, allocation_count, fragmentation, bytes_lost_to_fragmentation, non_malloc_section, num_os_transactions, pid, uptime, wall_clock_time" >> ${diagnostics_path}/${daemon_name}/footprint_and_transactions.csv
done


# Iterate and collect memory statistics if daemon exists
while :
do
	for daemon_name in "${daemons[@]}"
	do
		wall_clock_time=`date  "+%F_%H_%M_%S"`
    	pid_of_daemon=`pidof ${daemon_name}`
    	
    	if [ "$pid_of_daemon" = "" ]; then
  			echo "Daemon ${daemon_name} is not running"
  			continue
		fi
	
		# ======= Track PID changes
		uptime_daemon=`ps -o etime ${pid_of_daemon} | tr -d "  ELAPSED" | tr -d "\n"`

		#=== Track heap
		`heap  ${daemon_name}  >> ${diagnostics_path}/${daemon_name}/heap_${wall_clock_time}.txt`
		`footprint ${daemon_name} >> ${diagnostics_path}/${daemon_name}/footprint_${wall_clock_time}.txt`
		`vmmap --summary ${daemon_name} >> ${diagnostics_path}/${daemon_name}/vmmap_summary_${wall_clock_time}.txt`
	
		#==== Which zone should we use?
		zone_name="DefaultMallocZone_"
		for d in "${daemons_with_more_than_one_zone[@]}"
		do
			echo $d
	
    		if [ "$d" == "$daemon_name" ] ; then
        		zone_name="TOTAL"
    		fi
		done
		
		echo "Using Zone ${zone_name} for ${daemon_name}"
	
		cftime=`timetool now | cut -f3 -d" "`
		physical_footprint=`heap ${daemon_name} | grep "Physical footprint:    " | cut -f2 -d":" | tr -d "M" | awk '{$1=$1;print}'`
		num_os_transactions=`heap --addresses=OS_os_transaction ${daemon_name} | grep OS_os_transaction | grep "]" | wc -l | tr -d " "`
		dirty_size=`vmmap --summary ${daemon_name} | grep -A 8 "FRAG" | grep ${zone_name}  | awk '{ print $4}'`
		bytes_allocated=`vmmap --summary ${daemon_name} | grep -A 8 "FRAG" | grep ${zone_name}   | awk '{ print $7}'`
		allocation_count=`vmmap --summary ${daemon_name} | grep -A 8 "FRAG" | grep ${zone_name}   | awk '{ print $6}'`
    	bytes_lost_to_fragmentation=`vmmap --summary ${daemon_name} | grep -A 8 "FRAG" | grep ${zone_name}   | awk '{ print $8}'`
    	non_malloc_section=`footprint ${daemon_name} | grep KB | grep -v MALLOC | awk '{print $1}' | awk '{ sum += $1 } END { print sum }'`
		fragmentation=`vmmap --summary ${daemon_name} | grep -A 8 "FRAG" | grep ${zone_name}   | awk '{ print $9}'`
		
		echo "${cftime}, ${physical_footprint}, ${dirty_size}, ${bytes_allocated}, ${allocation_count}, ${fragmentation}, ${bytes_lost_to_fragmentation}, ${non_malloc_section}, ${num_os_transactions}, ${pid_of_daemon}, ${uptime_daemon}, ${wall_clock_time}" >> ${diagnostics_path}/${daemon_name}/footprint_and_transactions.csv
	done
	
	printf "Sleeping 60 seconds zzzzzzzz \n"
	sleep 60 
done