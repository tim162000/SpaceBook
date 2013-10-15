import cherrypy
import os
import TopButtonsHTML
import sqlite3
import time
class Gallery (object):
    
       
    @cherrypy.expose
    def BrowseGallery(self):
        
        cherrypy.response.headers['Content-Type']= 'text/html'
        page_id = cherrypy.session.get('page_id')
        images_data = sqlite3.connect('databases/images.db')
        
        login_credentials_database = sqlite3.connect('databases/login_credentials.db')
        c2 = login_credentials_database.cursor() 

        cur1 = images_data.cursor()    
        cur1.execute("SELECT * FROM Images WHERE page_id=? order by time DESC",[page_id])
        
        page = TopButtonsHTML.TopButtonsHTML("Gallery")
        page += '</div><div id="photo"><table>'
        
        data = cur1.fetchone()
        while data is not None:
            
            c2.execute('select * from login_credentials where username=?',[data[1]])
            namedata = c2.fetchone()
            page += "<tr><td><a href='/dynamic_image/%s'><img width='500' src='/dynamic_image/%s'></a></td>" % (data[5],data[5],)
            
            page += "<td><p class='name_comment'>%s %s" % (namedata[0],namedata[1],)
            if cherrypy.session.get('username') == data[1] or cherrypy.session.get('username') == cherrypy.session.get('page_id'):
                page += "  |  <a class='deletebutton' href='deletephoto?uuid=%s'>x</a></p>" % (data[5],)
            else:
                page += "</p>"
            
            
            
            
            page += "<p class='date_comment'>%s</p><p class='comment'>%s</p></td></tr>" % (time.strftime("%d %b %Y at %I:%M", time.localtime(float(data[0]))),data[3],)
            data = cur1.fetchone()
            
        page += "</table></div></div></p></body></html> "
        
        images_data.close()
        return page

    
    


        
