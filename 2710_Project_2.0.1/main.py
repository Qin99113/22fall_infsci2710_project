from datetime import datetime

from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#
def getLoginDetails():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            noOfItems = 0
        else:
            loggedIn = True
            cur.execute("SELECT customer_id, firstName FROM customers WHERE email = ?", (session['email'],))
            customer_id, firstName = cur.fetchone()
            cur.execute("SELECT count(productId) FROM cart WHERE userId = ?", (customer_id,))
            noOfItems = cur.fetchone()[0]
    conn.close()
    return (loggedIn, firstName, noOfItems)


@app.route("/")
def root():
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, inventory FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT productKindId, name FROM product_kind')
        categoryData = cur.fetchall()
        cur.execute('SELECT scent_id, scent_name FROM scent')
        scentData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('index.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems,
                           categoryData=categoryData, scentData=scentData)


@app.route("/home")
def homeRoot():
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, inventory FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT productKindId, name FROM product_kind')
        categoryData = cur.fetchall()
        cur.execute('SELECT scent_id, scent_name FROM scent')
        scentData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('home.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems,
                           categoryData=categoryData, scentData=scentData)


@app.route("/add")
def admin():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT productKindId, name FROM product_kind")
        categories = cur.fetchall()
    conn.close()
    return render_template('add.html', categories=categories)


@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        inventory = int(request.form['inventory'])
        productKindId = int(request.form['productKindId'])

        # Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    '''INSERT INTO products (name, price, description, image, inventory, productKindId) VALUES (?, ?, ?, ?, ?, ?)''',
                    (name, price, description, imagename, inventory, productKindId))
                conn.commit()
                msg = "added successfully"
            except:
                msg = "error occured"
                conn.rollback()
        conn.close()
        print(msg)
        return redirect(url_for('root'))


@app.route("/remove")
def remove():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, inventory FROM products')
        data = cur.fetchall()
    conn.close()
    return render_template('remove.html', data=data)


@app.route("/removeItem")
def removeItem():
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        try:
            cur = conn.cursor()
            cur.execute('DELETE FROM products WHERE productID = ?', (productId,))
            conn.commit()
            msg = "Deleted successsfully"
        except:
            conn.rollback()
            msg = "Error occured"
    conn.close()
    print(msg)
    return redirect(url_for('root'))


@app.route("/displayCategory")
def displayCategory():
    loggedIn, firstName, noOfItems = getLoginDetails()
    categoryId = request.args.get("productKindId")
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT products.productId, products.name, products.price, products.image, product_kind.name FROM products, product_kind WHERE products.productKindId = product_kind.productKindId AND product_kind.productKindId = ?",
            (categoryId,))
        data = cur.fetchall()
    conn.close()
    categoryName = data[0][4]
    data = parse(data)
    return render_template('displayCategory.html', data=data, loggedIn=loggedIn, firstName=firstName,
                           noOfItems=noOfItems, categoryName=categoryName)


@app.route("/displayScent")
def displayScent():
    loggedIn, firstName, noOfItems = getLoginDetails()
    scentId = request.args.get("scent_id")
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT products.productId, products.name, products.price, products.image, scent.scent_name FROM products, scent WHERE products.scent_id = scent.scent_id AND scent.scent_id = ?",
            (scentId,))
        data = cur.fetchall()
    conn.close()
    scentName = data[0][4]
    data = parse(data)
    return render_template('displayScent.html', data=data, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems,
                           scentName=scentName)


@app.route("/account/profile")
def profileHome():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT customer_id, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM customers WHERE email = ?",
            (session['email'],))
        profileData = cur.fetchone()
        cur.execute("SELECT customer_kind From customers WHERE email = ?", (session['email'],))
        customerKindData = cur.fetchone()
        customerBusinessData = []
        customerPersonalData = []
        if customerKindData[0] == "business":
            cur.execute('SELECT business_category, company_annual_income From customers WHERE email = ?',
                        (session['email'],))
            customerBusinessData = cur.fetchone()
        else:
            cur.execute('SELECT marriage_status, gender, age, personal_annual_income From customers WHERE email = ?',
                        (session['email'],))
            customerPersonalData = cur.fetchone()
    conn.close()
    return render_template("profileHome.html", profileData=profileData, customerKindData=customerKindData,
                           customerBusinessData=customerBusinessData, customerPersonalData=customerPersonalData,
                           loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)


