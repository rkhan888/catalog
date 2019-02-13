from flask import Flask, render_template, request, redirect, url_for, flash, \
    jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from catalogModels import Category, Item, User, Base

# imports for anti-forgery step
from flask import session as login_session
import random
import string

# imports for gconnect method
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r')
                       .read())['web']['client_id']
APPLICATION_NAME = "Catalog App"
# print("---clientID: " + CLIENT_ID)


@app.route("/login")
def showLogin():
    state = "".join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session["state"] = state
    # print("state: " + state)
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    print("----Entered fbConnect!")
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print("FB access token received %s ") % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r')
                        .read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r')
                            .read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_' \
          'type=fb_exchange_token&client_id=%s&' \
          'client_secret=%s&fb_exchange_token=%s' % \
          (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server
        token exchange we have to split the token first on
        commas and select the first index which gives us the
        key : value for the server access token then we split it
        on colons to pull out the actual token value
        and replace the remaining quotes with nothing
        so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&' \
          'fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&' \
          'redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;' \
              'border-radius: 150px;-webkit-border-radius: 150px;' \
              '-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    print("----Entered fbDisconnect!")
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    print("----Entered gConnect!")
    # Validate state token
    if request.args.get('state') != login_session['state']:
        print("login_session does not match!")
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    print("Code: " + code)

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
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
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
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

    if "name" in data:
        login_session['username'] = data['name']
    else:
        login_session['username'] = data['email']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # Check to see if user exists in the DB. Create one if does not exist
    # see if user exists
    user_id = getUserID(data['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;' \
              '-webkit-border-radius: 150px;' \
              '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


@app.route('/gdisconnect')
def gdisconnect():
    print("----In gdisconnect")
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Disconnect based on provider


@app.route('/disconnect')
def disconnect():
    print("----Entered disconnect!")
    print("--loginSession Before: ")
    print(login_session)
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        print("--loginSession After: ")
        print(login_session)
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


# User Helper Functions


def createUser(login_session):
    session = DBSession()

    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    session = DBSession()

    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    session = DBSession()

    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except NoResultFound:
        return None


@app.route("/")
@app.route("/catalog")
def showCategories():
    session = DBSession()

    categories = session.query(Category).all()
    latestItems = session.query(Item).order_by(Item.id.desc()).limit(8)

    if "username" not in login_session:
        return render_template('showCategories.html', categories=categories,
                               latestItems=latestItems, loginStatus=0,
                               login_session=login_session)
    else:
        return render_template('showCategories.html', categories=categories,
                               latestItems=latestItems, loginStatus=1,
                               login_session=login_session)


@app.route("/catalog/<category>/items")
def showItems(category):
    session = DBSession()

    items = session.query(Item).filter_by(cat_name=category).all()

    if "username" not in login_session:
        return render_template('showItems.html', myCategory=category,
                               items=items, loginStatus=0,
                               login_session=login_session)
    else:
        return render_template('showItems.html', myCategory=category,
                               items=items, loginStatus=1,
                               login_session=login_session)


@app.route("/catalog/<category>/<item>")
def itemInfo(category, item):
    session = DBSession()

    item = session.query(Item).filter(func.lower(Item.name) == func.lower(
        item), func.lower(Item.cat_name) == func.lower(category)).one()

    if "username" in login_session and \
            login_session["user_id"] != item.user_id:
        return render_template('showItemInfo.html', myCategory=category,
                               item=item, loginStatus=1, sameUser=0,
                               login_session=login_session)

    elif "username" in login_session and \
            login_session["user_id"] == item.user_id:
        return render_template('showItemInfo.html', myCategory=category,
                               item=item, loginStatus=1, sameUser=1,
                               login_session=login_session)

    else:
        return render_template('showItemInfo.html', myCategory=category,
                               item=item, loginStatus=0, sameUser=0,
                               login_session=login_session)


@app.route("/catalog/add", methods=["GET", "POST"])
def addItem():
    if "username" not in login_session:
        return redirect(url_for("showLogin"))

    session = DBSession()

    allCats = session.query(Category).all()

    if request.method == "POST":
        existingCat = session.query(Category).filter(func.lower(
            Category.name) == func.lower(request.form["catName"])).all()

        if (existingCat):
            item = session.query(Item)\
                .filter(func.lower(Item.name) == func
                        .lower(request.form["name"]),
                        func.lower(Item.cat_name) == func
                        .lower(existingCat[0].name)).all()
            if (item):
                flash("item already exist!")
                return render_template("addItem.html", allCats=allCats,
                                       login_session=login_session)
            print(existingCat[0].name)
            newItem = Item(name=request.form["name"],
                           description=request.form["desc"],
                           cat_name=existingCat[0].name,
                           user_id=login_session["user_id"])
            session.add(newItem)
            session.commit()
            flash("New Item Added!")
            print("New Item Added!")
            return redirect(url_for("showItems", category=existingCat[0].name))

        newCat = Category(name=request.form["catName"])
        session.add(newCat)
        session.commit()

        newItem = Item(name=request.form["name"],
                       description=request.form["desc"],
                       category=newCat,
                       user_id=login_session["user_id"])
        session.add(newItem)
        session.commit()
        flash("New Category & Item Added!")
        print("New Category & Item Added!")
        return redirect(url_for("showItems", category=newCat.name))

    else:
        return render_template("addItem.html", allCats=allCats,
                               login_session=login_session)


@app.route("/catalog/<category>/<item>/edit", methods=["GET", "POST"])
def editItem(category, item):

    if "username" not in login_session:
        return redirect(url_for("showLogin"))

    session = DBSession()

    itemToEdit = session.query(Item).\
        filter(func.lower(Item.name) == func.lower(item),
               func.lower(Item.cat_name) == func.lower(category)).one()
    owner = session.query(User).filter_by(id=itemToEdit.user_id).one()

    if owner.email != login_session["email"]:
        flash("You cannot make changes to the items created by others")
        return redirect(url_for("showCategories"))

    allCats = session.query(Category).all()

    if request.method == "POST":
        if request.form["newName"]:
            itemToEdit.name = request.form["newName"]
        if request.form["newDesc"]:
            itemToEdit.description = request.form["newDesc"]
        if request.form["newCat"]:
            itemToEdit.cat_name = request.form["newCat"]
        session.add(itemToEdit)
        session.commit()
        flash("item updated")
        return redirect(url_for("showItems", category=itemToEdit.cat_name))
    else:
        return render_template("editItem.html", item=itemToEdit,
                               allCats=allCats, login_session=login_session)


@app.route("/catalog/<category>/<item>/delete", methods=["GET", "POST"])
def deleteItem(category, item):
    if "username" not in login_session:
        return redirect(url_for("showLogin"))

    session = DBSession()

    itemToDelete = session.query(Item)\
        .filter(func.lower(Item.name) == func.lower(item),
                func.lower(Item.cat_name) == func.lower(category)).one()
    owner = session.query(User).filter_by(id=itemToDelete.user_id).one()

    if owner.email != login_session["email"]:
        flash("You cannot make changes to the items created by others")
        return redirect(url_for("showCategories"))

    if request.method == "POST":
        session.delete(itemToDelete)
        session.commit()
        flash("Item deleted successfully")
        return redirect(url_for("showItems", category=itemToDelete.cat_name))
    else:
        return render_template("deleteItem.html", item=itemToDelete,
                               login_session=login_session)

@app.route("/catalog/<category>/<item>/json")
def showSpecificJson(category, item):
    session = DBSession()

    try:
        item = session.query(Item).filter(func.lower(Item.name) == func.lower(
            item), func.lower(Item.cat_name) == func.lower(category)).one()

    except NoResultFound:
        return jsonify(error="no result found")

    return jsonify(Item=[item.serialize])

@app.route("/catalog.json")
def showJson():
    session = DBSession()

    categories = session.query(Category).all()

    return jsonify(Category=sorted([i.serialize for i in categories]))


if __name__ == '__main__':
    app.secret_key = "super secret key"
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
