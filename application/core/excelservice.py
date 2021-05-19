import xlrd
from . import dishservice
from application.core.models import DishCategory


def parse_excel_file(path_to_file: str):
    workbook = xlrd.open_workbook(path_to_file)
    worksheet = workbook.sheet_by_index(0)
    for rx in range(worksheet.nrows):
        if rx == 0:
            continue
        row = worksheet.row(rx)
        parent_category = row[0].value
        parent_category_uz = row[1].value
        product_name = row[2].value
        product_name_uz = row[3].value
        category_1 = row[4].value
        category_1_uz = row[5].value
        category_2 = row[6].value
        category_2_uz = row[7].value
        category_3 = row[8].value
        category_3_uz = row[9].value
        category_4 = row[10].value
        category_4_uz = row[11].value
        description = row[12].value
        description_uz = row[13].value
        price = row[14].value
        sale_price = row[15].value
        quantity = row[16].value
        image = row[17].value
        _create_product(product_name, product_name_uz, parent_category, parent_category_uz, category_1, category_1_uz,
                        category_2, category_2_uz, category_3, category_3_uz, category_4, category_4_uz, description,
                        description_uz, price, sale_price, quantity, image)


def _create_category(category4_name, category4_name_uz, category3_name, category3_name_uz, category2_name,
                     category2_name_uz, category1_name, category1_name_uz, parent_category_name,
                     parent_category_name_uz) -> DishCategory:
    parent_category = dishservice.get_category_by_name(parent_category_name, 'ru')
    if not parent_category:
        parent_category = dishservice.create_category(parent_category_name, parent_category_name_uz)
    category1 = _get_or_create_category(category1_name, category1_name_uz, parent_category)
    category2 = _get_or_create_category(category2_name, category2_name_uz, category1)
    category3 = _get_or_create_category(category3_name, category3_name_uz, category2)
    category4 = _get_or_create_category(category4_name, category4_name_uz, category3)
    if category4:
        return category4
    elif category3:
        return category3
    elif category2:
        return category2
    elif category1:
        return category1
    else:
        return parent_category


def _get_or_create_category(category_name, category_name_uz, parent_category):
    if not category_name:
        return None
    category = dishservice.get_category_by_name(category_name, 'ru', parent_category)
    if not category:
        category = dishservice.create_category(category_name, category_name_uz, parent_category.id)
    return category


def _create_product(product_name, product_name_uz, parent_category, parent_category_uz, category_1, category_1_uz,
                    category_2, category_2_uz, category_3, category_3_uz, category_4, category_4_uz, description,
                    description_uz, price, sale_price, quantity, image):
    if price:
        price = float(price)
    else:
        price = 0.0
    category = _create_category(category_4, category_4_uz, category_3, category_3_uz, category_2, category_2_uz, category_1, category_1_uz, parent_category, parent_category_uz)
    _get_or_create_dish(product_name, product_name_uz, description, description_uz, str(image), price, sale_price, quantity, category)


def _get_or_create_dish(product_name, product_name_uz, description, description_uz, image, price, sale_price, quantity, category):
    if not product_name:
        return None
    product = dishservice.get_dish_by_name(product_name, 'ru', category)
    if not product:
        dishservice.create_dish(product_name, product_name_uz, description, description_uz, str(image), price, quantity, category.id, False, sale_price)
    return product
