from models import Base, session, Brands, Product, engine
from datetime import datetime
import csv
from sqlalchemy import func, distinct

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
    with open('inventory.csv') as csvfile:
        data = csv.DictReader(csvfile)
        for row in data:
            product_name = row['product_name']
            product_price = clean_price(row['product_price'])
            product_quantity = int(row['product_quantity'])
            date_updated = clean_date(row['date_updated'])
            brand_name = row['brand_name']

            brand = session.query(Brands).filter_by(brand_name=brand_name).first()
            if not brand:
                brand = Brands(brand_name=brand_name)
                session.add(brand)
                session.commit()

            existing_product = session.query(Product).join(Brands).filter(
                Product.product_name == product_name,
                Brands.brand_name == brand_name
            ).first()

            if existing_product:
                existing_date_updated = datetime.combine(existing_product.date_updated, datetime.min.time())
                new_date_updated = datetime.combine(date_updated, datetime.min.time())

                if existing_date_updated < new_date_updated:
                    existing_product.product_price = product_price
                    existing_product.product_quantity = product_quantity
                    existing_product.date_updated = date_updated
                    print(f"Product '{product_name}' updated.")
                else:
                    print(f"Product '{product_name}' already exists with more recent data. Skipping...")
            else:
                new_product = Product(
                    product_name=product_name,
                    product_price=product_price,
                    product_quantity=product_quantity,
                    date_updated=date_updated,
                    brands=brand
                )
                session.add(new_product)
                print(f"Product '{product_name}' added to the database.")

    session.commit()
    print("Inventory added successfully.")

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
        product = session.query(Product).filter_by(product_id=product_id).first()
        if product:
            print("\nProduct details:")
            print(f"Product ID: {product.product_id}")
            print(f"Product Name: {product.product_name}")
            print(f"Quantity: {product.product_quantity}")
            print(f"Price: {product.product_price / 100}")
            print(f"Date Updated: {product.date_updated.strftime('%m/%d/%Y')}")
            print(f"Brand: {product.brands.brand_name}")
            print("\nOptions:")
            print("1. Edit Product")
            print("2. Delete Product")
            print("3. Go Back")
            option = input("\nEnter your choice: ")
            if option == '1':
                edit_product(product)
            elif option == '2':
                delete_product(product)
            elif option == '3':
                return
            else:
                print("Invalid option. Please enter a valid choice.")
        else:
            print("Product not found. Please enter a valid product ID.")
    except ValueError:
        print("Invalid product ID. Please enter a valid integer ID.")

def edit_product(product):
    print("\nEditing product details.")
    new_product_name = input("Enter the new product name (press enter to keep current): ")
    new_product_quantity = input("Enter the new quantity (press enter to keep current): ")
    new_product_price = input("Enter the new price (press enter to keep current): ")
    new_brand_name = input("Enter the new brand name (press enter to keep current): ")

    print(f"\nNew Product Name: {new_product_name}")
    print(f"New Quantity: {new_product_quantity}")
    print(f"New Price: {new_product_price}")
    print(f"New Brand Name: {new_brand_name}")

    if not any([new_product_name, new_product_quantity, new_product_price, new_brand_name]):
        print("\nNo changes provided. Exiting edit mode.")
        return

    if new_product_price:
        new_product_price = clean_price(new_product_price)
        if new_product_price is None:
            print("Invalid price format. Price not updated.")
            return

    if new_brand_name:
        brand = session.query(Brands).filter_by(brand_name=new_brand_name).first()
        if not brand:
            brand = Brands(brand_name=new_brand_name)
            session.add(brand)
            session.commit()

    if new_product_name:
        existing_product = session.query(Product).filter_by(product_name=new_product_name).first()
        if existing_product:
            if existing_product.date_updated < datetime.now():
                print(f"Product '{new_product_name}' already exists in the database with more recent data. Skipping...")
                return

    if new_product_name:
        product.product_name = new_product_name
    if new_product_quantity:
        product.product_quantity = int(new_product_quantity)
    if new_product_price:
        product.product_price = new_product_price
    if new_brand_name:
        product.brands = brand

    product.date_updated = datetime.now()
    session.commit()
    print("Product updated successfully.")

def delete_product(product):
    confirmation = input("Are you sure you want to delete this product? (yes/no): ").lower()
    if confirmation == 'yes':
        session.delete(product)
        session.commit()
        print("Product deleted successfully.")
    elif confirmation == 'no':
        print("Deletion canceled.")
    else:
        print("Invalid choice. Deletion canceled.")

def add_new_product():
    print("\nAdding a new product.")
    product_name = input("Enter the product name: ")
    product_quantity = input("Enter the product quantity: ")
    product_price = input("Enter the product price: ")
    brand_name = input("Enter the brand name: ")

    product_price = clean_price(product_price)
    if product_price:
        print("Invalid price format. Please enter a valid price.")
        return
    
    existing_product = session.query(Product).filter_by(product_name=product_name).first()

    if existing_product:
        existing_product.product_quantity = int(product_quantity)
        existing_product.product_price = product_price
        existing_product.date_updated = datetime.now()

        brand = session.query(Brands).filter_by(brand_name=brand_name).first()
        if not brand:
            brand = Brands(brand_name=brand_name)
            session.add(brand)
            session.commit()
        existing_product.brands = brand
        session.commit()
        print(f"Product '{product_name}' already exists in the database. Updated.")
    else:
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
    print("\nAnalyzing the database.")

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

    total_products = session.query(Product).count()
    total_price = session.query(func.sum(Product.product_price)).scalar()
    average_price = total_price / total_products if total_products > 0 else 0
    average_price = round(average_price / 100, 2)
    print(f"Average price of products: ${average_price}")

    total_inventory_value = session.query(func.sum(Product.product_price * Product.product_quantity)).scalar()
    print(f"Total inventory value: ${total_inventory_value / 100}")

    unique_brands_count = session.query(func.count(distinct(Brands.brand_name))).scalar()
    print(f"Number of unique brands: {unique_brands_count}")

    print("\nProduct count by brand:")
    for brand, count in brand_counts.items():
        print(f"{brand}: {count}")

    print("\nAnalysis complete.")

def backup_database():
    products = session.query(Product).all()
    if products:
        try:
            with open('backup_inventory.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["product_name", "product_price", "product_quantity", "date_updated", "brand_name"])

                for product in products:
                    writer.writerow([
                        product.product_name,
                        f"${product.product_price / 100:.2f}",
                        product.product_quantity,
                        product.date_updated.strftime("%m/%d/%Y"),
                        product.brands.brand_name
                    ])
            print("\nProduct data backed up successfully.")
        except Exception as e:
            print(f"An error occurred while creating the product backup: {e}")
    else:
        print("\nNo products found in the database.")

    brands = session.query(Brands).all()
    if brands:
        try:
            with open('backup_brands.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["brand_name"])
                for brand in brands:
                    writer.writerow([brand.brand_name])
            print("Brand data backed up successfully.")
        except Exception as e:
            print(f"An error occurred while creating the brand backup: {e}")
    else:
        print("No brands found in the database.")

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    add_brands_csv()
    add_inventory_csv()
    app()