mkdir -p ~/.pip/

if [[ -e ~/.pip/pip.conf ]]; then
  cp ~/.pip/pip.conf ~/.pip/pip.conf.backup.`date '+%Y%m%d'`
  echo "Backed-up pip.conf"
fi

cp pip.conf ~/.pip/pip.conf
echo "Copied pip.conf"
