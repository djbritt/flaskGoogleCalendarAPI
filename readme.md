# Google Calendar API - Get Calendars and ID, Submit Event :star2:
## By Daniel Britt

# Purpose
This is an app to show how to use Flask routes, and other calendar functions with the Google Calendar API.

# Tips and Notes
This app uses the CalendarList: get and CalendarList: import

You need to create a client_secrets.json file using the Google Developer Console. To do this, enable the Google Calendar API, create a project, add the information below. Have it in the same directory as the python file. In addition, the info I used is as follows.

```
Authorized Javascript Origins
http://localhost:8080

Authorized redirect URIs
http://localhost:8080/oauth2callback
```

# Running
Simply download the app, have the client_secrets.json file in the same directory as app.py, and type

```
$ python app.py
```

# Technologies
This project uses Python, Flask, SocketIO, rfc3339, HTML5, CSS3, and jQuery.
