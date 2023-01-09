from flask import redirect, render_template, url_for, flash, request, session, current_app
from shop import db, app, photos
from .models import Brand, Category, Addproduct
from .forms import Addproducts
import secrets, os

def brands():
    brands = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    return brands

def categories():
    categories = Category.query.join(Addproduct, (Category.id == Addproduct.category_id)).all()
    return categories

@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).paginate(page=page, per_page=4)
    return render_template('products/index.html', products=products, brands=brands(), categories=categories())

@app.route('/product/<int:id>')
def single_page(id):
    product = Addproduct.query.get_or_404(id)
    return render_template('products/single_page.html', product=product, brands=brands(), categories=categories())

@app.route('/brand/<int:id>')
def get_brand(id):
    page = request.args.get('page', 1, type=int)
    get_brand = Brand.query.filter_by(id=id).first_or_404()
    brand = Addproduct.query.filter_by(brand=get_brand).paginate(page=page, per_page=4)
    return render_template('products/index.html', brand=brand, brands=brands(), categories=categories(), get_brand=get_brand)

@app.route('/categories/<int:id>')
def get_category(id):
    page = request.args.get('page', 1, type=int)
    get_cat = Category.query.filter_by(id=id).first_or_404()
    get_category_product = Addproduct.query.filter_by(category=get_cat).paginate(page=page, per_page=4)
    return render_template('products/index.html', get_category_product=get_category_product, brands=brands(), categories=categories(), get_cat=get_cat)

@app.route('/addbrand', methods=['GET', 'POST'])
def addbrand():
    if 'email' not in session:
        flash('Please Login first', 'danger')
        return redirect(url_for('login'))
    if request.method == "POST":
        getbrand = request.form.get('brand')
        brand = Brand(name=getbrand)
        db.session.add(brand)
        flash(f'The Brand {getbrand} was added to you database', 'success')
        db.session.commit()
        return redirect(url_for('brands'))
    return render_template('products/addbrand.html', brands='brands')


@app.route('/updatebrand/<int:id>', methods=['GET','POST'])
def updatebrand(id):
    if 'email' not in session:
        flash('Please Login first', 'danger')
        return redirect(url_for('login'))
    updatebrand = Brand.query.get_or_404(id)
    oldbrandname = Brand.query.get_or_404(id).name
    brand = request.form.get('brand')
    if request.method == "POST":
        updatebrand.name = brand
        flash(f'The brand {oldbrandname} was changed to {updatebrand.name}', 'success')
        db.session.commit()
        return redirect(url_for('brands'))
    return render_template('products/updatebrand.html', title='Update brand Page', updatebrand=updatebrand)

@app.route('/deletebrand/<int:id>', methods=['POST'])
def deletebrand(id):
    if 'email' not in session:
        flash('Please Login first', 'danger')
        return redirect(url_for('login'))
    brand = Brand.query.get_or_404(id)
    if request.method =="POST":
        db.session.delete(brand)
        db.session.commit()
        flash(f'The brand {brand.name} was deleted from your database', 'success')
        return redirect(url_for('brands'))
    flash(f'The brand {brand.name} cannot be deleted', 'warning')
    return redirect(url_for('admin'))

@app.route('/addcategory', methods=['GET', 'POST'])
def addcategory():
    if 'email' not in session:
        flash('Please Login first', 'danger')
        return redirect(url_for('login'))
    if request.method == "POST":
        getcategory = request.form.get('category')
        category = Category(name=getcategory)
        db.session.add(category)
        flash(f'The Category {getcategory} was added to you database', 'success')
        db.session.commit()
        return redirect(url_for('categories'))
    
    return render_template('products/addbrand.html')


@app.route('/updatecategory/<int:id>', methods=['GET','POST'])
def updatecategory(id):
    if 'email' not in session:
        flash('Please Login first', 'danger')
        return redirect(url_for('login'))
    updatecategory = Category.query.get_or_404(id)
    oldcategoryname = Category.query.get_or_404(id).name
    category = request.form.get('category')
    if request.method == "POST":
        updatecategory.name = category
        flash(f'The category {oldcategoryname} was changed to {updatecategory.name}', 'success')
        db.session.commit()
        return redirect(url_for('categories'))
    return render_template('products/updatebrand.html', title='Update Category Page', updatecategory=updatecategory)

@app.route('/deletecategory/<int:id>', methods=['POST'])
def deletecategory(id):
    if 'email' not in session:
        flash('Please Login first', 'danger')
        return redirect(url_for('login'))
    category = Category.query.get_or_404(id)
    if request.method =="POST":
        db.session.delete(category)
        db.session.commit()
        flash(f'The category {category.name} was deleted from your database', 'success')
        return redirect(url_for('categories'))
    flash(f'The category {category.name} cannot be deleted', 'warning')
    return redirect(url_for('admin'))


@app.route('/addproduct', methods=['GET','POST'])
def addproduct():
    if 'email' not in session:
        flash('Please Login first', 'danger')
        return redirect(url_for('login'))
    form = Addproducts(request.form)
    brands = Brand.query.all()
    categories = Category.query.all()
    if request.method=="POST"and 'image_1' in request.files:
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        colors = form.colors.data
        desc = form.description.data
        brand = request.form.get('brand')
        category = request.form.get('category')
        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        addproduct = Addproduct(name=name,price=price,discount=discount,stock=stock,colors=colors,desc=desc,category_id=category,brand_id=brand,image_1=image_1,image_2=image_2,image_3=image_3)
        db.session.add(addproduct)
        flash(f'The product {name} was added in database','success')
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('products/addproduct.html', form=form, title='Add Product Page', brands=brands, categories=categories)

@app.route('/updateproduct/<int:id>', methods=['GET', 'POST'])
def updateproduct(id):
    if 'email' not in session:
        flash('Please Login first', 'danger')
        return redirect(url_for('login'))
    brands = Brand.query.all()
    categories = Category.query.all()
    product = Addproduct.query.get_or_404(id)
    brand = request.form.get('brand')
    category = request.form.get('category')
    form = Addproducts(request.form)
    if request.method == "POST":
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.brand_id = brand
        product.category_id = category
        product.stock = form.stock.data
        product.colors = form.colors.data
        product.desc = form.description.data

        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            except:
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            except:
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")

        db.session.commit()
        flash(f'The product data has been successfully updated', 'success')
        return redirect(url_for('admin'))
    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.colors.data = product.colors
    form.description.data = product.desc
    return render_template('products/updateproduct.html', form=form, brands=brands, categories=categories, product=product)

@app.route('/deleteproduct/<int:id>', methods=['POST'])
def deleteproduct(id):
    if 'email' not in session:
        flash('Please Login first', 'danger')
        return redirect(url_for('login'))
    product = Addproduct.query.get_or_404(id)
    if request.method =="POST":
        try:
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
        except Exception as e:
            print(e)
        db.session.delete(product)
        db.session.commit()
        flash(f'The product {product.name} was deleted from your database', 'success')
        return redirect(url_for('admin'))
    flash(f'The product {product.name} cannot be deleted', 'warning')
    return redirect(url_for('admin'))