from flask import redirect, render_template, url_for, flash, request, session, current_app
from shop import db, app
from shop.products.models import Addproduct
from shop.products.routes import brands, categories

def MergeDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1  + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False


@app.route('/addcart', methods=['POST'])
def addcart():
    try:
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        color = request.form.get('colors')
        product = Addproduct.query.filter_by(id=product_id).first()
        if product_id and quantity and color and request.method == "POST":
            DictItems = { product_id: { 'name': product.name, 'price': float(product.price), 'discount': int(product.discount), 'color': color, 'quantity': int(quantity), 'image': product.image_1, 'colors': product.colors, 'stock': product.stock } }
            if 'Shoppingcart' in session:
                if product_id in session['Shoppingcart']:
                    for key, item in session['Shoppingcart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item['quantity'] += 1
                else:
                    session['Shoppingcart'] = MergeDicts(session['Shoppingcart'], DictItems)
                    return redirect(request.referrer)
            else:
                session['Shoppingcart'] = DictItems
                return redirect(request.referrer)
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)

@app.route('/cart', methods=['GET'])
def getCart():
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    grandtotal = 0
    for key, product in session['Shoppingcart'].items():
        subtotal = float(product['price']) * int(product['quantity'])
        total_discount = (float(product['discount'])/100) * float(subtotal)
        grandtotal = float(grandtotal) + (float(subtotal) - float(total_discount))
    tax = ("%0.2f" % (0.05 * float(grandtotal)))
    grandtotal = ("%0.2f" % (float(tax) + float(grandtotal)))
    return render_template('products/cart.html', tax=tax, grandtotal=grandtotal, brands=brands(), categories=categories())


@app.route('/updatecart/<int:code>', methods=['POST'])
def updatecart(code):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    if request.method == 'POST':
        quantity = request.form.get('quantity')
        color = request.form.get('color')
        try:
            session.modified = True
            for key, item in session['Shoppingcart'].items():
                if int(key) == code:
                    item['quantity'] = int(quantity)
                    item['color'] = color
                    flash('Item is updated!', 'success')
                    return redirect(url_for('getCart'))
        except Exception as e:
            print(e)
            return redirect(url_for('getCart'))


@app.route('/deleteitem/<int:id>')
def deleteitem(id):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    try:
        session.modified = True
        for key, item in session['Shoppingcart'].items():
            if int(key) == id:
                session['Shoppingcart'].pop(key, None)
                return redirect(url_for('getCart'))
    except Exception as e:
        print(e)
        return redirect(url_for('home'))




@app.route('/clearcart')
def clearcart():
    try:
        session.pop('Shoppingcart', None)
        return redirect(url_for('home'))
    except Exception as e:
        print(e)