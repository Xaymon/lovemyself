from flask import Flask, render_template, request, redirect, url_for, session, jsonify, json,flash
import psycopg2
from app import app
from kk_con import *
from datetime import datetime

@app.route('/profile', methods=['GET', 'POST'])
def profile(): 
    with gobal.con:
        cursor = gobal.con.cursor()
        if request.method == 'GET':

            if 'loggedin' in session:
                cursor.execute("""
                SELECT cust_id, cust_name, cust_village, cust_district, cust_province, cust_tel, user_name, user_pwd, cust_gender, cust_bd, a.picname, 
                cust_province, cust_district, cust_village 
                        FROM customer s
                LEFT JOIN province p ON p.prov_code=s.cust_province
                LEFT JOIN city c ON c.city_code=s.cust_district
                LEFT JOIN village v ON v.village_code=s.cust_village 
                LEFT JOIN account a ON s.user_name = a.username
                WHERE user_name = %s 
                """, [session['name']])
                account = cursor.fetchone()

                curp = gobal.con.cursor()
                sql_p = "SELECT prov_code, prov_name FROM province ORDER BY prov_code"
                curp.execute(sql_p)
                pro_list = curp.fetchall()
        
                return render_template('profile.html', account=account, pro_list=pro_list, user=session['name'], roles = session['roles'])
        else:
            cursor.execute("""
            SELECT cust_id, cust_name, cust_village, cust_district, cust_province, cust_tel, user_name, user_pwd, cust_gender, cust_bd, a.picname, 
            cust_province, cust_district, cust_village 
                    FROM customer s
            LEFT JOIN province p ON p.prov_code=s.cust_province
            LEFT JOIN city c ON c.city_code=s.cust_district
            LEFT JOIN village v ON v.village_code=s.cust_village 
            LEFT JOIN account a ON s.user_name = a.username
            WHERE user_name = %s 
            """, [session['name']])
            account = cursor.fetchone()

            curp = gobal.con.cursor()
            sql_p = "SELECT prov_code, prov_name FROM province ORDER BY prov_code"
            curp.execute(sql_p)
            pro_list = curp.fetchall()

            cust_id = request.form['cust_id']
            cust_name = request.form['cust_name']
            cust_gender = request.form['cust_gender']
            cust_bd = request.form['cust_bd']
            cust_village = request.form['cust_village']
            cust_district = request.form['cust_district']
            cust_province = request.form['cust_province']
            cust_tel = request.form['cust_tel']

            cursor.execute('UPDATE customer SET cust_id=%s, cust_name=%s, cust_gender=%s, cust_bd = %s, cust_village=%s, cust_district=%s, cust_province=%s, cust_tel=%s WHERE cust_id=%s',
                        (cust_id, cust_name, cust_gender, cust_bd, cust_village, cust_district, cust_province, cust_tel, cust_id))
            gobal.con.commit()
            flash('ອັບ​ເດດ​ສຳ​ເລັດ')
            return render_template('profile.html', account=account, pro_list=pro_list, user=session['name'], roles = session['roles'])

        return redirect(url_for('login'))
# @app.route('/update_profile/<string:id>', methods=['POST'])
# def update_profile(id): 
#     with gobal.con:
#         cursor = gobal.con.cursor()

#         if 'loggedin' in session:
#             cursor.execute("""
#             SELECT cust_id, cust_name, v.village_name, c.city_name, p.prov_name, cust_tel, user_name, user_pwd, cust_gender, cust_bd, a.picname, 
#             cust_province, cust_district, cust_village 
#                     FROM customer s
#             LEFT JOIN province p ON p.prov_code=s.cust_province
#             LEFT JOIN city c ON c.city_code=s.cust_district
#             LEFT JOIN village v ON v.village_code=s.cust_village 
#             LEFT JOIN account a ON s.user_name = a.username
#             WHERE user_name = %s 
#             """, [session['name']])
#             account = cursor.fetchone()

#             cust_id = request.form['cust_id']
#             cust_name = request.form['cust_name']
#             cust_gender = request.form['cust_gender']
#             cust_bd = request.form['cust_bd']
#             cust_village = request.form['cust_village']
#             cust_district = request.form['cust_district']
#             cust_province = request.form['cust_province']
#             cust_tel = request.form['cust_tel']

#             cursor.execute('UPDATE customer SET cust_id=%s, cust_name=%s, cust_gender=%s, cust_bd = %s, cust_village=%s, cust_district=%s, cust_province=%s, cust_tel=%s WHERE cust_id=%s',
#                         (cust_id, cust_name, cust_gender, cust_bd, cust_village, cust_district, cust_province, cust_tel, (id,)))
#             gobal.con.commit()
#             flash('ອັບ​ເດດ​ສຳ​ເລັດ')
    
#             return render_template('profile.html', account=account)

#         return redirect(url_for('login'))

@app.route('/user_account')
def user_account(): 
    with gobal.con:
        cursor = gobal.con.cursor()

        if 'loggedin' in session:
            cursor.execute("""SELECT * FROM account WHERE username = %s""", [session['name']])
            account = cursor.fetchone()
    
            return render_template('user_account.html', account=account, user=session['name'], roles = session['roles'])

        return redirect(url_for('login'))

@app.route('/about')
def about(): 
    with gobal.con:

        if 'loggedin' in session:
    
            return render_template('about.html', user=session['name'], roles = session['roles'])

        return redirect(url_for('login'))

@app.route('/user_price')
def user_price():
    with gobal.con:
        if not 'loggedin' in session:
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = """SELECT ROW_NUMBER() OVER (), a.service_name, b.sc_desc, c.wt_name, to_char(price,'999,999,999,999'), b.unit_clothes, b.sc_desc, c.wt_name FROM public.service_detail a 
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
            return render_template('user_price.html', sv_c=sv_c, rate_trans=rate_trans,water_type=water_type, doc_date = doc_date, doc_no = doc_no, user=session['name'], roles = session['roles'])

@app.route('/user_service')
def user_service():
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
            sqlc = """ SELECT bill_date, b.bill_id, c.cust_name, e.emp_name ,(SELECT sum(qty) FROM bill_detail WHERE bill_id=b.bill_id), (SELECT TO_CHAR(sum(pay_rc),'999,999,999,999') FROM bill_detail WHERE bill_id=b.bill_id),
                     status_laundry FROM bill b
                     LEFT JOIN employee e ON e.emp_id = b.emp_id
                     LEFT JOIN customer c ON c.cust_id = b.cust_id
                     WHERE c.cust_name = %s
                    """
            curc.execute(sqlc, (session['name'],))
            home_list = curc.fetchall()
            return render_template('home_service.html', home_list=home_list, user=session['name'], roles = session['roles'])

@app.route('/user_servicing')
def user_servicing():
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
            sqlc = """ SELECT bill_date, b.bill_id, c.cust_name, e.emp_name ,(SELECT sum(qty) FROM bill_detail WHERE bill_id=b.bill_id), (SELECT TO_CHAR(sum(pay_rc),'999,999,999,999') FROM bill_detail WHERE bill_id=b.bill_id),
                     status_laundry FROM bill b
                     LEFT JOIN employee e ON e.emp_id = b.emp_id
                     LEFT JOIN customer c ON c.cust_id = b.cust_id
                     WHERE status_laundry=0 AND c.cust_name = %s
                    """
            curc.execute(sqlc, (session['name'],))
            home_list = curc.fetchall()
            return render_template('home_servicing.html', home_list=home_list, user=session['name'], roles = session['roles'])