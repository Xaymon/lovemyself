from flask import Flask, render_template, request, redirect, url_for, session, jsonify, json
import psycopg2
from app import app
from kk_con import *
from datetime import datetime

@app.route('/service_price')
def service_price():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = """SELECT a.service_id, a.service_name, a.sc_id, a.wt_id, TO_CHAR(price, '999G999'), b.unit_clothes, b.sc_desc, c.wt_name FROM public.service_detail a 
                    LEFT JOIN service_category b ON a.sc_id=b.sc_id 
                    LEFT JOIN water_type c ON a.wt_id =c.wt_id"""
            cur.execute(sql)
            rate_trans = cur.fetchall()

            curp = gobal.con.cursor()
            sql_p = "SELECT wt_id, wt_name FROM water_type ORDER BY wt_id"
            curp.execute(sql_p)
            water_type = curp.fetchall()

            curs = gobal.con.cursor()
            sql_s = "SELECT sc_id, sc_desc FROM service_category order by sc_id"
            curs.execute(sql_s)
            sv_c = curs.fetchall()

            dateTimeObj = datetime.now()
            doc_date = dateTimeObj.strftime("%Y-%m-%d")
            sql_d = """SELECT max(SPLIT_PART(service_id,'-', 2))::int from service_detail"""
            cur_d = gobal.con.cursor()
            cur_d.execute(sql_d)
            bil_no = cur_d.fetchone()
            doc_no = ''
            if bil_no[0] == None:
                doc_no = 'SV-100001'
            else:
                doc = bil_no[0]
                a = doc+1
                doc_no = "SV-"+str(a)
            doc_no = doc_no
            
            gobal.con.commit()
            return render_template('service/price.html', sv_c=sv_c, rate_trans=rate_trans,water_type=water_type, doc_date = doc_date, doc_no = doc_no, user=session['name'], roles = session['roles'])

@app.route('/save_service_price', methods=['POST'])
def save_service_price():
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            sql = """INSERT INTO service_detail(
                         service_id, service_name, price, wt_id, sc_id)
                         VALUES(%s,%s,%s,%s,%s)
                  """
            
            service_id = request.form['service_id']
            service_name = request.form['service_name']
            price = request.form['price']
            wt_id = request.form['wt_id']
            sc_id = request.form['sc_id']

            data = (service_id, service_name, price, wt_id, sc_id)
            cur.execute(sql, (data))
            gobal.con.commit()
            return redirect(url_for('service_price'))

@app.route('/update_service_price/<string:id>', methods=['POST'])
def update_service_price(id):
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:    
            service_id = request.form['service_id']
            service_name = request.form['service_name']
            price = request.form['price']
            wt_id = request.form['wt_id']
            sc_id = request.form['sc_id']

            cur.execute('UPDATE service_detail SET service_id=%s, service_name=%s, price=%s, wt_id=%s, sc_id=%s WHERE service_id=%s',
                        (service_id, service_name, price, wt_id, sc_id, (id,)))
            gobal.con.commit()
            return redirect(url_for('service_price'))

@app.route('/delete_service_price/<string:id>')
def delete_service_price(id):
    if not session.get("name"):
        return redirect("/login")
    else:
        cur = gobal.con.cursor()
        sql = "DELETE FROM service_detail WHERE service_id=%s"
        cur.execute(sql, (id,))
        gobal.con.commit()
        return redirect(url_for('service_price'))

@app.route("/unitpredict/<id>")
def unitpredict(id):
    sql_unit = "SELECT unit_clothes FROM service_category WHERE sc_id=%s"
    curc = gobal.con.cursor()
    curc.execute(sql_unit, (id,))
    unit = curc.fetchall()
    return jsonify({'unitlist': unit})

@app.route("/pricepredict/<id>")
def pricepredict(id):
    sql = "SELECT price FROM service_detail WHERE service_id=%s"
    cur = gobal.con.cursor()
    cur.execute(sql, (id,))
    price = cur.fetchall()
    return jsonify({'pricelist': price})

