from sqlalchemy import Column, Sequence, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    items = relationship("Item")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'items': [item.serialize for item in self.items]
        }

class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    name = Column(String (80), nullable=False)
    description = Column(String (250))
    cat_name = Column(String(80), ForeignKey("category.name"))
    category = relationship(Category)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id
        }

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)