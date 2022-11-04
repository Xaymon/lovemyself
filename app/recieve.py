from unicodedata import category
from flask import Flask, render_template, request, redirect, request_tearing_down, url_for, session, jsonify, json
from psycopg import Cursor
import psycopg2
from app import app
from kk_con import *
from datetime import datetime

#recieve
@app.route('/recieve')
def recieve():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            #ສະ​ແດງ​ລາຍ​ການ​ໃນ​ໜ້າ​ອໍ​ເດີ້
            cur = gobal.con.cursor()
            sql = """SELECT rc_date, r.rc_id, s.sup_name ,remark,(SELECT sum(rc_qty) FROM recieve_detail rd WHERE rc_id=r.rc_id), r.order_id FROM recieve r
                     LEFT JOIN supplier s ON s.sup_id = r.sup_id"""
            # SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id FROM order_detail od
            #         LEFT JOIN order_table ot ON ot.order_id = od.order_id WHERE ot.order_id is NOT NULL
            cur.execute(sql)
            rc_list = cur.fetchall()


            sql = """SELECT order_date, ot.order_id, s.sup_name ,remark,(SELECT sum(order_qty) FROM order_detail WHERE order_id=ot.order_id) FROM order_table ot
                     LEFT JOIN supplier s ON s.sup_id = ot.sup_id"""
            cur.execute(sql)
            od_list = cur.fetchall()

            # curshow = gobal.con.cursor()
            # sqlshow = """SELECT ot.order_date, od.order_id, ot.sup_id, s.sup_name, ot.remark, od.order_qty FROM order_detail od
            #          LEFT JOIN order_table ot ON ot.order_id = od.order_id 
            #          LEFT JOIN supplier s ON s.sup_id = ot.sup_id
            #          WHERE ot.order_id is NOT NULL"""
            # SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id FROM order_detail od
            #         LEFT JOIN order_table ot ON ot.order_id = od.order_id WHERE ot.order_id is NOT NULL
            # curshow.execute(sqlshow)
            # show = curshow.fetchone()

            cursp = gobal.con.cursor()
            sqlsp = """SELECT s.sup_id, s.sup_name, CONCAT(sup_village, ', ', sup_district, ', ', sup_province) address, sup_tel, sup_email FROM supplier s
                    ORDER BY sup_id"""
            cursp.execute(sqlsp)
            sp_list = cursp.fetchall()
            gobal.con.commit()
            return render_template('order & withdraw/recieve.html', od_list = od_list, rc_list = rc_list, sp_list = sp_list, user=session['name'], roles = session['roles'])

#recieve_about ສະແດງລາຍລະອຽດຕາມລະຫັດ order_id
@app.route('/recieve_about/<string:id>', methods=["POST", "GET"])
def recieve_about(id):
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            #ສະ​ແດງ​ລາຍ​ການ​ໃນ​ໜ້າ​ອໍ​ເດີ້
            cur = gobal.con.cursor()
            sql = """SELECT r.rc_date, rd.rc_id, r.sup_id, s.sup_name, remark FROM recieve_detail rd
                    LEFT JOIN recieve r ON r.rc_id = rd.rc_id
                    LEFT JOIN supplier s ON s.sup_id = r.sup_id
                    WHERE r.rc_id = %s"""
            # sql = """SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id, ot.remark FROM order_detail od
            #          LEFT JOIN order_table ot ON ot.order_id = od.order_id 
            #          LEFT JOIN supplier s ON s.sup_id = ot.sup_id
            #          WHERE ot.order_id = %s"""
            # SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id FROM order_detail od
            #         LEFT JOIN order_table ot ON ot.order_id = od.order_id WHERE ot.order_id is NOT NULL
            cur.execute(sql, (id,))
            show = cur.fetchone()

            curdt = gobal.con.cursor()
            sqldt = """SELECT row_number() OVER () as NO, p.p_id, p_name, rd.rc_qty, p_price, p_price * rd.rc_qty FROM recieve_detail rd
                    LEFT JOIN product p ON p.p_id = rd.p_id 
                    LEFT JOIN recieve r ON r.rc_id = rd.rc_id 
                    WHERE rd.rc_id  = %s"""
            curdt.execute(sqldt, (id,))
            detail_list = curdt.fetchall()

            # ສະເເດງລວມທັງໝົດ
            sql_sum = """SELECT sum(p_price * rd.rc_qty) FROM recieve_detail rd
                    LEFT JOIN product p ON p.p_id = rd.p_id 
                    LEFT JOIN recieve r ON r.rc_id = rd.rc_id 
                     WHERE rd.rc_id  = %s"""
            cur.execute(sql_sum, (id,))
            sum_amount = cur.fetchall()
            gobal.con.commit()
            return render_template('order & withdraw/recieve_about.html', show = show, detail_list = detail_list, sum_amount = sum_amount, user=session['name'], roles = session['roles'])

