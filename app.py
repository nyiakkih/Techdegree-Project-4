from models import Base, session, Brands, Product, engine
from datetime import datetime
import csv

def menu():
    print("\nWelcome to the Grocery Store Inventory App!")
    print("\nPlease select an option:")
    print("\nV - View details of a single product")
    print("N - Add a new product")
    print("A - View analysis")
    print("B - Backup database")
    print("Q - Quit")

def add_brands_csv():
    with open('brands.csv') as csvfile:
        data = csv.DictReader(csvfile)
        for row in data:
            brand_name = row['brand_name']
            new_brand = Brands(brand_name=brand_name)
            session.add(new_brand)
        session.commit()
    # print("Brands added successfully.")

def clean_date(date_str):
    date_object = datetime.strptime(date_str, '%m/%d/%Y')
    return date_object
    
def clean_price(price_str):
    try:
        price_str = ''.join(char for char in price_str if char.isdigit() or char == '.')
        price_float = float(price_str)
        return int(price_float * 100)
    except ValueError:
        print(f"Invalid price format: {price_str}")
        return

def add_inventory_csv():
    product_data = {}

    with open('inventory.csv') as csvfile:
        data = csv.DictReader(csvfile)
        for row in data:
            product_name = row['product_name']
            product_price = clean_price(row['product_price'])
            product_quantity = int(row['product_quantity'])
            date_updated = clean_date(row['date_updated'])
            brand_name = row['brand_name']

            if product_name in product_data:
                existing_product = product_data[product_name]
                if existing_product.date_updated < date_updated:
                    existing_product.product_price = product_price
                    existing_product.product_quantity = product_quantity
                    existing_product.date_updated = date_updated
                    existing_product.brand_name = brand_name
                    # print(f"Product '{product_name}' already exists in the database. Updated.")
            else:
                brand = session.query(Brands).filter_by(brand_name=brand_name).first()
                if not brand:
                    brand = Brands(brand_name=brand_name)
                    session.add(brand)
                    session.commit()

                new_product = Product(
                    product_name=product_name,
                    product_price=product_price,
                    product_quantity=product_quantity,
                    date_updated=date_updated,
                    brands=brand
                )
                product_data[product_name] = new_product
                # print(f"Product '{product_name}' added to the database.")

    session.add_all(product_data.values())
    session.commit()
    # print("Inventory added successfully.")

def app():
    while True:
        menu()
        choice = input("\nEnter your choice: ").strip().upper()

        if choice == 'V':
            view_product_details()
        elif choice == 'N':
            add_new_product()
        elif choice == 'A':
            analyze_database()
        elif choice == 'B':
            backup_database()
        elif choice == 'Q':
            print("Exiting the application. Goodbye!")
            break
        else:
            print("Invalid input. Please try again.")

def get_product_by_id(product_id):
    product = session.query(Product).filter_by(product_id=product_id).first()
    if product:
        print("\nProduct found:")
        print(product)
    else:
        print("Product not found. Please enter a valid product ID.")

def view_product_details():
    print("\nViewing details of a single product.")
    product_id = input("Enter the product ID: ")
    try:
        product_id = int(product_id)
        get_product_by_id(product_id)
    except ValueError:
        print("Invalid product ID. Please enter a valid integer ID.")

def add_new_product():
    print("\nAdding a new product.")
    product_name = input("Enter the product name: ")
    product_quantity = input("Enter the product quantity: ")
    product_price = input("Enter the product price: ")
    brand_name = input("Enter the brand name: ")

    product_price = clean_price(product_price)
    if product_price is None:
        print("Invalid price format. Please enter a valid price.")
        return
    
    brand = session.query(Brands).filter_by(brand_name=brand_name).first()
    if not brand:
        brand = Brands(brand_name=brand_name)
        session.add(brand)
        session.commit()

    new_product = Product(
        product_name=product_name,
        product_quantity=int(product_quantity),
        product_price=product_price,
        date_updated=datetime.now(),
        brands=brand
    )
    session.add(new_product)
    session.commit()
    print("New product added successfully.")

def analyze_database():
    most_expensive = session.query(Product).order_by(Product.product_price.desc()).first()
    print(f"\nThe most expensive item is: {most_expensive.product_name}, Price: ${most_expensive.product_price / 100}")

    least_expensive = session.query(Product).order_by(Product.product_price).first()
    print(f"The least expensive item is: {least_expensive.product_name}, Price: ${least_expensive.product_price / 100}")

    brand_counts = {}
    for product in session.query(Product):
        brand_name = product.brands.brand_name
        brand_counts[brand_name] = brand_counts.get(brand_name, 0) + 1

    most_products_brand = max(brand_counts, key=brand_counts.get)
    print(f"The brand with the most products is: {most_products_brand}; Number of products: {brand_counts[most_products_brand]}")

def backup_database():
    products = session.query(Product).all()
    if products:
        try:
            with open('backup.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["product_id", "product_name", "product_quantity", "product_price", "date_updated", "brand_name"])
                for product in products:
                    writer.writerow([product.product_id, product.product_name, product.product_quantity, product.product_price / 100, product.date_updated.strftime("%m/%d/%Y"), product.brands.brand_name])
            print("\nDatabase backup created successfully.")
        except Exception as e:
            print(f"An error occurred while creating the backup: {e}")
    else:
        print("No products found in the database.")

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    add_brands_csv()
    add_inventory_csv()
    app()