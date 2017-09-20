import sys, json, flask, flask_socketio, httplib2, uuid
from flask import Response, request
from flask_socketio import SocketIO
from apiclient import discovery
from oauth2client import client
from googleapiclient import sample_tools
from rfc3339 import rfc3339
from dateutil import parser

app = flask.Flask(__name__)
socketio = SocketIO(app)

#Begin flask route
@app.route('/')
def index():
    if 'credentials' not in flask.session:
      return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    return flask.render_template('index.html')

#Begin oauth callback route
@app.route('/oauth2callback')
def oauth2callback():
  flow = client.flow_from_clientsecrets(
      'client_secrets.json',
      scope='https://www.googleapis.com/auth/calendar',
      redirect_uri=flask.url_for('oauth2callback', _external=True))
  if 'code' not in flask.request.args:
    auth_uri = flow.step1_get_authorize_url()
    return flask.redirect(auth_uri)
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()
    return flask.redirect(flask.url_for('index'))

#On event submission from client
@socketio.on('eventDesc')
def eventDesc(data):
    print "INSIDE eventDesc!!!"
    name = data['name']
    sTime =  parser.parse(data['sTime'])
    eTime =  parser.parse(data['eTime'])
    cid = data['cid']
    sConverted = rfc3339(sTime)
    eConverted = rfc3339(eTime)
    oauth(name, cid, sConverted, eConverted)

#On getCalendars event from client. Gets the calendar names and their corresponding ID's
@socketio.on("getCalendars")
def getCalendars():
    calendars = []
    try:
        credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    except credError:
        print "did not assign credentials"
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http_auth)
    page_token = None
    while True:
      calendar_list = service.calendarList().list(pageToken=page_token).execute()
      for calendar_list_entry in calendar_list['items']:
        calendars.append({"name": calendar_list_entry['summary'], "id": calendar_list_entry['id']})
      page_token = calendar_list.get('nextPageToken')
      if not page_token:
        break
    flask_socketio.emit("calendarReturn", {"data": calendars})

#Function to add event into calendar selected
def oauth(name, cid, sTime, eTime):
    print sTime
    print eTime
    print name
    print cid
    try:
        credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    except credError:
        print "did not assign credentials"
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http_auth)
    eventName = ""
    event = {
        'summary': name,
        'start': {
        'dateTime': sTime
        },
        'end': {
        'dateTime': eTime
        },
        'iCalUID': 'originalUID'
    }
    imported_event = service.events().import_(calendarId=cid, body=event).execute()
    print "Succesfully Imported Event"

#Server setup
if __name__ == '__main__':
    app.secret_key = str(uuid.uuid4())
    socketio.run(
    app,
    host='localhost',
    port=int(8080)
    )
