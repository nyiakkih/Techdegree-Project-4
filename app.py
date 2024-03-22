from models import (Base, session, 
                    Brands, Product, engine)












if __name__ == '__main__':
    Base.metadata.create_all(engine)
