import os,sys
import requests
import pymysql
from collections import namedtuple
from re import sub
from bs4 import BeautifulSoup
from flask import flash,Flask, jsonify, render_template, request, redirect, url_for, session
from store_functions import *
from flask_cors import CORS
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import os
import numpy as np
import tempfile
from flask_mysqldb import MySQL
from flask import *  
from flask_mail import *  
import MySQLdb.cursors
import bcrypt
from itsdangerous import URLSafeTimedSerializer,SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = 'PriceComparision Project by Bhavya'

app.config["MAIL_SERVER"]='smtp.gmail.com'  
app.config["MAIL_PORT"] = 465      
app.config["MAIL_USERNAME"] = 'joshithanayaka1709@gmail.com'  
app.config['MAIL_PASSWORD'] = 'joshitha@1'  
app.config['MAIL_USE_TLS'] = False  
app.config['MAIL_USE_SSL'] = True  
#app.config['MAIL_SENDER'] = 'walkersunion345679@gmail.com'
app.config['SECURITY_PASSWORD_SALT'] = 'my_precious_two'



app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'PriceComparision'
#mysql.init_app(app)
CORS(app)
mail = Mail(app)
mysql = MySQL(app)

s = URLSafeTimedSerializer('Thisisasecret!')

amazon_URL = os.getenv('amazon_URL', 'https://www.amazon.in/s?k=')
flipkart_URL = os.getenv('flipkart_URL', 'https://www.flipkart.com/search?q=')
shopclues_URL = os.getenv('shopclues_URL', 'https://bazaar.shopclues.com/search?q=')
walmart_URL = os.getenv('walmart_URL', 'https://www.walmart.com/search?q=')
indiamart_URL= os.getenv('indiamart_URL', 'https://dir.indiamart.com/search.mp?ss=')
alibaba_URL = os.getenv('alibaba_URL','https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText=')

EMPTY_LIST = []

urls = [amazon_URL,flipkart_URL,shopclues_URL,walmart_URL,indiamart_URL,alibaba_URL]


@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s ', (username, ))
        account = cursor.fetchone()
        if account:
            hashed = account['password']
            #print('database has hashed: {} {}'.format(hashed,type(hashed)))
            #print('form supplied passwd: {} {}'.format(password,type(password)))
            hashed2 = bcrypt.hashpw(password.encode('utf-8'),hashed.encode('utf-8'))
            hashed2_str = hashed2.decode('utf-8')
            #print('rehash is: {} {}'.format(hashed2_str,type(hashed2_str)))
            if hashed2_str == hashed:
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                msg = 'Logged in successfully !'
                return render_template('index.html', msg = msg)
            else:
                return render_template('login.html',msg="Wrong Password")
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/signup', methods =['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        password_1 = request.form['password2']
        hashed = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
        hashed_str = hashed.decode('utf-8')
        if password!=password_1:
            return render_template('signup.html',msg='passwords must match')
        else :
            email = request.form['email']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists !'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address !'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers !'
            elif not username or not password or not email:
                msg = 'Please fill out the form !'
            else:
                cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, hashed_str, email, ))
                mysql.connection.commit()
                msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('signup.html', msg = msg)


