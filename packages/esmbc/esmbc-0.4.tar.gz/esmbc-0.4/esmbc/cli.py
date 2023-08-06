#!/usr/bin/env python
"""
cli
~~~~~

Cli program that calculates total ship volume of supplied ships and quantity
pairs.

:copyright: (c) 2013 Stuart Baker
:license: GNU GPL Version 3, see LICENSE

"""
import sys
import json
import os
import argparse


def load_volumes(filename):
    """Loads the ship volume dictionary from a JSON file and returns it.

    The funtion will return None in the event the data file can not be found.
    """
    if not os.path.exists(str(filename)):
        return None

    with open(filename, 'rt') as esmbc_data:
        return json.load(esmbc_data)


def parse_ship_pairs(pairs):
    """Parses the supplied ship count pairs and returns a ship count dict.

    Expects a list of strings with each string containing a ship and quantity
    using a colon as the seperator - ship:quanity.

    If the an empty list is passed or an error occurs trying to parse the input
    then None will be returned.
    """
    if not pairs:
        return None

    ship_counts = {}
    for pair in pairs:
        try:
            ship, count = pair.split(':', 1)
        except ValueError:
            return None
        else:
            ship_counts[str.lower(ship)] = count

    return ship_counts


def calculate_volume_totals(ship_counts, ship_volumes):
    """Builds and returns a dict of ships and subtotal of their volumes.

    Expects a dict of the ship names and a corresponding quantity.
    A dict of ship volumes should also be supplied which will be used to lookup
    and total the volumes.

    Will return the dictionary or None
    """
    if not ship_counts:
        return None

    volume_totals = {}
    for ship, count in ship_counts.items():
        if ship not in ship_volumes:
            return None
        try:
            volume_totals[ship] = int(ship_volumes[ship]) * int(count)
        except ValueError:
            return None

    return volume_totals


def format_table(volume_totals):
    """Returns a string containing the supplied ships and volume totals.

    The string returned will have a ship and subtotal volume on each line.
    On the final line will be a grand total of all the ship volumes.

    Will return the string or None
    """
    total = 0
    table = ''

    if not volume_totals:
        return None

    for ship, subtotal in volume_totals.items():
        total += subtotal
        table = '{}{}: {:,}m3\n'.format(table, pretty_ship(ship), subtotal)

    table = '{}Total: {:,}m3'.format(table, total)
    return table


def pretty_ship(ship):
    """Returns a ship name with underscores removed and title cased.

    Expects a string.
    All underscores in the string will be replaces with a single whitespace
    and each word in the string will have the first letter be in uppercase.
    """
    pretty = ship.replace('_', ' ')
    pretty = pretty.title()
    return pretty


def main():
    """Main entry point for the cli.

    Uses argparse to parse command line arguments.
    """
    esmbc_dir = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(esmbc_dir, 'ships.json')
    parser = argparse.ArgumentParser(prog='esmbc',
        description='''Tool for capital ship pilots in the MMORPG EVE Online.
                       Calculates the total volume of ships supplied.''')
    parser.add_argument('ships', nargs='+',
                        help='ships in the format ship:quantity')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 0.4.0')
    args = parser.parse_args()

    ship_volumes = load_volumes(filename)
    if not ship_volumes:
        sys.stderr.write('Unable to load ship/volume json data file.\n')
        sys.exit()

    ship_counts = parse_ship_pairs(args.ships)
    if not ship_counts:
        parser.print_help()
        sys.exit()

    volume_totals = calculate_volume_totals(ship_counts, ship_volumes)
    if not volume_totals:
        parser.print_help()
        sys.exit()

    total = format_table(volume_totals)
    if not total:
        parser.print_help()
        sys.exit()

    print('{}'.format(total))
    sys.exit()
