sudo rm -rf harbor

sudo rm -rf /data/database/

wget https://github.com/goharbor/harbor/releases/download/v2.5.0/harbor-offline-installer-v2.5.0.tgz

tar -xzf harbor-offline-installer-v2.5.0.tgz

# cp harbor-compose.yml ./harbor/docker-compose.yml

cd ./harbor

openssl genrsa -out ca.key 4096

openssl req -x509 -new -nodes -sha512 -days 3650 \
 -subj "//C=US/ST=Srbija/L=NoviSad/O=master-cat/OU=Dev/CN=registry" \
 -key ca.key \
 -out ca.crt

openssl genrsa -out master-cat.com.key 4096

openssl req -sha512 -new \
 -subj "//C=US/ST=Srbija/L=NoviSad/O=master-cat/OU=Dev/CN=registry" \
 -key master-cat.com.key \
 -out master-cat.com.csr

cat > v3.ext <<-EOF
     authorityKeyIdentifier=keyid,issuer
     basicConstraints=CA:FALSE
     keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
     extendedKeyUsage = serverAuth
     subjectAltName = @alt_names

     [alt_names]
     DNS.1=registry.master-cat.com
     DNS.2=registry.master-cat.local
     DNS.3=registry
EOF

openssl x509 -req -sha512 -days 3650 \
    -extfile v3.ext \
    -CA ca.crt -CAkey ca.key -CAcreateserial \
    -in master-cat.com.csr \
    -out master-cat.com.crt

sudo mkdir -p /data/cert/
sudo mkdir -p /etc/docker/certs.d/master-cat.com/

sudo cp master-cat.com.crt /data/cert/
sudo cp master-cat.com.key /data/cert/

openssl x509 -inform PEM -in master-cat.com.crt -out master-cat.com.cert


sudo cp master-cat.com.cert /etc/docker/certs.d/master-cat.com/
sudo cp master-cat.com.key /etc/docker/certs.d/master-cat.com/
sudo cp ca.crt /etc/docker/certs.d/master-cat.com/

sudo systemctl restart docker

cp ../harbor.yml .

pwd

./prepare

./install.sh

sudo docker-compose up -d