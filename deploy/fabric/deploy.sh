#!/usr/bin/env bash

while [[ $# > 1 ]]
do
key="$1"

case $key in
    -f|--extension)
    CONFIGFILE="$2"
    shift # past argument
    ;;
    --default)
    DEFAULT=YES
    ;;
    *)
            # unknown option
    ;;
esac
shift # past argument or value
done


if [[ ! $CONFIGFILE ]]; then
  CONFIGFILE='fabricrc'
fi


case $1 in
  "")
    echo "Usage: deploy.sh [-f config file] [command]
  Available commands are:
  update - update project from repository
  setup - deploy project to host
  start - start project applications
  stop - stop project applications
  restart - restart project applications
  status - get status of project applications
  "
  ;;
  *)
    fab -c $CONFIGFILE read_config $@
  ;;
esac