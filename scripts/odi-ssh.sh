#!/bin/sh
# SSH para a ODI (dropbear antigo). A senha vem de ODI_PW via SSH_ASKPASS; nada fica gravado aqui.
# uso: ODI_PW='senha' SSH_ASKPASS=./askpass.sh SSH_ASKPASS_REQUIRE=force DISPLAY=:0 ./odi-ssh.sh 'comando'
exec ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 -o PubkeyAuthentication=no \
 -o KexAlgorithms=+diffie-hellman-group1-sha1 -o HostKeyAlgorithms=+ssh-rsa -o Ciphers=+aes128-cbc,3des-cbc \
 admin@192.168.1.1 "$1"
