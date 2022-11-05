from flask import Flask, render_template, request, redirect, url_for, session, jsonify, json
from app import app
from kk_con import *
from datetime import datetime
from werkzeug.security import generate_password_hash

#customer
@app.route('/customer')
def customer():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = """SELECT cust_id, cust_name, CONCAT(cust_village, ', ', cust_district, ', ', cust_province) address, cust_tel, user_name, user_pwd, cust_gender, cust_bd, 
                    cust_province, cust_district, cust_village
                    FROM customer e
                  """
            cur.execute(sql)
            cust_list = cur.fetchall()

            #ເລືອກ​ແຂວງ
            curp = gobal.con.cursor()
            sql_p = "SELECT prov_code, prov_name FROM province ORDER BY prov_code"
            curp.execute(sql_p)
            pro_list = curp.fetchall()

            #current date
            dateTimeObj = datetime.now()
            doc_date = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
            sql_d = """SELECT
                    CASE WHEN COUNT(cust_id) = 0 
                        THEN 'CUS-000001'::text 
                        WHEN COUNT(cust_id) > 0 
                        THEN CONCAT('CUS-',LPAD((RIGHT(MAX(cust_id),6)::integer+1)::text, 6, 0::text) )
                    END as cust_id
                    FROM customer"""
            cur_d = gobal.con.cursor()
            cur_d.execute(sql_d)
            bill_no = cur_d.fetchone()
            doc_no = str(bill_no)
            doc_no = doc_no[2:12]
            gobal.con.commit()

            return render_template('manage/customer.html', doc_no = doc_no, doc_date = doc_date, cust_list = cust_list, pro_list = pro_list,user=session['name'], roles = session['roles'])

@app.route('/save_customer', methods=['POST'])
def save_customer():
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            sql = """INSERT INTO customer(
                         cust_id, cust_name, cust_gender, cust_bd, cust_village, cust_district, cust_province, cust_tel, user_name, user_pwd)
                         VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                  """
            
            cust_id = request.form['cust_id']
            cust_name = request.form['cust_name']
            cust_gender = request.form['cust_gender']
            cust_bd = request.form['cust_bd']
            cust_village = request.form['cust_village']
            cust_district = request.form['cust_district']
            cust_province = request.form['cust_province']
            cust_tel = request.form['cust_tel']
            user_name = request.form['user_name']
            user_pwd = request.form['user_pwd']
            _hashed_password = generate_password_hash(user_pwd)
            data = (cust_id, cust_name, cust_gender, cust_bd, cust_village, cust_district, cust_province, cust_tel, user_name, _hashed_password)
            cur.execute(sql, (data))

            sql_account = """INSERT INTO account(username, password, roles)
                             VALUES(%s,%s,'user')"""
            account = (user_name, _hashed_password)
            cur.execute(sql_account, account)
            gobal.con.commit()
            return redirect(url_for('customer'))

@app.route('/update_customer/<string:id>', methods=['POST'])
def update_customer(id):
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            cust_id = request.form['cust_id']
            cust_name = request.form['cust_name']
            cust_gender = request.form['cust_gender']
            cust_bd = request.form['cust_bd']
            cust_village = request.form['cust_village']
            cust_district = request.form['cust_district']
            cust_province = request.form['cust_province']
            cust_tel = request.form['cust_tel']
            user_name = request.form['user_name']
            # user_pwd = request.form['user_pwd']
            # _hashed_password = generate_password_hash(user_pwd)

            cur.execute('UPDATE customer SET cust_id=%s, cust_name=%s, cust_gender=%s, cust_bd = %s, cust_village=%s, cust_district=%s, cust_province=%s, cust_tel=%s, user_name=%s WHERE cust_id=%s',
                        (cust_id, cust_name, cust_gender, cust_bd, cust_village, cust_district, cust_province, cust_tel, user_name, (id,)))
            gobal.con.commit()
            return redirect(url_for('customer'))

@app.route('/delete_customer/<string:id>')
def delete_customer(id):
    if not session.get("name"):
        return redirect("/login")
    else:
        cur = gobal.con.cursor()
        sql = "DELETE FROM customer WHERE cust_id=%s"
        cur.execute(sql, (id,))
        gobal.con.commit()
        return redirect(url_for('customer'))