@app.route('/home_service')
def home_service():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            # cur = gobal.con.cursor()
            # sql = """SELECT a.service_id, a.service_name, b.sc_desc, c.wt_name, price, b.unit_clothes, b.sc_desc, c.wt_name FROM public.service_detail a 
            #         LEFT JOIN service_category b ON a.sc_id=b.sc_id 
            #         LEFT JOIN water_type c ON a.wt_id =c.wt_id"""
            # cur.execute(sql)
            # rate_trans = cur.fetchall()

            curc = gobal.con.cursor()
            sqlc = """ SELECT bill_date, b.bill_id, CASE WHEN c.cust_name IS NULL THEN b.cust_id ELSE c.cust_name END as custname, e.emp_name ,(SELECT sum(qty) FROM bill_detail WHERE bill_id=b.bill_id), (SELECT TO_CHAR(sum(pay_rc),'999,999,999,999') FROM bill_detail WHERE bill_id=b.bill_id),
                     status_laundry FROM bill b
                     LEFT JOIN employee e ON e.emp_id = b.emp_id
                     LEFT JOIN customer c ON c.cust_id = b.cust_id
                     ORDER BY b.bill_id
                    """
            curc.execute(sqlc)
            home_list = curc.fetchall()
            return render_template('service/home_service.html', home_list=home_list, user=session['name'], roles = session['roles'])
@app.route('/delete_home_service/<string:id>')
def delete_home_service(id):
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            # cur = gobal.con.cursor()
            # sql = """SELECT a.service_id, a.service_name, b.sc_desc, c.wt_name, price, b.unit_clothes, b.sc_desc, c.wt_name FROM public.service_detail a 
            #         LEFT JOIN service_category b ON a.sc_id=b.sc_id 
            #         LEFT JOIN water_type c ON a.wt_id =c.wt_id"""
            # cur.execute(sql)
            # rate_trans = cur.fetchall()

            cur = gobal.con.cursor()
            sql = "DELETE FROM bill_detail WHERE bill_id=%s"
            cur.execute(sql, (id,))
            sqlb = "DELETE FROM bill WHERE bill_id=%s"
            cur.execute(sqlb, (id,))
            return redirect(url_for('home_service'))

@app.route('/home_servicing')
def home_servicing():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            # cur = gobal.con.cursor()
            # sql = """SELECT a.service_id, a.service_name, b.sc_desc, c.wt_name, price, b.unit_clothes, b.sc_desc, c.wt_name FROM public.service_detail a 
            #         LEFT JOIN service_category b ON a.sc_id=b.sc_id 
            #         LEFT JOIN water_type c ON a.wt_id =c.wt_id"""
            # cur.execute(sql)
            # rate_trans = cur.fetchall()

            curc = gobal.con.cursor()
            sqlc = """ SELECT bill_date, b.bill_id, CASE WHEN c.cust_name IS NULL THEN b.cust_id ELSE c.cust_name END as custname, e.emp_name ,(SELECT sum(qty) FROM bill_detail WHERE bill_id=b.bill_id), (SELECT TO_CHAR(sum(pay_rc),'999G999G999G999') FROM bill_detail WHERE bill_id=b.bill_id),
                     status_laundry FROM bill b
                     LEFT JOIN employee e ON e.emp_id = b.emp_id
                     LEFT JOIN customer c ON c.cust_id = b.cust_id
                     WHERE status_laundry=0
                    """
            curc.execute(sqlc)
            home_list = curc.fetchall()
            return render_template('service/home_servicing.html', home_list=home_list, user=session['name'], roles = session['roles'])

@app.route('/print_bill/<string:id>', methods=['GET'])
def print_bill(id):
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = """SELECT b.bill_date, b.bill_id, b.cust_id, d.cust_name, b.emp_id, e.emp_name, CONCAT(cust_village, ', ', cust_district, ', ', cust_province) address, d.cust_tel, remark FROM bill_detail bd
                    LEFT JOIN bill b ON b.bill_id = bd.bill_id
                    LEFT JOIN employee e ON e.emp_id = b.emp_id
                    LEFT JOIN customer d ON d.cust_id = b.cust_id
                    LEFT JOIN province p ON p.prov_code=e.emp_province
                    LEFT JOIN city c ON c.city_code=e.emp_district
                    LEFT JOIN village v ON v.village_code=e.emp_village 
                    WHERE b.bill_id = %s"""
            # sql = """SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id, ot.remark FROM order_detail od
            #          LEFT JOIN order_table ot ON ot.order_id = od.order_id 
            #          LEFT JOIN supplier s ON s.sup_id = ot.sup_id
            #          WHERE ot.order_id = %s"""
            # SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id FROM order_detail od
            #         LEFT JOIN order_table ot ON ot.order_id = od.order_id WHERE ot.order_id is NOT NULL
            cur.execute(sql, (id,))
            show = cur.fetchone()

            curdt = gobal.con.cursor()
            sqldt = """SELECT row_number() OVER () as NO, bd.bill_id, s.service_name, basket_no, qty, to_char(s.price,'999G999G999G999'), to_char(pay_rc,'999G999G999G999') FROM bill_detail bd
                    LEFT JOIN bill b ON bd.bill_id = b.bill_id
                    LEFT JOIN service_detail s ON s.service_id = bd.service_id
                    WHERE b.bill_id = %s"""
            curdt.execute(sqldt, (id,))
            detail_list = curdt.fetchall()

            # ສະເເດງລວມທັງໝົດ
            sql_sum = """SELECT to_char(sum(pay_rc),'999G999G999G999') FROM bill_detail bd
                    LEFT JOIN bill b ON bd.bill_id = b.bill_id
                    LEFT JOIN service_detail s ON s.service_id = bd.service_id
                    WHERE b.bill_id = %s"""
            cur.execute(sql_sum, (id,))
            sum_amount = cur.fetchall()
            return render_template('service/bill.html', show = show, detail_list = detail_list, sum_amount = sum_amount, user=session['name'], roles = session['roles'])

