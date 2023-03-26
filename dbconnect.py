import mysql.connector as mc
conn = mc.connect(host="localhost", user="root", password="root", port=3030, database="supermarket", autocommit = True)
