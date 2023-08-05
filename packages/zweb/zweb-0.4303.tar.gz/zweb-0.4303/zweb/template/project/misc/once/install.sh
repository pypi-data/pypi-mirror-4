PREFIX=$(cd "$(dirname "$0")"; pwd)
cd $PREFIX/install
sudo mkdir -p /var/log/supervisor
python nginx.py
python supervisord.py 
sudo supervisorctl reload
sudo /etc/init.d/nginx restart

