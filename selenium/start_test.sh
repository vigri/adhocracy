#!/bin/bash

# Helper function for pushing elements to browser-array
function browser_push(){
	browser=("${browser[@]}" "$1")
}

function usage {
	echo "Run nosetests with additional features"
	echo "   -a, use all available browsers"
	echo "   -c, use Chrome for testing"
	echo "   -f, use Firefox for testing (default)"
	echo "   -h, print this message"
	echo "   -u, specify url for remote adhocracy server (ex. http://192.168.0.100)"
	echo "   -*, all other commands will be passed directly to nosetests"
	exit
}
while getopts :u:hacf opt; do
    case "$opt" in
	    u) adhocracy=$OPTARG ;;
	    h) usage ;;
	    a) browser_push "chrome"; browser_push "firefox" ;;
	    c) browser_push "chrome" ;;
	    f) browser_push "firefox" ;;
	    \?) commands="$commands "-"$OPTARG" ;;
    esac
done

shift $((OPTIND - 1))


# Check if an url for remote adhocracy server has been set
if [ -n "$adhocracy" ]; then
	export adhocracyUrl=$adhocracy
fi

# If no browser has been specified, firefox will be used as default
if [ ${#browser[@]} == 0 ]; then
	browser_push "firefox"
fi

# Start nosetests for each selected browser
for i in "${browser[@]}"; do
	export browser=$i
	echo "Starting nosetests with $i browser.........."
	NOSETESTS="nosetests $commands"
	$NOSETESTS
done
