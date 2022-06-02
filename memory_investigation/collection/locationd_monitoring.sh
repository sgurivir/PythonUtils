#!/bin/sh

mount -uw /

diagnostics_path="/var/root/diagnostics"

# Clean up old runs
rm -rf $diagnostics_path

mkdir -p ${diagnostics_path}
mkdir -p ${diagnostics_path}/locationd
cd ${diagnostics_path}

#mslutil `pidof locationd` --enable full
tailspin enable

while :
do
	boot_instance_id=`sysctl -A | grep boot | grep kern.bootsessionuuid | tr -d "kern.bootsessionuuid: " `
	wall_clock_time=`date  "+%F_%H_%M_%S"`
	
    pid_of_locationd=`pidof locationd`
    
    #===== Track os transactions
    #===== If too many transactions are held, wait and try again. This means
    #===== locationd is not clean and may have excessive temporary memory allocations
    touch ${diagnostics_path}/locationd/locationd_os_transactions.txt
	printf "\n $wall_clock_time \n"  >> ${diagnostics_path}/locationd/locationd_os_transactions.txt
	heap -addresses=OS_os_transaction locationd | grep OS_os_transaction  >> ${diagnostics_path}/locationd/locationd_os_transactions.txt
	
	num_os_transactions=`heap --addresses=OS_os_transaction locationd | grep OS_os_transaction | grep "]" | wc -l | tr -d " " | tr -d "\n"`
	num_os_transactions= expr ${num_os_transactions}
	if [ ${num_os_transactions} -gt 4 ]; then
		printf "Locationd is not clean at ${wall_clock_time} with ${num_os_transactions} transcations\n"
		sleep 60
    	continue
	fi
	
	rm -f /tmp/l.tailspin
	tailspin save /tmp/l.tailspin -p ${pid_of_locationd}
	
	# ===== Track spin dumps
	spindump -i /tmp/l.tailspin -o /tmp/s.txt
	mv /tmp/s.txt "${diagnostics_path}/locationd/spindump_locationd_${wall_clock_time}.txt"
	mv /tmp/l.tailspin "${diagnostics_path}/locationd/tailspin_locationd_${wall_clock_time}.tailspin"
	
	# ======= Track PID changes
	uptime_locationd=`ps -o etime ${pid_of_locationd} | tr -d "  ELAPSED" | tr -d "\n"`
	process_stats="WallClock: $wall_clock_time,  $boot_instance_id, locationd_pid:$pid_of_locationd, uptime: $uptime_locationd\n"
	
	# ===== Track VM Stats
	touch ${diagnostics_path}/locationd//pid_stats.txt
	printf " $process_stats " >> ${diagnostics_path}/locationd/pid_stats.txt
	vmmap locationd > ${diagnostics_path}/locationd/locationd_vm_stats_$pid_of_locationd_$wall_clock_time.txt
	
	
	#===== Track locationd Footprint
	#==== --fullStackHistory option gives full allocation history, but will significantly increase size of memgraph
	leaks --outputGraph ${diagnostics_path}/locationd/memgraph_locationd_$wall_clock_time.memgraph --physFootprint locationd	
	
	#======= Track open network ports
	touch ${diagnostics_path}/locationd/network_connections.txt
	printf "\n\n\n $wall_clock_time \n=====\n"  >> ${diagnostics_path}/locationd/network_connections.txt
	lsof -i -n -P | grep locatio >> ${diagnostics_path}/locationd/network_connections.txt
	
	
	
	printf "Sleeping 3600 seconds zzzzzzzz \n ---------------------\n"
	sleep 3600
done
