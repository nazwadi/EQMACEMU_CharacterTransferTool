# EQMACEMU_CharacterTransferTool
Python-based Character Transfer Tool to Copy characters from a EQEMU DB to a EQMACEMU DB

## Quickstart
This setup assumes your eqemu database is in the same mysql server as your TAKP database. 

However, you only need thhe player tables for this to work.

First copy the .env example file to a production copy that will keep your database secrets.
```bash
$ cp .env.example .env
```
Next update the .env file with your database details. 

```ini
HOST="localhost"
USERNAME="eqmac"
PASSWD="eqmacpassword"
EQEMU_DATABASE="eqemu_players"
EQMACEMU_DATABASE="eqmac"
```

Finally, use the script.
```
$ python migrate_sql.py --help
usage: migrate_sql.py [-h] [-c CHARACTER]

PEQ to TAKP character transfer tool

options:
  -h, --help            show this help message and exit
  -c CHARACTER, --character CHARACTER
```
Copying a character is as easy as the following:
```
$ python migrate_sql.py -c Soandso
```