@app.route('/service_desc', methods=["POST", "GET"])
def service_desc():
        if not session.get("name"):
            return redirect("/login")
        else:
            #current date
            dateTimeObj = datetime.now()
            doc_date = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
            doc_time = dateTimeObj.strftime("%H:%M:%S")
            sql_d = """SELECT
                    CASE WHEN COUNT(bill_id) = 0 
                        THEN 'BILL-000001'::text 
                        WHEN COUNT(bill_id) > 0 
                        THEN CONCAT('BILL-',LPAD((RIGHT(MAX(bill_id),6)::integer+1)::text, 6, 0::text) )
                    END as bill_id
                    FROM bill"""
            cur_d = gobal.con.cursor()
            cur_d.execute(sql_d)
            bill_no = cur_d.fetchone()
            doc_no = str(bill_no)
            doc_no = doc_no[2:13]

            session["bill_id"] = doc_no

            curc = gobal.con.cursor()
            sqlc = """SELECT cust_id, cust_name, CONCAT(cust_village, ', ', cust_district, ', ', cust_province) address, cust_tel, cust_gender, cust_bd, cust_province, cust_district, cust_village,
                    cust_province, cust_district, cust_village FROM customer e
                    LEFT JOIN province p ON p.prov_code=e.cust_province
                    LEFT JOIN city c ON c.city_code=e.cust_district
                    LEFT JOIN village v ON v.village_code=e.cust_village
                    ORDER BY cust_id
                    """
            curc.execute(sqlc)
            cust_list = curc.fetchall()

            curem = gobal.con.cursor()
            sqlem = """SELECT emp_id, emp_name, CONCAT(emp_village, ', ', emp_district, ', ', emp_province) address, emp_tel, emp_gender, emp_bd, emp_province, emp_district, emp_village,
                    emp_province, emp_district, emp_village FROM employee e 
                    LEFT JOIN province p ON p.prov_code=e.emp_province
                    LEFT JOIN city c ON c.city_code=e.emp_district
                    LEFT JOIN village v ON v.village_code=e.emp_village 
                    ORDER BY emp_id
                    """
            curem.execute(sqlem)
            emp_list = curem.fetchall()

            curdt = gobal.con.cursor()
            sqldt = """SELECT row_number() OVER () as NO, bd.bill_id, s.service_name, basket_no, qty, s.price, pay_rc FROM bill_detail bd
                    LEFT JOIN bill b ON bd.bill_id = b.bill_id
                    LEFT JOIN service_detail s ON s.service_id = bd.service_id
                    WHERE b.bill_id is NULL"""
            curdt.execute(sqldt)
            detail_list = curdt.fetchall()

            cursv = gobal.con.cursor()
            sqlsv = """SELECT service_id, service_name, price FROM public.service_detail ORDER BY service_id"""
            cursv.execute(sqlsv)
            sv_list = cursv.fetchall()
            sv_one = cursv.fetchone()

            curp = gobal.con.cursor()
            sql_p = "SELECT wt_id, wt_name FROM water_type ORDER BY wt_id"
            curp.execute(sql_p)
            water_type = curp.fetchall()

            curs = gobal.con.cursor()
            sql_s = "SELECT sc_id, sc_desc FROM service_category ORDER BY sc_id"
            curs.execute(sql_s)
            sv_c = curs.fetchall()

            cursum = gobal.con.cursor()
            sql_sum = """SELECT sum(pay_rc) FROM bill_detail bd
                    LEFT JOIN bill b ON bd.bill_id = b.bill_id
                    LEFT JOIN service_detail s ON s.service_id = bd.service_id
                    WHERE b.bill_id is NULL"""
            cursum.execute(sql_sum)
            sum_amount = cursum.fetchall()
            gobal.con.commit()
            return render_template('service/service_desc.html', sv_c=sv_c,water_type=water_type, doc_date=doc_date, doc_time=doc_time, doc_no=doc_no, cust_list=cust_list, emp_list=emp_list, sv_list=sv_list, sv_one=sv_one, detail_list=detail_list, sum_amount=sum_amount, user=session['name'], roles = session['roles'], bill_id = session["bill_id"])

