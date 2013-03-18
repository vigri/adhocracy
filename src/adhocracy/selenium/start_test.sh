#!/bin/bash

# Helper function for pushing elements to browser-array
function browser_push(){
	browser=("${browser[@]}" "$1")
}

function usage {
	echo "Run nosetests with additional features"
	echo "   -a, use all available browsers"
	echo "   -c, use Chrome for testing (default)"
	echo "   -f, use Firefox for testing"
	echo "	 -x, use HTMLUnit for testing"
	echo "   -h, print this message"
	echo "   -u, specify url for remote adhocracy server (ex. http://192.168.0.100:5001)"
	echo "	 -j, disable Javascript (if supported by browser)"
	echo "   -*, all other commands will be passed directly to nosetests"
	exit
}
while getopts :u:hacfjx opt; do
    case "$opt" in
	    u) adhocracy=$OPTARG ;;
	    h) usage ;;
	    j) disableJS=1 ;;
	    a) browser_push "chrome"; browser_push "firefox"; browser_push "htmlunit" ;;
	    c) browser_push "chrome" ;;
	    f) browser_push "firefox" ;;
	    x) browser_push "htmlunit" ;;
	    \?) commands="$commands "-"$OPTARG" ;;
    esac
done

shift $((OPTIND - 1))

# Check if an url for remote adhocracy server has been set
if [ "$disableJS" = 1 ]; then
	export selDisableJS=1
	echo "javascript disabled"
fi

# Check if an url for remote adhocracy server has been set
if [ -n "$adhocracy" ]; then
	export selAdhocracyUrl=$adhocracy
fi

# If no browser has been specified, firefox will be used as default
if [ ${#browser[@]} == 0 ]; then
	browser_push "FIREFOX"
fi

# Start nosetests for each selected browser
for i in "${browser[@]}"; do
	export selBrowser=$i
	echo "Starting nosetests with $i browser.........."
	NOSETESTS="nosetests $commands"
	$NOSETESTS
done
