import sqlite3
##connect
connection=sqlite3.connect("student.db")
cursor=connection.cursor()
table_info="""
create table STUDENT(NAME VARCHAR(25),CLASS VARCHAR(25),SECTION VARCHAR(25),MARKS INT)
""" 
cursor.execute(table_info)
cursor.execute("""INSERT INTO STUDENT values('AKSHIT','AI','A',85)""")
cursor.execute("""INSERT INTO STUDENT values('PARTH','CORE','A',75)""")
cursor.execute("""INSERT INTO STUDENT values('RAKSHIT','AI','A',70)""")
cursor.execute("""INSERT INTO STUDENT values('DAKSH','AI','A',55)""")
print("the inserted records are ")
data=cursor.execute("""SELECT * from STUDENT""")
for row in data:
    print(row)
connection.close()