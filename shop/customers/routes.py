from flask import redirect, render_template, url_for, flash, request, session, current_app, make_response
from flask_login import login_required, current_user, login_user, logout_user
from shop import db, app, bcrypt, login_manager
from shop.products.routes import brands, categories
from .forms import CustomerRegisterForm, CustomerLoginFrom
from .models import Register, CustomerOrder
import secrets, os
import pdfkit

@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        register = Register(name=form.name.data, username=form.username.data, email=form.email.data, password=hash_password, country=form.country.data, city=form.city.data, contact=form.contact.data, address=form.address.data, zipcode=form.zipcode.data)
        db.session.add(register)
        flash(f'Welcome {form.name.data}!!! Thank you for registering.', 'success')
        db.session.commit()
        return redirect(url_for('customerLogin'))
    return render_template('customers/register.html', form=form, brands=brands(), categories=categories())

@app.route('/customer/login', methods=['GET', 'POST'])
def customerLogin():
    form = CustomerLoginFrom()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You are now logged in!', 'success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('Incorrect email address or password', 'danger')
        return redirect(url_for('customerLogin'))

    return render_template('customers/login.html', form=form, brands=brands(), categories=categories())

@app.route('/customer/logout')
def customerLogout():
    logout_user()
    return redirect(url_for('home'))



@app.route('/getorder')
@login_required
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        try:
            order = CustomerOrder(invoice=invoice, customer_id=customer_id, orders=session['Shoppingcart'])
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash('Your order has been placed successfully!', 'success')
            return redirect(url_for('orders', invoice=invoice))
        except Exception as e:
            print(e)
            flash('Something went wrong while placing your order', 'danger')
            return redirect(url_for('getCart'))

@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        customer_id = current_user.id
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.desc()).first()
        grandtotal = 0
        for key, product in orders.orders.items():
            subtotal = float(product['price']) * int(product['quantity'])
            total_discount = (float(product['discount'])/100) * float(subtotal)
            grandtotal = float(grandtotal) + (float(subtotal) - float(total_discount))
        tax = ("%0.2f" % (0.05 * float(grandtotal)))
        grandtotal = ("%0.2f" % (float(tax) + float(grandtotal)))
    else:
        return redirect(url_for('customerLogin'))
    return render_template('customers/order.html', grandtotal=grandtotal, invoice=invoice, customer=customer, tax=tax, orders=orders, brands=brands(), categories=categories())


@app.route('/get_pdf/<invoice>', methods=['POST'])
@login_required
def get_pdf(invoice):
    if current_user.is_authenticated:
        customer_id = current_user.id
        if request.method == "POST":
            customer = Register.query.filter_by(id=customer_id).first()
            orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.desc()).first()
            grandtotal = 0
            for key, product in orders.orders.items():
                subtotal = float(product['price']) * int(product['quantity'])
                total_discount = (float(product['discount'])/100) * float(subtotal)
                grandtotal = float(grandtotal) + (float(subtotal) - float(total_discount))
            tax     = ("%0.2f" % (0.05 * float(grandtotal)))
            grandtotal = ("%0.2f" % (float(tax) + float(grandtotal)))

            path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
            config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
            options = {
                "enable-local-file-access": None,
                'page-size': 'A4',
                'margin-top': '0.40in',
                'margin-right': '0.40in',
                'margin-bottom': '0.40in',
                'margin-left': '0.40in',
            }
            rendered = render_template('customers/pdf.html', grandtotal=grandtotal, invoice=invoice, customer=customer, tax=tax, orders=orders)
            pdf = pdfkit.from_string(rendered, False, configuration=config, options=options)
            
            response = make_response(pdf)
            response.headers['content-Type'] = 'application/pdf'
            response.headers['content-Disposition'] = 'inline: filename='+invoice+'.pdf'
            return response
    return redirect(url_for('orders', invoice=invoice))
