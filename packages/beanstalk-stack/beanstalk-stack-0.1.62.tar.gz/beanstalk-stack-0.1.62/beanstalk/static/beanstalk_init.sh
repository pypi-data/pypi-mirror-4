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

. /etc/rc.d/init.d/functions

PROG=beanstalk-stack
DAEMON=/usr/local/bin/uwsgi
CONFIG=/etc/beanstalk/uwsgi.ini
RUN=/var/run/beanstalk
PID=${RUN}/uwsgi.pid
ARGS="--ini ${CONFIG} --log-syslog=uwsgi --pidfile=${PID}"

function start() {
    echo -n "Starting ${PROG}:"
    if [[ -f ${PID} ]]; then
        ${MOVE_TO_COL}
        echo -e "[\033[31mFAILED\033[0m]"
        echo "${PROG} has been already started."
        return 1
    else
        ${DAEMON} ${ARGS} 1>/dev/null 2>&1
        OUT=$?
        if [ ${OUT} -eq 0 ];then
            ${MOVE_TO_COL}
            echo -e "[\033[32m  OK  \033[0m]"
        else
            ${MOVE_TO_COL}
            echo -e "[\033[31mFAILED\033[0m]"
        fi
    fi
    return 0
}

function stop() {
    echo -n "Stopping ${PROG}:"
    if [[ -f ${PID} ]]; then
        ${DAEMON} --stop ${PID}
        rm -rf ${PID}
        ${MOVE_TO_COL}
        echo -e "[\033[32m  OK  \033[0m]"
    else
        ${MOVE_TO_COL}
        echo -e "[\033[31mFAILED\033[0m]"
        echo "${PROG} has been already stopped."
        return 1
    fi
    return 0
}

case "$1" in
    start)
        start
        OUT=$?
        if [ ${OUT} != 0 ]; then
            exit ${OUT}
        fi
        ;;
    stop)
        stop
        OUT=$?
        if [ ${OUT} != 0 ]; then
            exit ${OUT}
        fi
        ;;
    reload)
        echo "Reloading ${PROG} conf"
        if [[ -f ${PID} ]]; then
            ${DAEMON} --reload ${PID}
        fi
        ;;
    restart)
        echo "Restart ${PROG}"
        stop
        start
        ;;
    *)
        echo "Usage: $0 {start|stop|reload|restart}"
        exit 1
    ;;
esac

exit 0
