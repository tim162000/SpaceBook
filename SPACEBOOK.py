#!/usr/bin/python


# Requires:  CherryPy 3.1.2  (www.cherrypy.org)
#            Python  (We use 2.6)


import CreateAccount
import TopButtonsHTML
import Gallery
import calendar
import cherrypy
import os
from datetime import datetime
import time
import uuid
import cherrypy.process.plugins
import sqlite3
import urllib
import urllib2
import socket
import threading
import json
import cookielib
import logging as log

cookies = cookielib.CookieJar()
urlopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
 

		
print """
---------------------
SPACEBOOK Starting Up
---------------------"""
staticfolder = "static"

# Log any errors to the log file
log.basicConfig(filename="error.log", level=log.DEBUG)

cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': 80,
                       })

class MainApp(object):
    
    #Configuration
    _cp_config = {'tools.encode.on': True, 
                  'tools.encode.encoding': 'utf8',
                 }
    
    #pulls updates from friends servers
    def pull_friends_updates(self):
        
        login_credentials_database = sqlite3.connect('databases/login_credentials.db')
        c2=login_credentials_database.cursor()
        c2.execute('select * from ' + cherrypy.session.get('page_id') + ' where accepted=?', ["accepted"])

        friends = c2.fetchall()
        c2.close()
        listofupdates = []
        print "Now printing friends-------------------------------------------------"
        print friends
        
        for friend in friends:

            try:
                auth_URL = "http://%s:%s/authenticate?serverID=%s&clientID=%s&key=%s&page=getActivity" %(friend[3], friend[4], friend[0], cherrypy.session.get('username'), friend[11],)
                print auth_URL
                result = urlopener.open(auth_URL, timeout=2)
                data = result.read()
                print "Printing JSON data--------------------------------------------"
                print data
                
                listofupdates += json.loads(data)
                result.close()
            except:
                print "Error reading in JSON from URL"

                        
        statusfeed = sqlite3.connect('databases/statusfeed.db')
        c = statusfeed.cursor()
              
        for update in listofupdates:
            print update
            c.execute("INSERT into updates values(?,?,?,?,?,?,?)",[update['messageID'],update['created'],update['creator'],update['body'],update['link'],update['type'],cherrypy.session.get('page_id')])


        statusfeed.commit()
        c.close()

   
    #default page redirects lost users to login
    @cherrypy.expose
    def default(self, *args, **kwargs):

        defaulturl = "/welcome" 
        raise cherrypy.HTTPRedirect(defaulturl)
    
    #getActivity is part of the protocol, and supplies a JSON list of dictionaries of recent activity
    @cherrypy.expose
    def getActivity(self, minutes=None):
        
        if cherrypy.session.get('logged in')==None:
            return "Please Authenticate"
       
        statusfeed = sqlite3.connect('databases/statusfeed.db')
        c = statusfeed.cursor()
        c.execute('select * from status where page_id=? order by time DESC',[cherrypy.session.get('page_id')])
        
        newmessage = []
        
        comment = c.fetchone()
        while comment:
            if comment == None: break
            if comment[5] and  cherrypy.session.get('friends') or comment[6] and cherrypy.session.get('colleagues') or comment[7] and cherrypy.session.get('acquaintances') or comment[8] and cherrypy.session.get('public') or cherrypy.session.get('username') == cherrypy.session.get('page_id'):
                newmessage += str({
                    'messageID': comment[4],
                    'creator': comment[1],
                    'created': comment[0],
                    'link': "/home",
                    'type': '1',
                    'body': comment[3],
                    })
            comment = c.fetchone()
        
        reply = json.dumps(newmessage)
        return reply

    @cherrypy.expose
    def deleteevent(self, messageID=None):
        
        events = sqlite3.connect('databases/statusfeed.db')
        c = events.cursor()
        c.execute('DELETE from events WHERE messageID=?',[messageID])
        events.commit()
        c.close()
        
        raise cherrypy.HTTPRedirect("/events")
    
    @cherrypy.expose
    def newevent(self, day=None, month=None, year=None, body=None, friends=None, colleagues=None, acquaintances=None, public=None):
        
        current_time = datetime.now()
        username = cherrypy.session.get('username')
        page_id = cherrypy.session.get('page_id')
        
        events = sqlite3.connect('databases/statusfeed.db')
        c = events.cursor()

        for t in [(str(uuid.uuid4()),
                  int(time.time()),
                  username,
                  body,
                  None,
                  year,
                  month,
                  day,
                  None,
                  None,
                  None,
                  None,
                  friends,
                  colleagues,
                  acquaintances,
                  public,
                  page_id,)]:
            c.execute('insert into events values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',t)

        events.commit()
        c.close()        
        
        raise cherrypy.HTTPRedirect("/events")     
    
    
    #events manages the events tab
    @cherrypy.expose
    def events(self):
        
        page = TopButtonsHTML.TopButtonsHTML("Homepage")
        
        page += """<div id='body'><form action='/newevent' method='post'>
                <p class='date'>
                    
                    Day<input type='text' name='day'>
                    Month<input type='text' name='month'>
                    Year<input type='text' name='year'>
                    Details<input type='text' name='body'></br>
                    <input type='submit' value='create event'>
                    Friends<input type='checkbox' name='friends' value='1' checked>
                    Colleagues<input type='checkbox' name='colleagues' value='1'checked>
                    Acquaintances<input type='checkbox' name='acquaintances' value='1'checked>
                    Public<input type='checkbox' name='public' value='1'checked></p></form>
                """
        
        #TODO: Fancy calendar input style
        """<head>
        <link href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/themes/base/jquery-ui.css" rel="stylesheet" type="text/css"/>
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.5/jquery.min.js"></script>
        <script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/jquery-ui.min.js"></script>

        <script>
        $(document).ready(function() {
        $("#datepicker").datepicker();
        
        });
        </script>
        </head>
        <body style="font-size:62.5%;">

        <div id="datepicker"></div>

        </body>"""
        
        
        
        
        statusfeed = sqlite3.connect('databases/statusfeed.db')
        c = statusfeed.cursor()

        c.execute('select * from events where page_id=? order by created DESC',[cherrypy.session.get('page_id')])
        
        while 1:
            event = c.fetchone()
            if event == None: break
            if event[12] and  cherrypy.session.get('friends') or event[13] and cherrypy.session.get('colleagues') or event[14] and cherrypy.session.get('acquaintances') or event[15] and cherrypy.session.get('public') or cherrypy.session.get('username') == cherrypy.session.get('page_id'):
                
                #This fetches the authors name
                login_credentials_database = sqlite3.connect('databases/login_credentials.db')
                c2 = login_credentials_database.cursor() 
                c2.execute('select * from login_credentials where username=?',[event[1]])
                namedata = c2.fetchone()
                
                #page += "<p class='name'>%s %s" % (namedata[0],namedata[1],)
                if cherrypy.session.get('username') == event[2] or cherrypy.session.get('username') == cherrypy.session.get('page_id'):
                    page += "   <a class='deletebutton' href='deleteevent?uuid=%s'>x</a></p>" % (event[0],)
                else:
                    page += "</p>"
                
                page += "<p class='name'>Host, %s</p>" % (event[2],)
                page += "<p class='date'>invited you on %s</p>" % (time.strftime("%d %b %Y at %I:%M", time.localtime(float(event[1]))),)
                page += "<p class='date'>Planned for %s/%s/%s</p>" % (event[7],event[6],event[5],)
                page += "<p class='status'>%s</p>" % (event[3],)
                
                
                
                c2.close()          
        c.close()
        page += "</div></body></html>"
        return page

    #upload saves image data and metadata     
    @cherrypy.expose 
    def upload(self, myFile, caption=None, displaypic=None):
           
        username = cherrypy.session.get('username')
        page_id = cherrypy.session.get('page_id')
        
        images_data = sqlite3.connect('databases/images.db')
        cur = images_data.cursor()

        data = myFile.file.read()
        myFile.file.close()
        binary = sqlite3.Binary(data)
        
        if displaypic:
            picture_code=username
            existing_dp_cursor = images_data.cursor()
            existing_dp_cursor.execute("delete from Images WHERE uuid=?",[username])
        else:
            picture_code=str(uuid.uuid4())
        
        for t in [(int(time.time()), username, page_id, caption, binary, picture_code),]:
            cur.execute('insert into Images values (?,?,?,?,?,?)',t)

        images_data.commit()    

        raise cherrypy.HTTPRedirect("/home")
    
    #public allows access for strangers, and logs their data into the cookie.
    @cherrypy.expose
    def public(self, profile=None):
        
        if profile == None:
            page = """
            <html>
                <head>
                    <link rel="stylesheet" type="text/css" href="style.css" />
                    <title>SPACEBOOK | Welcome</title>
                </head>
                <body>
                    <div id="body">
                        <div id="popup_bg"></div>
                            <div id="popup">
                                <p class='white'>SPACEBOOK is multi-user</br>
                                Specify a username</br></br></p>
                            <a class="headderbutton" href="newaccountform">Dont have SPACEBOOK?</a>
                        </div>
                    </div>
                </body>
            </html>"""
            return page

        cherrypy.session['page_id'] = profile
        cherrypy.session['public'] = 1
        
        #TODO:check for page existance and friendship, if friend, login, if not, public access.
        
        raise cherrypy.HTTPRedirect("/home")
    
    #comment_on_status saves sub comments on parent statuses to the database
    @cherrypy.expose
    def comment_on_status(self, status=None, parent_uuid=None):
        
        current_time = datetime.now()
        username = cherrypy.session.get('username')
        page_id = cherrypy.session.get('page_id')
        
        commentfeed = sqlite3.connect('databases/statusfeed.db')
        c = commentfeed.cursor()

        for t in [(int(time.time()), username, page_id, status, parent_uuid, str(uuid.uuid4())),]:
            c.execute('insert into comment values (?,?,?,?,?,?)',t)

        commentfeed.commit()
        c.close()        
        
        raise cherrypy.HTTPRedirect("/home")        
    
    #statusupdate saves new parent page statuses to the database
    @cherrypy.expose
    def statusupdate(self, status=None, friends=None, colleagues=None, acquaintances=None, public=None):
        
        current_time = datetime.now()
        username = cherrypy.session.get('username')
        page_id = cherrypy.session.get('page_id')
        
        statusfeed = sqlite3.connect('databases/statusfeed.db')
        c = statusfeed.cursor()

        for t in [(int(time.time()), username, page_id, status, str(uuid.uuid4()),friends, colleagues, acquaintances, public)]:
            c.execute('insert into status values (?,?,?,?,?,?,?,?,?)',t)

        statusfeed.commit()
        c.close()        
        
        raise cherrypy.HTTPRedirect("/home")
    
    #newfriend saves details of the new friend form into the database
    @cherrypy.expose
    def newfriend(self, firstname=None, surname=None, serverID=None, key=None, friends=None, colleagues=None, acquaintances=None, public=None):
        
        login_credentials_database = sqlite3.connect('databases/login_credentials.db')
        c = login_credentials_database.cursor()
        c2 = login_credentials_database.cursor()
        c2.execute('select * from login_credentials where username=?',[cherrypy.session.get('page_id')])
        
        password = c2.fetchone()
        c2.close()
        for t in [(serverID, firstname, surname, None, None, key, None, friends, colleagues, acquaintances, public, password[3])]:
            c.execute("insert into " + cherrypy.session.get('page_id') + " values (?,?,?,?,?,?,?,?,?,?,?,?)",t)

        login_credentials_database.commit()
        c.close()
        
        raise cherrypy.HTTPRedirect("/home")
    
    #purgefriend deletes a friend from a page_ID permissions database
    @cherrypy.expose
    def purgefriend(self, serverID=None):
        
        login_credentials_database = sqlite3.connect('databases/login_credentials.db')
        c = login_credentials_database.cursor() 
        
        c.execute("DELETE from " + cherrypy.session.get('page_id') + " WHERE username=?",[serverID])
       
        login_credentials_database.commit()
        c.close()
        
        raise cherrypy.HTTPRedirect("/friends")
        
    
    #acceptfriend manages issuing permissions to clients whom request access
    @cherrypy.expose
    def acceptfriend(self, serverID=None, friends=None, colleagues=None, acquaintances=None, public=None):
        
        login_credentials_database = sqlite3.connect('databases/login_credentials.db')
        c2 = login_credentials_database.cursor() 
        c2.execute("UPDATE " + cherrypy.session.get('page_id') + " SET accepted=?, friends=?, colleagues=?, acquaintances=?, public=? WHERE username=?",['accepted', friends, colleagues, acquaintances, public, serverID])
        
        login_credentials_database.commit()
        c2.close()
        
        raise cherrypy.HTTPRedirect("/friends")
        

    @cherrypy.expose
    def changefriendserverkey(self, server_key=None, username=None):
        
        login_credentials_database = sqlite3.connect('databases/login_credentials.db')
        c2 = login_credentials_database.cursor() 
        c2.execute("UPDATE " + cherrypy.session.get('page_id') + " SET server_key=? WHERE username=?", [server_key, username])
        login_credentials_database.commit()
        c2.close()
        raise cherrypy.HTTPRedirect("/friends")
        
    #friends constructs the friends page
    @cherrypy.expose
    def friends(self):
        
        #connect to the correct address server
        ip = urllib.urlopen('http://whatismyip.org').read()      
        if ip.find("130.216") == -1: 
            fptr = urllib2.urlopen("http://69.55.232.11:10001/whoonline")           #if at home
        else:                                                                               
            fptr = urllib2.urlopen("http://130.216.24.19:10001/whoonline")          #if at uni
        who_online_page = fptr.read()
        fptr.close()
        
        who_online_list = who_online_page.splitlines()

        page = TopButtonsHTML.TopButtonsHTML("SPACEBOOK | Friend Management Center")
        page += "<div id='pending_requests'><h2>Pending Requests</h2>"

        #for those not yet friends but pending acceptance
        login_credentials_database = sqlite3.connect('databases/login_credentials.db')
        c2 = login_credentials_database.cursor() 
        c2.execute("SELECT * FROM " + cherrypy.session.get('page_id') + " WHERE accepted IS NULL")
        
        possible_friend = c2.fetchone()
        while possible_friend:
            page += """<p class='name'>
            %s %s<a class='add_button' href="javascript: submitform()"> +</a><a class='deletebutton' href='purgefriend?serverID=%s'> x</a></p>""" % (possible_friend[1], possible_friend[2], possible_friend[0])
            
            page += """
            <script type="text/javascript">
                function submitform()
                {
                    document.forms['%s'].submit();
                }
            </script>
            <form id='%s' action='/acceptfriend' method='post'>
                <p class='date'>
                    <input type='hidden' name='serverID' value='%s'/>
                    Friends<input type='checkbox' name='friends' value='1' checked/>
                    Colleagues<input type='checkbox' name='colleagues' value='1'checked/>
                    Acquaintances<input type='checkbox' name='acquaintances' value='1'checked/>
                    Public<input type='checkbox' name='public' value='1'checked/></p></form>
                """ % (possible_friend[0], possible_friend[0],possible_friend[0])

            possible_friend = c2.fetchone()
        c2.close()
        
        #for pre saved friends
        page += "</div><div id='friends_on_feed'><h2>Friends</h2>"
        c2 = login_credentials_database.cursor() 
        c2.execute("SELECT * FROM " + cherrypy.session.get('page_id') + " WHERE accepted IS NOT NULL")
        possible_friend = c2.fetchone()
        while possible_friend:

            page += "<a class='add_button' href='http://%s:%s/authenticate?serverID=%s&clientID=%s&key=%s'><p class='name'>%s %s</a><a class='deletebutton' href='purgefriend?serverID=%s'> x</a><form action='/changefriendserverkey' method='post'><input type='password' placeholder='Server Key' name='server_key'/><input type='hidden' name='username' value='%s'/></form></p></h1>" % (possible_friend[3], possible_friend[4], possible_friend[0], cherrypy.session.get('username'), possible_friend[11], possible_friend[1], possible_friend[2], possible_friend[0], possible_friend[0],)
            possible_friend = c2.fetchone()
        
        c2.close

        page += "</div><div id='register_of_users'><h2>Register of Users</h2>"
        
        login_credentials_database = sqlite3.connect('databases/login_credentials.db')
        for i in who_online_list:
            individual_user_split = i.split(",")
            random_server = login_credentials_database.cursor() 
            random_server.execute("UPDATE " + cherrypy.session.get('page_id') + " SET last_ip=?, last_port=? WHERE username=?",[individual_user_split[0], individual_user_split[1], individual_user_split[2]])
            login_credentials_database.commit()
            
            page += """<meta http-equiv="refresh" content="30"/><a class="headderbutton" href='http://%s:%s/public?profile=%s'>""" % (individual_user_split[0], individual_user_split[1],individual_user_split[2])
            page += "<p class=name>%s</p>" % (individual_user_split[2],)

            
            page += "<p class=date>%s</p>" % (time.strftime("%d %b %Y at %I:%M", time.localtime(float(individual_user_split[3]))),)
            page += "<p>%s:%s</br></br></p></a>" % (individual_user_split[0], individual_user_split[1],)
            
        page += "</div></body></html>"

       
        return page

    #deletestatus erases a single status and all of its children threads from the database
    @cherrypy.expose
    def deletestatus(self, uuid=None):

        statusfeed = sqlite3.connect('databases/statusfeed.db')
        c = statusfeed.cursor()
        c.execute('DELETE from status WHERE uuid=?',[uuid])
        c.execute('DELETE from comment WHERE parent_uuid=?',[uuid])
        statusfeed.commit()
        c.close()
        
        raise cherrypy.HTTPRedirect("/home")
    
    #deletephoto erases a single photo from the database
    @cherrypy.expose
    def deletephoto(self, uuid=None):

        imagefeed = sqlite3.connect('databases/images.db')
        c = imagefeed.cursor()
        c.execute('DELETE from Images WHERE uuid=?',[uuid])
        imagefeed.commit()
        c.close()
        
        raise cherrypy.HTTPRedirect("/gallery")
    
    #home manages the status feed html
    @cherrypy.expose
    def home(self):
        
        page = TopButtonsHTML.TopButtonsHTML("Homepage")
        page += """<div id='profilepic'><img width=170px src='/dynamic_image?uuid=%s'></div>""" % (cherrypy.session.get('page_id'),)
        page += """<div id='friends_on_feed'><h2>Network Neighbourhood</h2><meta http-equiv="refresh" content="30"/>"""
        
        statusfeed = sqlite3.connect('databases/statusfeed.db')
        c = statusfeed.cursor()
        c.execute('SELECT * from updates WHERE page_id=? order by created desc limit 100',[cherrypy.session.get('page_id')])

        updates = c.fetchall()
        c.close()
        
        for update in updates:
        
            login_credentials_database = sqlite3.connect('databases/login_credentials.db')
            c5 = login_credentials_database.cursor() 
            c5.execute("select * from " + cherrypy.session.get('page_id') + " where username=?",[update[2]])
            namedata = c5.fetchone()
            c5.close
            
            page += "<p class='name'>%s %s (%s)</p>" % (namedata[1], namedata[2], namedata[0])
            page += "<p class='date'>%s</p>" % (time.strftime("%d %b %Y at %I:%M", time.localtime(float(update[1]))),)
            page += "<p class='status'>%s</p></br>" % (update[3],)

        page +="</div><div id='body'>"
        self.pull_friends_updates()
        #Retrives Christian name for page headder
        login_credentials_database = sqlite3.connect('databases/login_credentials.db')
        c2 = login_credentials_database.cursor() 
        c2.execute('select * from login_credentials where username=?',[cherrypy.session.get('page_id')])
        namedata = c2.fetchone()
        page += "<h1>%s %s" % (namedata[0],namedata[1],)
        c2.close()
        
        #for those not yet friends
        if cherrypy.session.get('page_id') is not cherrypy.session.get('username'):
            c2 = login_credentials_database.cursor() 
            c2.execute("select * from " + cherrypy.session.get('page_id') + " where username=?",[cherrypy.session.get('page_id')])
            possible_friend = c2.fetchone()
            if possible_friend == None:
                page +="""</h1><p><form action='newfriend' method='post'>
                            <input type='text' name = 'firstname' placeholder = 'First Name' />
                            <input type='text' name = 'surname' placeholder = 'Surname' />
                            <input type='text' name = 'serverID' placeholder = 'serverID' />
                            <input type='password' name = 'key' placeholder = 'Password' />
                            <input type='submit' value = 'Submit' />
                            </form></p>"""
            else:
                if possible_friend[6]:
                    page += "</h1>"
                else:
                    "request sent</h1>"
        else:   
            page += "</h1>"
        
        page += "<table><tr><td><h2>Status Feed</h2></td>"
        
        if cherrypy.session.get('logged in') == True:
            page += """<td class='left'><form action='/statusupdate' method='post'><p class='date'>
                <input type='text' name='status' placeholder = "New Status..."/>
                Friends<input type='checkbox' name='friends' value='1' checked>
                Colleagues<input type='checkbox' name='colleagues' value='1'checked>
                Acquaintances<input type='checkbox' name='acquaintances' value='1'checked>
                Public<input type='checkbox' name='public' value='1'checked>
                
            </p></form></td>"""

        page += "</tr></table><div id=statusfeed>"
        statusfeed = sqlite3.connect('databases/statusfeed.db')
        c = statusfeed.cursor()

        c.execute('select * from status where page_id=? order by time DESC limit 100',[cherrypy.session.get('page_id')])
        
        while 1:
            comment = c.fetchone()
            if comment == None: break
            if comment[5] and  cherrypy.session.get('friends') or comment[6] and cherrypy.session.get('colleagues') or comment[7] and cherrypy.session.get('acquaintances') or comment[8] and cherrypy.session.get('public') or cherrypy.session.get('username') == cherrypy.session.get('page_id'):
                
                #This fetches the authors name
                login_credentials_database = sqlite3.connect('databases/login_credentials.db')
                c2 = login_credentials_database.cursor() 
                c2.execute('select * from login_credentials where username=?',[comment[1]])
                namedata = c2.fetchone()
                
                page += "<p class='name'>%s %s" % (namedata[0],namedata[1],)
                if cherrypy.session.get('username') == comment[1] or cherrypy.session.get('username') == cherrypy.session.get('page_id'):
                    page += "   <a class='deletebutton' href='deletestatus?uuid=%s'>x</a></p>" % (comment[4],)
                else:
                    page += "</p>"
                              
                page += "<p class='date'>%s</p>" % (time.strftime("%d %b %Y at %I:%M", time.localtime(float(comment[0]))),)
                page += "<p class='status'>%s</p>" % (comment[3],)
                
                #The following section prints comments on status'
                c3 = statusfeed.cursor()
                c3.execute('select * from comment where parent_uuid=? order by time asc',[comment[4]])
                
                subcomment = c3.fetchone()

                while subcomment is not None:

                    c2.execute('select * from login_credentials where username=?',[subcomment[1]])
                    namedata = c2.fetchone()
                    
                    
                    try:
                        page += "<p class='name_comment'>%s %s</p>" % (namedata[0], namedata[1],)
                    except:
                        page += "<p class='name_comment'>%s</p>" % (subcomment[1],)
                    
                    page += "<p class='date_comment'>%s</p>" % (time.strftime("%d %b %Y at %I:%M", time.localtime(float(subcomment[0]))),)
                    page += "<p class='comment'>%s</br></p>" % (subcomment[3],)
                    subcomment = c3.fetchone()

                #New Comment Form
                if cherrypy.session.get('logged in') == True:
                    page += """
                    <form class='comment' action='/comment_on_status' method='post'>
                        <input type='text' name='status' placeholder = "Comment..."/>
                        <input type='hidden' name='parent_uuid' value='%s' />
                    </form>""" % (comment[4],)
                
                c2.close()
                c3.close()            
        c.close()
        
        if cherrypy.session.get('logged in') == True:
            page +="""
            <form action="upload" method="post" enctype="multipart/form-data">
            <p class='date'>
            <input type="file" name="myFile" />
            <input type="text" name="caption" placeholder = "Caption..."/>"""
            
            if cherrypy.session.get('page_id') == cherrypy.session.get('username'):
                page += "Set as Avatar<input type='checkbox' name='displaypic' value='Make Display Picture'>"
            
            page += """
            </p>
            </form>"""

        #log.info("%s logged in." % (username, ) )
        page += "</div></div></body></html>"
        
        return page
    
    
    @cherrypy.expose
    def welcome(self):
    #Welcome form, with login and new account information

        return """
        <html>
            <head>
                <link rel="stylesheet" type="text/css" href="style.css" />
                <title>SPACEBOOK | Welcome</title>
            </head>
            <body>
                <div id="body">
                    <div id="popup_bg"></div>
                        <div id="popup">
                        <form action='/signin' method='post'>
                        <input type='text' name='username1' placeholder='Username'' />
                        <input type='password' placeholder='Password'name='password1' />
                        <input type='submit' name='signin1' value='Sign In'/>
                        </form>
                        <a class="headderbutton" href="newaccountform">Dont have SPACEBOOK?</a>
                    </div>
                </div>
            </body>
        </html>"""
        
    
    @cherrypy.expose
    def authenticate(self, serverID=None, clientID=None, key=None, page=home):
        
        login_credentials_database = sqlite3.connect('databases/login_credentials.db')
        c = login_credentials_database.cursor()
        
        for t in [(serverID, key),]:
            c.execute('select * from ' + serverID + ' where username=? and key=?',t)
        
        login_detail = c.fetchone()
        if login_detail:
                
            
            cherrypy.session['username'] = clientID
            cherrypy.session['page_id'] = serverID
            cherrypy.session['password'] = key
            cherrypy.session['logged in'] = True
            cherrypy.session['friends'] = login_detail[7]
            cherrypy.session['colleagues'] = login_detail[8]
            cherrypy.session['acquaintances'] = login_detail[9]
            cherrypy.session['public'] = login_detail[10]
            
            c.close() 
            
            raise cherrypy.HTTPRedirect("/%s") % page
        else:
            c.close()
            error_page="No."
        
        return error_page

    #signout expires log in session
    @cherrypy.expose
    def signout(self):
    
        cherrypy.lib.sessions.expire()  

        raise cherrypy.HTTPRedirect("/welcome")
        
    #Validates signin credentials
    @cherrypy.expose
    def signin(self, username1=None, password1=None, signin1=None):   
        
        login_credentials_database = sqlite3.connect('databases/login_credentials.db')
        c = login_credentials_database.cursor()
        
        for t in [(username1, password1),]:
            c.execute('select * from login_credentials where username=? and password=?',t)
        
        if c.fetchone():
            #Loads a Session cookie for friends to enjoy
            cherrypy.session['username'] = username1
            cherrypy.session['page_id'] = username1
            cherrypy.session['password'] = password1
            cherrypy.session['logged in'] = True
            cherrypy.session['friends'] = 1
            cherrypy.session['colleagues'] = 1
            cherrypy.session['acquaintances'] = 1
            cherrypy.session['public'] = 1
        else:
            raise cherrypy.HTTPRedirect("/welcome")
        

        #TODO: Behave.
        ip = urllib.urlopen('http://whatismyip.org').read()      
        
        postdata = {"ip" : ip, "port" : "80", "id" : username1 }
        print postdata
        '''
        if ip.find("130.216") == -1: #if at home
            print "conecting to at home server"
            fptr = urllib2.urlopen("http://69.55.232.11:10001/iamhere", urllib.urlencode(postdata))
        else: #if at uni
            print "connecting to at uni server"
            fptr = urllib2.urlopen("http://130.216.24.19:10001/iamhere", urllib.urlencode(postdata))

        data = fptr.read()
        fptr.close()
        '''
        print """
--------------------
Login Data Validated
--------------------
        """
 
        raise cherrypy.HTTPRedirect("/home")
    
    @cherrypy.expose
    def dynamic_image(self, uuid=None):
        

        cherrypy.response.headers['Content-Type'] = "image/jpeg"
        images_data = sqlite3.connect('databases/images.db')
        cur = images_data.cursor()    
        cur.execute("SELECT Data FROM Images WHERE uuid=?", [uuid])

        data = cur.fetchone()[0]
 
        
        images_data.close()
        return data
    
    @cherrypy.expose
    def img(self, fname):
    
        if cherrypy.session.get('logged in') == False:
            raise cherrypy.HTTPRedirect("/welcome")
            
        """ If they request some media, for example images, set the content type of
            the response, read the file, and dump it out in the response.
        """

        ext = os.path.splitext(fname)[1]

        if ext == ".jpg":
            cherrypy.response.headers['Content-Type'] = "image/jpeg"
        elif ext == ".png":
            cherrypy.response.headers['Content-Type'] = "image/png"
        elif ext == ".gif":
            cherrypy.response.headers['Content-Type'] = "image/gif"
        else:
            cherrypy.response.headers['Content-Type'] = "image/unknown"
        f = open(staticfolder+"/img/"+fname,"rb")
        data = f.read()
        f.close()

        return data
    
    #FIXME:Funny variable names and tricky to get.
    newAccount=CreateAccount.CreateAccount()
    newaccountform=newAccount.CreateAccountForm
    newUserDetails=newAccount.ValidateAccountForm
    
    instance_of_gallery=Gallery.Gallery()
    gallery=instance_of_gallery.BrowseGallery


# Tells the program where the root directory of the webpage is.
# Create an instance of MainApp and tell Cherrypy to send all requests under / to it. (ie all of them)
cherrypy.tree.mount(MainApp(), "/", config ="config.cfg")

# Start the web server, linking the configuration file
cherrypy.engine.start()

#Update the central address server at 30 sec interval


# And stop doing anything else. Let the web server take over.
cherrypy.engine.block()