@app.route('/save_recieve', methods=['POST'])
def save_recieve():
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            sql = """INSERT INTO recieve(
                         p_id, p_name, p_price)
                         VALUES(%s,%s,%s)
                  """
            
            p_id = request.form['p_id']
            p_name = request.form['​​p_name']
            p_price = request.form['p_price']
            data = (p_id, p_name, p_price)
            cur.execute(sql, (data))
            gobal.con.commit()
            return redirect(url_for('recieve'))

@app.route('/update_recieve/<string:id>', methods=['POST'])
def update_recieve(id):
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            p_id = request.form['p_id']
            p_name = request.form['​​p_name']
            p_price = request.form['p_price']

            cur.execute('UPDATE recieve SET p_id=%s, p_name=%s, p_price=%s WHERE p_id=%s',
                        (p_id, p_name, p_price, (id,)))
            gobal.con.commit()
            return redirect(url_for('recieve'))

@app.route('/delete_recieve/<string:id>')
def delete_recieve(id):
    if not session.get("name"):
        return redirect("/login")
    else:
        cur = gobal.con.cursor()
        up_stock = """UPDATE product AS p 
                    SET p_qty = p.p_qty-rd.rc_qty 
                    FROM 
                        (SELECT p_id, rc_qty
                          FROM recieve_detail WHERE rc_id = %s) AS rd
                    WHERE 
                         p.p_id=rd.p_id"""
        stock = (id,)
        cur.execute(up_stock, stock)
        
        sql = "DELETE FROM recieve WHERE rc_id=%s"
        cur.execute(sql, (id,))
        cursor = gobal.con.cursor()
        sql2 = "DELETE FROM recieve_detail WHERE rc_id=%s"
        cursor.execute(sql2, (id,))
        gobal.con.commit()
        return redirect(url_for('recieve'))

#order_desc
# @app.route('/order_desc/<string:id>',methods=['GET'])
# def order_desc(id):
#         if not session.get("name"):
#             return redirect("/login")
#         else:
#             cur = gobal.con.cursor()
#             sql = """SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id FROM order_detail od
#                     LEFT JOIN order_table ot ON ot.order_id = od.order_id"""
#             cur.execute(sql)
#             sc_list = cur.fetchall()

#             curdt = gobal.con.cursor()
#             sqldt = """SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id FROM order_detail od
#                     LEFT JOIN order_table ot ON ot.order_id = od.order_id WHERE ot.sup_id = %s"""
#             curdt.execute(sqldt,(id,))
#             detail_list = curdt.fetchall()

#             cursp = gobal.con.cursor()
#             sqlsp = "SELECT sup_id, sup_name FROM supplier WHERE sup_id = %s"
#             cursp.execute(sqlsp,(id,))
#             sp = cursp.fetchone()

