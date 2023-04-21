#!/bin/bash

echo "Parametry podane do skryptu: $@"
usage() { echo "Usage: [ -n <nazwa obrazu>] [ -s <obraz zródłowy>] [-u <yes - upgrade>] [-i <pakiety do instalacji>]" 1>&2; exit 1; }

while getopts "n:u:i:s:" option
do
    case "${option}"
        in
          n)name=${OPTARG};;
          u)upgrade="yes";;
          i)packages+=("$OPTARG");;
          s)squashfs=${OPTARG};;
          *)usage;;
    esac
done
shift $((OPTIND -1))

echo "Pakiety: ${packages[@]}"
echo "$squashfs"
sudo unsquashfs -d /tmp/squashfs $squashfs
sudo mount --bind /dev/pts /tmp/squashfs/dev/pts
sudo mount --bind /proc /tmp/squashfs/proc
sudo chroot /tmp/squashfs/ /bin/bash -c 'cat <<EOF> /etc/resolv.conf
nameserver 1.1.1.1
EOF'
sudo chroot /tmp/squashfs/ /bin/bash -c 'apt update'

if [ -n "$upgrade" ]; then
  sudo chroot /tmp/squashfs/ /bin/bash -c 'DEBIAN_FRONTEND=noninteractive apt upgrade -y'
fi
if [ -n "$packages" ]; then
  sudo chroot /tmp/squashfs/ /bin/bash -c "DEBIAN_FRONTEND=noninteractive apt install ${packages[@]} -y"
fi

sudo chroot /tmp/squashfs/ /bin/bash -c 'apt clean all'
sudo umount /tmp/squashfs/dev/pts
sudo umount /tmp/squashfs/proc
sudo rm -rf $name.squashfs
sudo mksquashfs /tmp/squashfs/ $name.squashfs -noappend -b 1048576 -comp xz -Xdict-size 100%
sudo rm -rf /tmp/squashfs