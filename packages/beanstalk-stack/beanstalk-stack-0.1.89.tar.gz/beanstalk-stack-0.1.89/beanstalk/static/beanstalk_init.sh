#!/bin/sh

### BEGIN INIT INFO
# Provides:          beanstalk
# Required-Start:    $local_fs $network $httpd
# Required-Stop:     $local_fs $network $httpd
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts the beanstalk app server
# Description:       starts beanstalk app server using start-stop-daemon
### END INIT INFO

case "$1" in
    start|stop|reload|restart)
        bsjack daemon.$1
        OUT=$?
        exit ${OUT}
        ;;
    *)
        echo "Usage: {start|stop|reload|restart}"
        exit 1
    ;;
esac
