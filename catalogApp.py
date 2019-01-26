from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from catalogModels import Category, Item, Base

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

app = Flask(__name__)

@app.route("/")
@app.route("/catalog")
def showCategories():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    categories = session.query(Category).all()

    return render_template('showCategories.html', categories=categories)

@app.route("/catalog/<category>/items")
def showItems(category):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    items = session.query(Item).filter_by(cat_name=category).all()

    return render_template('showItems.html', myCategory=category, items=items)

@app.route("/catalog/<category>/<item>")
def itemInfo(category, item):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    item = session.query(Item).filter(func.lower(Item.name) == func.lower(item), func.lower(Item.cat_name) == func.lower(category)).one()

    return render_template('showItemInfo.html', myCategory=category, item=item)

@app.route("/catalog/add", methods=["GET", "POST"])
def addItem():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    allCats = session.query(Category).all()

    if request.method == "POST":
        existingCat = session.query(Category).filter(func.lower(Category.name) == func.lower(request.form["catName"])).all()

        if (existingCat):
            item = session.query(Item).filter(func.lower(Item.name) == func.lower(request.form["name"]), func.lower(Item.cat_name) == func.lower(existingCat[0].name)).all()
            if (item):
                flash("item already exist!")
                return render_template("addItem.html", allCats=allCats)
            print(existingCat[0].name)
            newItem = Item(name=request.form["name"], description=request.form["desc"], cat_name=existingCat[0].name)
            session.add(newItem)
            session.commit()
            flash("New Item Added!")
            print("New Item Added!")
            return redirect(url_for("showItems", category=existingCat[0].name))

        newCat = Category(name=request.form["catName"])
        session.add(newCat)
        session.commit()

        newItem = Item(name=request.form["name"], description=request.form["desc"], category=newCat)
        session.add(newItem)
        session.commit()
        flash("New Category & Item Added!")
        print("New Category & Item Added!")
        return redirect(url_for("showItems", category=newCat.name))

    else:
        return render_template("addItem.html", allCats=allCats)

@app.route("/catalog/<category>/<item>/edit", methods=["GET", "POST"])
def editItem(category, item):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    allCats = session.query(Category).all()
    itemToEdit = session.query(Item).filter(func.lower(Item.name) == func.lower(item), func.lower(Item.cat_name) == func.lower(category)).one()
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
        return render_template("editItem.html", item=itemToEdit, allCats=allCats)

@app.route("/catalog/<category>/<item>/delete", methods=["GET", "POST"])
def deleteItem(category, item):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    itemToDelete = session.query(Item).filter(func.lower(Item.name) == func.lower(item), func.lower(Item.cat_name) == func.lower(category)).one()
    if request.method == "POST":
        session.delete(itemToDelete)
        session.commit()
        flash("Item deleted successfully")
        return redirect(url_for("showItems", category=itemToDelete.cat_name))
    else:
        return render_template("deleteItem.html", item=itemToDelete)

@app.route("/catalog.json")
def showJson():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    categories = session.query(Category).all()

    return jsonify(Category= sorted([i.serialize for i in categories]))

if __name__ == '__main__':
    app.secret_key = "super secret key"
    app.debug = True
    app.run(host="0.0.0.0", port=5000)