#             #ເລືອກສິນຄ້າ
#             curp = gobal.con.cursor()
#             sql_p = """SELECT p_id, p_name, p_price FROM product p LEFT JOIN supplier s ON s.sup_id = p.sup_id WHERE p.sup_id = %s"""
#             curp.execute(sql_p,(id,))
#             pro_list = curp.fetchall()
#             #current date
#             dateTimeObj = datetime.now()
#             doc_date = dateTimeObj.strftime("%Y-%m-%d")
#             doc_time = dateTimeObj.strftime("%H:%M:%S")
#             sql_d = """SELECT max(SPLIT_PART(order_id,'-', 2))::int from order_table"""
#             cur_d = gobal.con.cursor()
#             cur_d.execute(sql_d)
#             bil_no = cur_d.fetchone()
#             doc_no = ''
#             if bil_no[0] == None:
#                 doc_no = 'OD-000001'
#             else:
#                 doc = bil_no[0]
#                 a = doc+1
#                 doc_no = "OD-"+str(a)
#             doc_no = doc_no
#             gobal.con.commit()
#             return render_template('order & withdraw/order_desc.html', doc_date = doc_date, doc_time = doc_time, doc_no = doc_no, pro_list = pro_list, sp = sp, sc_list = sc_list, detail_list = detail_list, user=session.get("roles"))

@app.route('/recieve_desc', methods=["POST", "GET"])
def recieve_desc():
        if not session.get("name"):
            return redirect("/login")
        else:
            #current date
            dateTimeObj = datetime.now()
            doc_date = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
            doc_time = dateTimeObj.strftime("%H:%M:%S")
            sql_d = """SELECT
                    CASE WHEN COUNT(rc_id) = 0 
                        THEN 'RC-000001'::text 
                        WHEN COUNT(rc_id) > 0 
                        THEN CONCAT('RC-',LPAD((RIGHT(MAX(rc_id),6)::integer+1)::text, 6, 0::text) )
                    end as rc_id
                    FROM recieve"""
            cur_d = gobal.con.cursor()
            cur_d.execute(sql_d)
            bill_no = cur_d.fetchone()
            doc_no = str(bill_no)
            doc_no = doc_no[2:11]

            session["rc_id"] = doc_no
            # id = request.form['order_id']
            cur = gobal.con.cursor()
            sql = """SELECT r.rc_date, rd.rc_id, rd.rc_qty, r.sup_id FROM recieve_detail rd
                    LEFT JOIN recieve r ON r.rc_id = rd.rc_id"""
            cur.execute(sql)
            sc_list = cur.fetchall()

            curdt = gobal.con.cursor()
            sqldt = """SELECT row_number() OVER () as NO, p.p_id, p_name, rd.rc_qty, p_price, p_price * rd.rc_qty FROM recieve_detail rd
                    LEFT JOIN product p ON p.p_id = rd.p_id 
                    LEFT JOIN recieve r ON r.rc_id = rd.rc_id 
                    WHERE r.rc_id is NULL"""
            curdt.execute(sqldt)
            detail_list = curdt.fetchall()

            cursp = gobal.con.cursor()
            sqlsp = """SELECT s.sup_id, s.sup_name, CONCAT(sup_village, ', ', sup_district, ', ', sup_province) address, sup_tel, sup_email FROM supplier s
                        ORDER BY sup_id
                    """
            cursp.execute(sqlsp)
            sp = cursp.fetchall()

            #ເລືອກສິນຄ້າ
            curp = gobal.con.cursor()
            sql_p = """SELECT p.p_id, p.p_name, p.p_price FROM product p
                    WHERE p.p_id NOT IN(
                        SELECT rd.p_id FROM recieve_detail rd
                        LEFT JOIN recieve r ON r.rc_id = rd.rc_id 
                                        WHERE r.rc_id is NULL
                    )
                    ORDER BY p.p_id
                    """
            curp.execute(sql_p)
            pro_list = curp.fetchall()

            # ສະເເດງລວມທັງໝົດ
            sql_sum = """SELECT sum(p_price * rd.rc_qty) FROM recieve_detail rd
                    LEFT JOIN product p ON p.p_id = rd.p_id 
                    LEFT JOIN recieve r ON r.rc_id = rd.rc_id 
                    WHERE r.rc_id is NULL"""
            cur.execute(sql_sum)
            sum_amount = cur.fetchall()
            gobal.con.commit()
            return render_template('order & withdraw/recieve_desc.html', doc_date = doc_date, doc_time = doc_time, doc_no = doc_no, pro_list = pro_list, sp = sp, sc_list = sc_list, detail_list = detail_list, sum_amount = sum_amount, user=session['name'], roles = session['roles'], rc_id = session["rc_id"])

