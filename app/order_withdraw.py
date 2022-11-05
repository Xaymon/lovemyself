
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from app import app
from kk_con import *
from datetime import datetime

#order
@app.route('/order')
def order():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            #ສະ​ແດງ​ລາຍ​ການ​ໃນ​ໜ້າ​ອໍ​ເດີ້
            cur = gobal.con.cursor()
            sql = """SELECT order_date, ot.order_id, s.sup_name ,remark,(SELECT sum(order_qty) FROM order_detail WHERE order_id=ot.order_id) FROM order_table ot
                     LEFT JOIN supplier s ON s.sup_id = ot.sup_id"""
            # SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id FROM order_detail od
            #         LEFT JOIN order_table ot ON ot.order_id = od.order_id WHERE ot.order_id is NOT NULL
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
                    """
            cursp.execute(sqlsp)
            sp_list = cursp.fetchall()
            gobal.con.commit()
            return render_template('order & withdraw/order.html', od_list = od_list, sp_list = sp_list, user=session['name'], roles = session['roles'])

#order_about ສະແດງລາຍລະອຽດຕາມລະຫັດ order_id
@app.route('/order_about/<string:id>', methods=["POST", "GET"])
def order_about(id):
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            #ສະ​ແດງ​ລາຍ​ການ​ໃນ​ໜ້າ​ອໍ​ເດີ້
            cur = gobal.con.cursor()
            sql = """SELECT ot.order_date, od.order_id, ot.sup_id, s.sup_name, remark FROM order_detail od
                    LEFT JOIN order_table ot ON ot.order_id = od.order_id
                    LEFT JOIN supplier s ON s.sup_id = ot.sup_id
                    WHERE ot.order_id = %s"""
            # sql = """SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id, ot.remark FROM order_detail od
            #          LEFT JOIN order_table ot ON ot.order_id = od.order_id 
            #          LEFT JOIN supplier s ON s.sup_id = ot.sup_id
            #          WHERE ot.order_id = %s"""
            # SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id FROM order_detail od
            #         LEFT JOIN order_table ot ON ot.order_id = od.order_id WHERE ot.order_id is NOT NULL
            cur.execute(sql, (id,))
            show = cur.fetchone()

            curdt = gobal.con.cursor()
            sqldt = """SELECT row_number() OVER () as NO, p.p_id, p_name, od.order_qty FROM order_detail od
                    LEFT JOIN product p ON p.p_id = od.p_id 
                    LEFT JOIN order_table ot ON ot.order_id = od.order_id 
                    WHERE ot.order_id = %s"""
            curdt.execute(sqldt, (id,))
            detail_list = curdt.fetchall()

            # ສະເເດງລວມທັງໝົດ
            sql_sum = """SELECT (SELECT sum(order_qty) FROM order_detail WHERE order_id=ot.order_id) FROM order_table ot
                     LEFT JOIN supplier s ON s.sup_id = ot.sup_id 
                     WHERE ot.order_id = %s"""
            cur.execute(sql_sum, (id,))
            sum_amount = cur.fetchall()
            gobal.con.commit()
            return render_template('order & withdraw/order_about.html', show = show, detail_list = detail_list, sum_amount = sum_amount, user=session['name'], roles = session['roles'])

@app.route('/save_order', methods=['POST'])
def save_order():
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            sql = """INSERT INTO order(
                         p_id, p_name, p_price)
                         VALUES(%s,%s,%s)
                  """
            
            p_id = request.form['p_id']
            p_name = request.form['​​p_name']
            p_price = request.form['p_price']
            data = (p_id, p_name, p_price)
            cur.execute(sql, (data))
            gobal.con.commit()
            return redirect(url_for('order'))

@app.route('/update_order/<string:id>', methods=['POST'])
def update_order(id):
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            p_id = request.form['p_id']
            p_name = request.form['​​p_name']
            p_price = request.form['p_price']

            cur.execute('UPDATE order SET p_id=%s, p_name=%s, p_price=%s WHERE p_id=%s',
                        (p_id, p_name, p_price, (id,)))
            gobal.con.commit()
            return redirect(url_for('order'))

