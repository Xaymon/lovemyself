from flask import Flask, render_template, request, redirect, url_for, session, jsonify, json, flash
from app import app
from kk_con import *
from datetime import datetime
import re
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads/'
 
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
base_path = os.path.abspath(os.path.dirname(__file__))
upload_path = os.path.join(base_path, app.config['UPLOAD_FOLDER'])

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/home')
def home():
    with gobal.con:
        if not 'loggedin' in session:
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = """SELECT ROW_NUMBER() OVER (), a.service_name, b.sc_desc, c.wt_name, to_char(price,'999G999G999G999'), b.unit_clothes, b.sc_desc, c.wt_name FROM public.service_detail a 
                    LEFT JOIN service_category b ON a.sc_id=b.sc_id 
                    LEFT JOIN water_type c ON a.wt_id =c.wt_id"""
            cur.execute(sql)
            rate_ = cur.fetchall()

            sql_now = "SELECT TO_CHAR (CURRENT_DATE, 'DD-mm-YYYY')"
            cur.execute(sql_now)
            now = cur.fetchone()

            month = "SELECT EXTRACT(month FROM current_timestamp::timestamp)"
            cur.execute(month)
            month = cur.fetchone()
            
            sql_cust = "SELECT COUNT(cust_id), (SELECT COUNT(cust_id) FROM customer WHERE cust_gender='ຊາຍ'), (SELECT COUNT(cust_id) FROM customer WHERE cust_gender='ຍິງ') FROM customer"
            cur.execute(sql_cust)
            cust = cur.fetchone()
            # male = str(male)
            # male = male[1:2]

            sql_emp = "SELECT COUNT(emp_id), (SELECT COUNT(emp_id) FROM employee WHERE emp_gender='ຊາຍ'), (SELECT COUNT(emp_id) FROM employee WHERE emp_gender='ຍິງ') FROM employee"
            cur.execute(sql_emp)
            emp = cur.fetchone()

            sql_sv = """SELECT COUNT(bill_id)
                    FROM bill
                    WHERE EXTRACT(month FROM bill_date::timestamp) = EXTRACT(month FROM current_timestamp::timestamp)
                                AND EXTRACT(year FROM bill_date::timestamp) = EXTRACT(year FROM current_timestamp::timestamp)"""
            cur.execute(sql_sv)
            sv = cur.fetchone()

            sql_svc = "SELECT COUNT(bill_id) FROM bill WHERE status_laundry=0"
            cur.execute(sql_svc)
            svc = cur.fetchone()

            sql_in = """SELECT TO_CHAR(sum(pay_rc), '999,999,999,999')
                            FROM bill_detail bd
                             LEFT JOIN bill b ON b.bill_id = bd.bill_id
                            WHERE EXTRACT(month FROM bill_date::timestamp) = EXTRACT(month FROM current_timestamp::timestamp)
                                AND EXTRACT(year FROM bill_date::timestamp) = EXTRACT(year FROM current_timestamp::timestamp)"""
            cur.execute(sql_in)
            income = cur.fetchone()

            sql_out = """SELECT TO_CHAR(sum(rc_price), '999,999,999,999') 
                            FROM recieve_detail rd
                             LEFT JOIN recieve r ON r.rc_id = rd.rc_id
                            WHERE EXTRACT(month FROM r.rc_date::timestamp) = EXTRACT(month FROM current_timestamp::timestamp)
                                AND EXTRACT(year FROM r.rc_date::timestamp) = EXTRACT(year FROM current_timestamp::timestamp)"""
            cur.execute(sql_out)
            outcome = cur.fetchone()

            sql_od = """SELECT
                                COUNT(ot.order_id), SUM(od.order_qty)
                            FROM order_detail od
                            LEFT JOIN order_table ot ON ot.order_id = od.order_id
                            WHERE EXTRACT(month FROM ot.order_date::timestamp) = EXTRACT(month FROM current_timestamp::timestamp)
                                AND EXTRACT(year FROM ot.order_date::timestamp) = EXTRACT(year FROM current_timestamp::timestamp)"""
            cur.execute(sql_od)
            order = cur.fetchone()

            sql_od = """SELECT
                                COUNT(ot.order_id), SUM(od.order_qty)
                            FROM order_detail od
                            LEFT JOIN order_table ot ON ot.order_id = od.order_id
                            WHERE EXTRACT(month FROM ot.order_date::timestamp) = EXTRACT(month FROM current_timestamp::timestamp)
                                AND EXTRACT(year FROM ot.order_date::timestamp) = EXTRACT(year FROM current_timestamp::timestamp)"""
            cur.execute(sql_od)
            order = cur.fetchone()

            sql_r = """SELECT
                                COUNT(r.rc_id), SUM(rd.rc_qty)
                            FROM recieve_detail rd
                            LEFT JOIN recieve r ON r.rc_id = rd.rc_id
                            WHERE EXTRACT(month FROM r.rc_date::timestamp) = EXTRACT(month FROM current_timestamp::timestamp)
                                AND EXTRACT(year FROM r.rc_date::timestamp) = EXTRACT(year FROM current_timestamp::timestamp)"""
            cur.execute(sql_r)
            recieve = cur.fetchone()

            sql_wd = """SELECT
                                COUNT(wi.wd_id), SUM(wd.wd_qty)
                            FROM withdraw_detail wd
                            LEFT JOIN withdraw_item wi ON wi.wd_id = wd.wd_id
                            WHERE EXTRACT(month FROM wi.wd_date::timestamp) = EXTRACT(month FROM current_timestamp::timestamp)
                                AND EXTRACT(year FROM wi.wd_date::timestamp) = EXTRACT(year FROM current_timestamp::timestamp)"""
            cur.execute(sql_wd)
            withdraw = cur.fetchone()

            

            # cur = gobal.con.cursor()
            # sql = "SELECT * FROM account"
            # cur.execute(sql)
            # rate_ = cur.fetchall()
            return render_template('index.html', now=now, month=month, rate_=rate_, cust=cust, emp=emp, sv=sv, svc=svc, income=income, outcome=outcome, order=order, recieve=recieve, withdraw=withdraw, user=session['name'], roles = session['roles'])
 
