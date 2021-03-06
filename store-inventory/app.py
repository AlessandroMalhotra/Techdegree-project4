#! usr/bin/env python3
import csv
import datetime
import sys
import os

from collections import OrderedDict

from peewee import *

db = SqliteDatabase('inventory.db')


# Create Database with columns for product information
class Product(Model):
	product_id = AutoField()
	product_name = CharField(unique=True)
	product_price = IntegerField()
	product_quantity = IntegerField()
	date_updated = DateTimeField(default=datetime.datetime.now)

	class Meta():
		database = db

# Initialize database and create tables 
def initialize():
    db.connect()
    db.create_tables([Product], safe=True)
    db.close()


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


# Reads in the csv file turns into a dictionary and update values in 3 columns and then adds them to database
def read_csv():
    with open('inventory.csv', newline='') as inventory_csv:
        inventory_reader = csv.DictReader(inventory_csv, delimiter=',')
        rows = list(inventory_reader)
        for row in rows:
            row['product_price'] = int(row['product_price'].replace('$', '').replace('.', ''))
            row['product_quantity'] = int(row['product_quantity'])
            row['date_updated'] = (datetime.datetime.strptime(row['date_updated'],'%m/%d/%Y').date())
            try:
                Product.create(
                product_name = row['product_name'],
                product_price = row['product_price'],
                product_quantity = row['product_quantity'],
                date_updated = row['date_updated'],
                ).save()
            
            except IntegrityError:
                inventory_record = Product.get(product_name = row['product_name'])
                inventory_record.product_name = row['product_name']
                inventory_record.product_price = row['product_price']
                inventory_record.product_quantity = row['product_quantity']
                inventory_record.date_updated = row['date_updated']
                inventory_record.save()


# Displays menu with three choices : view individual entries, add entry and backup database
def menu():
    choice = None
    
    while choice != 'q':
        print("Enter 'q' to quit")
        
        for key, value in options_menu.items():
            print(f'{key}, {value.__doc__}.')
        choice = input('Action: ').lower().strip()
        
        if choice == 'q':
            print('Goodbye')
        
        elif choice not in options_menu:
            print('Sorry that is not a valid choice!')
            continue
        
        elif choice in options_menu:
            clear()
            options_menu[choice]()


# Prompts the user for an id and then searches the database for the product with that id 
def view_individual_entries():
     """ View Entries """
     while True:
        try:
            search_query = view_entries(int(input('Search by ID: ')))
            if search_query != Product.product_id:
                raise ValueError
            break
        except ValueError:
            print('That is not a valid value.')
            break


# If user searches then displays te product info for that id,
# else displays all products in the database
def view_entries(search_query=None):
    """ View Entries """
    products = Product.select().order_by(Product.product_id.desc())
    if search_query:
        products = Product.select().where(Product.product_id==search_query)

    for product in products:
        clear()
        print(product.product_id)
        print(product.product_name)
        print(f'${product.product_price/100}')
        print(product.product_quantity)
        print(f'Date: {product.date_updated.strftime("%m/%d/%Y")}')
        print('\n\n')
        print('r) return to main menu')
        print('n) next entry')
        next_action = input('Action: [r/n]  '.lower())
        if next_action == 'r':
            break
        elif next_action == 'n':
            clear()
 

# If user selects add new entry prompts user for name of the product 
def get_product_name():
    add = Product()
    while True:
        try:
            add.new_product = str(input('What is the name of your product?\n '))
        except ValueError:
            print('Please try again.')
            continue
        else:
            break
    return add.new_product


# Prompts the user for new product price 
def get_product_price():
    add = Product()
    while True:
        try:
            add.new_price = float(input('What is price of your product?\n $'))
            add.new_price = int(add.new_price*100)
        except ValueError:
            print("That's not a valid value try again.")
            continue
        else:
            break
    return add.new_price


# Prompts the user for new product quantity
def get_product_quantity():
    add = Product()
    while True:
        try:
            add.new_quantity = int(input('What is the quantity of your product?\n '))
        except:
            print('That is not a valid value please enter a number.')
            continue
        else:
            break
    return add.new_quantity


# Checks to see if new entry not in database if not adds the product,
# If entry already in the database then it updates existing entry
def add_entries():
    """ Add Entry """
    new_product = get_product_name()
    new_price = get_product_price()
    new_quantity = get_product_quantity()

    saved = input('Save entry? [Yn] ').lower()

    if saved != 'n':
        try:
            Product.create(
                product_name = new_product,
                product_price = new_price,
                product_quantity = new_quantity,
                date_updated = datetime.datetime.now().date(),
            ).save()
            clear()
            print('Saved Successfully!')
        except IntegrityError:
            new_record = Product.get(Product.product_name == new_product)
            new_record.product_price = new_price
            new_record.product_quantity = new_quantity
            new_record.date_updated = datetime.datetime.now().date()
            new_record.save()
            clear()
            print('Saved Successfully!')


# Backups the database
def backup_database():
    """ Backup Database """
    backup_file = 'Backup.csv'
    with open(backup_file, 'a', newline='') as backup_csv:
        fields = ['product_name', 'product_price', 'product_quantity', 'date_updated']
        backup_writer = csv.DictWriter(backup_csv, fieldnames=fields)
        backup_writer.writeheader()
        products = Product.select()
        for product in products:
            backup_writer.writerow({
                'product_name': product.product_name,
                'product_price': product.product_price,
                'product_quantity': product.product_quantity,
                'date_updated': product.date_updated,
            })
    if os.path.isfile(backup_file):
        clear()
        print('Backup successfully completed.')
    else:
        clear()
        print('Something went wrong, Please try again.')


options_menu = OrderedDict([('v', view_individual_entries), ('a', add_entries), ('b', backup_database)])


if __name__ == '__main__':
    initialize()
    read_csv()
    clear()
    menu()