@app.route('/search', methods=['GET','POST'])
def search_products():
    session['loggedin'] = True
    if request.method == 'POST' and 'search' in request.form:
        session['loggedin'] = True
        term = request.form['search'].strip()
        amazon = amazon_URL + sub(r"\s+",'+',str(term))+'&s=price-asc-rank&ref=nb_sb_noss_1&ref=sr_st_price-asc-rank'
        flip_kart = flipkart_URL + sub(r"\s+",'%20',str(term))+'&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&sort=price_asc'
        shopclues = shopclues_URL + sub(r"\s+", '+', str(term))+'&z=0&user_id=&user_segment=default&trend=1&z=0&sort_by=sort_price&sort_order=asc'
        walmart = walmart_URL + sub(r"\s+", '+', str(term)) + '&sort=price_low'
        india_mart = indiamart_URL + sub(r"\s+", '+', str(term)) + '&prdsrc=1'
        alibaba = alibaba_URL + sub(r"\s+", '+', str(term)) 
        
        results = parse_amazon(amazon)[:5]  + parse_shopclues(shopclues) [:5]+ parse_flip_kart(flip_kart)[:3] + parse_walmart(walmart)[:2]  + parse_alibaba(alibaba) #+ parse_indiamart(india_mart)
        
        #print(results)

        word = str(term)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO popular VALUES (%s) ',(word,))
        mysql.connection.commit()
        try:
            for prod in range(len(results)):
                cursor.execute('INSERT INTO product VALUES (NULL, % s, % s, % s, %s)', (results[prod]['title'], results[prod]['source']+str(prod),results[prod]['image'],results[prod]['price'], ))
                mysql.connection.commit()
        except Exception as e:
            print(str(e))
            pass
        
        return render_template('index.html',results=results)
    else:
        return render_template('index.html',msg='Enter a product name to search')

@app.route('/popular',methods=['GET','POST'])
def popular():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute('SELECT DISTINCT title FROM popular')
    rows=cursor.fetchall()
    return render_template('popular.html', rows=rows)

@app.route('/popularproduct',methods=['GET','POST'])
def popularproduct():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT DISTINCT * FROM product')
    rows=cursor.fetchall()
    return render_template('popularproduct.html', rows=rows)    

@app.route('/recieve', methods=['GET', 'POST'])
def recieve():
    return render_template('recieve.html')


@app.route('/graph', methods=['GET', 'POST'])
def graph():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT price FROM product')
    rows = cursor.fetchall()

    # Extracting prices from the fetched rows
    prices = [row['price'] for row in rows]

    # Creating x-axis values (indices)
    x = np.arange(len(prices))

    # Plotting the graph
    plt.bar(x, prices)
    plt.xlabel('Index')
    plt.ylabel('Price')
    plt.title('Product Prices')

    # Save the graph with a fixed file name
    plt.savefig('static/product_prices.png')

    return render_template('graph.html')


@app.route('/passwordreset',methods=['GET','POST'])
def passwordreset():
    session['loggedin'] = True
    username = request.form['username']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
    account = cursor.fetchone()
    if account:
        session['id'] = account['id']
        session['username'] = account['username']
        email = account['email']
        token = s.dumps(email, salt='email-confirm')
        msg = Message('Confirm Email', sender='bhavyasri5e5@gmail.com', recipients=[email])
        link = url_for('confirm_email', token=token, _external=True)
        msg.body = 'Your link is {}'.format(link)
        mail.send(msg)
        return '<h1>Check your mail for changing your password!</h1>'
    else :
        return render_template('login.html',msg='Sorry...!,please give correct username')
    #return render_template('reset.html')
         

@app.route('/confirm_email/<token>')
def confirm_email(token):   
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
    return render_template('reset.html')
    
@app.route('/reset',methods=['Get','Post'])
def reset():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'password2' in request.form:
            username = request.form['username']
            password = request.form['password']
            confirmPassword = request.form['password2']
            if (password!=confirmPassword):
                return render_template('reset.html',msg="both password fields must be entered same")
            else:
                hashed = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
                hashed_str = hashed.decode('utf-8')
                print(password, type(password), hashed, hashed_str)
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
                account = cursor.fetchone()
                if account:
                    session['id'] = account['id']
                    session['username'] = account['username']
                    cursor.execute('UPDATE accounts SET password = %s where username= %s ',(hashed_str,session['username'], ))
                    mysql.connection.commit()
                    return render_template('login.html',msg='password successfully changed')
                else :
                    msg='Account with given username is not present\n,If you didnot register before,Please register..!'
                    return render_template('login.html',msg=msg)
                            
        
@app.route('/profile',methods=['GET', 'POST'])
def profile():
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('index'))
    
@app.route('/delete',methods=['GET','POST'])
def delete():
    #session['loggedin'] = True
    return render_template('delete.html')
    