@app.route('/save_bill_desc', methods=['POST'])
def save_bill_desc():
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:

            sql_b = """INSERT INTO bill(
                         bill_id, bill_date, remark, emp_id, cust_id, status_laundry)
                         VALUES(%s,%s,%s,%s,%s, '0')
                  """
            
            bill_id = request.form['bill_id']
            bill_date = request.form['bill_date']
            remark = request.form['remark']
            emp_id = request.form['emp_id']
            cust_id = request.form['cust_id']

            bill = (bill_id, bill_date, remark, emp_id, cust_id)
            cur.execute(sql_b, (bill))
            gobal.con.commit()
            return redirect(url_for('home_service'))

# ກົດປຸ່ມຍົກເລີກເເລ້ວລົບ​ຂໍ້​ມູນ​ຢູ່ bill_detail ເເລະ ກັບໄປໜ້າ home_service
@app.route('/back_button_service_desc')
def back_button_service_desc():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = "DELETE FROM bill_detail WHERE bill_id=%s"
            cur.execute(sql, (session["bill_id"],))
        return redirect(url_for('home_service'))

@app.route('/save_bill_detail', methods=['POST'])
def save_bill_detail():
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:

            sql = """INSERT INTO bill_detail(
                         bill_id, basket_no, pay_rc, qty, service_id)
                         VALUES(%s,%s,%s,%s,%s)
                  """
            
            bill_id = request.form['bill_id']
            service_id = request.form['service_id']
            basket_no = request.form['basket_no']
            pay_rc = request.form['pay_rc']
            qty = request.form['qty']

            data = (bill_id, basket_no, pay_rc, qty, service_id)
            cur.execute(sql, (data))
            gobal.con.commit()
            return redirect(url_for('service_desc'))

@app.route('/service_about/<string:id>', methods=["POST", "GET"])
def service_about(id):
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            if request.method == 'GET':
            #ສະ​ແດງ​ລາຍ​ການ​ໃນ​ໜ້າ​ອໍ​ເດີ້
                cur = gobal.con.cursor()
                sql = """SELECT b.bill_date, b.bill_id, c.cust_id, CASE WHEN c.cust_name IS NULL THEN b.cust_id ELSE c.cust_name END as custname, b.emp_id, e.emp_name, remark FROM bill_detail bd
                        LEFT JOIN bill b ON b.bill_id = bd.bill_id
                        LEFT JOIN employee e ON e.emp_id = b.emp_id
                        LEFT JOIN customer c ON c.cust_id = b.cust_id
                        WHERE b.bill_id = %s"""
                # sql = """SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id, ot.remark FROM order_detail od
                #          LEFT JOIN order_table ot ON ot.order_id = od.order_id 
                #          LEFT JOIN supplier s ON s.sup_id = ot.sup_id
                #          WHERE ot.order_id = %s"""
                # SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id FROM order_detail od
                #         LEFT JOIN order_table ot ON ot.order_id = od.order_id WHERE ot.order_id is NOT NULL
                cur.execute(sql, (id,))
                show = cur.fetchone()

                curdt = gobal.con.cursor()
                sqldt = """SELECT row_number() OVER () as NO, bd.bill_id, s.service_name, basket_no, qty, s.price, pay_rc FROM bill_detail bd
                        LEFT JOIN bill b ON bd.bill_id = b.bill_id
                        LEFT JOIN service_detail s ON s.service_id = bd.service_id
                        WHERE b.bill_id = %s"""
                curdt.execute(sqldt, (id,))
                detail_list = curdt.fetchall()

                # ສະເເດງລວມທັງໝົດ
                sql_sum = """SELECT TO_CHAR(sum(pay_rc), '999,999,999') FROM bill_detail bd
                        LEFT JOIN bill b ON bd.bill_id = b.bill_id
                        LEFT JOIN service_detail s ON s.service_id = bd.service_id
                        WHERE b.bill_id = %s"""
                cur.execute(sql_sum, (id,))
                sum_amount = cur.fetchall()
                return render_template('service/service_about.html', show = show, detail_list = detail_list, sum_amount = sum_amount, user=session['name'], roles = session['roles'])
            
            if request.method == 'POST':

                cursor = gobal.con.cursor()
                sql_up = """UPDATE bill
                        SET status_laundry = 1
                        WHERE bill_id = %s"""
                cursor.execute(sql_up, (id,))
                gobal.con.commit()
                return redirect(url_for('home_service'))
                # return render_template('service/home_service.html', user=session.get("roles"))