@app.route('/')
def index():
    if not 'loggedin' in session:
        return redirect(url_for('login'))
    return redirect(url_for('home'))

@app.route("/loading")
def loading():
    if not 'loggedin' in session:
        return redirect('login')
    return render_template('loading.html')
    


@app.route('/login')
def loginform():
    return render_template('/login/login.html')

# @app.route("/login", methods=["POST", "GET"])
# def login():
#     if request.method == "POST":
#         user_login = request.form.get('username')
#         pass_login = request.form.get('password')
#         # sql = "SELECT roles FROM public.tb_user where username=%s and password=%s"
#         sql = "SELECT roles FROM account WHERE username=%s and password=%s"
#         cur = gobal.con.cursor()
#         chuer = (user_login, pass_login,)
#         cur.execute(sql, chuer)
#         logii = cur.fetchone()
#         if logii:
#             print(logii[0])
#             session["name"] = request.form.get("username")
#             session["roles"] = logii[0]
#             # msg = 'ບໍ່​ສຳ​ເລັດ'
#             return redirect(url_for('loading'))
#         else:
#             # msg = '​ສຳ​ເລັດ​ແລ້ວ'
#             return redirect(url_for('logout'))
 
@app.route('/login', methods=['GET', 'POST'])
def login():
    with gobal.con:
        cursor = gobal.con.cursor()
    

        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            print(password)
    
    
    
            cursor.execute('SELECT * FROM account WHERE username = %s', (username,))
    
            account = cursor.fetchone()
            print('account:', account)
    
            if account:
                
                
                
                password_rs = account[2]
                
                print(password_rs)
                print(account[0], account[1], account[2], account[3])
        
                if check_password_hash(password_rs, password):
            
                    session['loggedin'] = True
                    session['id'] = account[0]
                    
                    session["name"] = request.form.get("username")
                    session["roles"] = account[3]
                    print(session["roles"])
            
                    return redirect(url_for('loading'))
                else:
            
                    flash('ຊື່/ລະ​ຫັດ​ຜ່ານບໍ່​ຖືກ​ຕ້ອງ')
            else:
                flash('ຊື່/ລະ​ຫັດ​ຜ່ານບໍ່​ຖືກ​ຕ້ອງ')
            return redirect(url_for('loading'))
    
        return redirect(url_for('logout'))
  
