from flask import Flask, render_template, request, redirect,jsonify, url_for, flash

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from catalogModels import Category, Item, Base

#imports for anti-forgery step
from flask import session as login_session
import random
import string

# imports for gconnect method
# flow_from_clientsecrets method will create a flow object from the client_secrets.json file.
# this object will then contain client_id, client_secret and other oauth2 parameters
# FlowExchangeError method will catch errors if we run into any while exchanging one-time auth code
# for an access token
# httplib2: an http client library in python
# json: provides an API to convert in memory python objects to a serialize representation
# make_response: converts the return value from a function into a real response object that we can send off
# to the client
# requests: an apache2 licsensed HTTP library written in python similar to urllib but with few improvements
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

print("---clientID: " + CLIENT_ID)

#Create anti-forgery state token
def showLogin():
    state = "".join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session["state"] = state
    print("state: " + state)
    return render_template('login.html', STATE=state)

# @app.route('/gconnect', methods=['POST'])
def gconnect():
    print("----Entered gConnect!")
    # Validate state token
    if request.args.get('state') != login_session['state']:
        print("---login_session does not match!")
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    print("---Code: " + code)

    try:
        # Upgrade the authorization code into a credentials object
        print("---0")
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        print("---1 oauthflow")
        print(oauth_flow.client_secret)
        print(oauth_flow.redirect_uri)
        print(oauth_flow.auth_uri)
        print(oauth_flow.token_uri)
        oauth_flow.redirect_uri = 'postmessage'
        print("---2")
        print(oauth_flow.redirect_uri)
        credentials = oauth_flow.step2_exchange(code)
        print("---3")
        # print(credentials.to_json())
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    print("token gplus_id: %s" % gplus_id)

    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    # print("data:\n")
    # print(data)

    if data["name"]:
        login_session['username'] = data['name']
    else:
        login_session['username'] = data['email']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    #Check to see if user exists in the DB. Create one if does not exist
    # see if user exists
    # user_id = getUserID(data['email'])
    # if not user_id:
    #     user_id = createUser(login_session)
    # login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


 # DISCONNECT - Revoke a current user's token and reset their login_session


# @app.route('/gdisconnect')
def gdisconnect():
    print("----In gdisconnect")
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    print('access_token is: ')
    print(login_session['access_token'])
    print('gplus_id is: ')
    print(login_session['gplus_id'])
    print('User name is: ')
    print(login_session['username'])
    print('email is: ')
    print(login_session['email'])
    print('picture is: ')
    print(login_session['picture'])

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
