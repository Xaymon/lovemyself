from unicodedata import category
from flask import Flask, render_template, request, redirect, request_tearing_down, url_for, session, jsonify, json
from psycopg import Cursor
import psycopg2
from app import app
from kk_con import *
from datetime import datetime, date

@app.route('/income_rp')
def income_rp():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%Y-%m-%d")
            cur = gobal.con.cursor()
            # sql = """SELECT
            #             b.bill_date, b.bill_id, c.cust_id, c.cust_name, b.emp_id, e.emp_name, b.remark, (SELECT sum(qty) FROM bill_detail WHERE bill_id=b.bill_id),
            #              TO_CHAR(sum(pay_rc), '999G999G999G999D99'), (SELECT COUNT(service_id) FROM bill_detail WHERE bill_id = b.bill_id)
            #         FROM bill_detail bd
            #         LEFT JOIN bill b ON b.bill_id = bd.bill_id
            #         LEFT JOIN customer c ON c.cust_id = b.cust_id
            #         LEFT JOIN employee e ON e.emp_id = b.emp_id
            #         WHERE EXTRACT(month FROM b.bill_date::timestamp) = EXTRACT(month FROM current_timestamp::timestamp)
            #             AND EXTRACT(year FROM b.bill_date::timestamp) = EXTRACT(year FROM current_timestamp::timestamp)
            #         GROUP BY b.bill_id, b.bill_date, c.cust_id, c.cust_name, b.emp_id, e.emp_name, b.remark
            #         ORDER BY b.bill_id"""

            sql = """SELECT CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (DENSE_RANK() OVER(ORDER BY bd.bill_id)) ELSE NULL END as bill_date,  
                        ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc), 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (SELECT bill_date FROM bill WHERE bill_id=bd.bill_id) ELSE NULL END as bill_date,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN bd.bill_id ELSE NULL END as bill_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (CASE WHEN c.cust_name IS NULL THEN b.cust_id ELSE c.cust_name END) ELSE NULL END as cust_name, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN COALESCE (NULLIF(e.emp_name, ''), '-') ELSE NULL END as emp_name, 
                        service_id,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc DESC) = 1 THEN (SELECT remark FROM bill WHERE bill_id=bd.bill_id) ELSE ' ' END as REMARK,
                        qty, TO_CHAR(pay_rc, '999,999,999,999'), 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc DESC) = 1 THEN (SELECT(TO_CHAR(sum(pay_rc), '999,999,999,999')) FROM bill_detail WHERE bill_id=b.bill_id) ELSE NULL END as BILL_TOTAL,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (SELECT COUNT(bill_id) FROM bill_detail WHERE bill_id=b.bill_id) ELSE 0 END as rowspan,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (SELECT(sum(pay_rc)) FROM bill_detail WHERE bill_id=b.bill_id) ELSE 0 END as BILL_TOTAL
                     FROM bill_detail bd
                     LEFT JOIN bill b ON b.bill_id = bd.bill_id
                     LEFT JOIN customer c ON c.cust_id = b.cust_id
                     LEFT JOIN employee e ON e.emp_id = b.emp_id
                     WHERE EXTRACT(month FROM b.bill_date::timestamp) = EXTRACT(month FROM current_timestamp::timestamp)
                        AND EXTRACT(year FROM b.bill_date::timestamp) = EXTRACT(year FROM current_timestamp::timestamp)
                     ORDER BY bd.bill_id, pay_rc"""
            cur.execute(sql)
            report = cur.fetchall()

            curone = gobal.con.cursor()
            sqlone = "SELECT TO_CHAR(EXTRACT(month FROM current_timestamp::timestamp), '999')"
            curone.execute(sqlone)
            reportone = curone.fetchall()

            cursor = gobal.con.cursor()
            sql_total = """
                            SELECT
                                sum(bd.qty), 
                                TO_CHAR(sum(pay_rc), '999,999,999,999'), 
                                (SELECT TO_CHAR(sum(pay_rc), '999,999,999,999') FROM bill_detail bd LEFT JOIN bill b ON bd.bill_id = b.bill_id WHERE payment='1'), 
                                (SELECT TO_CHAR(sum(pay_rc), '999,999,999,999') FROM bill_detail bd LEFT JOIN bill b ON bd.bill_id = b.bill_id WHERE payment='2')
                            FROM bill_detail bd
                             LEFT JOIN bill b ON b.bill_id = bd.bill_id
                             LEFT JOIN customer c ON c.cust_id = b.cust_id
                             LEFT JOIN employee e ON e.emp_id = b.emp_id
                             WHERE EXTRACT(month FROM b.bill_date::timestamp) = EXTRACT(month FROM current_timestamp::timestamp)
                                 AND EXTRACT(year FROM b.bill_date::timestamp) = EXTRACT(year FROM current_timestamp::timestamp)
                        """
            cursor.execute(sql_total)
            total = cursor.fetchall()
            return render_template('/report/income.html', total=total, report=report, reportone=reportone, from_date=timestampStr, to_date=timestampStr,user=session['name'], roles = session['roles'])
