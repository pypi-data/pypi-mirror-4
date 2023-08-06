#! /usr/bin/env python

"""
sqlite
~~~~~~~~~~~~~~

Generates a JSON string of all the ship names and m3 volumes from the supplied
sqlite database. The database schema must be an identical schema to that of the
official CCP community database dump.

:copyright: (c) 2013 Stuart Baker
:license: GNU GPL Version 3, see LICENSE

"""

import sqlite3
import json
import argparse


def get_child_group_ids(cur, parent_group_id):
    """Recursive function that returns a list of tuples containing all the
    unique child group ids of the supplied parent group id"""
    cur.execute('''select marketGroupID from invMarketGroups where
                parentGroupID=?''', (parent_group_id,))
    children = cur.fetchall()

    for child in children:
        children = children + get_child_group_ids(cur, child[0])

    # Use set to make sure there are no duplicate group ids
    return list(set(children))


def get_ship_volumes(cur, group_ids):
    """Returns a tuple of the ship names and volumes in the supplied group
    ids. The group ids should be supplied as a list of tuples"""
    # Uses list comprehension to insert the appropiate about of placeholders
    # in the sql statement
    query = '''select typeName, volume from invTypes
            where published=1 and marketGroupID in ({})'''.format(
        ','.join('?' for i in group_ids))

    # Each of the tuples in the list should only contain one value so just
    # grab each of the first values and compile it into a list
    cur.execute(query, [group_id[0] for group_id in group_ids])
    return cur.fetchall()


def create_ship_dict(ship_volumes):
    """Creates and returns a dictionay of ship names and volumes with the
    supplied tuple"""
    ship_dict = {}
    for ship, volume in ship_volumes:
        ship = ship.replace(' ', '_')
        ship = ship.replace('-', '_')
        ship = ship.replace("'", '')
        ship = ship.lower()
        ship_dict[ship] = volume

    return ship_dict


def create_json(ship_dict):
    """Return a sorted json string of the supplied ship volume dictionary"""
    ship_json = json.dumps(ship_dict,
                           indent=4,
                           sort_keys=True,
                           separators=(',', ':'))
    return ship_json


def main():
    # This is the group id of the ship market group which is the parent to all
    # other market groups that contain ships
    parent_group_id = 4

    parser = argparse.ArgumentParser(description='Generate esmbc ship data.')
    parser.add_argument('database',
                        help='sqlite3 database file of ccp data dump')
    args = parser.parse_args()

    con = sqlite3.connect(args.database)
    cur = con.cursor()

    group_ids = get_child_group_ids(cur, parent_group_id)
    ship_volumes = get_ship_volumes(cur, group_ids)
    ship_dict = create_ship_dict(ship_volumes)
    print('{}'.format(create_json(ship_dict)))

    cur.close()
    con.close()


if __name__ == "__main__":
    main()
