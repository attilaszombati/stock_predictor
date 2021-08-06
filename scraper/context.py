from peewee import MySQLDatabase

mysql_db = \
    MySQLDatabase(
        user='root',
        password='attilaattila123',
        unix_socket="/cloudsql/crawling-315317:europe-west1:mysql-03",
        database='twitter'
    )