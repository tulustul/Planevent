from collections import namedtuple

import gspread

from planevent import (
    settings,
    models,
)
from planevent.async import (
    async,
    progress_counter,
)

Cell = namedtuple('Cell', ['column', 'header', 'field'])
columns_definitions = [
    Cell(column='A', header='Nazwa', field='name'),
    Cell(column='B', header='Opis', field='description'),
    Cell(column='C', header='url opisu', field='contacts'),
    Cell(column='D', header='Kategoria', field='categories'),
    Cell(column='E', header='Podkategoria', field='subcategories'),
    Cell(column='F', header='Ulica', field='street'),
    Cell(column='G', header='Miasto', field='city'),
    Cell(column='H', header='Kod pocztowy', field='postal_code'),
    Cell(column='I', header='www', field='www'),
    Cell(column='J', header='[opis www]', field='www_description'),
    Cell(column='K', header='Dane kontaktowe', field='contacts'),
    Cell(column='L', header='Youtube', field='youtube'),
    Cell(column='M', header='Czy darmowe', field='is_free'),
    Cell(column='N', header='Cena', field='price'),
    Cell(column='O', header='Link do cennika', field='price_list_url'),
    Cell(column='P', header='Ilość uczestników', field='participant_count'),
    Cell(column='Q', header='Ograniczenie wiekowe',
         field='age_restriction'),
    Cell(column='R', header='Galeria', field='gallery'),
    Cell(column='S', header='Facebook', field='facebook'),
    Cell(column='T', header='Dni-godziny', field='available_at'),
    Cell(column='U', header='Współrzędne geograficzne',
         field='coordinates'),
    Cell(column='V', header='Tagi', field='tags'),
    Cell(column='W', header='Logo', field='logo'),
    Cell(column='X', header='Data dodania', field='added_at'),
    Cell(column='Y', header='Data aktualizacji', field='updated_at'),
    Cell(column='Z', header='Promocja', field='promotion'),
    Cell(column='AA', header='Dostępność czasowa',
         field='available_at_date'),
]

CHUNKS = 10

last_column = columns_definitions[-1].column
columns_count = len(columns_definitions)


def connect_to_spreadsheet(key):
    client = gspread.login(
        settings.GOOGLE_DOCS_LOGIN,
        settings.GOOGLE_DOCS_PASSWORD,
    )

    return client.open_by_key(key)


@async
@progress_counter
def export(spreadsheet_name, worksheet_name, progress_counter):
    spreadsheet_name = spreadsheet_name or settings.GOOGLE_IMPORT_SPREADSHET
    worksheet_name = worksheet_name or settings.GOOGLE_IMPORT_WORKSHEET

    progress_counter.message = 'Preparing worksheet'

    count = models.Vendor.query().count()
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
            vendor_dict = vendor_export(vendor)
            for j, column in enumerate(columns_definitions):
                cells[i*columns_count + j].value = vendor_dict.get(column.field)

        worksheet.update_cells(cells)

        offset += len(vendors)
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
            vendor_dict = {}
            for j, column in enumerate(columns_definitions):
                vendor_dict[column.field] = cells[i*columns_count + j].value
            vendor_import(vendor_dict)

        offset += rows_count
        if progress_counter.is_canceled():
            return
        else:
            progress_counter.progress = offset

    progress_counter.message = '{} rows imported'.format(count)


def vendor_export(vendor):
    return {
        'name': vendor.name,
        'description': vendor.description,
        'category': vendor.category.name,
        'added_at': vendor.added_at,
        'updated_at': vendor.updated_at,
        'promotion': vendor.promotion,
        'price_min': vendor.price_min,
        'price_max': vendor.price_max,
        'to_complete': vendor.to_complete,
        'city': vendor.address.city,
        'street': vendor.address.street,
        'postal_code': vendor.address.postal_code,
        'contacts': '\n'.join([
            '{}: {} [{}]'.format(c.type, c.value, c.description)
            for c in vendor.contacts
        ]),
    }


def vendor_import(vendor_dict):
    vendor = models.Vendor()

    vendor.name = vendor_dict['name']
    vendor.description = vendor_dict['description']
    vendor.address = models.Address(
        city=vendor_dict['city'],
        street=vendor_dict['street'],
        postal_code=vendor_dict['postal_code'],
    )

    vendor.save()
