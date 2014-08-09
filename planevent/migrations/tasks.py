import gspread

import planevent
from planevent import (
    settings,
    sql,
)
from planevent.offers import models as offers_models
from planevent.accounts import models as account_models
from planevent.async import (
    async,
    progress_counter,
)
from planevent.scripts.initializedb import (
    create_test_offer,
    create_test_categories,
    create_test_tags,
    TestInstances,
)
from planevent.migrations.data_definition import columns_definitions


CHUNKS = 10

last_column = columns_definitions[-1].column
columns_count = len(columns_definitions)


def connect_to_spreadsheet(key):
    client = gspread.login(
        settings.GOOGLE_DOCS_LOGIN,
        settings.GOOGLE_DOCS_PASSWORD,
    )

    return client.open_by_key(key)


def offer_export(offer):
    return {
        'name': offer.name,
        'description': offer.description,
        'category': offer.category.name,
        'added_at': offer.added_at,
        'updated_at': offer.updated_at,
        'promotion': offer.promotion,
        'price_min': offer.price_min,
        'price_max': offer.price_max,
        'to_complete': offer.to_complete,
        'city': offer.address.city,
        'street': offer.address.street,
        'postal_code': offer.address.postal_code,
        'contacts': '\n'.join([
            '{}: {} [{}]'.format(c.type, c.value, c.description)
            for c in offer.contacts
        ]),
    }


def offer_import(offer_dict):
    offer = offers_models.Offer()

    offer.name = offer_dict['name']
    offer.description = offer_dict['description']
    offer.address = offers_models.Address(
        city=offer_dict['city'],
        street=offer_dict['street'],
        postal_code=offer_dict['postal_code'],
    )

    offer.save()


@async
@progress_counter
def export(spreadsheet_name, worksheet_name, progress_counter):
    spreadsheet_name = spreadsheet_name or settings.GOOGLE_IMPORT_SPREADSHET
    worksheet_name = worksheet_name or settings.GOOGLE_IMPORT_WORKSHEET

    progress_counter.message = 'Preparing worksheet'

    count = offers_models.Offer.query().count()
    progress_counter.max = count

    spreadsheet = connect_to_spreadsheet(spreadsheet_name)

    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        pass
    else:
        spreadsheet.del_worksheet(worksheet)

    worksheet = spreadsheet.add_worksheet(
        title=settings.GOOGLE_EXPORT_WORKSHEET,
        rows=count+2,
        cols=columns_count
    )

    cells = worksheet.range('A1:{}1'.format(last_column))

    for i, cells_definition in enumerate(columns_definitions):
        cells[i].value = cells_definition.header
    worksheet.update_cells(cells)

    progress_counter.message = 'Exporting rows'

    offset = 0
    while offset < count:
        offers = offers_models.Offer.query() \
            .limit(CHUNKS) \
            .offset(offset) \
            .all()

        cells = worksheet.range(
            'A{}:{}{}'
            .format(offset + 2, last_column,
                    min(offset + CHUNKS + 2, count + 1))
        )

        for i, offer in enumerate(offers):
            offer_dict = offer_export(offer)
            for j, column in enumerate(columns_definitions):
                cells[i*columns_count + j].value = offer_dict.get(column.field)

        worksheet.update_cells(cells)

        offset += len(offers)
        if progress_counter.is_canceled():
            return
        else:
            progress_counter.progress = offset

    progress_counter.message = '{} rows exported'.format(count)


@async
@progress_counter
def import_(spreadsheet_name, worksheet_name, progress_counter):
    spreadsheet_name = spreadsheet_name or settings.GOOGLE_IMPORT_SPREADSHET
    worksheet_name = worksheet_name or settings.GOOGLE_IMPORT_WORKSHEET

    spreadsheet = connect_to_spreadsheet(spreadsheet_name)
    worksheet = spreadsheet.worksheet(worksheet_name)

    count = worksheet.row_count
    progress_counter.max = count
    progress_counter.message = 'Importing rows'

    offset = 1
    while offset < count:
        cells = worksheet.range(
            'A{}:{}{}'
            .format(offset + 1, last_column,
                    min(offset + CHUNKS + 1, count))
        )

        rows_count = int(len(cells) / columns_count)
        for i in range(rows_count):
            offer_dict = {}
            for j, column in enumerate(columns_definitions):
                offer_dict[column.field] = cells[i*columns_count + j].value
            offer_import(offer_dict)

        offset += rows_count
        if progress_counter.is_canceled():
            return
        else:
            progress_counter.progress = offset

    progress_counter.message = '{} rows imported'.format(count)


@async
@progress_counter
def generate_random_tasks(quantity, progress_counter):
    progress_counter.message = 'Flushing database'
    progress_counter.max = quantity

    sql.Base.metadata.drop_all(planevent.sql_engine)
    sql.Base.metadata.create_all(planevent.sql_engine)

    categories, subcategories = create_test_categories()

    for admin_info in settings.ADMINS:
        admin = account_models.Account.create(
            name=admin_info.name,
            email=admin_info.email,
            role=account_models.Account.Role.ADMIN,
        )
        admin.set_password(admin_info.password)
        admin.save()

    tags = create_test_tags()

    progress_counter.message = 'Generating entities'
    for i in range(quantity):
        create_test_offer(TestInstances(tags, categories, subcategories))

        if i % 10 == 0:
            if progress_counter.is_canceled():
                return
            else:
                progress_counter.progress += 10

    progress_counter.message = '{} entities generated'.format(quantity)

