import mysql.connector

mydb = mysql.connector.connect(
  host="services-3855.eastus.cloudapp.azure.com",
  user="user",
  password="password",
  database="events"
)

mycursor = mydb.cursor()

sql = "drop table stock_news"
mycursor.execute(sql)
sql2 = "drop table stock_open_price"
mycursor.execute(sql2)

mydb.commit()

print(mycursor.rowcount, "record(s) deleted")