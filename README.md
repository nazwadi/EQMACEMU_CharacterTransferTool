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

## Please Read
Be aware that a TAKP-based server is from an era that had much less inventory and bank space than EQEMU servers using a RoF2 client.  Thus, there is a non-zero chance that not all inventory and bank items will have a slot to be copied to.

My core purpose was just to copy the base character, skills, languages, inventory, and spells over.  That being said, this script will copy the following tables:
* 'account'
* 'account_ip'
* 'character_bind'
* 'character_currency'
* 'character_data'
* 'character_faction_values'
* 'character_inventory'
* 'character_languages'
* 'character_spells'
* 'character_memmed_spells'
* 'character_skills'

However, the following tables are NOT copied by this script:
* account_flags
* account_rewards
* character_alternate_abilities
* character_consent
* character_bandolier
* character_buffs
* character_corpse_items
* character_corpse_items_backup
* character_corpses
* character_corpses_backup
* character_inspect_messages
* character_keyring
* character_lookup
* character_material
* character_pet_buffs
* character_pet_info
* character_pet_inventory
* character_soulmarks
* character_timers
* character_zone_flags
* discovered_items
* friends
* guilds
* guild_ranks
* guild_members
* mail
* petitions
* player_titlesets
* quest_globals
* spell_globals
* client_version
* commands_log
* titles
* trader