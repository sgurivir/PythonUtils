for f in $1/*.memgraph; 
do 
	echo "=======================================";
	echo "$f ";
	heap --addresses=OS_os_transaction $f
done
