# bind 0.0.0.0 for all remote client
sudo sed -i 's/^bind 127.0.0.1/bind 0.0.0.0/g' /etc/redis/redis.conf
# start redis service
sudo systemctl restart redis-server

sudo set -i 's/^bind_ip = 127.0.0.1/bin_ip = 0.0.0.0/g' /etc/mongdb.conf
# start mongodb service
sudo systemctl restart mongod
