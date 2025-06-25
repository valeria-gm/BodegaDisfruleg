import mysql.connector

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="jared",
        password="zoibnG31!!EAEA",
        database="disfruleg"
    )