@app.route('/save_recieve_desc', methods=['POST', 'GET'])
def save_recieve_desc():
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:

            sql = """INSERT INTO recieve(
                         rc_date, rc_id, sup_id, remark)
                         VALUES(%s,%s,%s,%s)
                  """
            
            rc_date = request.form['rc_date']
            rc_id = request.form['rc_id']
            sup_id = request.form['sup_id']
            remark = request.form['remark']
            data = (rc_date, rc_id, sup_id, remark)
            cur.execute(sql, (data))
            gobal.con.commit()
            return redirect(url_for('recieve'))
            # return render_template('order & withdraw/order_desc.html', sp = sp)

# ກົດປຸ່ມຍົກເລີກເເລ້ວເຄຍ trans_draft ເເລະ ກັບໄປໜ້າ pick_pro
@app.route('/back_button_recieve_desc')
def back_button_recieve_desc():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = "DELETE FROM recieve_detail WHERE rc_id=%s"
            cur.execute(sql, (session["rc_id"],))
        return redirect(url_for('recieve'))

@app.route('/save_recieve_detail', methods=['POST', 'GET'])
def save_recieve_detail():
    with gobal.con:
        cur = gobal.con.cursor()
        # cursp = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:

            rc_id = request.form['rc_id']
            p_id = request.form['p_id']
            rc_qty = request.form['rc_qty']
            rc_price = request.form['rc_price']

            sql = """INSERT INTO recieve_detail(
                        rc_id, p_id, rc_qty, rc_price)
                        VALUES(%s,%s,%s,%s)
                """
            data = (rc_id, p_id, rc_qty, rc_price)
            cur.execute(sql, data)

            #ເພີ່ມ stock
            cursor = gobal.con.cursor()
            up_stock = """UPDATE product 
                    SET p_qty = 
                    (SELECT rc_qty FROM recieve_detail WHERE p_id=%s AND rc_id = %s)+p_qty
                    WHERE p_id = %s"""
            stock = (p_id, rc_id, p_id)
            cursor.execute(up_stock, stock)
            gobal.con.commit()
            return redirect(url_for('recieve_desc'))

@app.route('/delete_recieve_detail/<string:id>', methods=['POST', 'GET'])
def delete_recieve_detail(id):
    with gobal.con:
        cur = gobal.con.cursor()
        # cursp = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            
            #ລົບ stock
            cursor = gobal.con.cursor()
            up_stock = """UPDATE product 
                    SET p_qty = 
                    p_qty - (SELECT rc_qty FROM recieve_detail WHERE p_id=%s AND rc_id = %s)
                    WHERE p_id = %s"""
            stock = ((id,),session["order_id"], (id,)) 
            cursor.execute(up_stock, stock)

            sql = "DELETE FROM recieve_detail WHERE p_id = %s"
            cur.execute(sql, (id,))
            gobal.con.commit()
            return redirect(url_for('recieve_desc'))

# @app.route('/save_order_detail', methods=['POST', 'GET'])
# def save_order_detail():
#     with gobal.con:
#         cur = gobal.con.cursor()
#         cursl = gobal.con.cursor()
#         cursp = gobal.con.cursor()
#         if not session.get("name"):
#             return redirect("/login")
#         else:
#             if request.method == 'POST':
#                 order_id = request.form['order_id']
#                 p_id = request.form['p_id']
#                 order_qty = request.form['order_qty']

#                 sql = """INSERT INTO order_detail(
#                             order_id, p_id, order_qty)
#                             VALUES(%s,%s,%s)
#                     """
#                 data = (order_id, p_id, order_qty)
#                 cur.execute(sql, (data)) 
#                 gobal.con.commit()
#                 return render_template('order & withdraw/order_desc.html')
#             else:

#                 sqlsl = "SELECT sup_id, sup_name FROM supplier"
#                 cursl.execute(sqlsl)
#                 sp = cursl.fetchone()

#                 sqlsp = """SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id FROM order_detail od
#                      LEFT JOIN order_table ot ON ot.order_id = od.order_id"""
#                 cursp.execute(sqlsp)
#                 detail_list = cursp.fetchone()
#                 return render_template('order & withdraw/order_desc.html', detail_list = detail_list, sp = sp)

