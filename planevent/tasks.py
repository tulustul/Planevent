from collections import namedtuple

import planevent
from planevent import (
    models,
    mailing,
    settings,
    logger,
    sql,
)
from planevent.async import (
    async,
    cron,
    progress_counter,
)
from planevent.scripts.initializedb import (
    create_test_vendor,
    create_test_categories,
    create_test_tags,
    TestInstances,
)


@async
def send_welcome_email(account):
    mailing.send(
        template='welcome',
        to=account.email,
        subject='Sie ma',
        account=account,
        app_url=settings.APP_URL,
    )


@cron(1, 1, -1, -1, -1)
def send_recomendations_emails(num):
    accounts = models.Account().all()

    for account in accounts:
        mailing.send(
            template='recomendations',
            to=account.email,
            subject='Planevent - dzisiejsze rekomendacje',
            account=account,
        )


@async
@progress_counter
def generate_random_tasks(quantity, progress_counter):
    progress_counter.message = 'Flushing database'
    progress_counter.start(quantity)

    sql.Base.metadata.drop_all(planevent.sql_engine)
    sql.Base.metadata.create_all(planevent.sql_engine)
    categories, subcategories = create_test_categories()
    tags = create_test_tags()

    progress_counter.message = 'Generating entities'
    for i in range(quantity):
        create_test_vendor(TestInstances(tags, categories, subcategories))

        if i % 10 == 0:
            if progress_counter.is_canceled():
                return
            else:
                progress_counter.progress += 10

    progress_counter.message = '{} entities generated'.format(quantity)


@async
@progress_counter
def export(progress_counter):
    import gspread

    progress_counter.message = 'Preparing worksheet'

    Cell = namedtuple('Cell', ['column', 'header', 'field'])

    columns_definitions = [
        Cell(column='A', header='Nazwa', field='name'),
        Cell(column='B', header='Opis', field='description'),
        Cell(column='C', header='Miasto', field='city'),
        Cell(column='D', header='Ulica', field='street'),
        Cell(column='E', header='Kod pocztowy', field='postal_code'),
        Cell(column='F', header='Dane kontaktowe', field='contacts'),
        # Cell(column='G', header='Nazwa', field='name'),
        # Cell(column='H', header='Nazwa', field='name'),
        # Cell(column='I', header='Nazwa', field='name'),
        # Cell(column='J', header='Nazwa', field='name'),
        # Cell(column='K', header='Nazwa', field='name'),
    ]

    last_column = columns_definitions[-1].column
    columns_count = len(columns_definitions)

    CHUNKS = 20

    count = models.Vendor.query().count()
    progress_counter.start(count)

    worksheet_name = 'export'

    client = gspread.login('planevent.export@gmail.com', 'cocojopre')

    spreadsheet = client.open('planevent-db')

    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        pass
    else:
        spreadsheet.del_worksheet(worksheet)

    worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=count+2,
                                          cols=columns_count)

    cells = worksheet.range('A1:{}1'.format(last_column))

    for i, cells_definition in enumerate(columns_definitions):
        cells[i].value = cells_definition.header
    worksheet.update_cells(cells)

    progress_counter.message = 'Exporting rows'

    offset = 0
    while offset < count:
        vendors = models.Vendor.query() \
            .limit(CHUNKS) \
            .offset(offset) \
            .all()

        cells = worksheet.range(
            'A{}:{}{}'
            .format(offset + 2, last_column,
                    min(offset + CHUNKS + 2, count + 1))
        )

        for i, vendor in enumerate(vendors):
            vendor_dict = vendor.export_dict()
            for j, column in enumerate(columns_definitions):
                cells[i*columns_count + j].value = vendor_dict[column.field]

        worksheet.update_cells(cells)

        offset += len(vendors)

        if progress_counter.is_canceled():
            return
        else:
            progress_counter.progress = offset

    progress_counter.message = '{} rows exported'.format(count)


@async
@progress_counter
def import_(progress_counter):
    raise NotImplementedError('NotImplementedError')
