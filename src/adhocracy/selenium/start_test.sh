#!/bin/bash

# Helper function for pushing elements to browser-array
function browser_push(){
	browser=("${browser[@]}" "$1")
}

function usage {
	echo ""
	echo "Run nosetests with additional features"
	echo "   -a, use all available browsers"
	echo "   -c, use Chrome for testing (default)"
	echo "   -f, use Firefox for testing"
        echo "   -x, use HTMLUnit for testing"
	echo "   -h, print this message"
	echo "   -u, specify url for remote adhocracy server (ex. http://192.168.0.100:5001)"
        echo "   -w, start adhocracy server"
        echo "   -j, disable Javascript (if supported by browser)"
        echo "   -y, make testing visible (not available for htmlunit)"
        echo "   -z, record video (not available for htmlunit)"
	echo "   -*, all other commands will be passed directly to nosetests"
        echo ""
	exit
}
while getopts :u:hacfjwxyz opt; do
    case "$opt" in
	    u) adhocracy=$OPTARG ;;
	    h) usage ;;
	    j) disableJS=1 ;;
	    a) browser_push "chrome"; browser_push "firefox"; browser_push "htmlunit" ;;
	    c) browser_push "chrome" ;;
	    f) browser_push "firefox" ;;
	    w) startAdh=1 ;;
	    x) browser_push "htmlunit" ;;
	    y) testVis=1 ;;
	    z) video=1 ;;
	    \?) commands="$commands "-"$OPTARG" ;;
    esac
done

shift $((OPTIND - 1))

echo "######################################"
# Check if an url for remote adhocracy server has been set
if [ "$disableJS" = 1 ]; then
	export selDisableJS=1
	echo " Javascript:    disabled"
else
	echo " Javascript:    enabled"
fi

# Check if we should start the adhocracy server
if [ "$startAdh" = 1 ]; then
	export selStartAdh=1
	echo " Adhocracy:     start"
else
	echo " Adhocracy:     don't start"
fi

# Check if an url for remote adhocracy server has been set
if [ -n "$adhocracy" ]; then
	export selAdhocracyUrl=$adhocracy
	echo " Remote adhocracy URL: "$adhocracy
fi

# Check if should make testing visible
if [ -n "$testVis" ]; then
	export selShowTests=$testVis
	echo " Display tests: on"
else
	echo " Display tests: off"
fi

# Check if we should record a video
if [ -n "$video" ]; then
	export selCreateVideo=$video
	echo " Record video:  on"
else
	echo " Record video:  off"
fi
echo "######################################"

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