@app.route('/update_recieve_desc/<string:id>', methods=['POST'])
def update_recieve_desc(id):
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            rc_id = request.form['wd_id']
            rc_date = request.form['wd_date']
            emp_id = request.form['emp_id']
            remark = request.form['remark']

            cur.execute('UPDATE recieve_desc SET rc_id=%s, rc_date=%s, emp_id=%s, remark=%s WHERE rc_id=%s',
                        (rc_id, rc_date, emp_id, remark, (id,)))
            gobal.con.commit()
            return redirect(url_for('recieve_desc'))

@app.route('/delete_recieve_desc/<string:id>')
def delete_recieve_desc(id):
    if not session.get("name"):
        return redirect("/login")
    else:
        cur = gobal.con.cursor()
        sql = "DELETE FROM recieve_detail WHERE rc_id=%s"
        cur.execute(sql, (id,))
        gobal.con.commit()
        return redirect(url_for('recieve_desc'))

#recieve_by_order
@app.route('/recieve_by_order/<string:id>',methods=['GET'])
def recieve_by_order(id):
        if not session.get("name"):
            return redirect("/login")
        else:
            #current date
            dateTimeObj = datetime.now()
            doc_date = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
            doc_time = dateTimeObj.strftime("%H:%M:%S")
            sql_d = """SELECT
                    CASE WHEN COUNT(rc_id) = 0 
                        THEN 'RC-000001'::text 
                        WHEN COUNT(rc_id) > 0 
                        THEN CONCAT('RC-',LPAD((RIGHT(MAX(rc_id),6)::integer+1)::text, 6, 0::text) )
                    end as rc_id
                    FROM recieve"""
            cur_d = gobal.con.cursor()
            cur_d.execute(sql_d)
            bill_no = cur_d.fetchone()
            doc_no = str(bill_no)
            doc_no = doc_no[2:11]

            session["rc_id"] = doc_no
            session["order_id"] = (id)
            print("id=", session["order_id"])
            # id = request.form['order_id']
            cur = gobal.con.cursor()
            # sql = """SELECT r.rc_date, rd.rc_id, rd.rc_qty, r.sup_id, r.order_id FROM recieve_detail rd
            #         LEFT JOIN recieve r ON r.rc_id = rd.rc_id"""
            sql = """SELECT r.rc_date, rd.rc_id, rd.rc_qty, r.sup_id, r.order_id FROM recieve_detail rd
                    LEFT JOIN recieve r ON r.rc_id = rd.rc_id"""
            cur.execute(sql)
            sc_list = cur.fetchall()

            sql_od = """SELECT order_date, ot.order_id, s.sup_name ,remark,(SELECT sum(order_qty) FROM order_detail WHERE order_id=ot.order_id) FROM order_table ot
                     LEFT JOIN supplier s ON s.sup_id = ot.sup_id
                     WHERE ot.order_id = %s"""
            # SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id FROM order_detail od
            #         LEFT JOIN order_table ot ON ot.order_id = od.order_id WHERE ot.order_id is NOT NULL
            cur.execute(sql_od, (id,))
            order = cur.fetchone()

            sql = """SELECT order_date, ot.order_id, s.sup_name ,remark,(SELECT sum(order_qty) FROM order_detail WHERE order_id=ot.order_id) FROM order_table ot
                     LEFT JOIN supplier s ON s.sup_id = ot.sup_id
                     WHERE ot.order_id = %s"""
            cur.execute(sql, (id,))
            od_list = cur.fetchall()

            curdt = gobal.con.cursor()
            sqldt = """SELECT row_number() OVER () as NO, p.p_id, p_name, rd.rc_qty, p_price, p_price * rd.rc_qty FROM recieve_detail rd
                    LEFT JOIN product p ON p.p_id = rd.p_id 
                    LEFT JOIN recieve r ON r.rc_id = rd.rc_id 
                    WHERE r.rc_id is NULL"""
            curdt.execute(sqldt, (id,))
            detail_list = curdt.fetchall()

            cursp = gobal.con.cursor()
            sqlsp = """SELECT s.sup_id, s.sup_name, CONCAT(sup_village, ', ', sup_district, ', ', sup_province) address, sup_tel, sup_email FROM supplier s
                    ORDER BY sup_id"""
            cursp.execute(sqlsp)
            sp = cursp.fetchall()

            #ເລືອກສິນຄ້າ
            curp = gobal.con.cursor()
            sql_p = """SELECT p.p_id, p.p_name, p.p_price FROM product p
                    WHERE p.p_id NOT IN(
                        SELECT rd.p_id FROM recieve_detail rd
                        LEFT JOIN recieve r ON r.rc_id = rd.rc_id 
                                        WHERE r.rc_id is NULL
                    )
                    ORDER BY p.p_id
                    """
            curp.execute(sql_p)
            pro_list = curp.fetchall()

            # ສະເເດງລວມທັງໝົດ
            sql_sum = """SELECT sum(p_price * rd.rc_qty) FROM recieve_detail rd
                    LEFT JOIN product p ON p.p_id = rd.p_id 
                    LEFT JOIN recieve r ON r.rc_id = rd.rc_id 
                    WHERE r.rc_id is NULL"""
            cur.execute(sql_sum)
            sum_amount = cur.fetchall()
            gobal.con.commit()
            return render_template('order & withdraw/recieve_by_order.html', order = order, od_list = od_list,doc_date = doc_date, doc_time = doc_time, doc_no = doc_no, pro_list = pro_list, sp = sp, sc_list = sc_list, detail_list = detail_list, sum_amount = sum_amount, user=session['name'], roles = session['roles'], rc_id = session["rc_id"], order_id = session["order_id"])

