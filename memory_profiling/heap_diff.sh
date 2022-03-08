set +x

if [ "$#" -ne 2 ];
  then
  	printf "====================================================\n"
  	printf "Finds differences in heap objects between two memgraphs\n"
  	printf "====================================================\n"
    printf "Usage: $(basename $0) PATH_TO_NEW_MEMGRAPH PATH_TO_OLD_MEMGRAPH \n"
    printf "Example: $(basename $0) 2022_01_02.memgraph  2022_01_01.memgraph \n"
    exit 1
fi

NEWER_MEMGRAPH=$1
OLDER_MEMGRAPH=$2

heap -s --guessNonObjects --sumObjectFields  $NEWER_MEMGRAPH --diffFrom $OLDER_MEMGRAPH