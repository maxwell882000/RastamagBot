from application.admin import bp
from flask_login import login_required
from flask import render_template, redirect, url_for, flash, request
from application.core import dishservice
from application.core.models import DishCategory, Dish
from application.admin.forms import CategoryForm, DishForm


@bp.route('/catalog', methods=['GET'])
@login_required
def catalog():
    categories = dishservice.get_parent_categories(sort_by_number=True)
    return render_template('admin/catalog.html', title='Каталог', area='catalog', categories=categories)


@login_required
@bp.route('/catalog/<int:category_id>', methods=['GET', 'POST'])
def show_category(category_id: int):
    category = dishservice.get_category_by_id(category_id)
    categories = category.get_children().order_by(DishCategory.number.asc()).all()

    return render_template('admin/category.html', title='{}'.format(category.name),
                           area='catalog', category=category, categories=categories)


@bp.route('/catalog/<int:category_id>/dishes', methods=['GET', 'POST'])
@login_required
def category_dishes(category_id: int):
    category = dishservice.get_category_by_id(category_id)
    dishes = category.dishes.order_by(Dish.number.asc()).all()

    return render_template('admin/category_dishes.html', title='{}'.format(category.name),
                           area='catalog', category=category, dishes=dishes)


@bp.route('/catalog/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id: int):
    form = CategoryForm()
    all_categories = dishservice.get_all_categories()
    form.parent.choices = [(c.id, '{}'.format(c.get_nested_names())) for c in all_categories]
    form.parent.choices.insert(0, (0, 'Нет'))
    if form.validate_on_submit():
        name_ru = form.name_ru.data
        name_uz = form.name_uz.data
        image = form.image.data
        parent_id = form.parent.data
        dishservice.update_category(category_id, name_ru, name_uz, parent_id, image)
        flash('Категория {} изменена'.format(name_ru), category='success')
        if parent_id != 0:
            return redirect(url_for('admin.show_category', category_id=parent_id))
        else:
            return redirect(url_for('admin.catalog'))
    category = dishservice.get_category_by_id(category_id)
    form.fill_from_object(category)
    return render_template('admin/edit_category.html',
                           title='{}'.format(category.name),
                           area='catalog', form=form, category=category)


@bp.route('/catalog/create', methods=['GET', 'POST'], defaults={'category_id': 0})
@bp.route("/catalog/create/<int:category_id>", methods=['GET', 'POST'])
def create_category(category_id):
    form = CategoryForm()
    all_categories = dishservice.get_all_categories()
    form.parent.choices = [(c.id, '{}'.format(c.get_nested_names())) for c in all_categories]
    form.parent.choices.insert(0, (0, 'Нет'))
    
    if form.validate_on_submit():
        name_ru = form.name_ru.data
        name_uz = form.name_uz.data
        image = form.image.data
        parent_id = form.parent.data
        redirect_category_id = dishservice.create_category(name_ru, name_uz, parent_id, image).id
        flash('Категория {} добавлена'.format(name_ru), category='success')
        return redirect(url_for('admin.show_category', category_id=redirect_category_id))
    form.parent.data = category_id
    form.parent.choices.sort()
    return render_template('admin/new_category.html', title='Добавить категорию', area='catalog', form=form)


@login_required
@bp.route('/catalog/<int:category_id>/remove', methods=['GET'])
def remove_category(category_id: int):
    cat = dishservice.get_category_by_id(category_id)
    if cat.parent:
        redirect_to_url = url_for('admin.show_category', category_id=cat.parent.id)
    else:
        redirect_to_url = url_for('admin.catalog')
    dishservice.remove_category(category_id)
    flash('Категория удалена', category='success')
    return redirect(redirect_to_url)


@login_required
@bp.route('/catalog/dish/create', methods=['GET', 'POST'], defaults={'category_id': -1})
@bp.route("/catalog/dish/create/<int:category_id>", methods=['GET', 'POST'])
def create_dish(category_id):
    form = DishForm()
    all_categories = dishservice.get_all_categories()
    form.category.choices = [(c.id, '{}'.format(c.get_nested_names())) for c in all_categories]
    if form.validate_on_submit():
        name = form.name_ru.data
        name_uz = form.name_uz.data
        description = form.description_ru.data
        description_uz = form.description_uz.data
        show_usd = form.show_usd.data
        quantity = form.quantity.data
        image = form.image.data
        price = form.price.data
        category = form.category.data
        new_dish = dishservice.create_dish(name=name, name_uz=name_uz, description=description,
                                           description_uz=description_uz, image=image,
                                           price=price, category_id=category, quantity=quantity, show_usd=show_usd)
        flash('Блюдо {} успешно добавлено в категорию {}'.format(
            name, new_dish.category.name
        ), category='success')
        return redirect(url_for('admin.category_dishes', category_id=category))
    form.category.data = category_id
    form.category.choices.sort()
    return render_template('admin/new_dish.html', title="Добавить блюдо", area='catalog', form=form)


@login_required
@bp.route('/catalog/dish/<int:dish_id>', methods=['GET', 'POST'])
def dish(dish_id: int):
    form = DishForm()
    all_categories = dishservice.get_all_categories()
    form.category.choices = [(c.id, '{}'.format(c.get_nested_names())) for c in all_categories]
    form.category.choices.sort()
    if form.validate_on_submit():
        name = form.name_ru.data
        name_uz = form.name_uz.data
        description = form.description_ru.data
        description_uz = form.description_uz.data
        image = form.image.data
        price = form.price.data
        quantity = form.quantity.data
        category_id = form.category.data
        delete_image = form.delete_image.data
        show_usd = form.show_usd.data
        is_sale = form.is_sale.data
        sale_price = form.sale_price.data
        dishservice.update_dish(dish_id, name, name_uz, description, description_uz, image, price,
                                category_id, delete_image, show_usd, quantity, is_sale, sale_price)
        flash('Блюдо {} изменено'.format(name, category='success'))
        return redirect(url_for('admin.category_dishes', category_id=category_id))
    dish = dishservice.get_dish_by_id(dish_id)
    form.fill_from_object(dish)
    return render_template('admin/dish.html', title='{}'.format(dish.name),
                           area='catalog', form=form, dish=dish)


@login_required
@bp.route('/catalog/dish/<int:dish_id>/remove', methods=['GET'])
def remove_dish(dish_id: int):
    category_id = dishservice.get_dish_by_id(dish_id).category_id
    dishservice.remove_dish(dish_id)
    flash('Блюдо удалено', category='success')
    return redirect(url_for('admin.category_dishes', category_id=category_id))


@login_required
@bp.route('/catalog/dish/<int:dish_id>/number', methods=['POST'])
def set_dish_number(dish_id: int):
    number = request.get_json()['number']
    dishservice.set_dish_number(dish_id, number)
    return '', 201


@login_required
@bp.route('/catalog/<int:category_id>/number', methods=['POST'])
def set_category_number(category_id: int):
    number = request.get_json()['number']
    dishservice.set_category_number(category_id, number)
    return '', 201


@bp.route('/catalog/dish/<int:dish_id>/toggle-hide', methods=['GET'])
@login_required
def toggle_hide_dish(dish_id: int):
    result = dishservice.toggle_hidden_dish(dish_id)
    if not result:
        message = 'Блюдо теперь будет показано в меню Telegram-бота'
    else:
        message = 'Блюдо скрыто из меню Telegram-бота!'
    flash(message, category='success')
    return redirect(request.referrer)
