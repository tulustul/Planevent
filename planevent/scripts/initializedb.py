import os
import sys
import random
import datetime
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from pyramid.scripts.common import parse_vars

import planevent.models as models
import planevent.scripts.testdata as testdata


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def create_test_address():
    address = models.Address()
    address.street = random.choice(testdata.addresses['streets'])
    address.city = random.choice(testdata.addresses['cities'])
    address.postal_code = str(random.randrange(10,100)) + '-' + \
        str(random.randrange(100, 1000))
    address.latitude = 0
    address.longitude = 0
    return address

def create_test_logo():
    image = models.Image()
    image.path = '/static/images/test/logos/' + \
                str(random.randrange(15)) + '.png'
    return image

def create_test_gallery(vendor, quantity):
    for i in range(quantity):
        image = models.ImageGallery()
        image.path = '/static/images/test/gallery/' + \
                    str(random.randrange(40)) + '.jpg'
        vendor.gallery.append(image)

def create_test_contacts(vendor, quantity):
    for i in range(quantity):
        contact = models.Contact()
        contact_data = random.choice(testdata.contacts)
        contact.type = contact_data['type']
        contact.value = random.choice(contact_data['values'])
        contact.description = random.choice(testdata.contact_descriptions)
        vendor.contacts.append(contact)

def create_test_vendor():
    vendor = models.Vendor()
    vendor.name = random.choice(testdata.vendors['names'])
    vendor.description = random.choice(testdata.vendors['descriptions'])
    vendor.category = random.randrange(1,6)
    vendor.added_at = datetime.datetime.now()
    vendor.address = create_test_address()
    vendor.logo = create_test_logo()
    create_test_contacts(vendor, random.randrange(0, 6))
    create_test_gallery(vendor, random.randrange(0, 10))
    vendor.save()

def create_test_instances(quantity):
    for i in range(quantity):
        create_test_vendor()

def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    models.DBSession.configure(bind=engine)
    models.Base.metadata.create_all(engine)
    with transaction.manager as manager:
        create_test_instances(500)
