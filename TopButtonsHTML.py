def TopButtonsHTML(page_title=""):

    page = """
    <html>
    <head>
    <link rel="stylesheet" type="text/css" href="style.css" />
    """
    page += "<title>%s</title>" % (page_title,)
    page +="""
    </head>

    <body>
    
    <div id="headder">
    <table align="center" width="100%">
    <tr>
    <td class="SPACEBOOK"><a class="SPACEBOOK" href="/home">SPACEBOOK</a></td>
    <td class="left"><a class="headderbutton" href="/home">STATUS FEED</a></td>
    <td class="left"><a class="headderbutton" href="/gallery">GALLERY</a></td>
    <td class="left"><a class="headderbutton" href="/friends">FRIENDS</a></td>
    <td class="left"><a class="headderbutton" href="/events">EVENTS</a></td>
    <td class="right"><a class="headderbutton" href="/signout">LOG OUT</a></td>
    </tr>
    </table>
    </div>

    """
    return page