@app.route("/account/profile/edit")
def editProfile():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT customer_id, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM customers WHERE email = ?",
            (session['email'],))
        profileData = cur.fetchone()
        cur.execute("SELECT customer_kind From customers WHERE email = ?", (session['email'],))
        customerKindData = cur.fetchone()
        customerBusinessData = []
        customerPersonalData = []
        if customerKindData[0] == "business":
            cur.execute('SELECT business_category, company_annual_income From customers WHERE email = ?',
                        (session['email'],))
            customerBusinessData = cur.fetchone()
        else:
            cur.execute('SELECT marriage_status, gender, age, personal_annual_income From customers WHERE email = ?',
                        (session['email'],))
            customerPersonalData = cur.fetchone()
    conn.close()
    return render_template("editProfile.html", profileData=profileData, customerKindData=customerKindData,
                           customerBusinessData=customerBusinessData, customerPersonalData=customerPersonalData,
                           loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)


@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT customer_id, password FROM customers WHERE email = ?", (session['email'],))
            customer_id, password = cur.fetchone()
            if (password == oldPassword):
                try:
                    cur.execute("UPDATE customers SET password = ? WHERE customer_id = ?", (newPassword, customer_id))
                    conn.commit()
                    msg = "Changed successfully"
                except:
                    conn.rollback()
                    msg = "Failed"
                return render_template("changePassword.html", msg=msg)
            else:
                msg = "Wrong password"
        conn.close()
        return render_template("changePassword.html", msg=msg)
    else:
        return render_template("changePassword.html")


@app.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():
    if request.method == 'POST':
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']
        customer_kind = request.form['customer_kind']
        if customer_kind == "business":
            business_type = request.form['business_type']
            company_annual_income = request.form['company_annual_income']
        elif customer_kind == "person":
            marriage_status = request.form['marriage_status']
            gender = request.form['gender']
            age = request.form['age']
            personal_annual_income = request.form['personal_annual_income']
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute(
                    'UPDATE customers SET firstName = ?, lastName = ?, address1 = ?, address2 = ?, zipcode = ?, city = ?, state = ?, country = ?, phone = ?, customer_kind= ? WHERE email = ?',
                    (firstName, lastName, address1, address2, zipcode, city, state, country, phone, customer_kind, email))
                if customer_kind == "business":
                    cur.execute('UPDATE customers SET business_category= ?, company_annual_income= ? WHERE email = ?', (business_type, company_annual_income, email))

                elif customer_kind == "person":
                    cur.execute('UPDATE customers SET marriage_status= ?, gender= ?, age= ?, personal_annual_income= ? WHERE email = ?',
                                (marriage_status, gender, age, personal_annual_income, email))




                con.commit()
                msg = "Saved Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        return redirect(url_for('profileHome'))


@app.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)


@app.route("/productDescription")
def productDescription():
    loggedIn, firstName, noOfItems = getLoginDetails()
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image FROM products WHERE productId = ?',
                    (productId,))
        productData = cur.fetchone()
    conn.close()
    return render_template("productDescription.html", data=productData, loggedIn=loggedIn, firstName=firstName,
                           noOfItems=noOfItems)


@app.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        productId = int(request.args.get('productId'))
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT customer_id FROM customers WHERE email = ?", (session['email'],))
            userId = cur.fetchone()[0]
            cur.execute("SELECT inventory, products.name FROM products WHERE productId = ?", (str(productId)))
            productData = cur.fetchone()
            product_inventory = productData[0]
            product_name = productData[1]
            if product_inventory == 0:
                msg = "No Stock!"
                return render_template("cart.html", msg=msg, product_inventory=product_inventory, product_name=product_name )
            else:
                try:
                    cur.execute("INSERT INTO cart (userId, productId) VALUES (?, ?)", (userId, productId))
                    conn.commit()
                    msg = "Added successfully"
                except:
                    conn.rollback()
                    msg = "Error occured"
                return redirect(url_for('cart'))
            conn.close()



