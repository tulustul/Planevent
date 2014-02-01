import os
import sys
import random
import datetime
import transaction
from collections import namedtuple

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from pyramid.scripts.common import parse_vars

import planevent.models as models
import planevent.scripts.testdata as testdata


TestInstances = namedtuple(
    'TestInstances', [
        'tags',
        'categories',
        'subcategories',
    ]
)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def create_test_address():
    city = random.choice(testdata.addresses['cities'])

    address = models.Address()
    address.street = random.choice(testdata.addresses['streets'])
    address.city = city['name']
    address.postal_code = str(random.randrange(10, 100)) + '-' + \
        str(random.randrange(100, 1000))
    address.longitude = city['lon'] + random.randrange(-50, 50) / 100
    address.latitude = city['lat'] + random.randrange(-50, 50) / 100
    address.validated = True
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


def create_test_vendor_tags(vendor, tags, quantity):
    tags_sample = random.sample(tags, quantity)
    for i in range(quantity):
        vendor_tag = models.VendorTag(
            vendor_id=vendor.id,
            tag=tags_sample[i],
        )
        vendor_tag.save()


def create_test_vendor(test_instances):
    vendor = models.Vendor()
    vendor.name = random.choice(testdata.vendors['names'])
    vendor.description = random.choice(testdata.vendors['descriptions'])
    vendor.category = random.choice(test_instances.categories)
    vendor.added_at = datetime.datetime.now()
    vendor.promotion = random.randrange(1000)
    vendor.address = create_test_address()
    vendor.logo = create_test_logo()
    create_test_contacts(vendor, random.randrange(6))
    create_test_gallery(vendor, random.randrange(10))
    vendor.save()
    create_test_vendor_tags(vendor, test_instances.tags, random.randrange(6))
    vendor.save()


def create_test_categories():
    categories_list, subcategories_list = [], []
    for category_name, subcategories in testdata.categories.items():
        category = models.Category(
            name=category_name,
            color=generate_random_color(),
            icon_path='/static/images/icons/question.png',
        )
        categories_list.append(category)
        category.save()
        for subcategory_name in subcategories:
            subcategory = models.Subcategory(
                name=subcategory_name,
                color=generate_random_color(),
                icon_path='/static/images/icons/question.png',
                category_id=category.id,
            )
            subcategory.save()
            subcategories_list.append(subcategory)
    return categories_list, subcategories_list


def create_test_tags():
    tags = []
    for tag_name in testdata.tags:
        tag = models.Tag(name=tag_name)
        tag.save()
        tags.append(tag)
    return tags


def create_test_instances(quantity):
    categories, subcategories = create_test_categories()
    tags = create_test_tags()
    for i in range(quantity):
        create_test_vendor(TestInstances(tags, categories, subcategories))


def generate_random_color():
    color = lambda: random.randint(150, 255)
    return '%02X%02X%02X' % (color(), color(), color())


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    models.DBSession.configure(bind=engine)
    models.Base.metadata.drop_all(engine)
    models.Base.metadata.create_all(engine)
    with transaction.manager:
        create_test_instances(int(settings.TEST_INSTANCES))
