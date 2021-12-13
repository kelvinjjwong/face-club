conda env export | egrep -v "^prefix:" | egrep -v "^name:" > ../conda_env_python371.yml

