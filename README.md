# Catalog App

## Introduction
This web application lists all the items from a variety of sports categories. Users can go around and see the details for each sports item. Users can log in to the application using their Google or Facebook account. Once logged in they can create new categories or add items to the existing categories. They can also remove and edit their items. 

A REST endpoint at `/catalog.json` is also implemented to provide all information in JSON.

## How to run

Running this application is simple.
Go ahead and clone the repo to your local vagrant shared directory. Before running the application run the `populateDB.py` file by using the following command `python populateDB.py`. This will populate the database with some data for the application.

After populating the database run `catalogApp.py` file to start the the application. Now to go to the web browser and navigate to `http://localhost:5000/catalog` to land on the application's homepage. Enjoy! :-)