@app.route('/delete_order/<string:id>')
def delete_order(id):
    if not session.get("name"):
        return redirect("/login")
    else:
        cur = gobal.con.cursor()
        sql = "DELETE FROM order_table WHERE order_id=%s"
        cur.execute(sql, (id,))
        cursor = gobal.con.cursor()
        sql2 = "DELETE FROM order_detail WHERE order_id=%s"
        cursor.execute(sql2, (id,))
        gobal.con.commit()
        return redirect(url_for('order'))

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

@app.route('/order_desc', methods=["POST", "GET"])
def order_desc():
        if not session.get("name"):
            return redirect("/login")
        else:
            #current date
            dateTimeObj = datetime.now()
            doc_date = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
            doc_time = dateTimeObj.strftime("%H:%M:%S")
            sql_d = """SELECT
                    CASE WHEN COUNT(order_id) = 0 
                        THEN 'OD-000001'::text 
                        WHEN count(order_id) > 0 
                        THEN CONCAT('OD-',LPAD((RIGHT(MAX(order_id),6)::integer+1)::text, 6, 0::text) )
                    END as order_id
                    FROM order_table"""
            cur_d = gobal.con.cursor()
            cur_d.execute(sql_d)
            bill_no = cur_d.fetchone()
            doc_no = str(bill_no)
            doc_no = doc_no[2:11]
            
            session["order_id"] = doc_no
            # id = request.form['order_id']
            cur = gobal.con.cursor()
            sql = """SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id FROM order_detail od
                    LEFT JOIN order_table ot ON ot.order_id = od.order_id"""
            cur.execute(sql)
            sc_list = cur.fetchall()

            curdt = gobal.con.cursor()
            sqldt = """SELECT row_number() OVER () as NO, p.p_id, p_name, od.order_qty FROM order_detail od
                    LEFT JOIN product p ON p.p_id = od.p_id 
                    LEFT JOIN order_table ot ON ot.order_id = od.order_id 
                    WHERE ot.order_id is NULL"""
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
                        SELECT od.p_id FROM order_detail od
                        LEFT JOIN order_table ot ON ot.order_id = od.order_id 
                                        WHERE ot.order_id is NULL
                    )
                    ORDER BY p.p_id
                    """
            curp.execute(sql_p)
            pro_list = curp.fetchall()

            # ສະເເດງລວມທັງໝົດ
            sql_sum = """SELECT sum(od.order_qty) FROM order_detail od
                    LEFT JOIN product p ON p.p_id = od.p_id 
                    LEFT JOIN order_table ot ON ot.order_id = od.order_id 
                    WHERE ot.order_id is NULL"""
            cur.execute(sql_sum)
            sum_amount = cur.fetchall()
            gobal.con.commit()
            return render_template('order & withdraw/order_desc.html', doc_date = doc_date, doc_time = doc_time, doc_no = doc_no, pro_list = pro_list, sp = sp, sc_list = sc_list, detail_list = detail_list, sum_amount = sum_amount, user=session['name'], roles = session['roles'], order_id = session["order_id"])

@app.route('/save_order_desc', methods=['POST', 'GET'])
def save_order_desc():
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:

            sql = """INSERT INTO order_table(
                         order_date, order_id, sup_id, remark)
                         VALUES(%s,%s,%s,%s)
                  """
            
            order_date = request.form['order_date']
            order_id = request.form['order_id']
            sup_id = request.form['sup_id']
            remark = request.form['remark']
            data = (order_date, order_id, sup_id, remark)
            cur.execute(sql, (data))
            gobal.con.commit()
            return redirect(url_for('order'))
            # return render_template('order & withdraw/order_desc.html', sp = sp)

# ກົດປຸ່ມຍົກເລີກເເລ້ວເຄຍ trans_draft ເເລະ ກັບໄປໜ້າ pick_pro
@app.route('/back_button_order_desc')
def back_button_order_desc():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = "DELETE FROM order_detail WHERE order_id=%s"
            cur.execute(sql, (session["order_id"],))
        return redirect(url_for('order'))

@app.route('/save_order_detail', methods=['POST', 'GET'])
def save_order_detail():
    with gobal.con:
        cur = gobal.con.cursor()
        # cursp = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:

            order_id = request.form['order_id']
            p_id = request.form['p_id']
            order_qty = request.form['order_qty']

            sql = """INSERT INTO order_detail(
                        order_id, p_id, order_qty)
                        VALUES(%s,%s,%s)
                """
            data = (order_id, p_id, order_qty)
            cur.execute(sql, data)

            #ເພີ່ມ stock
            # cursor = gobal.con.cursor()
            # up_stock = """UPDATE product 
            #         SET p_qty = 
            #         (SELECT order_qty FROM order_detail WHERE p_id=%s AND order_id = %s)+p_qty
            #         WHERE p_id = %s"""
            # stock = (p_id, order_id, p_id)
            # cursor.execute(up_stock, stock)
            gobal.con.commit()
            return redirect(url_for('order_desc'))

