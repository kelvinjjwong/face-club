#!/bin/bash

### conda shell initialization
conda_exec=`which conda`
if [[ "$conda_exec" = "" ]]; then
  echo "unable to locate command conda"
  echo
  exit 1
fi
eval "`$conda_exec 'shell.bash' 'hook' 2> /dev/null`"


source conda_env.conf

conda --version
if [[ $? -ne 0 ]]; then
  exit 1;
fi

if [[ ! -e ~/.pip/pip.conf ]]; then
  source ./setup_pip_source.sh
fi

exists=`conda env list | grep $ENV_NAME`
if [[ "$exists" != "" ]]; then
  conda env update -n $ENV_NAME -f conda_env_python371.yml
else
  conda env create -n $ENV_NAME -f conda_env_python371.yml
fi

echo "conda env: $ENV_NAME"

conda activate $ENV_NAME