#employee
@app.route('/employee')
def employee():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = """SELECT emp_id, emp_name, CONCAT(emp_village, ', ', emp_district, ', ', emp_province) address, emp_tel, admin_name, admin_pwd, emp_gender, emp_bd,
                    emp_province, emp_district, emp_village FROM employee e
                    """
            cur.execute(sql)
            emp_list = cur.fetchall()

            #ເລືອກ​ແຂວງ
            # curp = gobal.con.cursor()
            # sql_p = "SELECT prov_code, prov_name FROM province ORDER BY prov_code"
            # curp.execute(sql_p)
            # pro_list = curp.fetchall()

            #current date
            dateTimeObj = datetime.now()
            doc_date = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
            sql_d = """SELECT
                    CASE WHEN COUNT(emp_id) = 0 
                        THEN 'EMP-000001'::text 
                        WHEN COUNT(emp_id) > 0 
                        THEN CONCAT('EMP-',LPAD((RIGHT(MAX(emp_id),6)::integer+1)::text, 6, 0::text) )
                    END as emp_id
                    FROM employee"""
            cur_d = gobal.con.cursor()
            cur_d.execute(sql_d)
            bill_no = cur_d.fetchone()
            doc_no = str(bill_no)
            doc_no = doc_no[2:12]
            gobal.con.commit()

            return render_template('manage/employee.html', doc_no = doc_no, doc_date = doc_date, emp_list = emp_list,user=session['name'], roles = session['roles'])

@app.route('/save_employee', methods=['POST'])
def save_employee():
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            sql = """INSERT INTO employee(
                         emp_id, emp_name, emp_gender, emp_bd, emp_village, emp_district, emp_province, emp_tel, admin_name, admin_pwd)
                         VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                  """
            
            emp_id = request.form['emp_id']
            emp_name = request.form['emp_name']
            emp_gender = request.form['emp_gender']
            emp_bd = request.form['emp_bd']
            emp_village = request.form['emp_village']
            emp_district = request.form['emp_district']
            emp_province = request.form['emp_province']
            emp_tel = request.form['emp_tel']
            admin_name = request.form['admin_name']
            admin_pwd = request.form['admin_pwd']
            _hashed_password = generate_password_hash( admin_pwd)
            data = (emp_id, emp_name, emp_gender, emp_bd, emp_village, emp_district, emp_province, emp_tel, admin_name, _hashed_password)
            cur.execute(sql, (data))

            cura = gobal.con.cursor()
            sql_account = """INSERT INTO account(username, password, roles)
                             VALUES(%s,%s,'admin')"""
            account = (admin_name, _hashed_password)
            cura.execute(sql_account, account)
            gobal.con.commit()
            return redirect(url_for('employee'))

@app.route('/update_employee/<string:id>', methods=['POST'])
def update_employee(id):
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            emp_id = request.form['emp_id']
            emp_name = request.form['emp_name']
            emp_gender = request.form['emp_gender']
            emp_bd = request.form['emp_bd']
            emp_village = request.form['emp_village']
            emp_district = request.form['emp_district']
            emp_province = request.form['emp_province']
            emp_tel = request.form['emp_tel']
            admin_name = request.form['admin_name']
            # admin_pwd = request.form['admin_pwd']
            # _hashed_password = generate_password_hash( admin_pwd)

            cur.execute('UPDATE employee SET emp_id=%s, emp_name=%s, emp_gender=%s, emp_bd = %s, emp_village=%s, emp_district=%s, emp_province=%s, emp_tel=%s, admin_name=%s WHERE emp_id=%s',
                        (emp_id, emp_name, emp_gender, emp_bd, emp_village, emp_district, emp_province, emp_tel, admin_name, (id,)))
            gobal.con.commit()
            return redirect(url_for('employee'))

@app.route('/delete_employee/<string:id>')
def delete_employee(id):
    if not session.get("name"):
        return redirect("/login")
    else:
        cur = gobal.con.cursor()
        sql = "DELETE FROM employee WHERE emp_id=%s"
        cur.execute(sql, (id,))
        gobal.con.commit()
        return redirect(url_for('employee'))

#service category
@app.route('/service_category')
def service_category():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = "SELECT sc_id, sc_desc, unit_clothes FROM service_category ORDER BY sc_id"
            cur.execute(sql)
            sc_list = cur.fetchall()

            #current date
            dateTimeObj = datetime.now()
            doc_date = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
            sql_d = """SELECT
                    CASE WHEN COUNT(sc_id) = 0 
                        THEN 'SC-000001'::text 
                        WHEN COUNT(sc_id) > 0 
                        THEN CONCAT('SC-',LPAD((RIGHT(MAX(sc_id),6)::integer+1)::text, 6, 0::text) )
                    END as sc_id
                    FROM service_category"""
            cur_d = gobal.con.cursor()
            cur_d.execute(sql_d)
            bill_no = cur_d.fetchone()
            doc_no = str(bill_no)
            doc_no = doc_no[2:11]
            gobal.con.commit()

            return render_template('manage/service_category.html', doc_date = doc_date, doc_no = doc_no, sc_list = sc_list, user=session['name'], roles = session['roles'])