@app.route('/delete_order_detail/<string:id>', methods=['POST', 'GET'])
def delete_order_detail(id):
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
                    p_qty - (SELECT order_qty FROM order_detail WHERE p_id=%s AND order_id = %s)
                    WHERE p_id = %s"""
            stock = ((id,),session["order_id"], (id,)) 
            cursor.execute(up_stock, stock)

            sql = "DELETE FROM order_detail WHERE p_id = %s"
            cur.execute(sql, (id,))
            gobal.con.commit()
            return redirect(url_for('order_desc'))

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

@app.route('/update_order_desc/<string:id>', methods=['POST'])
def update_order_desc(id):
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            wd_id = request.form['wd_id']
            wd_date = request.form['wd_date']
            emp_id = request.form['emp_id']
            remark = request.form['remark']

            cur.execute('UPDATE order_desc SET wd_id=%s, wd_date=%s, emp_id=%s, remark=%s WHERE wd_id=%s',
                        (wd_id, wd_date, emp_id, remark, (id,)))
            gobal.con.commit()
            return redirect(url_for('order_desc'))

@app.route('/delete_order_desc/<string:id>')
def delete_order_desc(id):
    if not session.get("name"):
        return redirect("/login")
    else:
        cur = gobal.con.cursor()
        sql = "DELETE FROM order_desc WHERE wd_id=%s"
        cur.execute(sql, (id,))
        gobal.con.commit()
        return redirect(url_for('order_desc'))

@app.route('/print_order/<string:id>', methods=['GET'])
def print_order(id):
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = """SELECT ot.order_date, od.order_id, ot.sup_id, s.sup_name, s.sup_village, ', ', sup_district, ', ', sup_province, sup_tel, sup_email, remark FROM order_detail od
                    LEFT JOIN order_table ot ON ot.order_id = od.order_id
                    LEFT JOIN supplier s ON s.sup_id = ot.sup_id
                    WHERE ot.order_id = %s"""
            cur.execute(sql, (id,))
            show = cur.fetchone()

            curdt = gobal.con.cursor()
            sqldt = """SELECT row_number() OVER () as NO, p.p_id, p_name, od.order_qty FROM order_detail od
                    LEFT JOIN product p ON p.p_id = od.p_id 
                    LEFT JOIN order_table ot ON ot.order_id = od.order_id 
                    WHERE ot.order_id = %s"""
            curdt.execute(sqldt, (id,))
            detail_list = curdt.fetchall()

            # ສະເເດງລວມທັງໝົດ
            sql_sum = """SELECT sum(od.order_qty) FROM order_detail od
                    LEFT JOIN product p ON p.p_id = od.p_id 
                    LEFT JOIN order_table ot ON ot.order_id = od.order_id 
                    WHERE ot.order_id = %s"""
            cur.execute(sql_sum, (id,))
            sum_amount = cur.fetchall()
            return render_template('order & withdraw/order_bill.html', show = show, detail_list = detail_list, sum_amount = sum_amount, user=session['name'], roles = session['roles'])

#withdraw
@app.route('/withdraw_item')
def withdraw_item():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = """SELECT wd_date, wi.wd_id, e.emp_name ,remark,(SELECT sum(wd_qty) FROM withdraw_detail WHERE wd_id=wi.wd_id) FROM withdraw_item wi
                     LEFT JOIN employee e ON e.emp_id = wi.emp_id"""
            cur.execute(sql)
            wd_list = cur.fetchall()

            curc = gobal.con.cursor()
            sqlc = """SELECT emp_id, emp_name, CONCAT(emp_village, ', ', emp_district, ', ', emp_province) address, emp_tel, admin_name, admin_pwd, emp_gender, emp_bd, emp_province, emp_district, emp_village,
                    emp_province, emp_district, emp_village FROM employee e ORDER BY emp_id
                    """
            curc.execute(sqlc)
            cust_list = curc.fetchall()

            curp = gobal.con.cursor()
            sqlp = """SELECT p_id, p_name, p_price, p_qty FROM product ORDER BY p_id"""
            curp.execute(sqlp)
            pro_list = curp.fetchall()

            gobal.con.commit()

            return render_template('order & withdraw/withdraw_item.html', wd_list = wd_list, cust_list = cust_list, pro_list = pro_list, user=session['name'], roles = session['roles'])

#withdraw_about ສະແດງລາຍລະອຽດຕາມລະຫັດ order_id
@app.route('/withdraw_about/<string:id>', methods=["POST", "GET"])
def withdraw_about(id):
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            #ສະ​ແດງ​ລາຍ​ການ​ໃນ​ໜ້າ​ອໍ​ເດີ້
            cur = gobal.con.cursor()
            sql = """SELECT wi.wd_date, wd.wd_id, wi.emp_id, e.emp_name, remark FROM withdraw_detail wd
                    LEFT JOIN withdraw_item wi ON wi.wd_id = wd.wd_id
                    LEFT JOIN employee e ON e.emp_id = wi.emp_id
                    WHERE wi.wd_id = %s"""
            # sql = """SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id, ot.remark FROM order_detail od
            #          LEFT JOIN order_table ot ON ot.order_id = od.order_id 
            #          LEFT JOIN supplier s ON s.sup_id = ot.sup_id
            #          WHERE ot.order_id = %s"""
            # SELECT ot.order_date, od.order_id, od.order_qty, ot.sup_id FROM order_detail od
            #         LEFT JOIN order_table ot ON ot.order_id = od.order_id WHERE ot.order_id is NOT NULL
            cur.execute(sql, (id,))
            show = cur.fetchone()

            curdt = gobal.con.cursor()
            sqldt = """SELECT row_number() OVER () as NO, p.p_id, p_name, wd.wd_qty, p_price, p_price * wd.wd_qty FROM withdraw_detail wd
                    LEFT JOIN product p ON p.p_id = wd.p_id 
                    LEFT JOIN withdraw_item wi ON wi.wd_id = wd.wd_id 
                    WHERE wi.wd_id = %s"""
            curdt.execute(sqldt, (id,))
            detail_list = curdt.fetchall()

            # ສະເເດງລວມທັງໝົດ
            sql_sum = """SELECT sum(p_price * wd.wd_qty) FROM withdraw_detail wd
                    LEFT JOIN product p ON p.p_id = wd.p_id 
                    LEFT JOIN withdraw_item wi ON wi.wd_id = wd.wd_id 
                     WHERE wi.wd_id = %s"""
            cur.execute(sql_sum, (id,))
            sum_amount = cur.fetchall()
            gobal.con.commit()
            return render_template('order & withdraw/withdraw_about.html', show = show, detail_list = detail_list, sum_amount = sum_amount, user=session['name'], roles = session['roles'])