# @app.route('/service')
# def service():
#     with gobal.con:
#         if not session.get("name"):
#             return redirect("/login")
#         else:
#             # cur = gobal.con.cursor()
#             # sql = """SELECT a.service_id, a.service_name, b.sc_desc, c.wt_name, price, b.unit_clothes, b.sc_desc, c.wt_name FROM public.service_detail a 
#             #         LEFT JOIN service_category b ON a.sc_id=b.sc_id 
#             #         LEFT JOIN water_type c ON a.wt_id =c.wt_id"""
#             # cur.execute(sql)
#             # rate_trans = cur.fetchall()

#             curc = gobal.con.cursor()
#             sqlc = """SELECT cust_id, cust_name, CONCAT(v.village_name, ', ', c.city_name, ', ', p.prov_name) address, cust_tel, cust_gender, cust_bd, p.prov_name, c.city_name, v.village_name,
#                     cust_province, cust_district, cust_village FROM customer e
#                     LEFT JOIN province p ON p.prov_code=e.cust_province
#                     LEFT JOIN city c ON c.city_code=e.cust_district
#                     LEFT JOIN village v ON v.village_code=e.cust_village
#                     ORDER BY cust_id
#                     """
#             curc.execute(sqlc)
#             cust_list = curc.fetchall()

#             curem = gobal.con.cursor()
#             sqlem = """SELECT emp_id, emp_name, CONCAT(v.village_name, ', ', c.city_name, ', ', p.prov_name) address, emp_tel, emp_gender, emp_bd, p.prov_name, c.city_name, v.village_name,
#                     emp_province, emp_district, emp_village FROM employee e 
#                     LEFT JOIN province p ON p.prov_code=e.emp_province
#                     LEFT JOIN city c ON c.city_code=e.emp_district
#                     LEFT JOIN village v ON v.village_code=e.emp_village 
#                     ORDER BY emp_id
#                     """
#             curem.execute(sqlem)
#             emp_list = curem.fetchall()

#             cursv = gobal.con.cursor()
#             sqlsv = """SELECT service_id, service_name, price FROM public.service_detail ORDER BY service_id"""
#             cursv.execute(sqlsv)
#             sv_list = cursv.fetchall()
#             sv_one = cursv.fetchone()

#             curp = gobal.con.cursor()
#             sql_p = "SELECT wt_id, wt_name FROM water_type ORDER BY wt_id"
#             curp.execute(sql_p)
#             water_type = curp.fetchall()

#             curs = gobal.con.cursor()
#             sql_s = "SELECT sc_id, sc_desc FROM service_category ORDER BY sc_id"
#             curs.execute(sql_s)
#             sv_c = curs.fetchall()

#             dateTimeObj = datetime.now()
#             doc_date = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
#             sql_d = """SELECT
#                     CASE WHEN COUNT(bill_id) = 0 
#                         THEN 'BILL-000001'::text 
#                         WHEN COUNT(bill_id) > 0 
#                         THEN CONCAT('BILL-',LPAD((RIGHT(MAX(bill_id),6)::integer+1)::text, 6, 0::text) )
#                     END as bill_id
#                     FROM bill"""
#             cur_d = gobal.con.cursor()
#             cur_d.execute(sql_d)
#             bill_no = cur_d.fetchone()
#             doc_no = str(bill_no)
#             doc_no = doc_no[2:13]
#             gobal.con.commit()
#             return render_template('service/service.html', sv_c=sv_c,water_type=water_type, doc_date=doc_date, doc_no=doc_no, cust_list=cust_list, emp_list=emp_list, sv_list=sv_list, sv_one=sv_one, user=session['name'], roles = session['roles'])

