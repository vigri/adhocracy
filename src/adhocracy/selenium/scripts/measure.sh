#!/usr/bin/env bash

# This script measures the duration of single and multi-processing
# The output is written to 

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`

#http://stackoverflow.com/questions/4774054/reliable-way-for-a-bash-script-to-get-the-full-path-to-itself
ABSOLUTE_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)/`basename "${BASH_SOURCE[0]}"`
SCRIPT_FOLDER=`dirname $ABSOLUTE_PATH`
SELFOLDER=`dirname $SCRIPT_FOLDER`

# start timestamp
TS="$(date +%s)"

# for multi-processing uncomment the following line
#CMD="python start_multiprocessing.py"

# for single-processing uncomment the following line
CMD="$SELFOLDER/start_test.sh -a -b -sv"

# file to store results
LOGFILE="$SELFOLDER/tmp/measure_$TS.txt"

# create tmp-folder if needed
mkdir -p "$SELFOLDER/tmp"

# file header
date -d @${TS} "+%Y-%m-%d %T" >> $LOGFILE 
echo "Command: " $CMD >> $LOGFILE
echo " " >> $LOGFILE
echo "No  | Time in milliseconds" >> $LOGFILE

for I in {1..1}
do
   TS_START="$(date +%s%N)"

   $CMD

   TS_STOP="$(date +%s%N)"
   
   DIFF=$(expr $TS_STOP - $TS_START)

   DIFF=$(($DIFF/1000000))
   
   printf -v RES "%03d | %06d\n" $I $DIFF

   echo $RES >> $LOGFILE
   echo "Measure $I complete"
done