@app.route('/income_rp_date', methods=['POST'])
def income_rp_date():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            from_date = request.form['from_date']
            to_date = request.form['to_date']
            print(from_date, to_date)
            cur = gobal.con.cursor()
            sql = """SELECT CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (DENSE_RANK() OVER(ORDER BY bd.bill_id)) ELSE NULL END as bill_date,  
                        ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc), 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (SELECT bill_date FROM bill WHERE bill_id=bd.bill_id) ELSE NULL END as bill_date,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN bd.bill_id ELSE NULL END as bill_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (CASE WHEN c.cust_name IS NULL THEN b.cust_id ELSE c.cust_name END) ELSE NULL END as cust_name, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN COALESCE (NULLIF(e.emp_name, ''), '-') ELSE NULL END as emp_name, 
                        service_id,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc DESC) = 1 THEN (SELECT remark FROM bill WHERE bill_id=bd.bill_id) ELSE ' ' END as REMARK,
                        qty, TO_CHAR(pay_rc, '999,999,999,999'),  
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc DESC) = 1 THEN (SELECT(TO_CHAR(sum(pay_rc), '999,999,999,999')) FROM bill_detail WHERE bill_id=b.bill_id) ELSE NULL END as BILL_TOTAL,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (SELECT COUNT(bill_id) FROM bill_detail WHERE bill_id=b.bill_id) ELSE 0 END as rowspan,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (SELECT(sum(pay_rc)) FROM bill_detail WHERE bill_id=b.bill_id) ELSE 0 END as BILL_TOTAL
                     FROM bill_detail bd
                     LEFT JOIN bill b ON b.bill_id = bd.bill_id
                     LEFT JOIN customer c ON c.cust_id = b.cust_id
                     LEFT JOIN employee e ON e.emp_id = b.emp_id
                     WHERE bill_date::date between %s and %s
                     ORDER BY bd.bill_id, pay_rc
                    """
            data = (from_date, to_date,)
            cur.execute(sql, data)
            report = cur.fetchall()

            curtwo = gobal.con.cursor()
            sqltwo = "SELECT TO_CHAR(DATE %s, 'DD-MM-YYYY') || ' ຫາ ' ||TO_CHAR(DATE %s, 'DD-MM-YYYY')"
            data2 = (from_date, to_date,)
            curtwo.execute(sqltwo, data2)
            reporttwo = curtwo.fetchmany()

            cursor = gobal.con.cursor()
            sql_total = """SELECT
                                sum(bd.qty), TO_CHAR(sum(pay_rc), '999,999,999,999D99') 
                            FROM bill_detail bd
                             LEFT JOIN bill b ON b.bill_id = bd.bill_id
                             LEFT JOIN customer c ON c.cust_id = b.cust_id
                             LEFT JOIN employee e ON e.emp_id = b.emp_id
                            WHERE bill_date::date between %s and %s 
                        """
            total = (from_date, to_date,)
            cursor.execute(sql_total, total)
                    # to_char(total_value_2,'999G999G999G999D99')

            total = cursor.fetchall()
            return render_template('/report/income.html', total=total, report=report, reporttwo=reporttwo, from_date=from_date, to_date=to_date,user=session['name'], roles = session['roles'])

@app.route('/outcome_rp')
def outcome_rp():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%Y-%m-%d")
            cur = gobal.con.cursor()
            sql = """SELECT CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN (DENSE_RANK() OVER(ORDER BY rd.rc_id)) ELSE NULL END as rc_date,
                        ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price), 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN (SELECT rc_date FROM recieve WHERE rc_id=rd.rc_id) ELSE NULL END as rc_date, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN rd.rc_id ELSE NULL END as rc_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN COALESCE (NULLIF((SELECT order_id FROM recieve WHERE rc_id=rd.rc_id), ''), '-') ELSE NULL END as order_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN COALESCE (NULLIF(s.sup_name, ''), '-') ELSE NULL END as sup_name, 
                        rd.p_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price DESC) = 1 THEN (SELECT remark FROM recieve WHERE rc_id=rd.rc_id) ELSE ' ' END as REMARK,
                        rd.rc_qty, TO_CHAR(rc_price, '999,999,999,999'), 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price DESC) = 1 THEN (SELECT(TO_CHAR(sum(rc_price), '999,999,999,999')) FROM recieve_detail LEFT JOIN product p ON p.p_id = rd.p_id WHERE rc_id=r.rc_id) ELSE ' ' END as TOTAL, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN (SELECT COUNT(rc_id) FROM recieve_detail WHERE rc_id=r.rc_id) ELSE 0 END as rowspan,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN (SELECT(sum(rc_price)) FROM recieve_detail WHERE rc_id=r.rc_id) ELSE 0 END as BILL_TOTAL
                    FROM recieve_detail rd
                    LEFT JOIN product p ON p.p_id = rd.p_id
                    LEFT JOIN recieve r ON r.rc_id = rd.rc_id
                    LEFT JOIN supplier s ON s.sup_id = r.sup_id
                    WHERE EXTRACT(month FROM r.rc_date::timestamp) = EXTRACT(month FROM current_timestamp::timestamp)
                        AND EXTRACT(year FROM r.rc_date::timestamp) = EXTRACT(year FROM current_timestamp::timestamp)
                    ORDER BY rd.rc_id, rc_price"""
            cur.execute(sql)
            report = cur.fetchall()

            curone = gobal.con.cursor()
            sqlone = "SELECT TO_CHAR(EXTRACT(month FROM current_timestamp::timestamp), '999')"
            curone.execute(sqlone)
            reportone = curone.fetchall()

            cursor = gobal.con.cursor()
            sql_total = """SELECT
                                sum(rd.rc_qty), TO_CHAR(sum(rd.rc_price), '999,999,999,999') 
                            FROM recieve_detail rd
                             LEFT JOIN product p ON p.p_id = rd.p_id
                             LEFT JOIN recieve r ON r.rc_id = rd.rc_id
                             LEFT JOIN supplier s ON s.sup_id = r.sup_id
                            WHERE EXTRACT(month FROM r.rc_date::timestamp) = EXTRACT(month FROM current_timestamp::timestamp)
                                AND EXTRACT(year FROM r.rc_date::timestamp) = EXTRACT(year FROM current_timestamp::timestamp)
                        """
            cursor.execute(sql_total)
            total = cursor.fetchall()
            return render_template('/report/outcome.html', total=total, report=report, reportone=reportone, from_date=timestampStr, to_date=timestampStr,user=session['name'], roles = session['roles'])
