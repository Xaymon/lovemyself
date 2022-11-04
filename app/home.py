from flask import Flask, render_template, request, redirect, url_for, session
from kk_con import *
from app import app


# @app.route('/home')
# def home():
#     with gobal.con:
#         if not session.get("name"):
#             return redirect("/login")
#         else:
#             cur = gobal.con.cursor()
#             sql = "SELECT curency_code, curency_name, to_char(buy,'999G999G999G999D99'), to_char(sale,'999G999G999G999D99') FROM public.exchange_rate where date_end isnull order by curency_code "
#             cur.execute(sql)
#             rate_ = cur.fetchall()
#             return render_template('index.html', rate_=rate_,user=session.get("name"))
# @app.route('/homestock')
# def homestock():
#     with gobal.con:
#         if not session.get("name"):
#             return redirect("/login")
#         else:
#             # cur = gobal.con.cursor()
#             # sql = "SELECT curency_code, curency_name, buy, sale FROM public.exchange_rate where date_end isnull order by curency_code "
#             # cur.execute(sql)
#             # rate_ = cur.fetchall()
#             return render_template('homestock.html',user=session.get("roles"))
# @app.route('/stock_cash')
# def stock_cash():
#     with gobal.con:
#         if not session.get("name"):
#             return redirect("/login")
#         else:
#             cur = gobal.con.cursor()
#             sql = """SELECT row_number() OVER () as rnum,b.curency_name,to_char(sum(case when calc_flag=-1 then -1*amount_1 else amount_1 end ),'999G999G999G999G999G999G999D99') FROM public.cb_trans_detail a 
#                         left join public.tb_addcurrency b on b.curency_code=a.trans_number
#                         where trans_number in ('01','02','00') group by trans_number,b.curency_name"""
#             cur.execute(sql)
#             rate_ = cur.fetchall()
#             return render_template('homecash.html',rate_=rate_,user=session.get("roles"))
# @app.route('/stock_bank')
# def stock_bank():
#     with gobal.con:
#         if not session.get("name"):
#             return redirect("/login")
#         else:
#             cur = gobal.con.cursor()
#             sql = """
#                     SELECT row_number() OVER () as rnum,bank_name,to_char(sum(case when calc_flag=-1 then -1*amount_1 else amount_1 end ),'999G999G999G999G999G999G999D99')  FROM cb_trans_detail a 
#                     left join public.tb_bank b on b.bank_id=a.trans_number
#                     where trans_number not in ('01','02','00','') group by trans_number,b.bank_name
#                 """
#             cur.execute(sql)
#             rate_ = cur.fetchall()
#             return render_template('hometran.html',rate_=rate_,user=session.get("roles"))