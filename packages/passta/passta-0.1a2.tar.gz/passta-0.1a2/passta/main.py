import os
import json
import sys
from getpass import getpass
from argparse import ArgumentParser

from passta.gpg import encrypt, decrypt, GpgError


def get_password(entry):
    while True:
        password = getpass('Password for {}: '.format(entry))
        password_again = getpass('Password for {} again: '.format(entry))
        if password == password_again:
            return password
        else:
            print('Passwords did not match! Please try again.', file=sys.stderr)


def die(message):
    print('{}: {}'.format(sys.argv[0], message), file=sys.stderr)
    sys.exit(1)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        '-f', '--file', default='~/.passta',
        help='use another password safe file (default: ~/.passta)')
    parser.add_argument('-s', '--store', help='store entry')
    parser.add_argument('-r', '--remove', help='remove entry')
    parser.add_argument(
        '-l', '--list', action='store_true', help='list name of entries')
    parser.add_argument(
        'print', nargs='?', help='print password for entry on stdout')

    args = parser.parse_args()

    filename = os.path.expanduser(args.file)
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            encrypted = f.read()
        try:
            passwords = json.loads(decrypt(encrypted).decode('utf-8'))
        except (GpgError, ValueError) as e:
            die(e)
    else:
        passwords = {}

    if args.store:
        try:
            passwords[args.store] = get_password(args.store)
        except (KeyboardInterrupt, EOFError):
            die('Interrupted')
    elif args.remove:
        passwords.pop(args.remove, None)
    elif args.list:
        for entry in sorted(passwords.keys()):
            print(entry)
    elif args.print:
        try:
            print(passwords[args.print])
        except KeyError:
            die('No entry {}'.format(args.print))

    if args.store or args.remove:
        encrypted = encrypt(json.dumps(passwords).encode('utf-8'))
        with open(filename, 'wb') as f:
            f.write(encrypted)