@app.route('/outcome_rp_date', methods=['POST'])
def outcome_rp_date():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            from_date = request.form['from_date']
            to_date = request.form['to_date']
            print(from_date, to_date)
            cur = gobal.con.cursor()
            sql = """SELECT CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN (DENSE_RANK() OVER(ORDER BY rd.rc_id)) ELSE NULL END as rc_date,
                        ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price), 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN (SELECT rc_date FROM recieve WHERE rc_id=rd.rc_id) ELSE NULL END as rc_date, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN rd.rc_id ELSE NULL END as rc_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN COALESCE (NULLIF((SELECT order_id FROM recieve WHERE rc_id=rd.rc_id), ''), '-') ELSE NULL END as order_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN COALESCE (NULLIF(s.sup_name, ''), '-') ELSE NULL END as sup_name, 
                        rd.p_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price DESC) = 1 THEN (SELECT remark FROM recieve WHERE rc_id=rd.rc_id) ELSE ' ' END as REMARK,
                        rd.rc_qty, TO_CHAR(rc_price, '999,999,999,999'), 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price DESC) = 1 THEN (SELECT(TO_CHAR(sum(rc_price), '999,999,999,999')) FROM recieve_detail LEFT JOIN product p ON p.p_id = rd.p_id WHERE rc_id=r.rc_id) ELSE ' ' END as TOTAL, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN (SELECT COUNT(rc_id) FROM recieve_detail WHERE rc_id=r.rc_id) ELSE 0 END as rowspan,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN (SELECT(sum(rc_price)) FROM recieve_detail WHERE rc_id=r.rc_id) ELSE 0 END as BILL_TOTAL
                    FROM recieve_detail rd
                    LEFT JOIN product p ON p.p_id = rd.p_id
                    LEFT JOIN recieve r ON r.rc_id = rd.rc_id
                    LEFT JOIN supplier s ON s.sup_id = r.sup_id
                    WHERE rc_date::date between %s and %s
                    ORDER BY rd.rc_id, rc_price
                    """
            data = (from_date, to_date,)
            cur.execute(sql, data)
            report = cur.fetchall()

            curtwo = gobal.con.cursor()
            sqltwo = "SELECT TO_CHAR(DATE %s, 'DD-MM-YYYY') || ' ຫາ ' ||TO_CHAR(DATE %s, 'DD-MM-YYYY')"
            data2 = (from_date, to_date,)
            curtwo.execute(sqltwo, data2)
            reporttwo = curtwo.fetchmany()

            cursor = gobal.con.cursor()
            sql_total = """SELECT
                                sum(rd.rc_qty), TO_CHAR(sum(rd.rc_price), '999,999,999,999') 
                            FROM recieve_detail rd
                            LEFT JOIN product p ON p.p_id = rd.p_id
                            LEFT JOIN recieve r ON r.rc_id = rd.rc_id
                            LEFT JOIN supplier s ON s.sup_id = r.sup_id
                            WHERE rc_date::date between %s and %s 
                        """
            total = (from_date, to_date,)
            cursor.execute(sql_total, total)
                    # to_char(total_value_2,'999G999G999G999D99')

            total = cursor.fetchall()
            return render_template('/report/outcome.html', total=total, report=report, reporttwo=reporttwo, from_date=from_date, to_date=to_date,user=session['name'], roles = session['roles'])

# @app.route('/cashdollar')
# def cashdollar():
#     with gobal.con:
#         if not session.get("name"):
#             return redirect("/login")
#         else:
#             dateTimeObj = datetime.now()
#             timestampStr = dateTimeObj.strftime("%Y-%m-%d")
#             cur = gobal.con.cursor()
#             sql = """SELECT to_char(doc_date,'DD-MM-YYY HH24:MI:SS'),doc_no,case when trans_type='0' or trans_type='1' then 'ໂອນ' when trans_type='2' 
#                     then 'ແລກປ່ຽນ' when trans_type='5' then 'ລາຍຮັບອື່ນໆ' when  trans_type='6' then 'ລາຍຈ່າຍອື່ນໆ' when  trans_type='11' then 'ຝາກທະນາຄານ' 
#                     when  trans_type='12' then 'ຖອນຈາກທະນາຄານ'  end as trans_type,
#                     to_char(case when calc_flag='1' then amount_1 else 0 end , '999G999G999G999D99') as Amount_in, 
#                     to_char(case when calc_flag='-1' then amount_1 else 0 end , '999G999G999G999D99') as Amount_out, 
#                     to_char(SUM((case when calc_flag='1' then amount_1 else 0 end) - (case when calc_flag='-1' then amount_1 else 0 end))
#                     OVER (ORDER BY roworder ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), '999G999G999G999D99')  as Balance
#                                         FROM cb_trans_detail where trans_number='02' order by roworder ASC"""
#             cur.execute(sql)
#             dollar = cur.fetchall()
#             return render_template('/report/cash/dolla.html', dollar=dollar, from_date=timestampStr, to_date=timestampStr,user=session.get("roles"))

@app.route('/service_rp')
def service_rp():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%Y-%m-%d")
            cur = gobal.con.cursor()
            sql = """SELECT CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (DENSE_RANK() OVER(ORDER BY bd.bill_id)) ELSE NULL END as bill_date,  
                        ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc), 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (SELECT bill_date FROM bill WHERE bill_id=bd.bill_id) ELSE NULL END as bill_date,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN bd.bill_id ELSE NULL END as bill_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (CASE WHEN c.cust_name IS NULL THEN b.cust_id ELSE c.cust_name END) ELSE NULL END as cust_name, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN COALESCE (NULLIF(e.emp_name, ''), '-') ELSE NULL END as emp_name, 
                        service_id,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc DESC) = 1 THEN (SELECT remark FROM bill WHERE bill_id=bd.bill_id) ELSE ' ' END as REMARK,
                        qty, TO_CHAR(pay_rc, '999,999,999,999'), 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc DESC) = 1 THEN (SELECT(TO_CHAR(sum(pay_rc), '999,999,999,999')) FROM bill_detail WHERE bill_id=b.bill_id) ELSE NULL END as BILL_TOTAL,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (SELECT COUNT(bill_id) FROM bill_detail WHERE bill_id=b.bill_id) ELSE 0 END as rowspan,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (SELECT(sum(pay_rc)) FROM bill_detail WHERE bill_id=b.bill_id) ELSE 0 END as BILL_TOTAL
                     FROM bill_detail bd
                     LEFT JOIN bill b ON b.bill_id = bd.bill_id
                     LEFT JOIN customer c ON c.cust_id = b.cust_id
                     LEFT JOIN employee e ON e.emp_id = b.emp_id
                     WHERE EXTRACT(month FROM b.bill_date::timestamp) = EXTRACT(month FROM current_timestamp::timestamp)
                        AND EXTRACT(year FROM b.bill_date::timestamp) = EXTRACT(year FROM current_timestamp::timestamp)
                     ORDER BY bd.bill_id, pay_rc"""
            cur.execute(sql)
            report = cur.fetchall()
            
            curone = gobal.con.cursor()
            sqlone = "SELECT TO_CHAR(EXTRACT(month FROM current_timestamp::timestamp), '999')"
            curone.execute(sqlone)
            reportone = curone.fetchall()

            cursor = gobal.con.cursor()
            sql_total = """SELECT
                                sum(bd.qty), TO_CHAR(sum(pay_rc), '999,999,999,999') 
                            FROM bill_detail bd
                             LEFT JOIN bill b ON b.bill_id = bd.bill_id
                             LEFT JOIN customer c ON c.cust_id = b.cust_id
                             LEFT JOIN employee e ON e.emp_id = b.emp_id
                            WHERE EXTRACT(month FROM b.bill_date::timestamp) = EXTRACT(month FROM current_timestamp::timestamp)
                                AND EXTRACT(year FROM b.bill_date::timestamp) = EXTRACT(year FROM current_timestamp::timestamp)
                        """
            cursor.execute(sql_total)
            total = cursor.fetchall()
            return render_template('/report/service.html', total=total, report=report, reportone=reportone, from_date=timestampStr, to_date=timestampStr,user=session['name'], roles = session['roles'])
