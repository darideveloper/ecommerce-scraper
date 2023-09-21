import pymysql.cursors

class MySQL ():

    def __init__ (self, server:str, database:str, username:str, password:str):
        """ Connect with mysql db

        Args:
            server (str): server host
            database (str): database name
            username (str): database username
            password (str): database password
        """

        self.server = server
        self.database = database
        self.username = username
        self.password = password

    def run_sql (self, sql:str):
        """ Exceute sql code
            Run sql code in the current data base, and commit it
            
        Args:
            sql (str): sql code to run
        """

        # Connect and get cursor
        connection = pymysql.connect(host=self.server,
                                    user=self.username,
                                    database=self.database,
                                    passwd=self.password,
                                    cursorclass=pymysql.cursors.DictCursor)

        cursor = connection.cursor()

        # Try to run sql
        try:
            cursor.execute (sql)
        except Exception as err:

            print (err, sql)

            return None

        # try to get returned part
        try:
            results = cursor.fetchall()
        except:
            results = None

        connection.commit()
        connection.close()
        return results
    
    def get_clean_text (self, text:str) -> str():
        
        chars = [";", "--", "\b", "\r", "\t", "\n", "\f", "\v", "\0", "'", '"']
        for char in chars:
            text = text.replace(char, "")
        return text