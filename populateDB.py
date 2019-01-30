from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from catalogModels import Category, Item, Base, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

cat_rows_deleted = session.query(Category).delete()
item_rows_deleted = session.query(Item).delete()
user_rows_deleted = session.query(User).delete()
session.commit()

print("=============================")
print("cat_rows_deleted: %s" % cat_rows_deleted)
print("item_rows_deleted: %s" % item_rows_deleted)
print("user_rows_deleted: %s" % user_rows_deleted)
print("=============================")


try:
    # Create dummy user
    User1 = User(name="dummy", email="dummy@domain.com",
                 picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
    session.add(User1)
    session.commit()

    category1 = Category(name="Cricket")

    session.add(category1)
    session.commit()

    item1 = Item(name="Fiber Bat", description="Light weight fiber bat", category=category1, user_id=1)

    session.add(item1)
    session.commit()

    item2 = Item(name="Kookabura Ball", description="High quality cricket ball", category=category1, user_id=1)

    session.add(item2)
    session.commit()

    item3 = Item(name="Helmet", description="CA helmet batsman", category=category1, user_id=1)

    session.add(item3)
    session.commit()

    category2 = Category(name="Soccer")

    session.add(category2)
    session.commit()

    item4 = Item(name="Soccer ball", description="black and white", category=category2, user_id=1)

    session.add(item4)
    session.commit()

    category3 = Category(name="Snowboarding")

    session.add(category3)
    session.commit()

    item5 = Item(name="Snowboard", description="Slim and light snowboard", category=category3, user_id=1)

    session.add(item5)
    session.commit()




except IntegrityError:
    session.rollback()
    print("unique constraint error!")

print ("data added!")

#query data
data = session.query(Category).all()
item = session.query(Item).all()

for d in data:
    print(d.id)
    print(d.name)

for i in item:
    print(i.id)
    print(i.name)
    print(i.description)
    print(i.cat_name)
