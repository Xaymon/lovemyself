# import mysql.connector
# class gobal:
#     #for XAMP
#     con = mysql.connector.connect(user='root', password='', host='localhost', database='my_superstar',port='3306')
#     #for cloud server
#     # con = mysql.connector.connect(user='ufofq5glwl8tqerf', password='ts02WU1qz41PLjgdVK7k', host='blocd9sx8jzgucvo4lwz-mysql.services.clever-cloud.com', database='blocd9sx8jzgucvo4lwz',port='3306')


import psycopg2
class gobal:
        # cloud
        # con = psycopg2.connect(host="46.252.181.107", database="bmtd3kmwtd3co2d74myb",user="uqowcfe9spmvmoy40pgk", password="czq4yqurzFrfXtmdmRQa", port="5432")
        # localhost
        con = psycopg2.connect(host="localhost", database="m_soul_shop",user="postgres", password="55794519me", port="5433")