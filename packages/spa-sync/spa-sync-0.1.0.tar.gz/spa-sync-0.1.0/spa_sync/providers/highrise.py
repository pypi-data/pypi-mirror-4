import sys

try:
    import pyrise
except ImportError:
    sys.stderr.write('To use Highrise, please `pip install pyrise`\n')
    sys.exit(2)


def export(server, api):
    pyrise.Highrise.set_server(server)
    pyrise.Highrise.auth(api)

    entries = []

    for person in pyrise.Person.all():
        phones = person.contact_data.phone_numbers
        for phone in phones:
            name = '%s %s' % (person.first_name, person.last_name)
            if len(phones) > 1:
                name += ' (%s)' % phone.location
            entries.append((name, phone.number))

    for company in pyrise.Company.all():
        phones = company.contact_data.phone_numbers
        for phone in phones:
            name = company.name
            if len(phones) > 1:
                name += ' (%s)' % phone.location
            entries.append((name, phone.number))

    return entries
