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
                 picture='https://pbs.twimg.com/profile_images/'
                         '2671170543/18debd694829ed78203a5a36dd364160_400x400'
                         '.png')
    session.add(User1)
    session.commit()

    category1 = Category(name="Cricket")

    session.add(category1)
    session.commit()

    item1 = Item(name="Pro Impact Cricket Bat",
                 description="This cricket bat is expertly crafted using "
                             "Kashmir willow to provide long-lasting "
                             "performance on the pitch. The bat should be "
                             "knocked in before use with a mallet or a ball",
                 category=category1, user_id=1)

    session.add(item1)
    session.commit()

    item2 = Item(name="Kookaburra Gold King Cricket Ball",
                 description="Icc approved Kookaburra leather cricket ball "
                             "for all format.T20, 30-30 and 40+ overs "
                             "available in white, Red and Pink color",
                 category=category1, user_id=1)

    session.add(item2)
    session.commit()

    item3 = Item(name="Cricket Steel Visor Helmet",
                 description="CA helmet for batsman. An Ideal Entry Level "
                             "Most Economically Priced Helmet With Cloth "
                             "Covered Standard Protective Grill With Foam "
                             "Pasted Ear Flaps", category=category1, user_id=1)

    session.add(item3)
    session.commit()

    category2 = Category(name="Soccer")

    session.add(category2)
    session.commit()

    item4 = Item(name="adidas Telstar 18 World Cup Mini Soccer Ball",
                 description="A mini version of the ball used in 2018 FIFA "
                             "World Cup matches, this adidas Telstar 18 "
                             "World Cup Mini Soccer Ball, like the full-size "
                             "version has an innovative panel shape. "
                             "Inspired by Russia's urban landscapes. ",
                 category=category2, user_id=1)

    session.add(item4)
    session.commit()

    item5 = Item(name="Traditional Soccer ball",
                 description="Black and white hexagonals. Great hit power and "
                             "swing capabilities",
                 category=category2, user_id=1)

    session.add(item5)
    session.commit()

    category3 = Category(name="Snowboarding")

    session.add(category3)
    session.commit()

    item6 = Item(name="Burton Custom Snowboard",
                 description="Step onto a snowboard with performance and "
                             "style with the Burton Custom men's snowboard. "
                             "Burton crafted the men's Custom to be an "
                             "all-mountain, freeride board. The Burton Custom "
                             "has a directional shape allowing you to get a "
                             "little more pop out of your tail while still "
                             "having that rad flow Burton has "
                             "always given us. ",
                 category=category3, user_id=1)

    session.add(item6)
    session.commit()

    item7 = Item(name="PULSAR MAGNETIC GOGGLES",
                 description="New for the 18/19 season, the Pulsar is the "
                             "latest evolution in the Glade ski and "
                             "snowboard goggle line. With a magnetic bond "
                             "between lens and frame, you can swap between "
                             "lenses in seconds.",
                 category=category3, user_id=1)

    session.add(item7)
    session.commit()

    category4 = Category(name="Baseball")

    session.add(category4)
    session.commit()

    item8 = Item(name="Baseball bat",
                 description='This Personalized "Home Run" '
                             'Novelty Baseball Bat is a great gift for the '
                             'baseball fan who dreams of playing '
                             'in the majors and has always wanted their name '
                             'or custom design on a baseball bat. Engraving '
                             'is FREE and unlimited!',
                 category=category4, user_id=1)

    session.add(item8)
    session.commit()

    item9 = Item(name="MLB Team Logo Baseball",
                 description="Composite 80%/Synthetic 15%/5% Cotton, "
                             "Imported, Official regulation size Baseball, "
                             "Features primary team logo on front panel, "
                             "Commissioner's signature on the top panel",
                 category=category4, user_id=1)

    session.add(item9)
    session.commit()

    category5 = Category(name="Hockey")

    session.add(category5)
    session.commit()

    item10 = Item(name="STALLION HPR 1.2 ICE HOCKEY STICK",
                  description="With an ultra-High balance point and"
                  " performance engineering the High Performance "
                  "Ratio of the new Stallion stick has been "
                  "optimized for players seeking durability and "
                  "performance in one package.", category=category5, user_id=1)

    session.add(item10)
    session.commit()

    item11 = Item(name="SURGEON RX3 ICE HOCKEY GLOVE",
                  description="The RX3 glove combines Precision fit,"
                  " lightweight protection, next generation materials "
                  "for elite level feel and responsiveness. ",
                  category=category5, user_id=1)

    session.add(item11)
    session.commit()

    category6 = Category(name="Skating")

    session.add(category6)
    session.commit()

    item12 = Item(name="BATTLESHIP 27\" SKATEBOARD",
                  description="The latest addition to our Classics line, "
                  "the Battleship 27\" combines a muted grey deck and trucks "
                  "with poppy red wheels for the perfect color combination. "
                  "Constructed with our secret plastic formula and high "
                  "quality components, this cruiser will have you rolling "
                  "for years to come.", category=category6, user_id=1)

    session.add(item12)
    session.commit()

    category7 = Category(name="Basketball")

    session.add(category7)
    session.commit()

    item13 = Item(name="JORDAN MINI BASKETBALL",
                  description="The Jordan Mini Basketball gives you an "
                  " enhanced feel and signature style, making it the perfect "
                  "basketball for you. Whether you're hooping in the driveway "
                  "or heading to the gym, this mini basketball helps you take "
                  "your game to the next level.",
                  category=category7, user_id=1)

    session.add(item13)
    session.commit()

    item14 = Item(name="Spalding NBA Official Game Basketball",
                  description="Get into the game with the Spalding "
                  "NBA Official Game Basketball and achieve "
                  "greatness on the court. This game ball "
                  "holds "
                  "to the standard size and weight of the "
                  "association, while featuring the NBA "
                  "Twitter handle and the facsimile signature"
                  " of Commissioner Adam Silver",
                  category=category7, user_id=1)

    session.add(item14)
    session.commit()


except IntegrityError:
    session.rollback()
    print("unique constraint error!")

print("data added!")

# query data
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
