import sqlite3

statusfeed = sqlite3.connect('databases/statusfeed.db')
c = statusfeed.cursor()
c.execute('''create table status (time integer,
                                  username text,
                                  page_id text,
                                  status text,
                                  uuid text,
                                  friends integer,
                                  colleagues integer,
                                  acquaintances integer,
                                  public integer)''')

c.execute('''create table updates (messageID text,
                                  created text,
                                  creator text,
                                  body text,
                                  link text,
                                  type integer,
                                  page_id text)''')
                                  
c.execute('''create table comment (time integer,
                                   username text,
                                   page_id text,
                                   status text,
                                   parent_uuid text,
                                   uuid text)''')
                                   
c.execute('''create table events (messageID integer,
                                  created text,
                                  creator text,
                                  body text,
                                  link text,
                                  year integer,
                                  month integer,
                                  day integer,
                                  hour integer,
                                  minute integer,
                                  second integer,
                                  duration integer,
                                  friends integer,
                                  colleagues integer,
                                  acquaintances integer,
                                  public integer,
                                  page_id text)''')
                                  
                                   
c.close()


login_credentials_database = sqlite3.connect('databases/login_credentials.db')
c = login_credentials_database.cursor() 
c.execute('''create table login_credentials (firstName text, surname text, username text, password text)''')
c.close()

"""
images_database = sqlite3.connect('databases/images.db')
c = images_database.cursor() 
c.execute('''create table images_database (page_id text, posted_by text, time int, imagefile blob)''')
c.close()
"""

images_database = sqlite3.connect('databases/images.db')
c = images_database.cursor() 
c.execute("""CREATE TABLE Images(time integer, username text, page_id text, comment text, Data BLOB, uuid text)""")
c.close()


exit()
