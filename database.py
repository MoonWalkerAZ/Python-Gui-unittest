import mysql.connector


class DatabaseConnection():

    def __init__(self):
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="pass",
            database="unibloxDatabase"
        )


    def selectGlobalRun(self, koda):
        sql = "SELECT id FROM globalRun WHERE koda='"+koda+"';"
        mycursor = self.mydb.cursor()
        mycursor.execute(sql)
        return mycursor.fetchone()

    def insertGlobalRun(self, st_plosce, datum, tip_testa, koda):
        sql = "INSERT INTO globalRun (tip_testa, st_plosce, datum, koda) VALUES (%s, %s, %s, %s)"
        val = (tip_testa, st_plosce, datum, koda)
        mycursor = self.mydb.cursor()
        mycursor.execute(sql, val)
        self.mydb.commit()

    def insertIntoDatabase(self, ime_testa, cas_izvajanja, status, opis_napake, koda):

        globalniRun_id = self.selectGlobalRun(koda)[0] # dobimo id od testa

        sql = "INSERT INTO testi (ime_testa, cas_izvajanja, status, opis_napake, globalRun_id) VALUES (%s, %s, %s, %s, %s)"
        val = (ime_testa, cas_izvajanja, status, opis_napake, globalniRun_id)
        mycursor = self.mydb.cursor()
        mycursor.execute(sql, val)
        self.mydb.commit()