#!/bin/bash

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
if [[ "`which flask`" = "" ]]; then
  echo "unable to locate command flask"
  echo
  exit 1
fi

### flask startup
nohup flask run & 1>/dev/null 2>/dev/null

echo "Application started."