@app.route('/save_recieve_by_order', methods=['POST', 'GET'])
def save_recieve_by_order():
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:

            sql = """INSERT INTO recieve(
                         rc_date, rc_id, order_id, sup_id, remark)
                         VALUES(%s,%s,%s,%s,%s)
                  """
            
            rc_date = request.form['rc_date']
            rc_id = request.form['rc_id']
            order_id = request.form['order_id']
            sup_id = request.form['sup_id']
            remark = request.form['remark']
            data = (rc_date, rc_id, order_id, sup_id, remark)
            cur.execute(sql, (data))
            gobal.con.commit()
            return redirect(url_for('recieve'))

@app.route('/save_recieve_by_order_detail', methods=['POST', 'GET'])
def save_recieve_by_order_detail():
    with gobal.con:
        cur = gobal.con.cursor()
        # cursp = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            id = request.form["order_id"]
            rc_id = request.form['rc_id']
            p_id = request.form['p_id']
            rc_qty = request.form['rc_qty']
            rc_price = request.form['rc_price']

            sql = """INSERT INTO recieve_detail(
                        rc_id, p_id, rc_qty, rc_price)
                        VALUES(%s,%s,%s,%s)
                """
            data = (rc_id, p_id, rc_qty, rc_price)
            cur.execute(sql, data)

            #ເພີ່ມ stock
            cursor = gobal.con.cursor()
            up_stock = """UPDATE product 
                    SET p_qty = 
                    (SELECT rc_qty FROM recieve_detail WHERE p_id=%s AND rc_id = %s)+p_qty
                    WHERE p_id = %s"""
            stock = (p_id, rc_id, p_id)
            cursor.execute(up_stock, stock)
            gobal.con.commit()
            return redirect(url_for('recieve_by_order', id=(id,)))

@app.route('/delete_recieve_by_order_detail/<string:id>', methods=['POST', 'GET'])
def delete_recieve_by_order_detail(id):
    with gobal.con:
        cur = gobal.con.cursor()
        # cursp = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            
            #ລົບ stock
            cursor = gobal.con.cursor()
            up_stock = """UPDATE product 
                    SET p_qty = 
                    p_qty - (SELECT rc_qty FROM recieve_detail WHERE p_id=%s AND rc_id = %s)
                    WHERE p_id = %s"""
            stock = ((id,),session["rc_id"], (id,)) 
            cursor.execute(up_stock, stock)

            sql = "DELETE FROM recieve_detail WHERE p_id = %s"
            cur.execute(sql, (id,))
            gobal.con.commit()
            return redirect(url_for('recieve_by_order', id=session["order_id"]))