@app.route('/service_rp_date', methods=['POST'])
def service_rp_date():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            from_date = request.form['from_date']
            to_date = request.form['to_date']
            print(from_date, to_date)
            cur = gobal.con.cursor()
            sql = """SELECT CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (DENSE_RANK() OVER(ORDER BY bd.bill_id)) ELSE NULL END as bill_date,  
                        ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc), 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (SELECT bill_date FROM bill WHERE bill_id=bd.bill_id) ELSE NULL END as bill_date,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN bd.bill_id ELSE NULL END as bill_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (CASE WHEN c.cust_name IS NULL THEN b.cust_id ELSE c.cust_name END) ELSE NULL END as cust_name, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN COALESCE (NULLIF(e.emp_name, ''), '-') ELSE NULL END as emp_name, 
                        service_id,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc DESC) = 1 THEN (SELECT remark FROM bill WHERE bill_id=bd.bill_id) ELSE ' ' END as REMARK,
                        qty, TO_CHAR(pay_rc, '999,999,999,999'), 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc DESC) = 1 THEN (SELECT(TO_CHAR(sum(pay_rc), '999,999,999,999')) FROM bill_detail WHERE bill_id=b.bill_id) ELSE NULL END as BILL_TOTAL,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (SELECT COUNT(bill_id) FROM bill_detail WHERE bill_id=b.bill_id) ELSE 0 END as rowspan,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY bd.bill_id ORDER BY pay_rc) = 1 THEN (SELECT(sum(pay_rc)) FROM bill_detail WHERE bill_id=b.bill_id) ELSE 0 END as BILL_TOTAL
                     FROM bill_detail bd
                     LEFT JOIN bill b ON b.bill_id = bd.bill_id
                     LEFT JOIN customer c ON c.cust_id = b.cust_id
                     LEFT JOIN employee e ON e.emp_id = b.emp_id
                     WHERE bill_date::date between %s and %s
                     ORDER BY bd.bill_id, pay_rc
                    """
            data = (from_date, to_date,)
            cur.execute(sql, data)
            report = cur.fetchall()

            curtwo = gobal.con.cursor()
            sqltwo = "SELECT TO_CHAR(DATE %s, 'DD-MM-YYYY') || ' ຫາ ' ||TO_CHAR(DATE %s, 'DD-MM-YYYY')"
            data2 = (from_date, to_date,)
            curtwo.execute(sqltwo, data2)
            reporttwo = curtwo.fetchmany()

            cursor = gobal.con.cursor()
            sql_total = """SELECT
                                sum(bd.qty), TO_CHAR(sum(pay_rc), '999,999,999,999') 
                            FROM bill_detail bd
                             LEFT JOIN bill b ON b.bill_id = bd.bill_id
                             LEFT JOIN customer c ON c.cust_id = b.cust_id
                             LEFT JOIN employee e ON e.emp_id = b.emp_id
                            WHERE bill_date::date between %s and %s 
                        """
            total = (from_date, to_date,)
            cursor.execute(sql_total, total)
                    # to_char(total_value_2,'999G999G999G999D99')

            total = cursor.fetchall()
            return render_template('/report/service.html', total=total, report=report, reporttwo=reporttwo, from_date=from_date, to_date=to_date,user=session['name'], roles = session['roles'])

@app.route('/order_rp')
def order_rp():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%Y-%m-%d")
            cur = gobal.con.cursor()
            sql = """SELECT CASE WHEN ROW_NUMBER() OVER(PARTITION BY od.order_id ORDER BY order_qty) = 1 THEN (DENSE_RANK() OVER(ORDER BY od.order_id)) ELSE NULL END as order_date,  
                        ROW_NUMBER() OVER(PARTITION BY od.order_id ORDER BY order_qty), 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY od.order_id ORDER BY order_qty) = 1 THEN (SELECT order_date FROM order_table WHERE order_id=od.order_id) ELSE NULL END as order_date, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY od.order_id ORDER BY order_qty) = 1 THEN od.order_id ELSE NULL END as order_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY od.order_id ORDER BY order_qty) = 1 THEN COALESCE (NULLIF((SELECT sup_id FROM order_table WHERE order_id=od.order_id), ''), '-') ELSE NULL END as sup_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY od.order_id ORDER BY order_qty) = 1 THEN COALESCE (NULLIF(s.sup_name, ''), '-') ELSE NULL END as sup_name, 
                        od.p_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY od.order_id ORDER BY order_qty DESC) = 1 THEN (SELECT remark FROM order_table WHERE order_id=od.order_id) ELSE ' ' END as REMARK, 
                        order_qty, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY od.order_id ORDER BY order_qty) = 1 THEN (SELECT sum(order_qty) FROM order_detail WHERE order_id=ot.order_id) ELSE NULL END as TOTAL, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY od.order_id ORDER BY order_qty) = 1 THEN (SELECT COUNT(order_id) FROM order_detail WHERE order_id=ot.order_id) ELSE 0 END as rowspan
                    FROM order_detail od
                    LEFT JOIN product p ON p.p_id = od.p_id
                    LEFT JOIN order_table ot ON ot.order_id = od.order_id
                    LEFT JOIN supplier s ON s.sup_id = ot.sup_id
                    ORDER BY od.order_id, order_qty"""
            cur.execute(sql)
            report = cur.fetchall()

            curone = gobal.con.cursor()
            sqlone = "SELECT TO_CHAR(EXTRACT(month FROM current_timestamp::timestamp), '999')"
            curone.execute(sqlone)
            reportone = curone.fetchall()

            cursor = gobal.con.cursor()
            sql_total = """SELECT
                                sum(od.order_qty)
                            FROM order_detail od
                            LEFT JOIN product p ON p.p_id = od.p_id
                            LEFT JOIN order_table ot ON ot.order_id = od.order_id
                            LEFT JOIN supplier s ON s.sup_id = ot.sup_id
                        """
            cursor.execute(sql_total)
            total = cursor.fetchall()
            return render_template('/report/order.html', total=total, report=report, reportone=reportone, from_date=timestampStr, to_date=timestampStr,user=session['name'], roles = session['roles'])
