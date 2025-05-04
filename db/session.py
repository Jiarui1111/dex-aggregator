from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///./dex.db"  # Can be replaced by PostgreSQL

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
