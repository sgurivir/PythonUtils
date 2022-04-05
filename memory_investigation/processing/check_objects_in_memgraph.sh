 cat $1 | cut -d ' ' -f1 | xargs -L1 malloc_history -fullStacks $2 
