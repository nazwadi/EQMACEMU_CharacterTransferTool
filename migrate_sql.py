"""
PEQ to TAKP Database Character Transfer Tool

This tool does not copy the following player tables
since they are generally specific to a given server,
corpses, or pets:

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
"""
import argparse
import os
from enum import Enum
from os.path import join, dirname
from sqlalchemy import text, create_engine
from dotenv import load_dotenv, find_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)
# pylint: disable=no-member

DEBUG=True
HOST=os.environ.get("HOST")
USERNAME=os.environ.get("USERNAME")
PASSWD=os.environ.get("PASSWD")
EQEMU_DATABASE=os.environ.get("EQEMU_DATABASE")
EQMACEMU_DATABASE=os.environ.get("EQMACEMU_DATABASE")

class CharacterDoesNotExist(Exception):
    """Custom Exception for when a character can't be found in the target EQEMU_DATABASE"""

class TAKPInventorySlot(Enum):
    """Enum for Inventory Slots in TAKP database"""
    CHARM = 0
    LEFT_EAR = 1
    HEAD = 2
    FACE = 3
    RIGHT_EAR = 4
    NECK = 5
    SHOULDERS = 6
    ARMS = 7
    BACK = 8
    LEFT_WRIST = 9
    RIGHT_WRIST = 10
    RANGED = 11
    HANDS = 12
    PRIMARY = 13
    SECONDARY = 14
    LEFT_FINGER = 15
    RIGHT_FINGER = 16
    CHEST = 17
    LEGS = 18
    FEET = 19
    WAIST = 20
    AMMO = 21

class PEQInventorySlot(Enum):
    """Enum for Inventory Slots in PEQ database"""
    CHARM = 0
    LEFT_EAR = 1
    HEAD = 2
    FACE = 3
    RIGHT_EAR = 4
    NECK = 5
    SHOULDERS = 6
    ARMS = 7
    BACK = 8
    LEFT_WRIST = 9
    RIGHT_WRIST = 10
    RANGED = 11
    HANDS = 12
    PRIMARY = 13
    SECONDARY = 14
    LEFT_FINGER = 15
    RIGHT_FINGER = 16
    CHEST = 17
    LEGS = 18
    FEET = 19
    WAIST = 20
    POWER_SOURCE = 21
    AMMO = 22


