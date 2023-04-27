
# Projekt systemów zdalnych

Projekt uruchamiania zdalnych systemów.


## Instalacja wymaganych składników

Aby zainstalować wymagane składniki wydaj komendę:

```bash
  sudo apt install python3-venv python3-pip
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

Konfiguracja znajduje się w pliku config.py



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