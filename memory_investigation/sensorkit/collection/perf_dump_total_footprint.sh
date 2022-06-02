#!/bin/sh

for file in ls "$1"/*.json
do
	printf $file 
	jq . $file | grep "total footprint" | sed s/"\"total footprint\":"//g | sed s/,//g
done
