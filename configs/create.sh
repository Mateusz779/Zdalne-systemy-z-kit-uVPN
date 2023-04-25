#!/bin/bash
echo "Parametry podane do skryptu: $@"

kitcrypto_version="0.0.3"
uvpn3_version="3.0.4"

usage() { echo "Usage: [-a <root ssh authorized_keys>] [-b add executable to output] [-c <conf file>] [-d <sshd_config>] [-i <ini config>] [-k <pub server key>] [-l <priv key lenght>] [-m <msmtp script>] [-n <name>] [-o <config for msmtp>] [-p <vpn ipaddress>] [-s <scripts folder>]" 1>&2; exit 1; }

while getopts "a:b:c:d:e:i:k:l:m:n:o:p:s:" option
do
    case "${option}"
        in
          a)akeys=${OPTARG};;
          b)build="yes";;
          c)conf=${OPTARG};;
          d)sshconf=${OPTARG};;
          i)ini=${OPTARG};;
          k)key=${OPTARG};;
          l)keylen=${OPTARG};;
          m)msmtp=${OPTARG};;
          n)name=${OPTARG};;
          o)msmtp_conf=${OPTARG};;
          p)ip=${OPTARG};;
          s)scripts=${OPTARG};;
          *)usage;;
    esac
done
shift $((OPTIND-1))

CONFIGS=$(pwd)
echo "${CONFIGS}"

squashfs
#sudo apt update
#sudo apt install cmake make g++ gcc libssl-dev libgmp-dev

cd /tmp
wget -O uVPN.tar.xz https://opensource.krypto-it.pl/uVPN/uVPN-$uvpn3_version.tar.xz
mkdir uVPN
tar -xvf uVPN.tar.xz -C uVPN
rm uVPN.tar.xz
mv uVPN/*/* uVPN/

wget -O kit-crypto.tar.xz https://opensource.krypto-it.pl/kit-crypto-c/kit-crypto-c-$kitcrypto_version.tar.xz
mkdir kit-crypto
tar -xvf kit-crypto.tar.xz -C kit-crypto
rm kit-crypto.tar.xz
mv kit-crypto/*/* kit-crypto/
cd kit-crypto
cmake .
make

mkdir ../uVPN.bin
cd ../uVPN.bin
cmake ../uVPN -DKIT_CRYPTO_INCLUDES=/tmp/kit-crypto/include -DKIT_CRYPTO_LIB=/tmp/kit-crypto/libkitcryptoc_static.a
make
mkdir /tmp/output
mkdir /tmp/output/vpn
mkdir /tmp/output/ssh
./uVPN_rsagen $keylen > /tmp/output/vpn/uVPN.priv
head -2 /tmp/output/vpn/uVPN.priv > /tmp/output/vpn/"$name.pub"

if [ -n "$build" ]; then
  mv uVPN3 /tmp/output/vpn
fi

cd $CONFIGS
cp $conf /tmp/output/vpn
cp $ini /tmp/output/vpn
cp $key /tmp/output/vpn

if [ -n "$akeys" ]; then
  cp $akeys /tmp/output/ssh
fi

if [ -n "$sshconf" ]; then
  cp $sshconf /tmp/output/ssh
fi

mkdir /tmp/output/msmtp
if [ -n "$msmtp" ]; then
  cp $msmtp /tmp/output/msmtp
fi

if [ -n "$msmtp_conf" ]; then
  cp $msmtp_conf /tmp/output/msmtp
fi

if [ -n "$scripts" ]; then
  mkdir /tmp/output/vpn/scripts
  cp -r $scripts/* /tmp/output/vpn/scripts
fi

ls /tmp/output/vpn/scripts
ls /tmp/output/vpn/

sed -i 's/ip/'"$ip"'/g' /tmp/output/vpn/scripts/starttap.sh
sed -i '/^private_key/c\private_key uVPN.priv' /tmp/output/vpn/$(basename "$conf")
sed -i '/^tap_name/c\tap_name uvpnT2' /tmp/output/vpn/$(basename "$conf")
sed -i '/^name/c\name '"$name" /tmp/output/vpn/$(basename "$conf")
sed -i '/^servers_config/c\servers_config '"$(basename "$ini")" /tmp/output/vpn/$(basename "$conf")
sed -i '1s/.*/['"$name"']/' /tmp/output/vpn/$(basename "$ini")

cd /tmp/output
mkdir configs
mv * configs
mkdir "$CONFIGS/squash"
mksquashfs . $CONFIGS/squash/"$name.squashfs"
cp /tmp/output/configs/vpn/"$name.pub" $CONFIGS/squash/"$name.pub"

echo "$name"

rm -rf /tmp/kit-crypto
rm -rf /tmp/uVPN*
rm -rf /tmp/output