@app.route('/save_withdraw_item', methods=['POST'])
def save_withdraw_item():
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            sql = """INSERT INTO withdraw_item(
                         wd_id, wd_date, emp_id, remark)
                         VALUES(%s,%s,%s,%s)
                  """
            
            wd_id = request.form['wd_id']
            wd_date = request.form['wd_date']
            emp_id = request.form['emp_id']
            remark = request.form['remark']
            data = (wd_id, wd_date, emp_id, remark)
            cur.execute(sql, (data))
            gobal.con.commit()
            return redirect(url_for('withdraw_item'))

@app.route('/update_withdraw_item/<string:id>', methods=['POST'])
def update_withdraw_item(id):
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            wd_id = request.form['wd_id']
            wd_date = request.form['wd_date']
            emp_id = request.form['emp_id']
            remark = request.form['remark']

            cur.execute('UPDATE withdraw_item SET wd_id=%s, wd_date=%s, emp_id=%s, remark=%s WHERE wd_id=%s',
                        (wd_id, wd_date, emp_id, remark, (id,)))
            gobal.con.commit()
            return redirect(url_for('withdraw_item'))

@app.route('/delete_withdraw_item/<string:id>')
def delete_withdraw_item(id):
    if not session.get("name"):
        return redirect("/login")
    else:
        cur = gobal.con.cursor()
        up_stock = """UPDATE product AS p 
                    SET p_qty = p.p_qty-wd.wd_qty 
                    FROM 
                        (SELECT p_id, wd_qty
                          FROM withdraw_detail WHERE wd_id = %s) AS wd
                    WHERE 
                         p.p_id=wd.p_id"""
        stock = (id,)
        cur.execute(up_stock, stock)
        sql = "delete from withdraw_item where wd_id=%s"
        cur.execute(sql, (id,))

        sql = "delete from withdraw_detail where wd_id=%s"
        cur.execute(sql, (id,))
        gobal.con.commit()
        return redirect(url_for('withdraw_item'))

