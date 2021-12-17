#!/bin/bash

source ./stop.sh

### conda shell initialization
conda_exec=`which conda`
if [[ "$conda_exec" = "" ]]; then
  echo "unable to locate command conda"
  echo
  exit 1
fi
eval "`$conda_exec 'shell.bash' 'hook' 2> /dev/null`"

### conda profile activation
source ./python_env/conda_env.conf
echo "conda env: $ENV_NAME"
conda activate $ENV_NAME

### flask arguments
export FLASK_APP=main.py
export FLASK_ENV=development
export FLASK_DEBUG=0
export FLASK_RUN_PORT=80
if [[ "`which flask`" = "" ]]; then
  echo "unable to locate command flask"
  echo
  exit 1
fi

realpath() {
    [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
}

### mandatory environ variables
FACECLUB_DATABASE_CONFIG=$(realpath "~/database.yaml")
if [[ ! -e $FACECLUB_DATABASE_CONFIG ]]; then
  echo "FACECLUB_DATABASE_CONFIG file does not exist - $FACECLUB_DATABASE_CONFIG"
  echo
  exit 1
fi

### flask startup
nohup flask run --host=0.0.0.0 1>/dev/null 2>/dev/null &

echo "Application started at http://localhost:$FLASK_RUN_PORT"