@app.route('/order_rp_date', methods=['POST'])
def order_rp_date():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            from_date = request.form['from_date']
            to_date = request.form['to_date']
            print(from_date, to_date)
            cur = gobal.con.cursor()
            sql = """SELECT
                        ot.order_date, ot.order_id, ot.sup_id, s.sup_name, ot.remark, (SELECT sum(order_qty) FROM order_detail WHERE order_id=ot.order_id)
                    FROM order_detail od
                    LEFT JOIN product p ON p.p_id = od.p_id
                    LEFT JOIN order_table ot ON ot.order_id = od.order_id
                    LEFT JOIN supplier s ON s.sup_id = ot.sup_id
                    WHERE order_date::date between %s and %s
                    GROUP BY ot.order_id, ot.order_date, ot.sup_id, s.sup_name, ot.remark
                    ORDER BY ot.order_id 
                    """
            data = (from_date, to_date,)
            cur.execute(sql, data)
            report = cur.fetchall()

            curtwo = gobal.con.cursor()
            sqltwo = "SELECT TO_CHAR(DATE %s, 'DD-MM-YYYY') || ' ຫາ ' ||TO_CHAR(DATE %s, 'DD-MM-YYYY')"
            data2 = (from_date, to_date,)
            curtwo.execute(sqltwo, data2)
            reporttwo = curtwo.fetchmany()

            cursor = gobal.con.cursor()
            sql_total = """SELECT
                                sum(od.order_qty)
                            FROM order_detail od
                            LEFT JOIN product p ON p.p_id = od.p_id
                            LEFT JOIN order_table ot ON ot.order_id = od.order_id
                            LEFT JOIN supplier s ON s.sup_id = ot.sup_id
                            WHERE order_date::date between %s and %s 
                        """
            total = (from_date, to_date,)
            cursor.execute(sql_total, total)
                    # to_char(total_value_2,'999G999G999G999D99')

            total = cursor.fetchall()
            return render_template('/report/order.html', total=total, report=report, reporttwo=reporttwo, from_date=from_date, to_date=to_date,user=session['name'], roles = session['roles'])


# @app.route('/dollatbydate', methods=['POST'])
# def dollatbydate():
#     with gobal.con:
#         if not session.get("name"):
#             return redirect("/login")
#         else:
#             from_date = request.form['from_date']
#             to_date = request.form['to_date']
#             print(from_date, to_date)
#             cur = gobal.con.cursor()
#             sql = """SELECT  to_char(doc_date,'DD-MM-YYY HH24:MI:SS'),doc_no,case when trans_type='0' or trans_type='1' then 'ໂອນ' when trans_type='2' 
#                     then 'ແລກປ່ຽນ' when trans_type='5' then 'ລາຍຮັບອື່ນໆ' when  trans_type='6' then 'ລາຍຈ່າຍອື່ນໆ' when  trans_type='11' then 'ຝາກທະນາຄານ' 
#                     when  trans_type='12' then 'ຖອນຈາກທະນາຄານ'  end as trans_type,
#                     to_char(case when calc_flag='1' then amount_1 else 0 end , '999G999G999G999D99') as Amount_in, 
#                     to_char(case when calc_flag='-1' then amount_1 else 0 end , '999G999G999G999D99') as Amount_out, 
#                     to_char(SUM((case when calc_flag='1' then amount_1 else 0 end) - (case when calc_flag='-1' then amount_1 else 0 end))
#                     OVER (ORDER BY roworder ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), '999G999G999G999D99')  as Balance
#                                         FROM cb_trans_detail where trans_number='00' and doc_date::date between %s and %s order by roworder ASC"""
#             data = (from_date, to_date,)
#             cur.execute(sql, data)
#             kip = cur.fetchall()
#             return render_template('/report/cash/kip.html', kip=kip, from_date=from_date, to_date=to_date,user=session.get("roles"))

@app.route('/recieve_rp')
def recieve_rp():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%Y-%m-%d")
            cur = gobal.con.cursor()
            sql = """SELECT CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN (DENSE_RANK() OVER(ORDER BY rd.rc_id)) ELSE NULL END as rc_date,
                        ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price), 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN (SELECT rc_date FROM recieve WHERE rc_id=rd.rc_id) ELSE NULL END as rc_date, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN rd.rc_id ELSE NULL END as rc_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN COALESCE (NULLIF((SELECT order_id FROM recieve WHERE rc_id=rd.rc_id), ''), '-') ELSE NULL END as order_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN COALESCE (NULLIF(s.sup_name, ''), '-') ELSE NULL END as sup_name, 
                        rd.p_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price DESC) = 1 THEN (SELECT remark FROM recieve WHERE rc_id=rd.rc_id) ELSE ' ' END as REMARK,
                        rd.rc_qty, TO_CHAR(rc_price, '999,999,999,999'), 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price DESC) = 1 THEN (SELECT(TO_CHAR(sum(rc_price), '999,999,999,999')) FROM recieve_detail LEFT JOIN product p ON p.p_id = rd.p_id WHERE rc_id=r.rc_id) ELSE ' ' END as TOTAL, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN (SELECT COUNT(rc_id) FROM recieve_detail WHERE rc_id=r.rc_id) ELSE 0 END as rowspan,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN (SELECT(sum(rc_price)) FROM recieve_detail WHERE rc_id=r.rc_id) ELSE 0 END as BILL_TOTAL
                    FROM recieve_detail rd
                    LEFT JOIN product p ON p.p_id = rd.p_id
                    LEFT JOIN recieve r ON r.rc_id = rd.rc_id
                    LEFT JOIN supplier s ON s.sup_id = r.sup_id
                    WHERE EXTRACT(month FROM r.rc_date::timestamp) = EXTRACT(month FROM current_timestamp::timestamp)
                        AND EXTRACT(year FROM r.rc_date::timestamp) = EXTRACT(year FROM current_timestamp::timestamp)
                    ORDER BY rd.rc_id, rc_price"""
            cur.execute(sql)
            report = cur.fetchall()

            curone = gobal.con.cursor()
            sqlone = "SELECT TO_CHAR(EXTRACT(month FROM current_timestamp::timestamp), '999')"
            curone.execute(sqlone)
            reportone = curone.fetchall()

            cursor = gobal.con.cursor()
            sql_total = """SELECT
                                sum(rd.rc_qty), TO_CHAR(sum(rd.rc_price), '999,999,999,999') 
                            FROM recieve_detail rd
                            LEFT JOIN product p ON p.p_id = rd.p_id
                            LEFT JOIN recieve r ON r.rc_id = rd.rc_id
                            LEFT JOIN supplier s ON s.sup_id = r.sup_id
                        WHERE EXTRACT(month FROM r.rc_date::timestamp) = EXTRACT(month FROM current_timestamp::timestamp)
                            AND EXTRACT(year FROM r.rc_date::timestamp) = EXTRACT(year FROM current_timestamp::timestamp)
                        """
            cursor.execute(sql_total)
            total = cursor.fetchall()
            return render_template('/report/recieve.html', total=total, report=report, reportone=reportone, from_date=timestampStr, to_date=timestampStr,user=session['name'], roles = session['roles'])
