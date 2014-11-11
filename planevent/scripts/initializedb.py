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

from planevent import settings
from planevent.offers import models
from planevent.categories import models as categories_models
from planevent.core import sql
from planevent.core.models import Address
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

    address = Address()
    address.street = random.choice(testdata.addresses['streets'])
    address.city = city['name']
    address.postal_code = str(random.randrange(10, 100)) + '-' + \
        str(random.randrange(100, 1000))
    address.longitude = city['lon'] + random.randrange(-50, 50) / 100
    address.latitude = city['lat'] + random.randrange(-50, 50) / 100
    address.validated = True
    address.formatted = ', '.join([address.street, address.city])
    return address


def create_test_logo():
    image = models.Image()
    image.path = '/static/images/test/logos/' + \
        str(random.randrange(15)) + '.png'
    return image


def create_test_gallery(offer, quantity):
    for i in range(quantity):
        image = models.ImageGallery()
        image.path = '/static/images/test/gallery/' + \
            str(random.randrange(40)) + '.jpg'
        image.description = (
            'Lorem ipsum dolor sit amet, consectetur adipisicing elit, '
            'sed do eiusmod, tempor incididunt ut labore et dolore magna'
            ' aliqua. Ut enim ad minim veniam,'
        )
        max_desc_index = random.randrange(len(image.description))
        image.description = image.description[:max_desc_index]
        offer.gallery.append(image)


def create_test_contacts(offer, quantity):
    for i in range(quantity):
        contact = models.Contact()
        contact_data = random.choice(testdata.contacts)
        contact.type = contact_data['type']
        contact.value = random.choice(contact_data['values'])
        contact.description = random.choice(testdata.contact_descriptions)
        offer.contacts.append(contact)


def create_test_offer_tags(offer, tags, quantity):
    tags_sample = random.sample(tags, quantity)
    for i in range(quantity):
        offer_tag = models.OfferTag(
            offer_id=offer.id,
            tag=tags_sample[i],
        )
        offer_tag.save()


def get_random_preview_image():
    path = 'static/images/test/preview/'
    files = os.listdir(path)
    return '/' + path + random.choice(files)


def create_test_offer(test_instances):
    offer = models.Offer()
    offer.name = random.choice(testdata.offers['names'])
    offer.description = random.choice(testdata.offers['descriptions'])
    offer.category = random.choice(test_instances.categories)
    offer.added_at = datetime.datetime.now()
    offer.promotion = random.randrange(1000)
    offer.address = create_test_address()
    offer.logo = create_test_logo()
    if random.random() < 0.9:
        offer.price_min = random.randrange(1, 9) * 10**random.randrange(1, 3)
        if random.random() < 0.7:
            offer.price_max = offer.price_min * random.randrange(2, 4)
    offer.preview_image_url = get_random_preview_image()
    create_test_contacts(offer, random.randrange(6))
    create_test_gallery(offer, random.randrange(10))
    offer.save()
    create_test_offer_tags(offer, test_instances.tags, random.randrange(6))
    offer.save()


def create_test_categories():
    categories_list, subcategories_list = [], []
    for category_name, subcategories in testdata.categories.items():
        category = categories_models.Category(
            name=category_name,
            color=generate_random_color(),
            icon_path='/static/images/icons/question.png',
        )
        categories_list.append(category)
        category.save()
        for subcategory in subcategories:
            subcategory = categories_models.Subcategory(
                name=subcategory['name'],
                color=generate_random_color(),
                icon_path=subcategory['icon'],
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
        create_test_offer(TestInstances(tags, categories, subcategories))


def generate_random_color():
    color = lambda: random.randint(150, 255)
    return '%02X%02X%02X' % (color(), color(), color())


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    # from planevent.abtesting import models as ab_models
    configs = get_appsettings(config_uri, options=options)
    engine = engine_from_config(configs, 'sqlalchemy.')
    sql.DBSession.configure(bind=engine)
    sql.Base.metadata.drop_all(engine)
    sql.Base.metadata.create_all(engine)
    with transaction.manager:
        create_test_instances(settings.TEST_INSTANCES)