@app.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT customer_id FROM customers WHERE email = ?", (email,))
        userId = cur.fetchone()[0]
        cur.execute(
            "SELECT products.productId, products.name, products.price, products.image FROM products, cart WHERE products.productId = cart.productId AND cart.userId = ?",
            (userId,))
        products = cur.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("cart.html", products=products, totalPrice=totalPrice, loggedIn=loggedIn,
                           firstName=firstName, noOfItems=noOfItems)


@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    email = session['email']
    productId = int(request.args.get('productId'))
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT customer_id FROM customers WHERE email = ?", (email,))
        userId = cur.fetchone()[0]
        try:
            cur.execute("DELETE FROM cart WHERE userId = ? AND productId = ?", (userId, productId))
            conn.commit()
            msg = "removed successfully"
        except:
            conn.rollback()
            msg = "error occured"
    conn.close()
    return redirect(url_for('cart'))
@app.route("/checkout")
def checkOut():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT customer_id FROM customers WHERE email = ?", (email,))
        userId = cur.fetchone()[0]
        cur.execute('SELECT * FROM customers WHERE email = ?', (email,))
        deliveryinfo = cur.fetchone()
        cur.execute(
            "SELECT products.productId, products.name, products.price, products.image FROM products, cart WHERE products.productId = cart.productId AND cart.userId = ?",
            (userId,))
        products = cur.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("checkout.html", data=deliveryinfo, products=products, totalPrice=totalPrice,
                           loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/orderConfirmed")
def orderConfirmed():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT customer_id FROM customers WHERE email = ?", (email,))
        userId = cur.fetchone()[0]
        cur.execute('SELECT * FROM customers WHERE email = ?', (email,))
        deliveryinfo = cur.fetchone()
        cur.execute(
            "SELECT products.productId, products.name, products.price, products.image, products.inventory FROM products, cart WHERE products.productId = cart.productId AND cart.userId = ?",
            (userId,))
        products = cur.fetchall()
    totalPrice = 0
    num_product = 0
    for row in products:
        totalPrice += row[2]
        num_product += 1
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        date = datetime.now()
        for row in products:
            productId = row[0]
            product_price = row[2]
            product_quantity = 1
            product_inventory = row[4] - 1
            try:

                cur.execute('UPDATE products SET inventory = ? WHERE productId = ?', (product_inventory, productId))
                con.commit()
            except:
                msg = "Sorry, there is no" + row[1] + "in stock"
                return render_template("orderConfirmed.html", data=deliveryinfo, products=products,
                                       totalPrice=totalPrice, product_inventory=product_inventory,
                                       loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, msg=msg)

            else:
                cur.execute(
                'INSERT INTO Transactions (productId, customerId, date, product_quantity, product_price) VALUES (?, ?, ?, ?, ?)',
                (productId, userId, date, product_quantity, product_price))
                conn.commit()


                return render_template("orderConfirmed.html", data=deliveryinfo, products=products, totalPrice=totalPrice,
                                       product_inventory=product_inventory, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)
@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))