@app.route('/recieve_rp_date', methods=['POST'])
def recieve_rp_date():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            from_date = request.form['from_date']
            to_date = request.form['to_date']
            print(from_date, to_date)
            cur = gobal.con.cursor()
            sql = """SELECT CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN (DENSE_RANK() OVER(ORDER BY rd.rc_id)) ELSE NULL END as rc_date,
                        ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price), 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN (SELECT rc_date FROM recieve WHERE rc_id=rd.rc_id) ELSE NULL END as rc_date, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN rd.rc_id ELSE NULL END as rc_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN COALESCE (NULLIF((SELECT order_id FROM recieve WHERE rc_id=rd.rc_id), ''), '-') ELSE NULL END as order_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN COALESCE (NULLIF(s.sup_name, ''), '-') ELSE NULL END as sup_name, 
                        rd.p_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price DESC) = 1 THEN (SELECT remark FROM recieve WHERE rc_id=rd.rc_id) ELSE ' ' END as REMARK,
                        rd.rc_qty, TO_CHAR(rc_price, '999,999,999,999'), 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price DESC) = 1 THEN (SELECT(TO_CHAR(sum(rc_price), '999,999,999,999')) FROM recieve_detail LEFT JOIN product p ON p.p_id = rd.p_id WHERE rc_id=r.rc_id) ELSE ' ' END as TOTAL, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN (SELECT COUNT(rc_id) FROM recieve_detail WHERE rc_id=r.rc_id) ELSE 0 END as rowspan,
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY rd.rc_id ORDER BY rc_price) = 1 THEN (SELECT(sum(rc_price)) FROM recieve_detail WHERE rc_id=r.rc_id) ELSE 0 END as BILL_TOTAL
                    FROM recieve_detail rd
                    LEFT JOIN product p ON p.p_id = rd.p_id
                    LEFT JOIN recieve r ON r.rc_id = rd.rc_id
                    LEFT JOIN supplier s ON s.sup_id = r.sup_id
                    WHERE rc_date::date between %s and %s
                    ORDER BY rd.rc_id, rc_price
                    """
            data = (from_date, to_date,)
            cur.execute(sql, data)
            report = cur.fetchall()

            curtwo = gobal.con.cursor()
            sqltwo = "SELECT TO_CHAR(DATE %s, 'DD-MM-YYYY') || ' ຫາ ' ||TO_CHAR(DATE %s, 'DD-MM-YYYY')"
            data2 = (from_date, to_date,)
            curtwo.execute(sqltwo, data2)
            reporttwo = curtwo.fetchmany()

            cursor = gobal.con.cursor()
            sql_total = """SELECT
                                sum(rd.rc_qty), TO_CHAR(sum(rd.price), '999,999,999,999') 
                            FROM recieve_detail rd
                            LEFT JOIN product p ON p.p_id = rd.p_id
                            LEFT JOIN recieve r ON r.rc_id = rd.rc_id
                            LEFT JOIN supplier s ON s.sup_id = r.sup_id
                            WHERE rc_date::date between %s and %s 
                        """
            total = (from_date, to_date,)
            cursor.execute(sql_total, total)
                    # to_char(total_value_2,'999G999G999G999D99')

            total = cursor.fetchall()
            return render_template('/report/recieve.html', total=total, report=report, reporttwo=reporttwo, from_date=from_date, to_date=to_date,user=session['name'], roles = session['roles'])