#withdraw_item
# @app.route('/withdraw_item')
# def withdraw_item():
#     with gobal.con:
#         if not session.get("name"):
#             return redirect("/login")
#         else:
#             cur = gobal.con.cursor()
#             # sql = "SELECT wd_id, wd_name, wd_date, emp_id FROM withdraw_item ORDER BY wd_id"
#             # cur.execute(sql)
#             # sc_list = cur.fetchall()
#             #ເລືອກສິນຄ້າ
#             sql_p = """SELECT p_id, p_name, p_price FROM product p LEFT JOIN supplier s ON s.sup_id = p.sup_id"""
#             cur.execute(sql_p)
#             pro_list = cur.fetchall()

#             sql_s = """SELECT s.sup_id, s.sup_name, CONCAT(v.village_name, ', ', c.city_name, ', ', p.prov_name) address, sup_tel, sup_email FROM supplier s
#                     LEFT JOIN village v ON v.village_code = s.sup_village LEFT JOIN city c ON c.city_code = s.sup_district 
#                     LEFT JOIN province p ON p.prov_code = s.sup_province"""
#             cur.execute(sql_s)
#             sp = cur.fetchall()

#             dateTimeObj = datetime.now()
#             doc_date = dateTimeObj.strftime("%Y-%m-%d")
#             doc_time = dateTimeObj.strftime("%H:%M:%S")
#             sql_d = """SELECT max(SPLIT_PART(wd_id,'-', 2))::int from withdraw_item"""
#             cur_d = gobal.con.cursor()
#             cur_d.execute(sql_d)
#             bil_no = cur_d.fetchone()
#             doc_no = ''
#             if bil_no[0] == None:
#                 doc_no = 'WD-100001'
#             else:
#                 doc = bil_no[0]
#                 a = doc+1
#                 doc_no = "WD-"+str(a)
#             doc_no = doc_no
#             gobal.con.commit()

#             return render_template('order & withdraw/withdraw_item.html', doc_date = doc_date, doc_time = doc_time, doc_no = doc_no, pro_list = pro_list, sp = sp, user=session.get("roles"))

