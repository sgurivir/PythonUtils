#!/bin/sh

diagnostics_path="/var/root/diagnostics"

mkdir -p ${diagnostics_path}
mkdir -p ${diagnostics_path}/locationd
cd ${diagnostics_path}

	boot_instance_id=`sysctl -A | grep boot | grep kern.bootsessionuuid | tr -d "kern.bootsessionuuid: " `
	wall_clock_time=`date  "+%F_%H_%M_%S"`
	
    	pid_of_locationd=`pidof locationd`
	
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
	footprint ${diagnostics_path}/locationd/memgraph_locationd_$wall_clock_time.memgraph > ${diagnostics_path}/locationd/footprint_stats_locationd_$pid_of_locationd_$wall_clock_time.txt
	footprint -j ${diagnostics_path}/locationd/footprint_locationd_$pid_of_locationd_$wall_clock_time.json -p `pidof locationd` > /dev/null

	#======= Track os_transactions
	touch ${diagnostics_path}/locationd/locationd_os_transactions.txt
	printf "\n $wall_clock_time \n"  >> ${diagnostics_path}/locationd/locationd_os_transactions.txt
	heap -addresses=OS_os_transaction locationd | grep OS_os_transaction  >> ${diagnostics_path}/locationd/locationd_os_transactions.txt
	