@app.route('/remove',methods=['GET','POST'])
def remove():
    if 'loggedin' in session:
        if request.method == 'POST' :
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts where id=%s',(session['id'],))
            account = cursor.fetchone()
            if account :
                session['id']=account['id']
                session['username'] = account['username']
                if request.form["LoginBtn1"]=="Yes":
                    cursor.execute('DELETE from accounts where username= %s and id = %s',(session['username'],session['id'], ))
                    mysql.connection.commit()
                    return render_template('signup.html',msg='account deleted')
                elif request.form["LoginBtn1"]=="No":
                    return render_template('index.html')
            else :
                return redirect(url_for('login'))
    return redirect(url_for('login'))           

@app.route('/contact',methods=['GET','POST'])
def contact():
    return render_template('contact.html')

@app.route('/report',methods=['GET','POST'])
def report():
    if 'loggedin' in session:
        if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'subject' in request.form:
            fname = request.form['firstname']
            lname = request.form['lastname']
            #country = request.form['country']
            subject = request.form['subject']
            print(fname,lname)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO contact VALUES(%s, % s, %s)', (fname, lname,subject, ))
            mysql.connection.commit()
            return render_template('index.html')
        else:
            return render_template('contact.html')
    else:
        render_template('login.html')

@app.route('/about',methods=['GET','POST'])
def about():
    if 'loggedin' in session:
        return render_template('about.html')
    else:
        return render_template('index.html')
def parse_all(soup,STORE):

    titles = parse_titles(soup,STORE)
    images = parse_images(soup,STORE)
    prices = parse_prices(soup,STORE)
    ratings = parse_product_ratings(soup, STORE)  
    #ratings = parse_ratings(soup,STORE)
    product_urls = parse_product_urls(soup,STORE)
    source = STORE
    #price_drops = parse_price_drops(soup,STORE)
    search_results = []
    for search_result in zip(titles, images, prices,ratings, product_urls):
        search_results.append({
            'title': search_result[0],
            'image': search_result[1],
            'price': search_result[2],
            'rating': search_result[3],
            'url': search_result[4],
            'source': source,
        })
    return search_results


def parse_amazon(url):
    
    print(url)
    STORE = "AMAZON"
    try:
        headers = {"Host": "www.amazon.in","User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate, br","Connection": "keep-alive"}
        r1 = requests.get(url, headers=headers)
        content = r1.content
        soup=BeautifulSoup(content,features="lxml")
    except Exception as e:  
        print(e)
        sys.exit(1)
    table_present = soup.find_all('div', {'class': 'a-section a-spacing-base a-text-center'})
    if table_present is None:
        return EMPTY_LIST
    return parse_all(soup,STORE)

def parse_flip_kart(url):
    
    print(url)
    STORE = "FLIPKART"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate, br","Connection": "keep-alive"}
        r1 = requests.get(url, headers=headers)
        content = r1.content
        soup=BeautifulSoup(content,features="lxml")
    except Exception as e: 
        print(e)
        sys.exit(1)
    #print(soup)
    table_present = soup.find_all('div')
    if table_present is None:
        return parse_all(soup,STORE)
    return parse_all(soup,STORE)

def parse_shopclues(url):
    STORE = "SHOPCLUES"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate, br","Connection": "keep-alive"}
        r1 = requests.get(url, headers=headers)
        content = r1.content
        soup=BeautifulSoup(content,features="lxml")
    except Exception as e:  
        print(e)
        sys.exit(1)
    #print(soup)
    table_present = soup.find_all('div', {'class': 'column col3 search_blocks'})
    if table_present is None:
        return EMPTY_LIST
    return parse_all(soup,STORE)

def parse_walmart(url):
    
    STORE = "WALMART"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate, br","Connection": "keep-alive"}
        r1 = requests.get(url, headers=headers)
        content = r1.content
        soup=BeautifulSoup(content,features="lxml")
    except Exception as e:  
        print(e)
        sys.exit(1)
    #print(soup)
    table_present = soup.find_all('div', {'class': 'mb1 ph1 pa0-xl bb b--near-white w-25'})
    if table_present is None:
        return EMPTY_LIST
    return parse_all(soup,STORE)
    