@app.route('/withdraw_desc', methods=["POST", "GET"])
def withdraw_desc():
        if not session.get("name"):
            return redirect("/login")
        else:
                       #current date
            dateTimeObj = datetime.now()
            doc_date = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
            doc_time = dateTimeObj.strftime("%H:%M:%S")
            sql_d = """SELECT
                    CASE WHEN COUNT(wd_id) = 0 
                        THEN 'WD-000001'::text 
                        WHEN COUNT(wd_id) > 0 
                        THEN CONCAT('WD-',LPAD((RIGHT(MAX(wd_id),6)::integer+1)::text, 6, 0::text) )
                    end as wd_id
                    FROM withdraw_item"""
            cur_d = gobal.con.cursor()
            cur_d.execute(sql_d)
            bill_no = cur_d.fetchone()
            doc_no = str(bill_no)
            doc_no = doc_no[2:11]
            session["wd_id"] = doc_no

            cur = gobal.con.cursor()
            sql = """SELECT wi.wd_date, wd.wd_id, wd.wd_qty, wi.emp_id FROM withdraw_detail wd
                    LEFT JOIN withdraw_item wi ON wi.wd_id = wd.wd_id"""
            cur.execute(sql)
            sc_list = cur.fetchall()

            curdt = gobal.con.cursor()
            sqldt = """SELECT row_number() OVER () as NO, p.p_id, p_name, wd.wd_qty, p_price, p_price * wd.wd_qty FROM withdraw_detail wd
                    LEFT JOIN product p ON p.p_id = wd.p_id 
                    LEFT JOIN withdraw_item wi ON wi.wd_id = wd.wd_id 
                    WHERE wi.wd_id is NULL"""
            curdt.execute(sqldt)
            detail_list = curdt.fetchall()

            #khor moun phou berk
            curem = gobal.con.cursor()
            sqlem = """SELECT emp_id, emp_name, CONCAT(emp_village, ', ', emp_district, ', ', emp_province) address, emp_tel, admin_name, admin_pwd, emp_gender, emp_bd, emp_province, emp_district, emp_village,
                    emp_province, emp_district, emp_village FROM employee e 
                    ORDER BY emp_id"""
            curem.execute(sqlem)
            emp_list = curem.fetchall()

            #ເລືອກສິນຄ້າ
            curp = gobal.con.cursor()
            sql_p = """SELECT p.p_id, p.p_name, p.p_price FROM product p
                    WHERE p.p_id NOT IN(
                        SELECT wd.p_id FROM withdraw_detail wd
                        LEFT JOIN withdraw_item wi ON wi.wd_id = wd.wd_id 
                                        WHERE wi.wd_id is NULL
                    ) ORDER BY p.p_id
                    """
            curp.execute(sql_p)
            pro_list = curp.fetchall()
            
            #ສະເເດງລາຍການໃນຕາຕະລາງເມື່ອກົດເພີ່ມ
            # sql_item = """SELECT row_number() OVER () as rnum, item_code, item_name,
            #             case when qty_update is null then qty
            #             else qty_update end as qty,
            #             unit_code, doc_no FROM ic_trans_detail where doc_no = %s and del_item IN (0,2) ORDER BY roworder"""
            # cur.execute(sql_item, (id,))
            # item_list = cur.fetchall()
            # ສະເເດງລວມທັງໝົດ
            sql_sum = """SELECT sum(p_price * wd.wd_qty) FROM withdraw_detail wd
                    LEFT JOIN product p ON p.p_id = wd.p_id 
                    LEFT JOIN withdraw_item wi ON wi.wd_id = wd.wd_id 
                    WHERE wi.wd_id is NULL"""
            cur.execute(sql_sum)
            sum_amount = cur.fetchall()
            gobal.con.commit()
            return render_template('order & withdraw/withdraw_desc.html', doc_date = doc_date, doc_time = doc_time, doc_no = doc_no, pro_list = pro_list, sc_list = sc_list, emp_list = emp_list, detail_list = detail_list, sum_amount = sum_amount, user=session['name'], roles = session['roles'], wd_id = session["wd_id"])

@app.route('/save_withdraw_desc', methods=['POST', 'GET'])
def save_withdraw_desc():
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            sql = """INSERT INTO withdraw_item(
                         wd_id, wd_date, emp_id, remark)
                         VALUES(%s,%s,%s,%s)
                  """
            
            wd_id = request.form['wd_id']
            wd_date = request.form['wd_date']
            emp_id = request.form['emp_id']
            remark = request.form['remark']
            data = (wd_id, wd_date, emp_id, remark)
            cur.execute(sql, (data))
            gobal.con.commit()
            return redirect(url_for('withdraw_item'))

# ກົດປຸ່ມຍົກເລີກເເລ້ວລົບ​ຂໍ້​ມູນ​ຢູ່ withdraw_detail ເເລະ ກັບໄປໜ້າ withdraw_item
@app.route('/back_button_withdraw_desc')
def back_button_withdraw_desc():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = "DELETE FROM withdraw_detail WHERE wd_id=%s"
            cur.execute(sql, (session["wd_id"],))
        return redirect(url_for('withdraw_item'))

