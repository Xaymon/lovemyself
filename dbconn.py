# from mysql.connector import pooling
# from contextlib import contextmanager
# import mysql.connector

# #for cloud server
# # PoolName="pynative_pool"
# # PoolSize=1
# # host='blocd9sx8jzgucvo4lwz-mysql.services.clever-cloud.com'
# # database='blocd9sx8jzgucvo4lwz'
# # user='ufofq5glwl8tqerf'
# # password='ts02WU1qz41PLjgdVK7k'

# #for XAMP
# PoolName="pynative_pool"
# PoolSize=10
# host="localhost"
# database="my_superstar"
# user="root"
# password=""
# connectionpool = mysql.connector.pooling.MySQLConnectionPool(pool_name=PoolName,
#                                             pool_size=PoolSize,
#                                             pool_reset_session=True,
#                                             host=host,
#                                             database=database,
#                                             user=user,
#                                             password=password)

# @contextmanager
# def getcursor():
#     con = connectionpool.getconn()
#     con.autocommit = True
#     try:
#         yield con.cursor()
#     finally:
#         connectionpool.putconn(con)