def is_valid(email, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM customers')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

# Manager Part
def mgrLoginDetails():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            noOfItems = 0
        else:
            loggedIn = True
            cur.execute("SELECT mgrId, firstName FROM manager WHERE email = ?", (session['email'], ))
            mgrId, firstName = cur.fetchone()
            cur.execute("SELECT count(productId) FROM cart WHERE userId = ?", (mgrId, ))
            noOfItems = cur.fetchone()[0]
    conn.close()
    return (loggedIn, firstName, noOfItems)

@app.route("/managerpage/mgrroot")
def mgrroot():
    loggedIn, firstName, noOfItems = mgrLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, inventory, productKindId, scent_id FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT productKindId, name FROM product_kind')
        categoryData = cur.fetchall()
        cur.execute('SELECT scent_id, scent_name FROM scent')
        scentData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('managerpage.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData, scentData=scentData)

@app.route("/managerpage/mgrlogout")
def mgrlogout():
    session.pop('email', None)
    return redirect(url_for('root'))

def mgr_valid(email, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM manager')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

@app.route("/managerpage/mgrloginForm", methods=["POST","GET"])
def mgrloginForm():
    # if 'email' in session:
    #     return redirect(url_for('mgrroot'))
    # else:
    if request.method == "POST":
        return render_template('mgrlogin.html', error='')
    return render_template('mgrlogin.html', error='')

@app.route("/managerpage/mgrlogin", methods = ['POST', 'GET'])
def mgrlogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if mgr_valid(email, password):
            session['email'] = email
            return redirect(url_for('mgrroot'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('mgrlogin.html', error=error)

@app.route("/managerpage/mgrregister", methods = ['GET', 'POST'])
def mgrregister():
    if request.method == 'POST':
        #Parse form data    
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']

        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO manager (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, address1, address2, zipcode, city, state, country, phone))
                cur.execute('INSERT INTO customers (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, address1, address2, zipcode, city, state, country, phone))
                con.commit()

                msg = "Registered Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        return render_template("mgrlogin.html", error=msg)

@app.route("/managerpage/mgrregisterationForm")
def mgrregistrationForm():
    return render_template("mgrregister.html")

@app.route("/managerpage/manageproductForm")
def manageproductForm():
    loggedIn, firstName, noOfItems = mgrLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, inventory FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT productKindId, name FROM product_kind')
        categoryData = cur.fetchall()
        cur.execute('SELECT scent_id, scent_name FROM scent')
        scentData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('manageproduct.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData, scentData=scentData)


@app.route("/managerpage/manageproduct", methods = ['GET', 'POST'])
def manageproduct():
    if request.method == 'POST':
        #Parse form data    
        productId = request.form['productID']
        name = request.form['name']
        inventory = request.form['inventory']
        price = request.form['price']
        description = request.form['description']
        image = request.form['image']
        productKindId = request.form['image']
        scent_id = request.form['categoryId']

        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO products (productId, name, inventory, price, description, image, productKindId, scent_id) VALUES (?, ?, ?, ?, ?, ?, ?)', (productId, name, inventory, price, description, image, productKindId, scent_id))
                con.commit()
                msg = "Updated Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        return redirect(url_for('mgrroot'))

@app.route("/mgrdisplayCategory")
def mgrdisplayCategory():
    loggedIn, firstName, noOfItems = mgrLoginDetails()
    categoryId = request.args.get("productKindId")
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT products.productId, products.name, products.price, products.image, product_kind.name FROM products, product_kind WHERE products.productKindId = product_kind.productKindId AND product_kind.productKindId = ?",
            (categoryId,))
        data = cur.fetchall()
    conn.close()
    categoryName = data[0][4]
    data = parse(data)
    return render_template('mgrdisplayCategory.html', data=data, loggedIn=loggedIn, firstName=firstName,
                           noOfItems=noOfItems, categoryName=categoryName)


@app.route("/mgrdisplayScent")
def mgrdisplayScent():
    loggedIn, firstName, noOfItems = mgrLoginDetails()
    scentId = request.args.get("scent_id")
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT products.productId, products.name, products.price, products.image, scent.scent_name FROM products, scent WHERE products.scent_id = scent.scent_id AND scent.scent_id = ?",
            (scentId,))
        data = cur.fetchall()
    conn.close()
    scentName = data[0][4]
    data = parse(data)
    return render_template('mgrdisplayScent.html', data=data, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems,
                           scentName=scentName)
@app.route("/mgrproductDescription")
def mgrproductDescription():
    loggedIn, firstName, noOfItems = mgrLoginDetails()
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, inventory, ProductKindId, scent_id FROM products WHERE productId = ?',
                    (productId,))
        productData = cur.fetchone()
    conn.close()
    return render_template("mgrproductDescription.html", data=productData, loggedIn=loggedIn, firstName=firstName,
                           noOfItems=noOfItems)

@app.route("/managerpage/managestockForm")
def managestockForm():
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, inventory FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT productKindId, name FROM product_kind')
        categoryData = cur.fetchall()
        cur.execute('SELECT scent_id, scent_name FROM scent')
        scentData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('managestock.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData, scentData=scentData)


@app.route("/managerpage/managestock", methods = ['GET', 'POST'])
def managestock():
    if request.method == 'POST':
        productID = request.form['productID']
        inventory = request.form['stock']
        
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('UPDATE products SET inventory = ? WHERE productID = ?', (inventory, productID))
                con.commit()
                msg = "Updated Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        return redirect(url_for('mgrroot'))


@app.route("/managerpage/managedeleteForm")
def managedeleteForm():
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, inventory FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT productKindId, name FROM product_kind')
        categoryData = cur.fetchall()
        cur.execute('SELECT scent_id, scent_name FROM scent')
        scentData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('managedelete.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData, scentData=scentData)

@app.route("/managerpage/managedelete", methods = ['GET', 'POST'])
def managedelete():
    if request.method == 'POST':
        productID = request.form['productID']
        name = request.form['name']
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('DELETE from products where name = ? or productID = ?', (name, productID))
                con.commit()
                msg = "Item Deleted Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        return redirect(url_for('mgrroot'))

# Update product information
@app.route("/managerpage/manageinfoForm")
def manageinfoForm():
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, inventory FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT productKindId, name FROM product_kind')
        categoryData = cur.fetchall()
        cur.execute('SELECT scent_id, scent_name FROM scent')
        scentData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('manageinfo.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData, scentData=scentData)

@app.route("/managerpage/manageinfo", methods = ['GET', 'POST'])
def productinfo():
    if request.method == 'POST':
        #Parse form data    
        productId = request.form['productID']
        name = request.form['name']
        inventory = request.form['inventory']
        price = request.form['price']
        description = request.form['description']
        image = request.form['image']
        productKindId = request.form['image']
        scent_id = request.form['categoryId']

        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('DELETE FROM products WHERE productId = ?', (productId))
                cur.execute('INSERT INTO products (productId, name, inventory, price, description, image, productKindId, scent_id) VALUES (?, ?, ?, ?, ?, ?, ?)', (productId, name, inventory, price, description, image, productKindId, scent_id))
                con.commit()
                msg = "Updated Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        return redirect(url_for('mgrroot'))

@app.route("/managerpage/statisticsForm")
def managestaticticsForm():
    return render_template("statistics.html")

@app.route("/returnhomeForm")
def returnhomeForm():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT customer_id FROM customers WHERE email = ?", (email, ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT products.productId, products.inventory FROM products, cart WHERE products.productId = cart.productId AND cart.userId = ?", (userId, ))
        products = cur.fetchall()
        cur.execute('DELETE FROM cart WHERE userId = ?', (userId, ))
        for row in products:
            cur.execute('UPDATE products SET inventory = ? WHERE productId = ?', (row[1]-1, row[0]))
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, inventory FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT productKindId, name FROM product_kind')
        categoryData = cur.fetchall()
        cur.execute('SELECT scent_id, scent_name FROM scent')
        scentData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('home.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData, scentData=scentData)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Parse form data
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']
        customer_kind = request.form['customer_kind']
        business_type = request.form['business_type']
        company_annual_income = request.form['company_annual_income']
        marriage_status = request.form['marriage_status']
        gender = request.form['gender']
        age = request.form['age']
        personal_annual_income = request.form['personal_annual_income']

        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute(
                    'INSERT INTO customers (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone, customer_kind, marriage_status, gender, age, personal_annual_income, business_category, company_annual_income) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (
                        hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, address1, address2,
                        zipcode,
                        city, state, country, phone, customer_kind, marriage_status, gender, age,
                        personal_annual_income,
                        business_type, company_annual_income))

                con.commit()

                msg = "Registered Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        return render_template("login.html", error=msg)


@app.route("/registerationForm")
def registrationForm():
    return render_template("register.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans


if __name__ == '__main__':
    app.run(debug=True)
