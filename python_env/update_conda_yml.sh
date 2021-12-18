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

conda deactivate
conda activate $ENV_NAME

conda env export | egrep -v "^prefix:" | egrep -v "^name:" > conda_env_python371.yml
echo "done"
