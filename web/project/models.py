import uuid

from sqlalchemy import Integer, Column, String, DECIMAL, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Menu(Base):
    __tablename__: str = "menus"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, index=True)
    description = Column(String, index=True)

    submenus = relationship(
        "Submenu",
        back_populates="menu",
        cascade="all, delete",
        passive_deletes=True,
    )



class Submenu(Base):
    __tablename__: str = "submenus"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    menu_id = Column(ForeignKey("menus.id", ondelete="CASCADE"), index=True)

    menu = relationship("Menu", back_populates="submenus")

    dishes = relationship(
        "Dish",
        back_populates="submenu",
        cascade="all, delete",
        passive_deletes=True,
    )



class Dish(Base):
    __tablename__: str = "dishes"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(Numeric(scale=2), index=True)
    submenu_id = Column(ForeignKey("submenus.id", ondelete="CASCADE"), index=True)

    submenu = relationship("Submenu", back_populates="dishes")


