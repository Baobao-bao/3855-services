import mysql.connector
import logging
import logging.config

mydb = mysql.connector.connect(
  host="services-3855.eastus.cloudapp.azure.com",
  user="user",
  password="password",
  database="events"
)

mycursor = mydb.cursor()

mycursor.execute('''
          CREATE TABLE stock_open_price
          (id INT NOT NULL AUTO_INCREMENT, 
           date VARCHAR(100) NOT NULL,
           stock_code VARCHAR(10) NOT NULL,
           open_price FLOAT,
           CONSTRAINT stock_open_price_pk PRIMARY KEY (id))
          ''')

mycursor.execute('''
          CREATE TABLE stock_news
          (id INT NOT NULL AUTO_INCREMENT,
           date VARCHAR(100) NOT NULL,
           stock_code VARCHAR(10) NOT NULL,
           news VARCHAR(1000),
           source VARCHAR(20),
           CONSTRAINT stock_news_pk PRIMARY KEY (id))
          ''')

mydb.commit()
mydb.close()