@app.route('/register', methods=['GET', 'POST'])
def register():
    with gobal.con:

        #ເລືອກ​ແຂວງ
        cursor = gobal.con.cursor()
        # curp = gobal.con.cursor()
        # sql_p = "SELECT prov_code, prov_name FROM province ORDER BY prov_code"
        # curp.execute(sql_p)
        # pro_list = curp.fetchall()

        dateTimeObj = datetime.now()
        doc_date = dateTimeObj.strftime("%Y-%m-%d")
        sql_d = """SELECT max(SPLIT_PART(cust_id,'-', 2))::int from customer"""
        cur_d = gobal.con.cursor()
        cur_d.execute(sql_d)
        bil_no = cur_d.fetchone()
        doc_no = ''
        if bil_no[0] == None:
            doc_no = 'CUS-100001'
        else:
            doc = bil_no[0]
            a = doc+1
            doc_no = "CUS-"+str(a)
        doc_no = doc_no
    

        if request.method == 'POST' and 'user_name' in request.form and 'user_pwd' in request.form:
    
            cust_id = request.form['cust_id']
            cust_name = request.form['cust_name']
            cust_gender = request.form['cust_gender']
            cust_bd = request.form['cust_bd']
            cust_village = request.form['cust_village']
            cust_district = request.form['cust_district']
            cust_province = request.form['cust_province']
            cust_tel = request.form['cust_tel']
            username = request.form['user_name']
            password = request.form['user_pwd']
        
            _hashed_password = generate_password_hash(password)
    
    
            cursor.execute('SELECT * FROM account WHERE username = %s', (username,))
            account = cursor.fetchone()
            print(account)
    
            if account:
                flash('​ຊື່​ນີ້​ມີ​ຜູ້​ນຳ​ໃຊ້​ແລ້ວ')
            # elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            #     flash('Invalid email address!')
            elif not re.match(r'[A-Za-z0-9]+', username):
                flash('ຊື່ບໍ່​ຖືກ​ຕ້ອງ')
            # elif not username or not password or not email:
            #     flash('Please fill out the form!')
            else:
        
                cursor.execute("INSERT INTO account (username, password, roles) VALUES (%s,%s, 'user')", (username, _hashed_password))

                data = (cust_id, cust_name, cust_gender, cust_bd, cust_village, cust_district, cust_province, cust_tel, username, password)
                sql = """INSERT INTO customer(
                         cust_id, cust_name, cust_gender, cust_bd, cust_village, cust_district, cust_province, cust_tel, user_name, user_pwd)
                         VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                cursor.execute(sql, (data))
                # gobal.con.commit()
                flash('ສະ​ໝັກ​ສະ​ມາຊຶກ​ສຳເລັດ!')
                # return render_template('/login/login.html', user=session.get("name"))
                # return redirect(url_for('login'))
            if 'file' not in request.files:
                # flash('No file part')
                return redirect('/register')
            file = request.files['file']
            if file.filename == '':
                # flash('No image selected for uploading')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # file.save(os.path.join(UPLOAD_FOLDER, filename))
                file.save(os.path.join(upload_path, secure_filename(file.filename)))
                #print('upload_image filename: ' + filename)
                flash('ອັບ​ໂຫລດ​ຮູບ​ສຳ​ເລັດ')
                cursor.execute("UPDATE account SET picname = %s WHERE username = %s", (filename, username))
                # return render_template('register.html', filename=filename)
            else:
                flash('Allowed image types are - png, jpg, jpeg, gif')
                return redirect(request.url)
        elif request.method == 'POST':
            # Form is empty... (no POST data)
            flash('ກະ​ລຸ​ນາ​ຕື່ມ​ຟອ​ມ​ໃຫ້​ຄົບ!')
        # Show registration form with message (if any)
        return render_template('register.html', doc_no=doc_no, doc_date=doc_date)
   
   
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))