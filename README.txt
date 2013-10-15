====================
SPACEBOOK USER GUIDE
====================


----CONTENTS


    1.      Installation and Running Server
    
    2.      Status Feed
    
    3.      Gallery
    
    4.      Friends
    
    5.      Events
    

===============================
1. INSTALLATION AND RUNNING SERVER
===============================


----Initalizing SPACEBOOK
        
            Run "python INITIALIZE.py" from your SPACEBOOK directory. This will
        initialize all database tables. This must be done before running
        SPACEBOOK.py for the first time, and can only be run once,
        with the exception of cleaning the system.
    
----Running SPACEBOOK
    
        To run SPACEBOOK, run "./SPACEBOOK.py" from the spacebook directory.
    
----Delete all accounts and data from SPACEBOOK
        
            Run "make clean" from the SPACEBOOK directory.
        Dont forget to initalize before running SPACEBOOK again
   
    
==============
2. STATUS FEED
==============
    
    
----Status Feed
    
            The "Comment..." box allows the user to make a new status on
        their own wall, and set permissions as to who can view them.
            
            Public statuses are avaliable to clients whom arent logged in
        as they visit your page.
            
            Comment boxes are supplied below each status
        these allow those who have permission to make further comments.
            
            Entire status messages are able to be deleted locally using
        the small hyperlinked "x" next to the authors name
        
        
----Network Neighbourhood
    
    
            This part of the page allows the logged in user to see the latest 100
        friend's statuses. These are in decending date order, and are
        fetched automatically.
        
        
----Browse and Caption
    
    
            This allows the user to upload a new image into the gallery,
        all of which is publicly avaliable. To set the image as your avatar,
        check the checkbox. Avatars appear beside the users status feed,
        and in the gallery. When a user creates a new avatar,
        the previous one is replaced, and removed from the gallery.
            A caption may be added to the image to appear alongside it in the gallery.
        To submit the image, press return in the "Caption" Dialogue box
        
==========
3. GALLERY
==========


            The gallery is a publicly viewable area which the user may post
        images to broadcast. The users avatar is included in this gallery.
            It is possible, for those authenticated, and with permission, to delete
        images saved in the gallery.




==========
4. FRIENDS
==========


----Register of users
    
    
            A list of all users listed on the current users server. They are listed
        with their username, time last seen, and their IP address and port.
        These entries are hyperlinked to the corresponding users public page.
        
----Friends

    
            A list of friends by full name. Friends can be deleted using the small "x"
        next to the corresponding entry. If their server requires a key other than
        your logon key, it may be privately entered. The persons name is hyperlinked
        to their default authentication page.
    
    
----Pending Requests


            When somebody fills out the forms on your public page, a friend request is
        issued to the server, and is shown here. You may assign which permissions
        they may have, then accept them with the "+" symbol, or delete the request
        with the "x"
        
        
=========
5. EVENTS
=========


            Creating events is as simple as entering the date details into the form,
        and filling out a description in the details box. Events are not currently
        able to be pushed or pulled from SPACEBOOK; these must be viewed by visiting
        a users events tab.
        
        
