from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
#             type of DB+DB driver  username:password@host/DBname
DATABASE_URL='postgresql+psycopg2://postgres:postgres@localhost:5433/Blogger'
# engine that handles all connection and queries to and on DB
engine= create_engine(DATABASE_URL)

# sessionFactory manmages transations and interactions with the DB
SessionLocal= sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base: DeclarativeMeta = declarative_base()


