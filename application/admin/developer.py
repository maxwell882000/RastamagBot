from . import bp
from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from .forms import DeliveryPriceForm, CafeLocationForm
import settings as app_settings


@bp.route('/developer', methods=['GET'])
@login_required
def developer():
    return render_template('admin/developer.html', title='Developer', area='settings')


        