@app.route('/print_recieve/<string:id>', methods=['GET'])
def print_recieve(id):
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = """SELECT r.rc_date, rd.rc_id, r.sup_id, s.sup_name, sup_village||' '|| sup_district ||' '|| sup_province, sup_tel, sup_email, remark FROM recieve_detail rd
                    LEFT JOIN recieve r ON r.rc_id = rd.rc_id
                    LEFT JOIN supplier s ON s.sup_id = r.sup_id
                    WHERE r.rc_id = %s"""
            cur.execute(sql, (id,))
            show = cur.fetchone()

            curdt = gobal.con.cursor()
            sqldt = """SELECT row_number() OVER () as NO, p.p_id, p_name, rd.rc_qty ,to_char(p_price,'999G999G999G999'), to_char(p_price * rd.rc_qty,'999G999G999G999') FROM recieve_detail rd
                    LEFT JOIN product p ON p.p_id = rd.p_id 
                    LEFT JOIN recieve r ON r.rc_id = rd.rc_id 
                    WHERE r.rc_id = %s"""
            curdt.execute(sqldt, (id,))
            detail_list = curdt.fetchall()

            # ສະເເດງລວມທັງໝົດ
            sql_sum = """SELECT to_char(sum(p_price * rd.rc_qty),'999G999G999G999') FROM recieve_detail rd
                    LEFT JOIN product p ON p.p_id = rd.p_id 
                    LEFT JOIN recieve r ON r.rc_id = rd.rc_id 
                    WHERE r.rc_id = %s"""
            cur.execute(sql_sum, (id,))
            sum_amount = cur.fetchall()
            return render_template('order & withdraw/recieve_bill.html', show = show, detail_list = detail_list, sum_amount = sum_amount, user=session['name'], roles = session['roles'])

#order_desc
# @app.route('/order_desc/<string:id>',methods=['GET'])
# def order_desc(id):
#         if not session.get("name"):
#             return redirect("/login")
#         else:
#             cur = gobal.con.cursor()
#             sql = """SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id FROM order_detail od
#                     LEFT JOIN order_table ot ON ot.order_id = od.order_id"""
#             cur.execute(sql)
#             sc_list = cur.fetchall()

#             curdt = gobal.con.cursor()
#             sqldt = """SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id FROM order_detail od
#                     LEFT JOIN order_table ot ON ot.order_id = od.order_id WHERE ot.sup_id = %s"""
#             curdt.execute(sqldt,(id,))
#             detail_list = curdt.fetchall()

#             cursp = gobal.con.cursor()
#             sqlsp = "SELECT sup_id, sup_name FROM supplier WHERE sup_id = %s"
#             cursp.execute(sqlsp,(id,))
#             sp = cursp.fetchone()

#             #ເລືອກສິນຄ້າ
#             curp = gobal.con.cursor()
#             sql_p = """SELECT p_id, p_name, p_price FROM product p LEFT JOIN supplier s ON s.sup_id = p.sup_id WHERE p.sup_id = %s"""
#             curp.execute(sql_p,(id,))
#             pro_list = curp.fetchall()
#             #current date
#             dateTimeObj = datetime.now()
#             doc_date = dateTimeObj.strftime("%Y-%m-%d")
#             doc_time = dateTimeObj.strftime("%H:%M:%S")
#             sql_d = """SELECT max(SPLIT_PART(order_id,'-', 2))::int from order_table"""
#             cur_d = gobal.con.cursor()
#             cur_d.execute(sql_d)
#             bil_no = cur_d.fetchone()
#             doc_no = ''
#             if bil_no[0] == None:
#                 doc_no = 'OD-000001'
#             else:
#                 doc = bil_no[0]
#                 a = doc+1
#                 doc_no = "OD-"+str(a)
#             doc_no = doc_no
#             gobal.con.commit()
#             return render_template('order & withdraw/order_desc.html', doc_date = doc_date, doc_time = doc_time, doc_no = doc_no, pro_list = pro_list, sp = sp, sc_list = sc_list, detail_list = detail_list, user=session.get("roles"))