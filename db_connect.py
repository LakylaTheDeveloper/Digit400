import MySQLdb

def connection():
    conn = MySQLdb.connect(host="localhost", 
                          user = "root", 
                          passwd = "PrincessLola", 
                          db = "Lola")
    c = conn.cursor()
    
    return c, conn