@app.route('/withdraw_rp')
def withdraw_rp():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%Y-%m-%d")
            cur = gobal.con.cursor()
            sql = """SELECT CASE WHEN ROW_NUMBER() OVER(PARTITION BY wd.wd_id ORDER BY wd_qty) = 1 THEN (DENSE_RANK() OVER(ORDER BY wd.wd_id)) ELSE NULL END as ordinal,  
                        ROW_NUMBER() OVER(PARTITION BY wd.wd_id ORDER BY wd_qty), 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY wd.wd_id ORDER BY wd_qty) = 1 THEN (SELECT wd_date FROM withdraw_item WHERE wd_id=wi.wd_id) ELSE NULL END as wd_date, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY wd.wd_id ORDER BY wd_qty) = 1 THEN wd.wd_id ELSE NULL END as wd_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY wd.wd_id ORDER BY wd_qty) = 1 THEN COALESCE (NULLIF((SELECT emp_id FROM withdraw_item WHERE wd_id=wi.wd_id), ''), '-') ELSE NULL END as emp_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY wd.wd_id ORDER BY wd_qty) = 1 THEN COALESCE (NULLIF(e.emp_name, ''), '-') ELSE NULL END as emp_name, 
                        wd.p_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY wd.wd_id ORDER BY wd_qty DESC) = 1 THEN (SELECT remark FROM withdraw_item WHERE wd_id=wd.wd_id) ELSE ' ' END as REMARK, 
                        wd.wd_qty, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY wd.wd_id ORDER BY wd_qty DESC) = 1 THEN (SELECT sum(wd_qty) FROM withdraw_detail WHERE wd_id=wi.wd_id) ELSE NULL END as TOTAL, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY wd.wd_id ORDER BY wd_qty DESC) = 1 THEN (SELECT COUNT(wd_id) FROM withdraw_detail WHERE wd_id=wi.wd_id) ELSE 0 END as rowspan
                    FROM withdraw_detail wd
                    LEFT JOIN product p ON p.p_id = wd.p_id
                    LEFT JOIN withdraw_item wi ON wi.wd_id = wd.wd_id
                    LEFT JOIN employee e ON e.emp_id = wi.emp_id
                    ORDER BY wd.wd_id, wd.wd_qty"""
            cur.execute(sql)
            report = cur.fetchall()

            curone = gobal.con.cursor()
            sqlone = "SELECT TO_CHAR(EXTRACT(month FROM current_timestamp::timestamp), '999')"
            curone.execute(sqlone)
            reportone = curone.fetchall()

            cursor = gobal.con.cursor()
            sql_total = """SELECT
                                sum(wd.wd_qty) 
                            FROM withdraw_detail wd
                            LEFT JOIN product p ON p.p_id = wd.p_id
                            LEFT JOIN withdraw_item wi ON wi.wd_id = wd.wd_id
                            LEFT JOIN employee e ON e.emp_id = wi.emp_id
                        """
            cursor.execute(sql_total)
            total = cursor.fetchall()
            return render_template('/report/withdraw.html', total=total, report=report, reportone=reportone, from_date=timestampStr, to_date=timestampStr,user=session['name'], roles = session['roles'])
@app.route('/withdraw_rp_date', methods=['POST'])
def withdraw_rp_date():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            from_date = request.form['from_date']
            to_date = request.form['to_date']
            print(from_date, to_date)
            cur = gobal.con.cursor()
            sql = """SELECT CASE WHEN ROW_NUMBER() OVER(PARTITION BY wd.wd_id ORDER BY wd_qty) = 1 THEN (DENSE_RANK() OVER(ORDER BY wd.wd_id)) ELSE NULL END as ordinal,  
                        ROW_NUMBER() OVER(PARTITION BY wd.wd_id ORDER BY wd_qty), 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY wd.wd_id ORDER BY wd_qty) = 1 THEN (SELECT wd_date FROM withdraw_item WHERE wd_id=wi.wd_id) ELSE NULL END as wd_date, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY wd.wd_id ORDER BY wd_qty) = 1 THEN wd.wd_id ELSE NULL END as wd_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY wd.wd_id ORDER BY wd_qty) = 1 THEN COALESCE (NULLIF((SELECT emp_id FROM withdraw_item WHERE wd_id=wi.wd_id), ''), '-') ELSE NULL END as emp_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY wd.wd_id ORDER BY wd_qty) = 1 THEN COALESCE (NULLIF(e.emp_name, ''), '-') ELSE NULL END as emp_name, 
                        wd.p_id, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY wd.wd_id ORDER BY wd_qty DESC) = 1 THEN (SELECT remark FROM withdraw_item WHERE wd_id=wd.wd_id) ELSE ' ' END as REMARK, 
                        wd.wd_qty, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY wd.wd_id ORDER BY wd_qty DESC) = 1 THEN (SELECT sum(wd_qty) FROM withdraw_detail WHERE wd_id=wi.wd_id) ELSE NULL END as TOTAL, 
                        CASE WHEN ROW_NUMBER() OVER(PARTITION BY wd.wd_id ORDER BY wd_qty DESC) = 1 THEN (SELECT COUNT(wd_id) FROM withdraw_detail WHERE wd_id=wi.wd_id) ELSE 0 END as rowspan
                    FROM withdraw_detail wd
                    LEFT JOIN product p ON p.p_id = wd.p_id
                    LEFT JOIN withdraw_item wi ON wi.wd_id = wd.wd_id
                    LEFT JOIN employee e ON e.emp_id = wi.emp_id
                    WHERE wd_date::date between %s and %s
                    ORDER BY wd.wd_id, wd.wd_qty
                    """
            data = (from_date, to_date,)
            cur.execute(sql, data)
            report = cur.fetchall()

            curtwo = gobal.con.cursor()
            sqltwo = "SELECT TO_CHAR(DATE %s, 'DD-MM-YYYY') || ' ຫາ ' ||TO_CHAR(DATE %s, 'DD-MM-YYYY')"
            data2 = (from_date, to_date,)
            curtwo.execute(sqltwo, data2)
            reporttwo = curtwo.fetchmany()

            cursor = gobal.con.cursor()
            sql_total = """SELECT
                                sum(wd.wd_qty), TO_CHAR(sum(p_price * wd.wd_qty), '999G999G999G999D99') 
                            FROM withdraw_detail wd
                            LEFT JOIN product p ON p.p_id = wd.p_id
                            LEFT JOIN withdraw_item wi ON wi.wd_id = wd.wd_id
                            LEFT JOIN employee e ON e.emp_id = wi.emp_id
                            WHERE wd_date::date between %s and %s 
                        """
            total = (from_date, to_date,)
            cursor.execute(sql_total, total)
                    # to_char(total_value_2,'999G999G999G999D99')

            total = cursor.fetchall()
            return render_template('/report/withdraw.html', total=total, report=report, reporttwo=reporttwo, from_date=from_date, to_date=to_date,user=session['name'], roles = session['roles'])