# @app.route('/save_service', methods=['POST'])
# def save_service():
#     with gobal.con:
#         cur = gobal.con.cursor()
#         if not session.get("name"):
#             return redirect("/login")
#         else:
#             sql = """INSERT INTO bill_detail(
#                          bill_id, basket_no, pay_rc, qty, service_id, status_laundry)
#                          VALUES(%s,%s,%s,%s,%s, '0')
#                   """
            
#             bill_id = request.form['bill_id']
#             service_id = request.form['service_id']
#             basket_no = request.form['basket_no']
#             pay_rc = request.form['pay_rc']
#             qty = request.form['qty']

#             data = (bill_id, basket_no, pay_rc, qty, service_id)
#             cur.execute(sql, (data))

#             sql_b = """INSERT INTO bill(
#                          bill_id, bill_date, remark, payment, emp_id, cust_id)
#                          VALUES(%s,%s,%s,%s,%s,%s)
#                   """
            
#             bill_id = request.form['bill_id']
#             bill_date = request.form['bill_date']
#             remark = request.form['remark']
#             payment = request.form['payment']
#             emp_id = request.form['emp_id']
#             cust_id = request.form['cust_id']

#             bill = (bill_id, bill_date, remark, payment, emp_id, cust_id)
#             cur.execute(sql_b, (bill))
#             gobal.con.commit()
#             return redirect(url_for('service'))

# @app.route('/update_service/<string:id>', methods=['POST'])
# def update_service(id):
#     with gobal.con:
#         cur = gobal.con.cursor()
#         if not session.get("name"):
#             return redirect("/login")
#         else:    
#             service_id = request.form['service_id']
#             service_name = request.form['service_name']
#             price = request.form['price']
#             wt_id = request.form['wt_id']
#             sc_id = request.form['sc_id']

#             cur.execute('UPDATE service_detail SET service_id=%s, service_name=%s, price=%s, wt_id=%s, sc_id=%s WHERE service_id=%s',
#                         (service_id, service_name, price, wt_id, sc_id, (id,)))
#             gobal.con.commit()
#             return redirect(url_for('service'))

# @app.route('/delete_service/<string:id>')
# def delete_service(id):
#     if not session.get("name"):
#         return redirect("/login")
#     else:
#         cur = gobal.con.cursor()
#         sql = "DELETE FROM service_detail WHERE service_id=%s"
#         cur.execute(sql, (id,))
#         gobal.con.commit()
#         return redirect(url_for('service'))

# @app.route('/bill')
# def bill():
#     with gobal.con:
#         if not session.get("name"):
#             return redirect("/login")
#         else:
#             dateTimeObj = datetime.now()
#             timestampStr = dateTimeObj.strftime("%Y-%m-%d")
#             cur = gobal.con.cursor()
#             sql = """SELECT  to_char(doc_date,'DD-MM-YYY HH24:MI:SS'),doc_no,case when trans_type='0' or trans_type='1' then 'ໂອນ' when trans_type='2' 
#                     then 'ແລກປ່ຽນ' when trans_type='5' then 'ລາຍຮັບອື່ນໆ' when  trans_type='6' then 'ລາຍຈ່າຍອື່ນໆ' when  trans_type='11' then 'ຝາກທະນາຄານ' 
#                     when  trans_type='12' then 'ຖອນຈາກທະນາຄານ'  end as trans_type,
#                     to_char(case when calc_flag='1' then amount_1 else 0 end , '999G999G999G999G999G999D99') as Amount_in, 
#                     to_char(case when calc_flag='-1' then amount_1 else 0 end , '999G999G999G999G999G999D99') as Amount_out, 
#                     to_char(SUM((case when calc_flag='1' then amount_1 else 0 end) - (case when calc_flag='-1' then amount_1 else 0 end))
#                     OVER (ORDER BY roworder ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), '999G999G999G999G999G999G999D99')  as Balance
#                     FROM cb_trans_detail where trans_number='01' and doc_date::date=current_date order by roworder ASC"""
#             cur.execute(sql)
#             kip = cur.fetchall()

#             return render_template('service/bill.html', kip=kip, from_date=timestampStr, to_date=timestampStr,user=session['name'], roles = session['roles'])




