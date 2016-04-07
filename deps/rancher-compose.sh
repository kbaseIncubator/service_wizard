wget https://github.com/rancher/rancher-compose/releases/download/v0.7.4/rancher-compose-linux-amd64-v0.7.4.tar.gz
tar xvfz rancher-compose-*.tar.gz
mkdir -p bin
mv rancher-compose-*/rancher-compose bin
rm -rf rancher-compose-*