@app.route('/save_service_category', methods=['POST'])
def save_service_category():
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            sql = """INSERT INTO service_category(
                         sc_id, sc_desc, unit_clothes)
                         VALUES(%s,%s,%s)
                  """
            
            sc_id = request.form['sc_id']
            sc_desc = request.form['​​sc_desc']
            unit_clothes = request.form['unit_clothes']
            data = (sc_id, sc_desc, unit_clothes)
            cur.execute(sql, (data))
            gobal.con.commit()
            return redirect(url_for('service_category'))

@app.route('/update_service_category/<string:id>', methods=['POST'])
def update_service_category(id):
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            sc_id = request.form['sc_id']
            sc_desc = request.form['sc_desc']
            unit_clothes = request.form['unit_clothes']

            cur.execute('UPDATE service_category SET sc_id=%s, sc_desc=%s, unit_clothes=%s WHERE sc_id=%s',
                        (sc_id, sc_desc, unit_clothes, (id,)))
            gobal.con.commit()
            return redirect(url_for('service_category'))

@app.route('/delete_service_category/<string:id>')
def delete_service_category(id):
    if not session.get("name"):
        return redirect("/login")
    else:
        cur = gobal.con.cursor()
        sql = "delete from service_category where sc_id=%s"
        cur.execute(sql, (id,))
        gobal.con.commit()
        return redirect(url_for('service_category'))


#water_type
@app.route('/water_type')
def water_type():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = "SELECT wt_id, wt_name FROM water_type ORDER BY wt_id"
            cur.execute(sql)
            wt_list = cur.fetchall()

            #current date
            dateTimeObj = datetime.now()
            doc_date = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
            sql_d = """SELECT
                    CASE WHEN COUNT(wt_id) = 0 
                        THEN 'WT-01'::text 
                        WHEN COUNT(wt_id) > 0 
                        THEN CONCAT('WT-',LPAD((RIGHT(MAX(wt_id),2)::integer+1)::text, 2, 0::text) )
                    END as wt_id
                    FROM water_type"""
            cur_d = gobal.con.cursor()
            cur_d.execute(sql_d)
            bill_no = cur_d.fetchone()
            doc_no = str(bill_no)
            doc_no = doc_no[2:7]
            gobal.con.commit()

            return render_template('manage/water_type.html', doc_date = doc_date, doc_no = doc_no, wt_list = wt_list, user=session['name'], roles = session['roles'])

@app.route('/save_water_type', methods=['POST'])
def save_water_type():
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            sql = """INSERT INTO water_type(
                         wt_id, wt_name)
                         VALUES(%s,%s)
                  """
            
            wt_id = request.form['wt_id']
            wt_name = request.form['​​wt_name']
            data = (wt_id, wt_name)
            cur.execute(sql, (data))
            gobal.con.commit()
            return redirect(url_for('water_type'))

@app.route('/update_water_type/<string:id>', methods=['POST'])
def update_water_type(id):
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            wt_id = request.form['wt_id']
            wt_name = request.form['​​wt_name']

            cur.execute('UPDATE water_type SET wt_id=%s, wt_name=%s WHERE wt_id=%s',
                        (wt_id, wt_name, (id,)))
            gobal.con.commit()
            return redirect(url_for('water_type'))

@app.route('/delete_water_type/<string:id>')
def delete_water_type(id):
    if not session.get("name"):
        return redirect("/login")
    else:
        cur = gobal.con.cursor()
        sql = "delete from water_type where wt_id=%s"
        cur.execute(sql, (id,))
        gobal.con.commit()
        return redirect(url_for('water_type'))

#supplier
@app.route('/supplier')
def supplier():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = """SELECT sup_id, sup_name, sup_village, sup_district, sup_province, sup_tel, sup_email 
                    FROM supplier s
                    """
            cur.execute(sql)
            supplier_list = cur.fetchall()

            # curv = gobal.con.cursor()
            # sql_v = "SELECT village_code, village_name, city_code FROM village order by village_code"
            # curv.execute(sql_v)
            # vil_list = curv.fetchall()

            #current date
            dateTimeObj = datetime.now()
            doc_date = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
            sql_d = """SELECT
                    CASE WHEN COUNT(sup_id) = 0 
                        THEN 'SUP-000001'::text 
                        WHEN COUNT(sup_id) > 0 
                        THEN CONCAT('SUP-',LPAD((RIGHT(MAX(sup_id),6)::integer+1)::text, 6, 0::text) )
                    END as sup_id
                    FROM supplier"""
            cur_d = gobal.con.cursor()
            cur_d.execute(sql_d)
            bill_no = cur_d.fetchone()
            doc_no = str(bill_no)
            doc_no = doc_no[2:12]
            gobal.con.commit()

            return render_template('manage/supplier.html', doc_date = doc_date, doc_no = doc_no, supplier_list = supplier_list, user=session['name'], roles = session['roles'])

