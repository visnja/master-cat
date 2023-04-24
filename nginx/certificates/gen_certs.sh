openssl req -x509 -out master.cat.crt -keyout master.cat.key \
-newkey rsa:2048 -nodes -sha256 \
-subj '/CN=*.master.cat' -extensions EXT -config openssl.cnf