def parse_indiamart(url):
    
    STORE = "INDIAMART"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate, br","Connection": "keep-alive"}
        r1 = requests.get(url, headers=headers)
        content = r1.content
        soup=BeautifulSoup(content,features="lxml")
    except Exception as e:  
        print(e)
        sys.exit(1)
    #print(soup)
    table_present = soup.find_all('section', {'class': 'lst_cl prd-card fww brs5 pr bg1 prd-card-mtpl '})
    if table_present is None:
        return EMPTY_LIST
    return parse_all(soup,STORE)

def parse_alibaba(url):
    print(url)
    
    STORE = "ALIBABA"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate, br","Connection": "keep-alive"}
        r1 = requests.get(url, headers=headers)
        content = r1.content
        soup=BeautifulSoup(content,features="lxml")
    except Exception as e:  
        print(e)
        sys.exit(1)
    #print(soup)
    table_present = soup.find('div', {'class': 'list-no-v2-outter J-offer-wrapper'})
    if table_present is None:
        return EMPTY_LIST
    return parse_all(soup,STORE)

def parse_titles(soup,STORE):
    switcher = {
        'AMAZON': parse_title_amazon,
        'FLIPKART': parse_title_flipkart,
        'SHOPCLUES': parse_title_shopclues,
        'WALMART': parse_title_walmart,
	    'INDIAMART': parse_title_indiamart,
        'ALIBABA' : parse_title_alibaba
    }
    # Get the function from switcher dictionary
    func = switcher.get(STORE, lambda: "Store is not supported yet")
    # Execute the function
    titles = func(soup)
    return titles



def parse_images(soup,STORE):
    switcher = {
        'AMAZON': parse_image_amazon,
        'FLIPKART': parse_image_flipkart,
        'SHOPCLUES': parse_image_shopclues,
        'WALMART': parse_image_walmart,
        'INDIAMART': parse_image_indiamart,
        'ALIBABA' : parse_image_alibaba
    }
    # Get the function from switcher dictionary
    func = switcher.get(STORE, lambda: "Store is not supported yet")
    # Execute the function
    images = func(soup)
    return images


def parse_prices(soup,STORE):
    switcher = {
        'AMAZON': parse_price_amazon,
        'FLIPKART': parse_price_flipkart,
        'SHOPCLUES': parse_price_shopclues,
        'WALMART': parse_price_walmart,
        'INDIAMART': parse_price_indiamart,
        'ALIBABA' : parse_price_alibaba
    }
    # Get the function from switcher dictionary
    func = switcher.get(STORE, lambda: "Store is not supported yet")
    # Execute the function
    images = func(soup)
    return images


def parse_product_urls(soup,STORE):
    switcher = {
        'AMAZON': parse_url_amazon,
        'FLIPKART': parse_url_flipkart,
        'SHOPCLUES': parse_url_shopclues,
        'WALMART': parse_url_walmart,
        'INDIAMART': parse_url_indiamart,
        'ALIBABA' : parse_url_alibaba
    }
    # Get the function from switcher dictionary
    func = switcher.get(STORE, lambda: "Store is not supported yet")
    # Execute the function
    urls = func(soup)
    return urls
def parse_product_ratings(soup, STORE):
    switcher = {
        'AMAZON': parse_rating_amazon,
        'FLIPKART': parse_rating_flipkart,
        'SHOPCLUES': parse_rating_shopclues,
        'WALMART': parse_rating_walmart,
        'INDIAMART': parse_rating_indiamart,
        'ALIBABA': parse_rating_alibaba
    }
    # Get the function from the switcher dictionary
    func = switcher.get(STORE, lambda: "Store is not supported yet")
    # Execute the function
    ratings = func(soup)
    return ratings


if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=5000)