class CharacterTransferTool():
    """Top level class that contains all the copy functions
    
    Example use:
        ctt = CharacterTransferTool('Soandso')
        ctt.copy_account()
        ...
    """
    def __init__(self, character_name: str):
        self.eqemu_engine = create_engine(
                f"mysql+pymysql://{USERNAME}:{PASSWD}@{HOST}:3306/{EQEMU_DATABASE}")
        self.eqmacemu_engine = create_engine(
                f"mysql+pymysql://{USERNAME}:{PASSWD}@{HOST}:3306/{EQMACEMU_DATABASE}")

        with self.eqemu_engine.connect() as eqemu_conn:
            # Get character id, account id, and login server account id from character name
            sql = text("SELECT c.id, c.account_id, a.lsaccount_id  \
                        FROM character_data AS c INNER JOIN account AS a \
                        ON a.id = c.account_id WHERE c.name = :character_name")
            sql = sql.bindparams(character_name=character_name)
            results = eqemu_conn.execute(sql)
            if results.rowcount == 0:
                raise CharacterDoesNotExist("The character you are trying to \
                                            copy does not exist in the target \
                                            EQEMU database. Check your \
                                            EQEMU_DATABASE configuration variable.")

            for record in results:
                self.new_char_id, self.new_account_id, self.ls_account_id = record
                print(self.new_char_id, self.new_account_id, self.ls_account_id)

    def clear_character_from_eqmacdb(self):
        """
        Clears character records from EQMAC database target:

        This is useful if you want to run this script indemptotently without 
        creating duplicate copies.
        """
        with self.eqmacemu_engine.connect() as eqmac_conn:

            for table, column in zip(['account', 'account_ip'], ['id', 'accid']):
                sql = text(f"DELETE FROM {table} WHERE {column} = :new_account_id")
                sql = sql.bindparams(new_account_id=self.new_account_id)
                eqmac_conn.execute(sql)

            for table in ['character_bind', 'character_currency', 'character_data',
                          'character_faction_values', 'character_inventory', 'character_languages',
                          'character_spells', 'character_memmed_spells', 'character_skills']:

                sql = text(f"DELETE FROM {table} WHERE id = :new_char_id")
                sql = sql.bindparams(new_char_id=self.new_char_id)
                eqmac_conn.execute(sql)

            eqmac_conn.commit()

    def copy_account(self):
        """
        Copies the compatible account table columns between a PEQ database and a TAKP database
        """
        sql = text("SELECT * FROM account WHERE id = :new_account_id")
        sql = sql.bindparams(new_account_id=self.new_account_id)
        with self.eqemu_engine.connect() as eqemu_conn:
            results = eqemu_conn.execute(sql)

        insert_sql = text("INSERT INTO account (`id`, `name`, `charname`, `sharedplat`, `password`,\
                          `status`, `lsaccount_id`, `gmspeed`, `revoked`, `karma`, `minilogin_ip`,\
                          `hideme`, `rulesflag`, `suspendeduntil`, `time_creation`, `expansion`,\
                           `ban_reason`, `suspend_reason`, `flymode`, `ignore_tells`) \
                          VALUES (:id, :name, :charname, :sharedplat, :password, :status, \
                          :lsaccount_id, :gmspeed, :revoked, :karma, :minilogin_ip, :hideme,\
                          :rulesflag, :suspendeduntil, :time_creation, :expansion, :ban_reason,\
                          :suspend_reason,:flymode, :ignore_tells)")

        with self.eqmacemu_engine.connect() as eqmac_conn:
            for record in results:
                char_id, name, charname, sharedplat, password, status, _, lsaccount_id, gmspeed, _, flymode, ignore_tells, revoked, karma, minilogin_ip, hideme, rulesflag, suspendeduntil, time_creation, ban_reason, suspend_reason, _, _, _ = record
                if suspendeduntil is None:
                    suspendeduntil = "0000-00-00 00:00:00"  # Prevents IntegrityError 1048, Column 'suspendeduntil' cannot be null'
                insert_sql = insert_sql.bindparams(id=char_id,
                                                   name=name,
                                                   charname=charname,
                                                   sharedplat=sharedplat,
                                                   password=password,
                                                   status=status,
                                                   lsaccount_id=lsaccount_id,
                                                   gmspeed=gmspeed,
                                                   revoked=revoked,
                                                   karma=karma,
                                                   minilogin_ip=minilogin_ip,
                                                   hideme=hideme,
                                                   rulesflag=rulesflag,
                                                   suspendeduntil=suspendeduntil,
                                                   time_creation=time_creation,
                                                   expansion=12,
                                                   ban_reason=ban_reason,
                                                   suspend_reason=suspend_reason,
                                                   flymode=flymode,
                                                   ignore_tells=ignore_tells)
                eqmac_conn.execute(insert_sql)

            eqmac_conn.commit()

    def copy_account_ip(self):
        """
        Copies the compatible account_ip table columns between a PEQ database and a TAKP database
        """
        sql = text("SELECT * FROM account_ip WHERE accid = :new_account_id")
        sql = sql.bindparams(new_account_id=self.new_account_id)
        with self.eqemu_engine.connect() as eqemu_conn:
            results = eqemu_conn.execute(sql)

        insert_sql = text("INSERT INTO account_ip (accid, ip, count, lastused) \
                           VALUES (:accid, :ip, :count, :lastused)")

        with self.eqmacemu_engine.connect() as eqmac_conn:
            for record in results:
                accid, ip, count, lastused = record
                insert_sql = insert_sql.bindparams(accid=accid,
                                                   ip=ip,
                                                   count=count,
                                                   lastused=lastused)
                eqmac_conn.execute(insert_sql)

            eqmac_conn.commit()

    def copy_character_bind(self):
        """
        Copies the compatible character_bind table columns between a PEQ
        database and a TAKP database
        """
        sql = text("SELECT * from character_bind WHERE id = :new_char_id")
        sql = sql.bindparams(new_char_id=self.new_char_id)
        with self.eqemu_engine.connect() as eqemu_conn:
            results = eqemu_conn.execute(sql)

        insert_sql = text("INSERT INTO character_bind (id, is_home, zone_id, x, y, z, heading) \
                           VALUES (:id, :is_home, :zone_id, :x, :y, :z, :heading)")

        with self.eqmacemu_engine.connect() as eqmac_conn:
            for record in results:
                char_id, slot, zone_id, _, x, y, z, heading = record
                if slot in (0, 1):
                    insert_sql = insert_sql.bindparams(id=char_id,
                                                       is_home=slot,
                                                       zone_id=zone_id,
                                                       x=x,
                                                       y=y,
                                                       z=z,
                                                       heading=heading)
                    eqmac_conn.execute(insert_sql)

            eqmac_conn.commit()

    def copy_character_currency(self):
        """
        Copies PEQ character_currency table to the TAKP character_currency table
        """
        sql = text("SELECT * FROM character_currency WHERE id = :new_char_id")
        sql = sql.bindparams(new_char_id=self.new_char_id)
        with self.eqemu_engine.connect() as eqemu_conn:
            results = eqemu_conn.execute(sql)

        insert_sql = text("INSERT INTO character_currency (id, platinum, gold, silver, copper,\
                           platinum_bank, gold_bank, silver_bank, copper_bank, platinum_cursor,\
                           gold_cursor, silver_cursor, copper_cursor)\
                           VALUES (:id, :platinum, :gold, :silver, :copper, :platinum_bank, \
                           :gold_bank, :silver_bank, :copper_bank, :platinum_cursor, :gold_cursor,\
                           :silver_cursor, :copper_cursor)")
        with self.eqmacemu_engine.connect() as eqmac_conn:
            for record in results:
                char_id, platinum, gold, silver, copper, platinum_bank, gold_bank, silver_bank, copper_bank, platinum_cursor, gold_cursor, silver_cursor, copper_cursor, _, _, _, _ = record
                insert_sql = insert_sql.bindparams(id=char_id,
                                                   platinum=platinum,
                                                   gold=gold,
                                                   silver=silver,
                                                   copper=copper,
                                                   platinum_bank=platinum_bank,
                                                   gold_bank=gold_bank,
                                                   silver_bank=silver_bank,
                                                   copper_bank=copper_bank,
                                                   platinum_cursor=platinum_cursor,
                                                   gold_cursor=gold_cursor,
                                                   silver_cursor=silver_cursor,
                                                   copper_cursor=copper_cursor)
                eqmac_conn.execute(insert_sql)

            eqmac_conn.commit()

    def copy_character_data(self):
        """
        Copies PEQ character_data table to the TAKP character_data table
        """
        sql = text("SELECT * FROM character_data WHERE id = :new_char_id")
        sql = sql.bindparams(new_char_id=self.new_char_id)
        with self.eqemu_engine.connect() as eqemu_conn:
            results = eqemu_conn.execute(sql)

        insert_sql = text("INSERT INTO character_data(id, account_id, forum_id, name, last_name, \
                           title, suffix, zone_id, y, x, z, heading, gender, race, class, level, \
                           deity, birthday, last_login, time_played, level2, anon, gm, face, \
                           hair_color, hair_style, beard, beard_color, eye_color_1, eye_color_2,\
                           exp, aa_points_spent, aa_exp, aa_points, points, cur_hp, mana, \
                           endurance, intoxication, str, sta, cha, dex, `int`, agi, wis, \
                           zone_change_count, hunger_level, thirst_level, pvp_status, \
                           air_remaining, autosplit_enabled, mailkey, firstlogon, e_aa_effects, \
                           e_percent_to_aa, e_expended_aa_spent, showhelm)\
                           VALUES (:charid, :account_id, :forum_id, :name, :last_name, :title, \
                           :suffix, :zone_id, :y, :x, :z, :heading, :gender, :race, :charclass, \
                           :level, :deity, :birthday, :last_login, :time_played, :level2, :anon, \
                           :gm, :face, :hair_color, :hair_style, :beard, :beard_color, \
                           :eye_color_1, :eye_color_2, :exp, :aa_points_spent, :aa_exp, :aa_points,\
                           :points, :cur_hp, :mana, :endurance, :intoxication, :charstr, :sta, \
                           :cha, :dex, :charint, :agi, :wis, :zone_change_count, :hunger_level,\
                           :thirst_level, :pvp_status, :air_remaining, :autosplit_enabled, :mailkey,\
                           :firstlogon, :e_aa_effects, :e_percent_to_aa, :e_expended_aa_spent, \
                           :showhelm)")

        with self.eqmacemu_engine.connect() as eqmac_conn:
            for record in results:
                charid, account_id, name, last_name, title, suffix, zone_id, _, y, x, z, heading, gender, race, charclass, level, deity, birthday, last_login, time_played, level2, anon, gm, face, hair_color, hair_style, beard, beard_color, eye_color_1, eye_color_2, _, _, _, _, _, _, _, exp, aa_points_spent, aa_exp, aa_points, _, _, _, _, points, cur_hp, mana, endurance, intoxication, charstr, sta, cha, dex, charint, agi, wis, zone_change_count, _, hunger_level, thirst_level, _, _, _, _, _, _, _, _, _, _, _, pvp_status, _, _, _, _, _, _, _, _, _, showhelm, _, _, _, _, _, air_remaining, autosplit_enabled, _, _, mailkey, _, firstlogon, e_aa_effects, e_percent_to_aa, e_expended_aa_spent, _, _, _, _ = record
                insert_sql = insert_sql.bindparams(charid=charid,
                                                   account_id=account_id,
                                                   forum_id=0,
                                                   name=name,
                                                   last_name=last_name,
                                                   title=title,
                                                   suffix=suffix,
                                                   zone_id=zone_id,
                                                   y=y,
                                                   x=x,
                                                   z=z,
                                                   heading=heading,
                                                   gender=gender,
                                                   race=race,
                                                   charclass=charclass,
                                                   level=level,
                                                   deity=deity,
                                                   birthday=birthday,
                                                   last_login=last_login,
                                                   time_played=time_played,
                                                   level2=level2,
                                                   anon=anon,
                                                   gm=gm,
                                                   face=face,
                                                   hair_color=hair_color,
                                                   hair_style=hair_style,
                                                   beard=beard,
                                                   beard_color=beard_color,
                                                   eye_color_1=eye_color_1,
                                                   eye_color_2=eye_color_2,
                                                   exp=exp,
                                                   aa_points_spent=aa_points_spent,
                                                   aa_exp=aa_exp,
                                                   aa_points=aa_points,
                                                   points=points,
                                                   cur_hp=cur_hp,
                                                   mana=mana,
                                                   endurance=endurance,
                                                   intoxication=intoxication,
                                                   charstr=charstr,
                                                   sta=sta,
                                                   cha=cha,
                                                   dex=dex,
                                                   charint=charint,
                                                   agi=agi,
                                                   wis=wis,
                                                   zone_change_count=zone_change_count,
                                                   hunger_level=hunger_level,
                                                   thirst_level=thirst_level,
                                                   pvp_status=pvp_status,
                                                   air_remaining=air_remaining,
                                                   autosplit_enabled=autosplit_enabled,
                                                   mailkey=mailkey,
                                                   firstlogon=firstlogon,
                                                   e_aa_effects=e_aa_effects,
                                                   e_percent_to_aa=e_percent_to_aa,
                                                   e_expended_aa_spent=e_expended_aa_spent,
                                                   showhelm=showhelm)
                eqmac_conn.execute(insert_sql)

            eqmac_conn.commit()

    def copy_character_faction_values(self):
        """
        Copies PEQ faction_values table to the TAKP character_faction_values table
        """
        sql = text("SELECT * FROM faction_values WHERE char_id = :new_char_id")
        sql = sql.bindparams(new_char_id=self.new_char_id)
        with self.eqemu_engine.connect() as eqemu_conn:
            results = eqemu_conn.execute(sql)

        insert_sql = text("INSERT INTO character_faction_values(id, faction_id, current_value, temp)\
                           VALUES(:id, :faction_id, :current_value, :temp)")

        with self.eqmacemu_engine.connect() as eqmac_conn:
            for record in results:
                char_id, faction_id, current_value, temp = record
                insert_sql = insert_sql.bindparams(id=char_id,
                                                   faction_id=faction_id,
                                                   current_value=current_value,
                                                   temp=temp)
                eqmac_conn.execute(insert_sql)

            eqmac_conn.commit()

    def copy_character_inventory(self):
        """
        Copies the character_inventory from PEQ db to TAKP

        This is not straightforward because item ids and inventory slots are not equivalent
        """
        sql = text("SELECT * FROM inventory WHERE charid = :new_char_id")
        sql = sql.bindparams(new_char_id=self.new_char_id)
        with self.eqemu_engine.connect() as eqemu_conn:
            results = eqemu_conn.execute(sql)

        insert_sql = text("INSERT INTO character_inventory(id, slotid, itemid, charges) \
                           VALUES (:id, :slotid, :itemid, :charges)")

        with self.eqmacemu_engine.connect() as eqmac_conn:
            for record in results:
                char_id, slotid, itemid, charges, _, _, _, _, _, _, _, _, _, _, _, _ = record
                insert_sql = insert_sql.bindparams(id=char_id,
                                                   slotid=slotid,
                                                   itemid=itemid,
                                                   charges=charges)
                eqmac_conn.execute(insert_sql)

            eqmac_conn.commit()

    def copy_character_languages(self):
        """
        Copies the PEQ character_languages table to the TAKP character_languages table
        """
        sql = text("SELECT * FROM character_languages WHERE id = :new_char_id")
        sql = sql.bindparams(new_char_id=self.new_char_id)
        with self.eqemu_engine.connect() as eqemu_conn:
            results = eqemu_conn.execute(sql)

        insert_sql = text("INSERT INTO character_languages(id, lang_id, value) \
                           VALUES (:id, :lang_id, :value)")

        with self.eqmacemu_engine.connect() as eqmac_conn:
            for record in results:
                char_id, lang_id, value = record
                insert_sql = insert_sql.bindparams(id=char_id, lang_id=lang_id, value=value)
                eqmac_conn.execute(insert_sql)

            eqmac_conn.commit()

    def copy_character_spells(self):
        """
        Copies the character_spells table from PEQ to TAKP databases
        """
        sql = text("SELECT * FROM character_spells WHERE id = :new_char_id")
        sql = sql.bindparams(new_char_id=self.new_char_id)
        with self.eqemu_engine.connect() as eqemu_conn:
            results = eqemu_conn.execute(sql)

        insert_sql = text("INSERT INTO character_spells(id, slot_id, spell_id)\
                           VALUES (:id, :slot_id, :spell_id)")

        with self.eqmacemu_engine.connect() as eqmac_conn:
            for record in results:
                char_id, slot_id, spell_id = record
                insert_sql = insert_sql.bindparams(id=char_id, slot_id=slot_id, spell_id=spell_id)
                eqmac_conn.execute(insert_sql)

            eqmac_conn.commit()

    def copy_character_memmed_spells(self):
        """
        Copies the character_memmed_spells table from PEQ to TAKP databases
        """
        sql = text("SELECT * FROM character_memmed_spells WHERE id = :new_char_id")
        sql = sql.bindparams(new_char_id=self.new_char_id)
        with self.eqemu_engine.connect() as eqemu_conn:
            results = eqemu_conn.execute(sql)

        insert_sql = text("INSERT INTO character_memmed_spells(id, slot_id, spell_id) \
                           VALUES (:id, :slot_id, :spell_id)")

        with self.eqmacemu_engine.connect() as eqmac_conn:
            for record in results:
                char_id, slot_id, spell_id = record
                insert_sql = insert_sql.bindparams(id=char_id, slot_id=slot_id, spell_id=spell_id)
                eqmac_conn.execute(insert_sql)

            eqmac_conn.commit()

    def copy_character_skills(self):
        """
        Copies the character_skills table from PEQ to TAKP databases
        """
        sql = text("SELECT * FROM character_skills WHERE id = :new_char_id")
        sql = sql.bindparams(new_char_id=self.new_char_id)
        with self.eqemu_engine.connect() as eqemu_conn:
            results = eqemu_conn.execute(sql)

        insert_sql = text("INSERT INTO character_skills(id, skill_id, value) \
                           VALUES (:id, :skill_id, :value)")

        with self.eqmacemu_engine.connect() as eqmac_conn:
            for record in results:
                char_id, skill_id, value = record
                insert_sql = insert_sql.bindparams(id=char_id, skill_id=skill_id, value=value)
                eqmac_conn.execute(insert_sql)

            eqmac_conn.commit()

    # maybe quest globals

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PEQ to TAKP character transfer tool')
    parser.add_argument('-c', '--character')
    args = parser.parse_args()

    ctt = CharacterTransferTool(args.character)
    ctt.clear_character_from_eqmacdb()
    ctt.copy_account()
    ctt.copy_account_ip()
    ctt.copy_character_bind()
    ctt.copy_character_currency()
    ctt.copy_character_data()
    ctt.copy_character_faction_values()
#    ctt.copy_character_inventory()
    ctt.copy_character_languages()
    ctt.copy_character_spells()
    ctt.copy_character_memmed_spells()
    ctt.copy_character_skills()