# @app.route("/districtpredict/<id>")
# def districtpredict(id):
#     sql_city = "SELECT city_code, city_name FROM city WHERE prov_code=%s"
#     cur = gobal.con.cursor()
#     cur.execute(sql_city, (id,))
#     city = cur.fetchall()
#     return jsonify({'districtlist': city})

# @app.route("/villagepredict/<id>")
# def villagepredict(id):
#     sql_village = "SELECT village_code, village_name FROM village WHERE city_code=%s"
#     cur = gobal.con.cursor()
#     cur.execute(sql_village, (id,))
#     village = cur.fetchall()
#     return jsonify({'villagelist': village})

@app.route('/save_supplier', methods=['POST'])
def save_supplier():
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            sql = """INSERT INTO supplier(
                         sup_id, sup_name, sup_village, sup_district, sup_province, sup_tel, sup_email)
                         VALUES(%s,%s,%s,%s,%s,%s,%s)
                  """
            
            sup_id = request.form[sup_id]
            sup_name = request.form['sup_name']
            sup_village = request.form['sup_village']
            sup_district = request.form['sup_district']
            sup_province = request.form['sup_province']
            sup_tel = request.form['sup_tel']
            sup_email = request.form['sup_email']
            data = (sup_id, sup_name, sup_village, sup_district, sup_province, sup_tel, sup_email)
            cur.execute(sql, (data))
            gobal.con.commit()
            return redirect(url_for('supplier'))

@app.route('/update_supplier/<string:id>', methods=['POST'])
def update_supplier(id):
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            sup_id = request.form['sup_id']
            sup_name = request.form['sup_name']
            sup_village = request.form['sup_village']
            sup_district = request.form['sup_district']
            sup_province = request.form['sup_province']
            sup_tel = request.form['sup_tel']
            sup_email = request.form['sup_email']

            cur.execute('UPDATE supplier SET sup_id=%s, sup_name=%s, sup_village=%s, sup_district=%s, sup_province=%s, sup_tel=%s, sup_email=%s WHERE sup_id=%s',
                        (sup_id, sup_name, sup_village, sup_district, sup_province, sup_tel, sup_email, (id,)))
            gobal.con.commit()
            return redirect(url_for('supplier'))

@app.route('/delete_supplier/<string:id>')
def delete_supplier(id):
    if not session.get("name"):
        return redirect("/login")
    else:
        cur = gobal.con.cursor()
        sql = "delete from supplier where sup_id=%s"
        cur.execute(sql, (id,))
        gobal.con.commit()
        return redirect(url_for('supplier'))

#product
@app.route('/product')
def product():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = "SELECT p_id, p_name, to_char(p_price, '999,999'), p_qty FROM product ORDER BY p_id"
            cur.execute(sql)
            sc_list = cur.fetchall()

            #current date
            dateTimeObj = datetime.now()
            doc_date = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
            sql_d = """SELECT
                    CASE WHEN COUNT(p_id) = 0 
                        THEN 'PD-000001'::text 
                        WHEN COUNT(p_id) > 0 
                        THEN CONCAT('PD-',LPAD((RIGHT(MAX(p_id),6)::integer+1)::text, 6, 0::text) )
                    END as p_id
                    FROM product"""
            cur_d = gobal.con.cursor()
            cur_d.execute(sql_d)
            bill_no = cur_d.fetchone()
            doc_no = str(bill_no)
            doc_no = doc_no[2:11]
            gobal.con.commit()

            return render_template('manage/product.html', doc_date = doc_date, doc_no = doc_no, sc_list = sc_list, user=session['name'], roles = session['roles'])

@app.route('/save_product', methods=['POST'])
def save_product():
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            sql = """INSERT INTO product(
                         p_id, p_name, p_price, p_qty)
                         VALUES(%s,%s,%s, '0')
                  """
            
            p_id = request.form['p_id']
            p_name = request.form['​​p_name']
            p_price = request.form['p_price']
            data = (p_id, p_name, p_price)
            cur.execute(sql, (data))
            gobal.con.commit()
            return redirect(url_for('product'))

@app.route('/update_product/<string:id>', methods=['POST'])
def update_product(id):
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            p_id = request.form['p_id']
            p_name = request.form['​​p_name']
            p_price = request.form['p_price']

            cur.execute('UPDATE product SET p_id=%s, p_name=%s, p_price=%s WHERE p_id=%s',
                        (p_id, p_name, p_price, (id,)))
            gobal.con.commit()
            return redirect(url_for('product'))

@app.route('/delete_product/<string:id>')
def delete_product(id):
    if not session.get("name"):
        return redirect("/login")
    else:
        cur = gobal.con.cursor()
        sql = "delete from product where p_id=%s"
        cur.execute(sql, (id,))
        gobal.con.commit()
        return redirect(url_for('product'))