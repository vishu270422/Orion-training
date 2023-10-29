from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.secret_key = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydb'
mongo = PyMongo(app)
users_collection = mongo.db.users

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if users_collection.find_one({'email': email}):
            return 'Email already exists. Choose another one.'
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({'email': email, 'password': hashed_password})
        session['email'] = email
        return redirect(url_for('profile'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            session['email'] = email
            if 'email' in session:
                email = session['email']
                if email == 'vishu@1234.com':
                    return render_template('admin.html')
            return redirect(url_for('profile'))
        return 'Invalid email or password. Please try again.'
    return render_template('login.html')


    

@app.route('/update_user', methods=['POST'])
def update_user():
    if request.method == 'POST':
        if 'email' in session:
            email = session['email']
            if email == 'vishu@1234.com':
                email = request.form['email']
                password = request.form['password']
                hashed_password = generate_password_hash(password)
                users_collection.update_one({'email': email}, {'$set': {'password': hashed_password}})
                return 'User updated successfully.'
            else:
                return 'You are not authorized to perform this action.'
        else:
            return 'You need to log in first.'
    return redirect(url_for('home'))

@app.route('/delete_user', methods=['POST'])
def delete_user():
    if request.method == 'POST':
        if 'email' in session:
            email = session['email']
            if email == 'vishu@1234.com':
                email = request.form['email']
                users_collection.delete_one({'email': email})
                return 'User deleted successfully.'
            else:
                return 'You are not authorized to perform this action.'
        else:
            return 'You need to log in first.'
    return redirect(url_for('home'))


@app.route('/profile')
def profile():
    if 'email' in session:
        email = session['email']
        
        return f'Hello , {email}!!!!'  
    return 'You need to log in first.'

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('home'))

  

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        price = float(request.form.get('price'))
        discount = float(request.form.get('discount'))
        add_product(product_name, price, discount)
    
    products = get_products()
    return render_template('admin.html', products=products)

def add_product(name, price, discount):
    product_data = {
        'name': name,
        'price': price,
        'discount': discount
    }
    mongo.db.products.insert_one(product_data)

def get_products():
    return list(mongo.db.products.find())




if __name__ == '__main__':
    app.run(debug=True)