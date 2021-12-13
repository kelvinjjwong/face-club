source conda_env.conf

conda --version
if [[ $? -ne 0 ]]; then
  exit 1;
fi

conda deactivate
conda activate $ENV_NAME

conda env export | egrep -v "^prefix:" | egrep -v "^name:" > conda_env_python371.yml