@app.route('/save_withdraw_detail', methods=['POST', 'GET'])
def save_withdraw_detail():
    with gobal.con:
        cur = gobal.con.cursor()
        # cursp = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:

            wd_id = request.form['wd_id']
            p_id = request.form['p_id']
            wd_qty = request.form['wd_qty']

            sql = """INSERT INTO withdraw_detail(
                        wd_id, p_id, wd_qty)
                        VALUES(%s,%s,%s)
                """
            data = (wd_id, p_id, wd_qty)
            cur.execute(sql, data)

            #ເພີ່ມ stock
            cursor = gobal.con.cursor()
            up_stock = """UPDATE product 
                    SET p_qty = 
                    p_qty - (SELECT wd_qty FROM withdraw_detail WHERE p_id=%s AND wd_id = %s)
                    WHERE p_id = %s"""
            stock = (p_id, wd_id, p_id)
            cursor.execute(up_stock, stock)
            gobal.con.commit()
            return redirect(url_for('withdraw_desc'))

@app.route('/update_withdraw_desc/<string:id>', methods=['POST'])
def update_withdraw_desc(id):
    with gobal.con:
        cur = gobal.con.cursor()
        if not session.get("name"):
            return redirect("/login")
        else:
            wd_id = request.form['wd_id']
            wd_date = request.form['wd_date']
            emp_id = request.form['emp_id']
            remark = request.form['remark']

            cur.execute('UPDATE withdraw_item SET wd_id=%s, wd_date=%s, emp_id=%s, remark=%s WHERE wd_id=%s',
                        (wd_id, wd_date, emp_id, remark, (id,)))
            gobal.con.commit()
            return redirect(url_for('withdraw_desc'))

@app.route('/delete_withdraw_detail/<string:id>', methods=['POST', 'GET'])
def delete_withdraw_detail(id):
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
                    (SELECT wd_qty FROM withdraw_detail WHERE p_id=%s AND wd_id = %s)+p_qty
                    WHERE p_id = %s"""
            stock = ((id,),session["wd_id"], (id,)) 
            cursor.execute(up_stock, stock)

            sql = "DELETE FROM withdraw_detail WHERE p_id = %s"
            cur.execute(sql, (id,))
            gobal.con.commit()
            return redirect(url_for('withdraw_desc'))

@app.route('/delete_withdraw_desc/<string:id>')
def delete_withdraw_desc(id):
    if not session.get("name"):
        return redirect("/login")
    else:
        cur = gobal.con.cursor()
        sql = "delete from withdraw_item where wd_id=%s"
        cur.execute(sql, (id,))
        gobal.con.commit()
        return redirect(url_for('withdraw_desc'))

@app.route('/print_withdraw/<string:id>', methods=['GET'])
def print_withdraw(id):
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = """SELECT wi.wd_date, wd.wd_id, wi.emp_id, e.emp_name, emp_province||' '|| emp_district ||' '|| emp_village, emp_tel, remark FROM withdraw_detail wd
                    LEFT JOIN withdraw_item wi ON wi.wd_id = wd.wd_id
                    LEFT JOIN employee e ON e.emp_id = wi.emp_id
                    WHERE wi.wd_id = %s"""
            cur.execute(sql, (id,))
            show = cur.fetchone()

            curdt = gobal.con.cursor()
            sqldt = """SELECT row_number() OVER () as NO, p.p_id, p_name, wd.wd_qty, p_price, p_price * wd.wd_qty FROM withdraw_detail wd
                    LEFT JOIN product p ON p.p_id = wd.p_id 
                    LEFT JOIN withdraw_item wi ON wi.wd_id = wd.wd_id 
                    WHERE wi.wd_id = %s"""
            curdt.execute(sqldt, (id,))
            detail_list = curdt.fetchall()

            # ສະເເດງລວມທັງໝົດ
            sql_sum = """SELECT sum(wd.wd_qty) FROM withdraw_detail wd
                    LEFT JOIN product p ON p.p_id = wd.p_id 
                    LEFT JOIN withdraw_item wi ON wi.wd_id = wd.wd_id 
                    WHERE wi.wd_id = %s"""
            cur.execute(sql_sum, (id,))
            sum_amount = cur.fetchall()
            return render_template('order & withdraw/withdraw_bill.html', show = show, detail_list = detail_list, sum_amount = sum_amount, user=session['name'], roles = session['roles'])