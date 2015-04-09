#!/usr/bin/env bash
case $1 in
  "")
    echo "Usage: deploy.sh [command]
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
    fab -c fabricrc read_config $@
  ;;
esac