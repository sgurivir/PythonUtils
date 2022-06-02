#!/bin/sh

mount -uw /

diagnostics_path="/var/root/diagnostics"

# Clean up old runs
rm -rf $diagnostics_path

mkdir -p ${diagnostics_path}
mkdir -p ${diagnostics_path}/sensorkitd
cd ${diagnostics_path}

mslutil `pidof sensorkitd` --enable full
tailspin enable

while :
do
	boot_instance_id=`sysctl -A | grep boot | grep kern.bootsessionuuid | tr -d "kern.bootsessionuuid: " `
	wall_clock_time=`date  "+%F_%H_%M_%S"`
	
    pid_of_sensorkitd=`pidof sensorkitd`
	
	rm -f /tmp/l.tailspin
	tailspin save /tmp/l.tailspin -p ${pid_of_sensorkitd}
	
	# ===== Track spin dumps
	spindump -i /tmp/l.tailspin -o /tmp/s.txt
	mv /tmp/s.txt "${diagnostics_path}/sensorkitd/spindump_sensorkitd_${wall_clock_time}.txt"
	mv /tmp/l.tailspin "${diagnostics_path}/sensorkitd/tailspin_sensorkitd_${wall_clock_time}.tailspin"
	
	# ======= Track PID changes
	uptime_sensorkitd=`ps -o etime ${pid_of_sensorkitd} | tr -d "  ELAPSED" | tr -d "\n"`
	process_stats="WallClock: $wall_clock_time,  $boot_instance_id, sensorkitd_pid:$pid_of_sensorkitd, uptime: $uptime_sensorkitd\n"
	
	# ===== Track VM Stats
	touch ${diagnostics_path}/sensorkitd//pid_stats.txt
	printf " $process_stats " >> ${diagnostics_path}/sensorkitd/pid_stats.txt
	vmmap sensorkitd > ${diagnostics_path}/sensorkitd/sensorkitd_vm_stats_$pid_of_sensorkitd_$wall_clock_time.txt
	
	
	#===== Track sensorkitd Footprint
	#==== --fullStackHistory option gives full allocation history, but will significantly increase size of memgraph
	leaks --fullStackHistory --outputGraph ${diagnostics_path}/sensorkitd/memgraph_sensorkitd_$wall_clock_time.memgraph --physFootprint sensorkitd
	#footprint ${diagnostics_path}/sensorkitd/memgraph_sensorkitd_$wall_clock_time.memgraph > ${diagnostics_path}/sensorkitd/footprint_stats_sensorkitd_$pid_of_sensorkitd_$wall_clock_time.txt
	#footprint -j ${diagnostics_path}/sensorkitd/footprint_sensorkitd_$pid_of_sensorkitd_$wall_clock_time.json -p `pidof sensorkitd` > /dev/null

	#======Track malloc_history
	#malloc_history sensorkitd -consolidateAllBySymbol -callTree > ${diagnostics_path}/sensorkitd/malloc_history_$pid_of_sensorkitd_$wall_clock_time.txt
	
	#======= Track os_transactions
	touch ${diagnostics_path}/sensorkitd/sensorkitd_os_transactions.txt
	printf "\n $wall_clock_time \n"  >> ${diagnostics_path}/sensorkitd/sensorkitd_os_transactions.txt
	heap -addresses=OS_os_transaction sensorkitd | grep OS_os_transaction  >> ${diagnostics_path}/sensorkitd/sensorkitd_os_transactions.txt
	
	#======= Track open network ports
	touch ${diagnostics_path}/sensorkitd/network_connections.txt
	printf "\n\n\n $wall_clock_time \n=====\n"  >> ${diagnostics_path}/sensorkitd/network_connections.txt
	lsof -i -n -P | grep locatio >> ${diagnostics_path}/sensorkitd/network_connections.txt
	
	
	
	printf "Sleeping 3600 seconds zzzzzzzz \n ---------------------\n"
	sleep 3600
done
