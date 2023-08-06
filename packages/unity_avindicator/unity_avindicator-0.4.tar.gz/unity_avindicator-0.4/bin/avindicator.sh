#!/bin/bash
CWD=`pwd`
LAUNCH_APP=./unity_avindicator/avindicator.py

pidfile=$CWD/unity_webmic.pid

function pidfile_cleanup {
    if [ -e "$pidfile" ]; then
        echo $pidfile removed.
        rm $pidfile
    fi
}

trap pidfile_cleanup SIGINT SIGTERM

if [ -e "$pidfile" ]; then
    pid=`cat $pidfile`
    echo $pid found
    if kill -0  $pid; then
        echo still running
        exit 1
    else
        echo removing the pid file
        rm $pidfile
    fi
fi
echo $$ > $pidfile

$(python $LAUNCH_APP)

pidfile_cleanup
