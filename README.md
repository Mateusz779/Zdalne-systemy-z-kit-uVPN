
# Projekt systemów zdalnych z Krypto-IT uVPN

Projekt uruchamiania zdalnych systemów.


## Instalacja wymaganych składników

Aby zainstalować wymagane składniki wydaj komendę:

```bash
  sudo apt install python3-venv python3-pip postgresql postgresql-contrib
```

A następnie:

```bash
  python3 -m venv venv
  source venv/bin/activate
```

I zainstaluj wymagane paczki pip

```bash
  pip install -r requirements.txt
```


    
## Konfiguracja

Aby dodać bazę i użytkownika w PostgreSQL należy wykonać następujące kroki:
```bash
sudo adduser <username>
sudo passwd <username>
sudo -u postgres psql
```

```sql
CREATE USER <username> WITH PASSWORD 'PASSWORD';
CREATE DATABASE <db_name>;
GRANT ALL PRIVILEGES ON DATABASE <db_name> to <username> ;
```

Konfiguracja dostępu do serwera PostgreSQL znajduje się w pliku config.py



## Pliki konfiguracyjne

- config.py - zawiera konfiguracje dostępu do bazy danych plik domyslny czy też port dostępu do serwera ssh
- configs/msmtprc - zawiera konfiguracje msmtp 
- configs/sendmail.sh - skrypt w którym znajduje sie konfiguracja co i w jaki sposób ma zostac wysłane mailem
- configs/sshd_config - plik zawierający konfiguracje serwera ssh 
- configs/uVPN.conf,uVPN.ini - pliki konfiguracyjne do uVPNa 
## Uruchomienie

Aby uruchomić serwer deweloperski: 

```bash
  flask run --host=0.0.0.0
```


## Dodanie nowego użytkownika

Aby dodać użytkownika do bazy w pliku app.py w funkcji 
```python
login_api
```
należy odkomentować linijkę:

```python
    # db.add_user(username, password)
```

A następnie przejść na stronę logowania wpisac żądaną nazwę użytkownika i hasło a następnie wyłączyć serwer zakomentować tą linijkę i uruchomic serwer ponownie.
## Aktualizacja i instalacja kolejnych pakietów do rootfs

Aby zainstalować nowe pakiety należy uruchomic skrypt 
```bash
update_rootfs.sh
```

W celu instalacji dodatkowych pakietów można wydać polecenie:
```bash
sudo ./update_rootfs.sh -n <obraz wyjściowy> -s <obraz żródłowy> -i "<pakiety do instalacji>"
```

Natomiast w celu aktualizacji pakietów w obrazie :
```bash
sudo ./update_rootfs.sh -n <obraz wyjściowy> -s <obraz żródłowy> -u
```
## Tworzenie initramfs

Aby zacząć tworzenie obrazu initramfs należy najpierw zainstalować poniższe składniki:
```bash
sudo apt install build-essential libncurses5-dev
```

Następnie pobrac i rozpakować buildroota z tej strony: https://buildroot.org/download.html i przejść do katalogu w którym został on wypakowany. Kolejnym krokiem jest wypakowanie paczki external.tar.gz do głównego katalogu buildroota i skopiowanie pliku .config również do głównego katalogu. 
Kolejnym krokiem jest wydanie polecenia
```bash
make BR2_EXTERNAL=/path/to/external
```
I finalnie uruchomienie kompilacji

```bash
make
```

W katalogu ./output/images znajdują sie pliki:
- bzImage -  kernel linuxa
- rootfs.cpio.xz - spakowany obraz initramfs
## Przykładowe parametry startowe

Dodatkowe parametry wymagane:

- root=/dev/ram0
- server=<adres serwera dysponującego wraz z portem>
- sqfile=<nazwa obrazu rootfs>
- nfsrootfs=<ip>:/<ścieżka do folderu z plikami systemu>
- token=<nazwa tokenu>


Opcjonalnie podawane do uruchomienia systemu:

- ip=<ip>
- netmask=<maska podsieci w postaci pełnej>
- gateway=<adres gateway>


Przykład uruchomienia qemu:

```bash
sudo qemu-system-x86_64 -kernel bzImage -append "root=/dev/ram0 console=ttyS0 ip=dhcp nfsrootfs=<ip>:/<path/to/foo> sqfile=<obraz> server=<adres serwera z portem> token=<token> panic=5" -initrd rootfs.cpio.xz -nographic -net nic,model=virtio,macaddr=00:00:00:00:00:02 -net tap,ifname=tap0 -m 512 -no-reboot -smp cpus=4

```
## Przykład konfiguracji dla iPXE

```ipxe 
#!ipxe

set server_ip <ip serwera>
set root_path /tftpboot/os-images
set boot_url http://${server_ip}

set os_locate <nazwa folderu z obrazami>
set os_root ${boot_url}/${url_path}/${os_locate}
kernel ${os_root}/bzImage
initrd ${os_root}/initramfs.cpio.xz
imgargs bzImage initrd=initramfs.cpio.xz root=/dev/ram0 console=ttyS0 ip=dhcp nfsrootfs=${server_ip}:${root_path}/${os_locate} sqfile=<obraz> server=<adres serwera z portem> token=<token> panic=5
boot || goto failed


```
## Jak uzyskać obraz rootfs

Najprostrzym sposobem do uzyskania obrazu rootfs jest pobranie obrazu ubuntu serwer ser strony: https://ubuntu.com/download/server następnie otwarcie go lub wypakowanie i skopiowanie z folderu casper pliku 

```bash
ubuntu-server-minimal.squashfs
```

Następnie plik ten można poddać modyfikacjom za pomocą skryptu 

```bash
update_rootfs.sh
```
