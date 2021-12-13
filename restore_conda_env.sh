ENV_NAME=face37

if [[ ! -e ~/.pip/pip.conf ]]; then
  source ./setup_pip_source.sh
fi

exists=`conda env list | grep $ENV_NAME`
if [[ "$exists" != "" ]]; then
  conda env update -n $ENV_NAME -f conda_env_python371.yml
else
  conda env create -n $ENV_NAME -f conda_env_python371.yml
fi
