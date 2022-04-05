#!/bin/bash

set +x

if [ $# -ne 2 ];
  then
    printf "Finds references to a given object type in the provided memgraph"
    printf "\n\n"
    echo "Usage: $(basename $0) OBJECT_TYPE PATH_TO_MEMGRAPH"
    echo "Example: $(basename $0) HTTPHeaderDict ./locationd.memgraph"
    exit 1
fi

OBJECT_TYPE=$1
PATH_TO_MEMGRAPH=$2

heap --addresses=$OBJECT_TYPE $PATH_TO_MEMGRAPH | grep "$OBJECT_TYPE "  | cut -f1 -d":" | xargs -L1 malloc_history -fullStacks  $PATH_TO_MEMGRAPH 
