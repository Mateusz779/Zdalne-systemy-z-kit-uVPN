#!/bin/bash

usage() { echo "Usage: [-i <ini config>] [-c <conf file>] [-k <pub server key>] [-l <priv key lenght>] [-n <name>] [-s <dir with scripts>]" 1>&2; exit 1; }

while getopts "i:c:k:l:n:s:" option
do 
    case "${option}"
        in
        i)ini=${OPTARG};;
        c)conf=${OPTARG};;
        k)key=${OPTARG};;
	l)keylen=${OPTARG};;
	n)name=${OPTARG};;
	s)scripts=${OPTARG};;
	*)usage;;
    esac
done
shift $((OPTIND-1))

CONFIGS=$(pwd)
echo "${CONFIGS}"

sudo apt update
sudo apt install cmake make g++ gcc libssl-dev libgmp-dev

cd /tmp
wget -O uVPN.tar.xz https://opensource.krypto-it.pl/uVPN/uVPN-3.0.3.tar.xz
mkdir uVPN
tar -xvf uVPN.tar.xz -C uVPN
rm uVPN.tar.xz
mv uVPN/*/* uVPN/

wget -O kit-crypto.tar.xz https://opensource.krypto-it.pl/kit-crypto-c/kit-crypto-c-0.0.2.tar.xz
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
echo $keylen
./uVPN_rsagen $keylen > /tmp/output/uVPN.priv
head -2 /tmp/output/uVPN.priv > /tmp/output/$name.pub

mv uVPN3 /tmp/output
cd $CONFIGS
cp $conf /tmp/output
cp $ini /tmp/output
cp $key /tmp/output
if [ "$scripts" ]; then
  echo "Podano parametr."
 cp -r $scripts /tmp/output/
fi
sed -i '/^private_key/c\private_key uVPN.priv' /tmp/output/$conf
sed -i '/^name/c\name '"$name" /tmp/output/$conf
sed -i '/^servers_config/c\servers_config '"$ini" /tmp/output/$conf
sed -i '1s/.*/['"$name"']/' /tmp/output/$ini

cd /tmp/output
mkdir vpn
mv * vpn
mkdir $CONFIGS/squash/$name
mksquashfs . $CONFIGS/squash/$name.squashfs
cp /tmp/output/vpn/$name.pub $CONFIGS/squash/$name

rm -rf /tmp/kit-crypto
rm -rf /tmp/uVPN*
rm -rf /tmp/output
