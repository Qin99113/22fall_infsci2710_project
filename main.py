from datetime import datetime

from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# User Part
# Get user login details
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


# Enter the cover page
@app.route("/")
def root():
    # loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, inventory FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT productKindId, name FROM product_kind')
        categoryData = cur.fetchall()
        cur.execute('SELECT scent_id, scent_name FROM scent')
        scentData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('cover.html', itemData=itemData,
                           categoryData=categoryData, scentData=scentData)


# Enter the home page-all products displayed
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


# Enter the user register page
@app.route("/registerationForm")
def registrationForm():
    return render_template("register.html")


# Operate user register
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


# Enter the login page
@app.route("/loginForm")
def loginForm():
    # if 'email' in session:
    #     return redirect(url_for('root'))
    # else:
        return render_template('login.html', error='')


def is_valid(email, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM customers')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False


# Operate user login
@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            return redirect(url_for('homeRoot'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)


@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))


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
@app.route("/displayStore")
def displayStore():
    loggedIn, firstName, noOfItems = getLoginDetails()
    return render_template("store.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

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


@app.route("/addToCart")
def addToCart():
    loggedIn, firstName, noOfItems = getLoginDetails()
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
                return render_template("cart.html", msg=msg, product_inventory=product_inventory, product_name=product_name, loggedIn=loggedIn,
                           firstName=firstName, noOfItems=noOfItems )
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




# Manager Part
#Get manager login details.
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


# Verify account
def mgr_valid(email, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM manager')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False


# Enter manager login page
@app.route("/managerpage/mgrloginForm", methods=["POST","GET"])
def mgrloginForm():
    # if 'email' in session:
    #     return redirect(url_for('mgrroot'))
    # else:
    if request.method == "POST":
        return render_template('mgrlogin.html', error='')
    return render_template('mgrlogin.html', error='')


# Operate manager login
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


@app.route("/managerpage/mgrregisterationForm")
def mgrregistrationForm():
    return render_template("mgrregister.html")


# operate manager register
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
                # cur.execute('INSERT INTO customers (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, address1, address2, zipcode, city, state, country, phone))
                con.commit()

                msg = "Registered Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        return render_template("mgrlogin.html", error=msg)


# Get information for manager home page
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


# Log out the manager account
@app.route("/managerpage/mgrlogout")
def mgrlogout():
    session.pop('email', None)
    return redirect(url_for('root'))


# display the products by selected category
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


# display the products by selected scent
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


# display the details of a single product
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

@app.route("/mgrdisplayStore")
def mgrdisplayStore():
    loggedIn, firstName, noOfItems = mgrLoginDetails()
    return render_template("mgrstore.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)


# Enter the update product information page
@app.route("/updateproductInfo")
def updateproductInfo():
    loggedIn, firstName, noOfItems = mgrLoginDetails()
    productId = int(request.args.get("productId"))
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, inventory, productKindId, scent_id FROM products WHERE productId = ?', (productId, ))
        itemData = cur.fetchall()[0]
        productKindId = int(itemData[6])
        scent_id = int(itemData[7])
        cur.execute('SELECT productKindId, name FROM product_kind WHERE productKindId = ?', (productKindId, ))
        categoryData = cur.fetchall()[0]
        cur.execute('SELECT scent_id, scent_name FROM scent WHERE scent_id = ?', (scent_id, ))
        scentData = cur.fetchall()[0]

    return render_template('updateProduct.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData, scentData=scentData, msg="")


# update product information function
@app.route("/updateproduct", methods=['GET', 'POST'])
def updateProduct():
    loggedIn, firstName, noOfItems = mgrLoginDetails()
    if request.method == 'POST':
        #Parse form data    
        productId = int(request.form['productId'])
        print(type(productId))
        name = request.form['name']
        inventory = int(request.form['inventory'])
        price = float(request.form['price'])
        description = request.form['description']
        image = request.form['image']
        # productKindName = request.form['productKindName']
        # scentName = request.form['scentName']


        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                # cur.execute('SELECT productKindId, name FROM product_kind WHERE name= ?', (productKindName, ))

                # productKindId = cur.fetchall()[0][0]

                # cur.execute('SELECT scent_id, scent_name FROM scent WHERE scent_name = ?', (scentName, ))
                # scent_id = cur.fetchall()[0][0]

                cur.execute('Update products SET name = ?, inventory = ?, price = ?, description = ?, image = ? WHERE productId = ?', (name, inventory, price, description, image, productId))
                con.commit()

                msg = "Updated Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        # con.close()
        cur.execute(
            'SELECT productId, name, price, description, image, inventory, productKindId, scent_id FROM products WHERE productId = ?',
            (productId,))
        itemData = cur.fetchall()[0]
        productKindId = int(itemData[6])
        scent_id = int(itemData[7])
        cur.execute('SELECT productKindId, name FROM product_kind WHERE productKindId = ?', (productKindId,))
        categoryData = cur.fetchall()[0]
        cur.execute('SELECT scent_id, scent_name FROM scent WHERE scent_id = ?', (scent_id,))
        scentData = cur.fetchall()[0]
        print(msg)
        return render_template("updateProduct.html", itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData, scentData=scentData, msg=msg)

# Delete product by inputting the product details
@app.route("/managerpage/managedeleteForm")
def managedeleteForm():
    loggedIn, firstName, noOfItems = mgrLoginDetails()
    return render_template('managedelete.html', loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)


@app.route("/managerpage/managedelete", methods = ['GET', 'POST'])
def managedelete():
    loggedIn, firstName, noOfItems = mgrLoginDetails()
    if request.method == 'POST':
        productId = int(request.form['productId'])
        name = request.form['name']


        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                if name == "":
                    cur.execute('SELECT name FROM products WHERE productId = ?', (productId, ))
                    product_name = cur.fetchall()[0][0]
                else:
                    cur.execute('SELECT productId FROM products WHERE name = ?', (name,))
                    productId = cur.fetchall()[0][0]
                    cur.execute('SELECT name FROM products WHERE productId = ?', (productId,))
                    product_name = cur.fetchall()[0][0]

                cur.execute('DELETE from products where name = ? or productId = ?', (name, productId))
                con.commit()
                msg = "Item Deleted Successfully"
                return render_template('managedelete.html', loggedIn=loggedIn, firstName=firstName,
                                       noOfItems=noOfItems, msg=msg, product_name=product_name)
            except:
                con.rollback()
                msg = "Error occured"
                return render_template('managedelete.html', loggedIn=loggedIn, firstName=firstName,
                                       noOfItems=noOfItems, msg=msg)


# Delete product by clicking the button ("Delete Product")in the product description page
@app.route("/deleteitem", methods = ['GET', 'POST'])
def deleteItem():
    loggedIn, firstName, noOfItems = mgrLoginDetails()

    productId = int(request.args.get('productId'))
    print(productId)
    with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('DELETE from products where productId = ?', (productId, ))
                con.commit()
                msg = "Item Deleted Successfully"
                # return render_template("managerpage.html", loggedIn=loggedIn, firstName=firstName,
                #                        noOfItems=noOfItems, msg=msg)
                return redirect(url_for('mgrroot'))
            except:
                con.rollback()
                msg = "Error occured"
                # return render_template("managerpage.html", loggedIn=loggedIn, firstName=firstName,
                #                        noOfItems=noOfItems, msg=msg)
                return redirect(url_for('mgrroot'))


# Manage the inventory
@app.route("/managerpage/managestockForm")
def managestockForm():
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
    return render_template('managestock.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName,
                           noOfItems=noOfItems, categoryData=categoryData, scentData=scentData)


@app.route("/managerpage/managestock", methods=['GET', 'POST'])
def managestock():
    loggedIn, firstName, noOfItems = mgrLoginDetails()
    if request.method == 'POST':
        productId = request.form['productId']
        inventory = request.form['inventory']
        name = request.form["name"]

        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()

                cur.execute('UPDATE products SET inventory = ? WHERE productId = ? or name = ?', (inventory, productId, name))
                con.commit()
                msg = "Updated Successfully"
                if name == "":
                    cur.execute('SELECT name FROM products WHERE productId = ?', (productId,))
                    product_name = cur.fetchall()[0][0]
                else:
                    cur.execute('SELECT productId FROM products WHERE name = ?', (name,))
                    productId = cur.fetchall()[0][0]
                    cur.execute('SELECT name FROM products WHERE productId = ?', (productId,))
                    product_name = cur.fetchall()[0][0]
            except:
                con.rollback()
                msg = "Error occured"
                return render_template('managestock.html', loggedIn=loggedIn, firstName=firstName,
                                       noOfItems=noOfItems, msg=msg)


        return render_template('managestock.html',  loggedIn=loggedIn, firstName=firstName,
                               noOfItems=noOfItems, msg=msg, inventory=inventory, product_name=product_name)

# Data aggregation
@app.route("/managerpage/statisticsForm")
def managestaticticsForm():
    loggedIn, firstName, noOfItems = mgrLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()

        cur.execute(
            "SELECT c.state from Transactions t join customers c on c.customer_id order by(t.product_quantity) DESC LIMIT 1")
        bestRegion = cur.fetchone()[0]
        print(bestRegion)

        cur.execute("SELECT p.name  from Transactions t join products p order by(t.product_quantity) DESC LIMIT 1")
        bestSeller = cur.fetchone()[0]
        print(bestSeller)

    conn.close()
    return render_template("dataAggregation.html", bestRegion=bestRegion, bestSeller=bestSeller, loggedIn=loggedIn, firstName=firstName,
                               noOfItems=noOfItems)

# Add item
@app.route("/managerpage/addItemForm")
def addItemForm():
    loggedIn, firstName, noOfItems = mgrLoginDetails()
    return render_template("manageAddItem.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)


@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    loggedIn, firstName, noOfItems = mgrLoginDetails()
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        inventory = int(request.form['inventory'])
        productKindName = request.form['productKindName']
        scent_name = request.form['scent_name']

        # Uploading image procedure
        image = request.files['image']
        print(image)
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('SELECT productKindId, name FROM product_kind WHERE name= ?', (productKindName, ))

                productKindId = cur.fetchall()[0][0]

                cur.execute('SELECT scent_id, scent_name FROM scent WHERE scent_name = ?', (scent_name, ))
                scent_id = cur.fetchall()[0][0]
                cur.execute(
                    'INSERT INTO products (name, price, description, image, inventory, productKindId, scent_Id) VALUES (?, ?, ?, ?, ?, ?,?)',
                    (name, price, description, imagename, inventory, productKindId, scent_id))
                conn.commit()
                msg = "added successfully"

                return render_template("manageAddItem.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, msg=msg)
            except:
                msg = "error occured"
                conn.rollback()

                return render_template("manageAddItem.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, msg=msg)



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