@app.route('/customer_rp')
def customer_rp():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = """SELECT 
                        CASE WHEN c.cust_id IS NULL THEN b.cust_id ELSE c.cust_id END, CASE WHEN c.cust_name IS NULL THEN b.cust_id ELSE c.cust_name END as custname, 
						CONCAT(cust_village, ', ', cust_district, ', ', cust_province) address, 
						cust_tel, user_name, user_pwd, cust_gender, EXTRACT(year FROM AGE(NOW()::timestamp, cust_bd::timestamp)) :: int as age, cust_province, cust_district, cust_village,
                    cust_province, cust_district, cust_village
					FROM bill b
					LEFT JOIN customer c ON b.cust_id = c.cust_id
					
					UNION
                    
                     SELECT 
                        CASE WHEN c.cust_id IS NULL THEN b.cust_id ELSE c.cust_id END, CASE WHEN c.cust_name IS NULL THEN b.cust_id ELSE c.cust_name END as custname, 
						CONCAT(cust_village, ', ', cust_district, ', ', cust_province) address, 
						cust_tel, user_name, user_pwd, cust_gender, EXTRACT(year FROM AGE(NOW()::timestamp, cust_bd::timestamp)) :: int as age, cust_province, cust_district, cust_village,
                    cust_province, cust_district, cust_village
					FROM bill b
					LEFT JOIN customer c ON b.cust_id <> c.cust_id
					ORDER BY cust_id"""
            cur.execute(sql)
            report = cur.fetchall()

            cursor = gobal.con.cursor()
            sql_total ="""
					   SELECT DISTINCT (SELECT COUNT(*) FROM (
                                SELECT
                                    CASE WHEN c.cust_id IS NULL THEN b.cust_id ELSE c.cust_id END
                                FROM bill b
                                LEFT JOIN customer c ON b.cust_id = c.cust_id
					
                                UNION
                                
                                SELECT 
                                    CASE WHEN c.cust_id IS NULL THEN b.cust_id ELSE c.cust_id END
                                FROM bill b
                                LEFT JOIN customer c ON b.cust_id <> c.cust_id
					                                            )
                                AS sumcus), 
                            (SELECT count(cust_id) FROM customer) AS mycus, 
                            (SELECT COUNT(*) FROM (
                                SELECT DISTINCT
                                     CASE WHEN c.cust_id IS NULL THEN b.cust_id END
                                FROM bill b
								LEFT JOIN customer c ON b.cust_id = c.cust_id
								WHERE c.cust_id IS NULL
					                                            )
                                AS nocus), 
                            (SELECT count(cust_id) FROM customer WHERE cust_gender = 'ຊາຍ'), 
                            (SELECT count(cust_id) FROM customer WHERE cust_gender = 'ຍິງ')
                        FROM customer
                        """
            cursor.execute(sql_total)
            total = cursor.fetchall()

            sql_count = """ SELECT (SELECT COUNT(DISTINCT cust_id) FROM bill WHERE cust_id = e.cust_id AND cust_id LIKE '%CUS%') AS cust_id, (SELECT COUNT(DISTINCT cust_id) FROM bill ) AS cust_name
                            FROM customer e
                            ORDER BY cust_id
                        """
            cursor.execute(sql_count)
            count = cursor.fetchall()
            return render_template('/report/customer.html',report=report, total=total, count=count, user=session['name'], roles = session['roles'])

@app.route('/customer_rp_gender', methods=['POST'])
def customer_rp_gender():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            gender = request.form['gender']
            cur = gobal.con.cursor()
            sql = """SELECT
                        cust_id, cust_name, CONCAT(cust_village, ', ', cust_district, ', ', cust_province) address, cust_tel, user_name, user_pwd, cust_gender, cust_bd, cust_province, cust_district, cust_village,
                    cust_province, cust_district, cust_village FROM customer e
                    WHERE cust_gender LIKE %s
                    ORDER BY cust_id"""
            cur.execute(sql, (gender,))
            print(gender)
            report = cur.fetchall()

            curone = gobal.con.cursor()
            sqlone = """SELECT 
                        DISTINCT cust_gender
                        FROM customer
                    WHERE cust_gender = %s"""
            curone.execute(sqlone, (gender,))
            reportone = curone.fetchall()

            cursor = gobal.con.cursor()
            sql_total = """ SELECT count(cust_id)
                            FROM customer
                            WHERE cust_gender LIKE %s
                        """
            cursor.execute(sql_total, (gender,))
            total = cursor.fetchall()
            check_gd=gender
            print('OOOOOOOOOOOOOOOOOOOO',check_gd)
            return render_template('/report/customer_gender.html', gender=gender, reportone=reportone, report=report, total=total, user=session['name'], roles = session['roles'],check_gd=check_gd,)

@app.route('/employee_rp')
def employee_rp():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            cur = gobal.con.cursor()
            sql = """SELECT
                        emp_id, emp_name, CONCAT(emp_village, ', ', emp_district, ', ', emp_province) address, emp_tel, admin_name, admin_pwd, emp_gender, emp_bd, emp_province, emp_district, emp_village,
                    emp_province, emp_district, emp_village FROM employee e
                    ORDER BY emp_id"""
            cur.execute(sql)
            report = cur.fetchall()

            cursor = gobal.con.cursor()
            sql_total = """ SELECT count(emp_id), 
                                    (SELECT count(emp_id) FROM employee WHERE emp_gender = 'ຊາຍ'), 
                                    (SELECT count(emp_id) FROM employee WHERE emp_gender = 'ຍິງ')
                            FROM employee
                        """
            cursor.execute(sql_total)
            total = cursor.fetchall()
            return render_template('/report/employee.html',report=report, total=total, user=session['name'], roles = session['roles'])

@app.route('/employee_rp_gender', methods=['POST'])
def employee_rp_gender():
    with gobal.con:
        if not session.get("name"):
            return redirect("/login")
        else:
            gender = request.form['gender']
            cur = gobal.con.cursor()
            sql = """SELECT
                        emp_id, emp_name, CONCAT(emp_village, ', ', emp_district, ', ', emp_province) address, emp_tel, admin_name, admin_pwd, emp_gender, emp_bd, emp_province, emp_district, emp_village,
                    emp_province, emp_district, emp_village FROM employee e
                    WHERE emp_gender LIKE %s
                    ORDER BY emp_id"""
            cur.execute(sql, (gender,))
            print(gender)
            report = cur.fetchall()

            curone = gobal.con.cursor()
            sqlone = """SELECT 
                        DISTINCT emp_gender
                        FROM employee
                    WHERE emp_gender = %s"""
            curone.execute(sqlone, (gender,))
            reportone = curone.fetchall()

            cursor = gobal.con.cursor()
            sql_total = """ SELECT count(emp_id)
                            FROM employee
                            WHERE emp_gender LIKE %s
                        """
            cursor.execute(sql_total, (gender,))
            total = cursor.fetchall()
            check_gd=gender
            print('OOOOOOOOOOOOOOOOOOOO',check_gd)
            return render_template('/report/employee_gender.html', gender=gender, reportone=reportone, report=report, total=total, user=session['name'], roles = session['roles'], check_gd=check_gd,)

