#!/usr/bin/env
# coding=utf-8

from flask_script import Server, Manager, Command
from dotenv import load_dotenv, find_dotenv
import os
import sys


# add import paths for internal imports
cmd_folder = os.path.dirname(os.path.abspath(__file__))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

load_dotenv(find_dotenv())

import app

manager = Manager(app.APP)


class Runserver(Server):
    def run(self):
        self.__call__(app.APP,
                      self.port,
                      self.host,
                      self.use_debugger,
                      self.use_reloader,
                      self.threaded,
                      self.process,
                      self.passthrough_errors,
                      (self.ssl_crt, self.ssl_key)
                      )


# User management
@manager.command
def adduser(username, password):
    """Adds a new user"""
    from app.auth import _adduser
    _adduser(username, password)

@manager.command
def rmuser(user_id):
    """Removes an existing user"""
    from app.auth import _rmuser
    _rmuser(user_id)


@manager.command
def setuser(user_id, key, value):
    """Sets a user's credentials and other parameters"""
    from app.auth import _setuser
    _setuser(user_id, key, value)


@manager.command
def assignrole(user_id, role):
    """Adds a role to an user"""
    from app.auth import _assignrole
    _assignrole(user_id, role)


@manager.command
def revokerole(user_id, role):
    """Revokes a role from a user"""
    from app.auth import _revokerole
    _revokerole(user_id, role)


@manager.command
def listusers():
    """Lists all the existing users"""
    from app.auth import _listusers
    users = _listusers()
    print("{:<4} {:<32} {:<2} {:<2} {:<10} {:<10} {:<32}".format(
        'Id', 'Name', 'A', 'D', 'Created', 'Edited', 'Ref id'))
    for user in users:
        _df = "%s"
        user["user_ref_id"] = str(user["user_ref_id"])
        user["created"] = user["created"].strftime(_df)
        user["edited"] = user["edited"].strftime(_df)
        print("{id:<4} {name:<32} {is_active:<2} {is_deleted:<2} {created:<10} {edited:<10} {user_ref_id:<32}".format(**user))


@manager.command
def listuserroles(user_id):
    """Lists all the roles assigned to a user"""
    from app.auth import _listuserroles
    print(", ".join(p["name"] for p in _listuserroles(user_id)))
    pass


@manager.command
def listroles():
    """Lists all the existing roles"""
    from app.auth import _listroles
    roles = _listroles()
    print("{:<4} {:<32}".format('Id', 'Name'))
    for role in roles:
        print("{id:<4} {name:<32}".format(**role))


# Database maanagement
@manager.command
def createdb():
    """Creates the inital database schema and default users"""
    from app import components
    components.create_tables(app.APP, app.MODELS)

    # Quick and dirty way to add a default admin role and user
    from app.auth import _addrole, _adduser, _assignrole, _setuser
    roles = ["ADMIN"] # ... add more if needed later
    for role in roles:
        _addrole(role)
    uid = _adduser("admin", "admin")
    _assignrole(uid, "admin")
    _setuser(uid, "is_active", "1")


@manager.command
def backupdb(filename):
    """Creates a backup from the database"""
    import json
    from app.components import MyJsonEncoder, _database_backup
    with open(filename, mode="w") as file:
        backup = _database_backup(app.MODELS)
        json.dump(backup, file, cls=MyJsonEncoder, indent=2)


@manager.command
def restoredb(filename):
    """Restores db from a backup"""
    import json
    from app.components import MyJsonDecoder, _database_restore
    with open(filename, mode="r") as file:
        backup = json.load(file)
        _database_restore(app.MODELS, backup)


@manager.command
def createmigration(migration_name):
    """Creates a migration script from the database"""
    from peewee_migrate import Router
    from app.components import DB
    router = Router(DB)
    router.create(migration_name)


@manager.command
def runmigration(migration_name):
    """Runs a migration script from the database"""
    from peewee_migrate import Router
    from app.components import DB
    router = Router(DB)
    router.run(migration_name)


@manager.command
def rollbackmigration(migration_name):
    """Rolls back a migration script from the database"""
    from peewee_migrate import Router
    from app.components import DB
    router = Router(DB)
    router.rollback(migration_name)


# Entity management
@manager.command
def flattencategories():
    """ Reorganizes and make catecory trees flatten for all users """
    from app.categories import _flatten_all_categories
    _flatten_all_categories()


# override the default 127.0.0.1 binding address
manager.add_command("runserver", Server(host="0.0.0.0", port=5000))

if __name__ == "__main__":
    manager.run()
