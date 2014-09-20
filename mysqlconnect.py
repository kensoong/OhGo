from keys import keys
import MySQLdb

def mysqlcon():
  db = MySQLdb.connect(user=keys.mysqluser, host=keys.mysqlhost, passwd=keys.mysqlpasswd, port=keys.mysqlport, db=keys.mysqldb)
  return db

def main():
  print 'i do nothing'

if __name__ == '__main__':
  main()
