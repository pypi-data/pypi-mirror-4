from argparse import ArgumentParser
import sys
from spa_api import write


def main():
    parser = ArgumentParser(description='Linksys/Sipura SPA IP Phone Sync')

    parser.add_argument('ip', help='SPA Phone IP Address')

    if sys.platform == 'darwin':
        parser.add_argument('--contacts', action='append', nargs='?',
                            help='read from OSX Contacts and specify an '
                                 'optional GROUP', metavar='GROUP')
    elif sys.platform == 'win32':
        parser.add_argument('--outlook', action='append', nargs='?',
                            help='read from MS Outlook and specify an '
                                 'optional GROUP', metavar='GROUP')

    parser.add_argument('--highrise', action='append', nargs=2,
                        help='read from Highrise HQ, specify your server '
                             'name and API KEY', metavar=('NAME', 'KEY'))

    args = parser.parse_args()

    entries = []

    if getattr(args, 'contacts', None):
        from spa_sync.providers import contacts
        for group in args.contacts:
            entries += contacts.export(group)

    if getattr(args, 'outlook', None):
        from spa_sync.providers import outlook
        for group in args.outlook:
            entries += outlook.export(group)

    if args.highrise:
        from spa_sync.providers import highrise
        for name, key in args.highrise:
            entries += highrise.export(name, key)

    write(args.ip, entries)
    print 'Synced', len(entries), 'entries'

if __name__ == '__main__':
    main()
