#!/usr/pkg/bin/bash

files=$(ls *zip)

for zip in $files
do
	regex1='\-[0-9\.]+\.zip$'
	regex2='[^\-]+'	
	if [[ $zip =~ $regex1 ]]
	then
		[[ $zip =~ $regex2 ]]
		echo " * $zip --> $BASH_REMATCH"
		zips="$zips $zip"
	fi
done
echo "Hit Enter to proceed with filing..."
read -s

chmod 751 *.zip
for zip in $zips
do
	[[ $zip =~ $regex2 ]]
	fo=$BASH_REMATCH
	if ! [ -d $fo ]
	then
		echo "  (creating directory $fo)"
		mkdir $fo
		chmod 751 $fo
	fi
	echo " * $zip ==> $fo"	
	mv $zip $fo
done

ls -al
