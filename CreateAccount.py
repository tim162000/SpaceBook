import cherrypy
import sqlite3
import time

class CreateAccount (object):
    
    @cherrypy.expose
    def CreateAccountForm(self, error=""):
    
        return """<html>
        <head><title>Create Account</title>
        </head>
        <body>
        <form action='newUserDetails' method='post'>
        <input type='text' name = 'firstName1' placeholder = 'First Name' />
        <input type='text' name = 'surname1' placeholder = 'Surname' />
        <input type='text' name = 'username1' placeholder = 'Username' />
        <input type='password' name = 'password1' placeholder = 'Password' />
        <input type='submit' value = 'Submit' />
        """ + error + """
        </form>
        </body>
        </html>"""
    
    @cherrypy.expose
    def ValidateAccountForm(self, firstName1=None, surname1=None, username1=None, password1=None):
     
        error = ""
        
        
         
        if not firstName1:
            error += "First Name Required<br />"
            
        if not surname1:
            error += "Surname Required<br />"
            
        if not username1:
            error += "Username Required<br />"
                        
        if not password1:
            error += "Surname Required<br />"
        
         
        if error:
            self.CreateAccountForm(error)
        else:
            login_credentials_database = sqlite3.connect('databases/login_credentials.db')
            c = login_credentials_database.cursor() 
            for t in [(firstName1, surname1, username1, password1),]:
                c.execute('insert into login_credentials values (?,?,?,?)',t)
            login_credentials_database.commit()
            c.close()
            
            c = login_credentials_database.cursor() 
            c.execute("create table " + username1 + """(username text,
                                                        first_name text,
                                                        last_name text,
                                                        last_ip text,
                                                        last_port text,
                                                        key text,
                                                        accepted text,
                                                        friends integer,
                                                        colleagues integer,
                                                        acquaintances integer,
                                                        public integer,
                                                        server_key text)""")
            c.close()
                                                        
            images_data = sqlite3.connect('databases/images.db')
            cur = images_data.cursor()
            
            f = open("static/img/BlankProfilePhoto.jpg","rb")
            data = f.read()
            f.close()

            binary = sqlite3.Binary(data)


            for t in [(int(time.time()), username1, username1, 'Blank Profile Image', binary, username1),]:
                cur.execute('insert into Images values (?,?,?,?,?,?)',t)

            images_data.commit()    
                                       
            cur.close()
            
            
            
            cherrypy.session['username'] = username1
            cherrypy.session['page_id'] = username1
            cherrypy.session['password'] = password1
            cherrypy.session['logged in'] = True
            
            raise cherrypy.HTTPRedirect("/home")
            
        
