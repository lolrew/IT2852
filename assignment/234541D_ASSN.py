
# Name: Leroy Hooi
# Admin no: 234541D
# Tutorial Group: IT2852

# additional features
# admin view all users
# admin can reset user password
# admin can delete a user or all users
# librarian can view all customers requests and other details
# librarian can delete each customer request or delete all customer requests
# customers can earn points by borrowing books and based on their points, their tier will increase (Tier A, B, C)
# customers can view cafe menu
# customer can order food and drinks from the cafe using their points
# customer email validation
# customerID is using randomized method and generates a unique customerID
#


import logging
import shelve
from tabulate import tabulate
import random
import string
import re       # for email validation

# Configure logging
logging.basicConfig(filename='book_management.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class User:
    def __init__(self, username, password, role, customer_id=None, email=None, points=0):
        self.username = username
        self.password = password
        self.role = role
        self.email = email
        self.points = points if role != "customer" else 0  # Set points to 0 for customers
        self.tier = self.determine_tier()
        if role == "customer":
            self.customer_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        else:
            self.customer_id = None

    def determine_tier(self):
        if self.points >= 1001:
            return 'A'
        elif self.points >= 501:
            return 'B'
        else:
            return 'C'

    def update_points(self, additional_points):
        self.points += additional_points
        self.tier = self.determine_tier()

    def spend_points(self, points):
        if self.points >= points:
            self.points -= points
            self.tier = self.determine_tier()
            return True
        else:
            return False

class MenuItem:
    def __init__(self, name, points):
        self.name = name
        self.points = points

class Book:
    def __init__(self, ISBN_Num, title, Publisher, Language, NumberOfCopies, Availability, author, genre, points_value=None):
        self._title = title
        self._isbn = ISBN_Num
        self._publisher = Publisher
        self._language = Language
        self._noOfCopies = NumberOfCopies
        self._availability = Availability
        self._author = author
        self._genre = genre
        self._points_value = points_value if points_value is not None else 0  # Set default points value if none provided # Points awarded for borrowing this book

    # Getter methods for retrieving book information
    def get_title(self):
        return self._title

    def get_isbn(self):
        return self._isbn

    def get_publisher(self):
        return self._publisher

    def get_language(self):
        return self._language

    def get_noOfCopies(self):
        return self._noOfCopies

    def get_availability(self):
        return "Yes" if self._availability else "No"

    def get_author(self):
        return self._author

    def get_genre(self):
        return self._genre

    # Add a getter for the points value
    def get_points_value(self):
        return getattr(self, '_points_value', 0)  # Return 0 if _points_value is not set

# Sample user data for users to access in
# admin, librarian and user are the username
# admin123, librarian123, and user123 are the passwords
# roles are assigned so that for example if users wanna add a new record,
# they can't as they don't have permissions to do it.
def initialize_users():
    with shelve.open('book_management_db') as db:
        if 'users' not in db:
            db['users'] = [
                User("admin", "admin123", "admin"),
                User("librarian", "librarian123", "librarian"),
                User("customer", "customer123", "customer", "customer001", "customer@email.com")
            ]
        return list(db['users'])

# Initialize shelve for storing user and book data
with shelve.open('book_management_db') as db:
    if 'books' not in db:  # Use 'books' for consistency
        db['books'] = {}
    if 'menu_items' not in db:
        db['menu_items'] = [
            MenuItem("Coffee", 10),
            MenuItem("Tea", 8),
            MenuItem("Sandwich", 15),
            MenuItem("Cake", 12)
        ]

    # Load book and menu data
    booklist = db['books']
    menu_items = db['menu_items']

def display_cafe_menu():
    print("\n-- Cafe Menu --\n")
    headers = ["Item", "Points"]
    table = [[item.name, item.points] for item in menu_items]
    print(tabulate(table, headers, tablefmt="grid"))

def order_from_cafe(user):
    try:
        display_cafe_menu()
        item_name = input("Enter the name of the item you want to order or type 'B' to go back: ").strip().title()
        if item_name.upper() == 'B':
            return
        item = next((item for item in menu_items if item.name == item_name), None)
        if not item:
            print("\n** Item not found in the menu. **")
            return
        if user.spend_points(item.points):
            print(f"\n-- You have successfully ordered {item_name}. --")
            with shelve.open('book_management_db') as db:
                users = db['users']
                for db_user in users:
                    if db_user.username == user.username:
                        db_user.points = user.points
                        db_user.tier = user.tier
                        break
                db['users'] = users
        else:
            print("\n** You do not have enough points to order this item. **")
    except Exception as e:
        print(f"An error occurred: {e}")


def generate_unique_customer_id(existing_ids):
    while True:
        customer_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        if customer_id not in existing_ids:
            return customer_id

def create_account():
    while True:
        try:
            username = input("\nEnter a new username or type 'B' to go back:")
            if username == "B":
                break
            if any(user.username == username for user in users):
                raise ValueError("\n** Username already exists. **")
            password = input("Enter a password or type 'B' to go back:")
            if password == "B":
                break
            role = input("Enter a role (admin/librarian/customer) or type 'B' to go back:").lower()
            if role not in ["admin", "librarian", "customer"]:
                raise ValueError("\n** Invalid role. **")
            if role == "customer":
                email = input("Enter email (e.g., example@domain.com): ")

                # Validate email format
                email_regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                if not re.match(email_regex, email):
                    raise ValueError("\n** Invalid email format. Please enter a valid email address. **")

                existing_customer_ids = [user.customer_id for user in users if user.customer_id]
                customer_id = generate_unique_customer_id(existing_customer_ids)
                user = User(username, password, role, customer_id=customer_id, email=email)
            else:
                user = User(username, password, role)
            users.append(user)
            with shelve.open('book_management_db') as db:
                db['users'] = users
            print("Account created successfully.")
            return user
        except ValueError as ve:
            print(ve)

def authenticate(username, password):
    for user in users:
        if user.username == username and user.password == password:
            return user
    return None

def is_admin(user):
    return user.role == "admin"

def display_all_books(user):
    print("\n-- These are all the book records --\n")
    if is_admin(user) or user.role in ["librarian", "customer"]:
        table = []
        headers = ["ISBN", "Title", "Publisher", "Language", "Number of Copies", "Availability", "Author", "Genre", "Points"]

        for k, v in booklist.items():
            table.append([
                k,
                v.get_title(),
                v.get_publisher(),
                v.get_language(),
                v.get_noOfCopies(),
                v.get_availability(),
                v.get_author(),
                v.get_genre(),
                v.get_points_value()  # Use the getter method
            ])

        print(tabulate(table, headers, tablefmt="grid"))
        logging.info(f"{user.username} viewed all books.")
    else:
        print("** Unauthorized access. **")

def add_new_book(user, isbn, title, publisher, language, noOfCopies, availability, author, genre):
    try:
        if not (is_admin(user) or user.role == "librarian"):
            raise PermissionError("** Unauthorized access. **")
        if isbn in booklist:
            raise ValueError("\n** ISBN must be unique. **\n")

        # Add a prompt to enter points value for the book
        points_value = int(input("Enter points value for the book: "))

        book = Book(isbn, title, publisher, language, noOfCopies, availability, author, genre, points_value)
        booklist[isbn] = book

        with shelve.open('book_management_db') as db:
            db['books'] = booklist
        print('\n-- Book added successfully. --')
    except (PermissionError, ValueError) as e:
        print(e)
    except TypeError:
        print("\n** Invalid input for points. Please enter a valid number. **")

def update_book(user, isbn):
    try:
        if is_admin(user) or user.role == "librarian":
            if isbn not in booklist:
                print("\n** Book not found. **")
                return

            book = booklist[isbn]
            print("\n-- Current Book Details --")
            print_book_info(book)

            new_title = input("Enter new title or press enter to keep current [or type 'B' to go back]: ")
            if new_title.upper() == 'B':
                return
            elif new_title:
                book._title = new_title

            new_publisher = input("Enter new publisher or press enter to keep current [or type 'B' to go back]: ")
            if new_publisher.upper() == 'B':
                return
            elif new_publisher:
                book._publisher = new_publisher

            new_language = input("Enter new language or press enter to keep current [or type 'B' to go back]: ")
            if new_language.upper() == 'B':
                return
            elif new_language:
                book._language = new_language

            new_noOfCopies = input("Enter new number of copies or press enter to keep current [or type 'B' to go back]: ")
            if new_noOfCopies.upper() == 'B':
                return
            elif new_noOfCopies:
                book._noOfCopies = int(new_noOfCopies)

            new_availability = input("Enter new availability (Y/N) or press enter to keep current [or type 'B' to go back]: ").upper()
            if new_availability == 'B':
                return
            elif new_availability in ['Y', 'N']:
                book._availability = True if new_availability == 'Y' else False

            new_author = input("Enter new author or press enter to keep current [or type 'B' to go back]: ")
            if new_author.upper() == 'B':
                return
            elif new_author:
                book._author = new_author

            new_genre = input("Enter new genre or press enter to keep current [or type 'B' to go back]: ")
            if new_genre.upper() == 'B':
                return
            elif new_genre:
                book._genre = new_genre

            new_points_value = input("Enter new points value or press enter to keep current [or type 'B' to go back]: ")
            if new_points_value.upper() == 'B':
                return
            elif new_points_value:
                book._points_value = int(new_points_value)

            with shelve.open('book_management_db') as db:
                db['books'] = booklist

            print("Book updated successfully.")
            logging.info(f"{user.username} updated book with ISBN: {isbn}.")
        else:
            raise PermissionError("** Unauthorized access. **")
    except PermissionError as e:
        print(e)
    except ValueError as error:
        print(f"Error: {error}. Please enter valid inputs.")

def delete_book(user, isbn):
    try:
        if not (is_admin(user) or user.role == "librarian"):
            raise PermissionError("** Unauthorized access. **")

        if isbn not in booklist:
            raise ValueError("\n** Book not found. **")

        del booklist[isbn]

        # Save the updated booklist to the shelve database
        with shelve.open('book_management_db') as db:
            db['books'] = booklist

        print('Books deleted successfully')
        logging.info(f"{user.username} deleted book with ISBN: {isbn}.")
    except (ValueError, PermissionError) as e:
        print(e)

def delete_user(admin_user):
    try:
        if not is_admin(admin_user):
            raise PermissionError("** Unauthorized access. **")

        username_to_delete = input("Enter the username of the user to delete or type 'B' to go back to the main menu: ")

        if username_to_delete == 'B':
            return

        user_to_delete = next((user for user in users if user.username == username_to_delete), None)

        if user_to_delete:
            users.remove(user_to_delete)

            # Save the updated user list to the shelve database
            with shelve.open('book_management_db') as db:
                db['users'] = users

            print(f"\n-- User '{username_to_delete}' deleted successfully. --")
            logging.info(f"Admin {admin_user.username} deleted user '{username_to_delete}'.")
        else:
            print("\n** User not found. **")
    except PermissionError as e:
        print(e)

def delete_all_users(admin_user):
    try:
        if not is_admin(admin_user):
            raise PermissionError("** Unauthorized access. Only admins can delete all user accounts. **")

        confirmation = input(
            "Are you sure you want to delete ALL user accounts? This action cannot be undone. Type 'yes' to confirm: ")
        if confirmation.lower() == 'yes':
            global users
            users = []

            with shelve.open('book_management_db', writeback=True) as db:
                db['users'] = users

            print("All user accounts have been successfully deleted.")
            logging.info(f"Admin {admin_user.username} deleted all user accounts.")
        else:
            print("-- Deletion cancelled. --")
    except PermissionError as e:
        print(e)

def sort_book_publisher(user):
    def get_publisher(book):
        return book.get_publisher()

    try:
        print("\n---------------------------------------------------------------")
        if is_admin(user) or user.role in ["librarian", "customer"]:
            with shelve.open('book_management_db') as db:
                booklist = db.get('books', {})

                books = list(booklist.values())

                n = len(books)
                for i in range(n - 1):
                    for j in range(0, n - i - 1):
                        if get_publisher(books[j]) > get_publisher(books[j + 1]):
                            books[j], books[j + 1] = books[j + 1], books[j]

                headers = ["ISBN", "Title", "Publisher", "Language", "Number of Copies", "Availability", "Author", "Genre", "Points"]
                table = []

                for book in books:
                    table.append([
                        book.get_isbn(),
                        book.get_title(),
                        book.get_publisher(),
                        book.get_language(),
                        book.get_noOfCopies(),
                        book.get_availability(),
                        book.get_author(),
                        book.get_genre(),
                        book.get_points_value()
                    ])

                print(tabulate(table, headers, tablefmt="grid"))
                logging.info(f"{user.username} sorted books by publisher in ascending order.")
        else:
            raise PermissionError("** Unauthorized access. **")
    except PermissionError as e:
        print(e)

def search_book_by_title(user, title):
    with shelve.open('book_management_db') as db:
        booklist = db.get('books', {})

        search_results = []
        headers = ["ISBN", "Title", "Publisher", "Language", "Number of Copies", "Availability", "Author", "Genre", "Points"]

        for book in booklist.values():
            if book.get_title().lower() == title.lower():
                search_results.append([
                    book.get_isbn(),
                    book.get_title(),
                    book.get_publisher(),
                    book.get_language(),
                    book.get_noOfCopies(),
                    book.get_availability(),
                    book.get_author(),
                    book.get_genre(),
                    book.get_points_value()
                ])

        if search_results:
            print("\n-- Search Results --\n")
            print(tabulate(search_results, headers, tablefmt="grid"))
        else:
            print("\n** Book not found. **")

def sort_noOfCopies(user):
    def get_noOfCopies(book):
        return book.get_noOfCopies()

    try:
        print("\n---------------------------------------------------------------")
        if is_admin(user) or user.role in ["librarian", "customer"]:
            with shelve.open('book_management_db') as db:
                booklist = list(db.get('books', {}).values())

                for i in range(1, len(booklist)):
                    current_book = booklist[i]
                    j = i - 1
                    while j >= 0 and get_noOfCopies(booklist[j]) < get_noOfCopies(current_book):
                        booklist[j + 1] = booklist[j]
                        j -= 1
                    booklist[j + 1] = current_book

                headers = ["ISBN", "Title", "Publisher", "Language", "Number of Copies", "Availability", "Author", "Genre", "Points"]
                table = []

                for book in booklist:
                    table.append([
                        book.get_isbn(),
                        book.get_title(),
                        book.get_publisher(),
                        book.get_language(),
                        book.get_noOfCopies(),
                        book.get_availability(),
                        book.get_author(),
                        book.get_genre(),
                        book.get_points_value()
                    ])

                print(tabulate(table, headers, tablefmt="grid"))
                logging.info(f"{user.username} sorted books by number of copies in descending order.")
        else:
            raise PermissionError("** Unauthorized access. **")
    except PermissionError as e:
        print(e)

def print_book_info(book):
    print(
        f' ISBN: {book.get_isbn()}\n Title: {book.get_title()}\n Publisher: {book.get_publisher()}\n Language: {book.get_language()}\n Number of Copies: {book.get_noOfCopies()}\n Availability: {book.get_availability()} Author: {book.get_author()}\n Genre: {book.get_genre()}\n Points: {book.get_points_value()}\n\n')

def borrow_book(user, isbn):
    try:
        if user.role != "customer":
            raise PermissionError("\n** Only customers can borrow books. **")
        if isbn not in booklist:
            raise ValueError("\n** Book not found. **")
        book = booklist[isbn]
        if book.get_availability() == "No" or book.get_noOfCopies() == 0:
            print("\n** This book is not available for borrowing. **")
            return
        num_copies_to_borrow = int(input("Enter the number of copies you want to borrow: "))
        if num_copies_to_borrow <= 0 or num_copies_to_borrow > book.get_noOfCopies():
            print("\n** Invalid number of copies. **")
            return
        book._noOfCopies -= num_copies_to_borrow
        if book.get_noOfCopies() == 0:
            book._availability = False
        user.update_points(book.get_points_value() * num_copies_to_borrow)
        with shelve.open('book_management_db') as db:
            db['books'] = booklist
            db['users'] = users
        print("-- Books borrowed successfully. --")
    except (PermissionError, ValueError) as e:
        print(e)

def view_all_users():
    headers = ["Username", "Role", "CustomerID", "Email", "Tier", "Points"]
    table = []
    for user in users:
        table.append([user.username, user.role, user.customer_id or "N/A", user.email or "N/A", user.tier or "N/A", user.points])
    print(tabulate(table, headers, tablefmt="grid"))

def reset_password():
    try:
        username = input("Enter the username for which you want to reset the password: ")

        for user in users:
            if user.username == username:
                new_password = input("Enter the new password or type 'B' to go back to main menu: ")
                if new_password == 'B':
                    return
                user.password = new_password

                with shelve.open('book_management_db') as db:
                    db['users'] = users

                print(f"\n-- Password for user '{username}' has been reset. --")
                logging.info(f"Password for user '{username}' was reset by the admin.")
                return

        print("\n** Username not found. **")
    except Exception as e:
        print(f"An error occurred: {e}")

def quick_sort_books_by_title(books):
    if len(books) <= 1:
        return books
    else:
        pivot = books[0]
        less_than_pivot = [book for book in books[1:] if book.get_title().lower() <= pivot.get_title().lower()]
        greater_than_pivot = [book for book in books[1:] if book.get_title().lower() > pivot.get_title().lower()]
        return quick_sort_books_by_title(less_than_pivot) + [pivot] + quick_sort_books_by_title(greater_than_pivot)

def display_sorted_books_by_title(user):
    try:
        print("\n-- Sorted Books by Title in Ascending Order --\n")
        if is_admin(user) or user.role in ["librarian", "customer"]:
            with shelve.open('book_management_db') as db:
                booklist = list(db.get('books', {}).values())

                sorted_books = quick_sort_books_by_title(booklist)

                headers = ["ISBN", "Title", "Publisher", "Language", "Number of Copies", "Availability", "Author", "Genre", "Points"]
                table = []

                for book in sorted_books:
                    table.append([
                        book.get_isbn(),
                        book.get_title(),
                        book.get_publisher(),
                        book.get_language(),
                        book.get_noOfCopies(),
                        book.get_availability(),
                        book.get_author(),
                        book.get_genre(),
                        book.get_points_value()
                    ])

                print(tabulate(table, headers, tablefmt="grid"))
                logging.info(f"{user.username} sorted books by title in ascending order.")
        else:
            raise PermissionError("** Unauthorized access. **")
    except PermissionError as e:
        print(e)

def merge_sort_books(books, key1, key2):
    if len(books) <= 1:
        return books

    def get_key(book, key):
        return getattr(book, key)()

    mid = len(books) // 2
    left_half = books[:mid]
    right_half = books[mid:]

    left_sorted = merge_sort_books(left_half, key1, key2)
    right_sorted = merge_sort_books(right_half, key1, key2)

    sorted_books = []
    i = j = 0

    while i < len(left_sorted) and j < len(right_sorted):
        if get_key(left_sorted[i], key1) < get_key(right_sorted[j], key1) or \
                (get_key(left_sorted[i], key1) == get_key(right_sorted[j], key1) and get_key(left_sorted[i],
                                                                                             key2) <= get_key(
                    right_sorted[j], key2)):
            sorted_books.append(left_sorted[i])
            i += 1
        else:
            sorted_books.append(right_sorted[j])
            j += 1

    sorted_books.extend(left_sorted[i:])
    sorted_books.extend(right_sorted[j:])

    return sorted_books

def display_sorted_books_by_language_and_isbn(user):
    try:
        print("\n-- Sorted Books by Language and ISBN in Ascending Order --\n")
        if is_admin(user) or user.role in ["librarian", "customer"]:
            with shelve.open('book_management_db') as db:
                booklist = list(db.get('books', {}).values())

                sorted_books = merge_sort_books(booklist, 'get_language', 'get_isbn')

                headers = ["ISBN", "Title", "Publisher", "Language", "Number of Copies", "Availability", "Author",
                           "Genre", "Points"]
                table = []

                for book in sorted_books:
                    table.append([
                        book.get_isbn(),
                        book.get_title(),
                        book.get_publisher(),
                        book.get_language(),
                        book.get_noOfCopies(),
                        book.get_availability(),
                        book.get_author(),
                        book.get_genre(),
                        book.get_points_value()
                    ])

                print(tabulate(table, headers, tablefmt="grid"))
                logging.info(f"{user.username} sorted books by language and ISBN in ascending order.")
        else:
            raise PermissionError("** Unauthorized access. **")
    except PermissionError as e:
        print(e)

########################### 3A - 3D ###################################

class CustomerRequest:
    def __init__(self, customer_id, request_detail):
        self.customer_id = customer_id
        self.request_detail = request_detail

    def __repr__(self):
        return f"CustomerRequest(customer_id={self.customer_id}, request_detail={self.request_detail})"

class Queue:
    def __init__(self):
        self.queue = []
        self.load_queue()

    def load_queue(self):
        with shelve.open('book_management_db') as db:
            self.queue = db.get('customer_requests', [])

    def save_queue(self):
        with shelve.open('book_management_db') as db:
            db['customer_requests'] = self.queue

    def is_empty(self):
        return len(self.queue) == 0

    def enqueue(self, item):
        self.queue.append(item)
        self.save_queue()

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Dequeue from an empty queue")
        item = self.queue.pop(0)
        self.save_queue()
        return item

    def peek(self):
        if self.is_empty():
            raise IndexError("Peek from an empty queue")
        return self.queue[0]

    def size(self):
        return len(self.queue)

def view_customer_details(user):
    if user.role != "librarian":
        print("** Unauthorized access. Only librarians can view customer details. **")
        return

    with shelve.open('book_management_db') as db:
        queue = db.get('customer_requests', [])

    customer_requests = {}
    for request in queue:
        if request.customer_id in customer_requests:
            customer_requests[request.customer_id].append(request.request_detail)
        else:
            customer_requests[request.customer_id] = [request.request_detail]

    headers = ["Customer ID", "Name", "Email", "Tier", "Points", "Requests"]
    table = []

    print("\n-- List of all customers and their details with Requests: --\n")
    for user in users:
        if user.role == "customer":
            requests = "\n".join(customer_requests.get(user.customer_id, ["No requests"]))
            table.append([user.customer_id, user.username, user.email, user.tier, user.points, requests])

    print(tabulate(table, headers, tablefmt="grid"))

def sequential_search(queue, customer_id):
    for request in queue.queue:
        if request.customer_id == customer_id:
            return True
    return False

def delete_customer_request_by_id(user):
    if user.role != "librarian":
        print("** Unauthorized access. Only librarians can manage customer requests. **")
        return

    customer_id = input("Enter the Customer ID for the request to delete: ")

    with shelve.open('book_management_db', writeback=True) as db:
        queue = db.get('customer_requests', [])

        filtered_requests = [req for req in queue if req.customer_id == customer_id]

        if not filtered_requests:
            print("No requests found for this customer ID.")
            return

        print("\nFound requests:")
        for idx, req in enumerate(filtered_requests, start=1):
            print(f"{idx}. {req.request_detail}")

        while True:
            try:
                delete_idx = int(input("Enter the number of the request to delete (or 0 to cancel): "))
                if delete_idx == 0:
                    print("-- Deletion cancelled. --")
                    break

                if delete_idx < 1 or delete_idx > len(filtered_requests):
                    print("Invalid index. Please select a valid number from the list.")
                    continue

                request_to_delete = filtered_requests[delete_idx - 1]
                queue.remove(request_to_delete)
                db['customer_requests'] = queue
                print("Request deleted successfully.")
                break
            except ValueError:
                print("Invalid input. Please enter a valid number.")

def delete_all_customer_requests(user):
    if user.role != "librarian":
        print("** Unauthorized access. Only librarians can manage customer requests. **")
        return

    confirmation = input("Are you sure you want to delete ALL customer requests? Type 'yes' to confirm: ").lower()
    if confirmation == 'yes':
        with shelve.open('book_management_db', writeback=True) as db:
            db['customer_requests'] = []
            print("All customer requests have been successfully deleted.")
            queue = Queue()
            queue.queue.clear()
            queue.save_queue()
    else:
        print("-- Deletion cancelled. --")

def manage_customer_requests(user):
    if user.role != "librarian":
        print("** Unauthorized access. Only librarians can manage customer requests. **")
        return

    queue = Queue()

    while True:
        print("\nCustomer Request Menu:")
        print("1. View all customers")
        print("2. Input customer request")
        print("3. View number of requests")
        print("4. Service next request in Queue")
        print("5. Delete customer request")
        print("6. Delete all customer requests")
        print("0. Return to Main Menu")
        choice = input("Please select one: ")

        if choice == '1':
            view_customer_details(user)

        elif choice == '2':
            while True:
                customer_id = input("Enter Customer ID or type '-1' to go back to Customer Request Menu: ")
                if customer_id == "-1":
                    break

                if not validate_customer_id(customer_id):
                    print("Invalid Customer ID. Please try again!")
                    continue

                request_detail = input("Enter Customer's request or type 'B' to go back to Customer Request Menu: ")

                if request_detail == "B":
                    break

                request = CustomerRequest(customer_id, request_detail)
                queue.enqueue(request)
                print("Customer's request added successfully!")
                break

        elif choice == '3':
            queue.load_queue()
            print(f"Number of customer requests: {queue.size()}")

        elif choice == '4':
            if queue.is_empty():
                print("No requests to process.")
            else:
                processed_request = queue.dequeue()
                customer = next((user for user in users if user.customer_id == processed_request.customer_id), None)
                print("\nCustomer Request Details:")
                print("--------------------------------------------------")
                if customer:
                    print(f"Customer ID: {customer.customer_id}")
                    print(f"Name: {customer.username}")
                    print(f"Email: {customer.email}")
                    print(f"Tier: {customer.tier}")
                    print(f"Points: {customer.points}")
                print("--------------------------------------------------")
                print(f"Request: {processed_request.request_detail}")
                print("--------------------------------------------------")
                print(f"Remaining requests: {queue.size()}")

        elif choice == '5':
            delete_customer_request_by_id(user)

        elif choice == '6':
            delete_all_customer_requests(user)

        elif choice == '0':
            print("Returning to Main Menu.")
            break

        else:
            print("\n** Invalid choice. Please try again. **")

def validate_customer_id(customer_id):
    with shelve.open('book_management_db') as db:
        users = db.get('users', [])
        return any(user.customer_id == customer_id for user in users if hasattr(user, 'customer_id'))

########################### END OF 3A - 3D ###################################




########################### TEST PROGRAM ###################################




while True:
    users = initialize_users()

    print("\n\nWelcome to the Book Management System!")
    print("\nInput 1 to log in \nInput 2 to create a new account \nInput 3 to exit")
    choice = input("\nEnter your choice: ")

    if choice == "1":
        print("\n-- Please log in or press 'B' on username or password to go back to Welcome Page. --\n")
        username = input("Enter username: ")
        if username.upper() == 'B':
            continue
        password = input("Enter password: ")
        if password.upper() == 'B':
            continue
        user = authenticate(username, password)
        if user:
            while True:
                print(f"\n\nWelcome, {user.username}!! :)")
                if user.role == "customer":
                    print("ID", user.customer_id)
                    print("Points:", user.points)  # Display customer points

                if user.role == "admin":
                    print("\n-- Welcome to Book Management System's Main Menu --")
                    print("\nWhat would you like to do today?\n")
                    print("\nInput 1 to display all books \n"
                          "Input 2 to add a new book record \n"
                          "Input 3 to update a book record \n"
                          "Input 4 to delete a book record \n"
                          "Input 5 to sort books by publisher \n"
                          "Input 6 to sort books by number of copies \n"
                          "Input 7 to sort books by Title \n"
                          "Input 8 to sort books by Language and then ISBN Num \n"
                          "Input 9 to view all users \n"
                          "Input 10 to reset user password \n"
                          "Input 11 to delete a user \n"
                          "Input 12 to delete all users \n"
                          "Input 13 to log out \n"
                          )
                    typeInput = input("\nEnter your input: ")
                    if typeInput not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"]:
                        print("Invalid input. Please try again.")
                        continue
                    if typeInput == "1":
                        display_all_books(user)

                    elif typeInput == "2":
                        try:
                            print("\n-- Add a book --\n ")
                            isbn = int(input("Enter ISBN or type '-1' to go back to main menu: "))
                            if isbn == -1:
                                continue
                            elif len(str(isbn)) > 13:
                                print("\n** ISBN must have a maximum of 13 digits. **")
                                continue
                            title = input("Enter book title or type 'B' to go back to main menu: ")
                            if title == 'B':
                                continue
                            publisher = input("Enter publisher or type 'B' to go back to main menu: ")
                            if publisher == 'B':
                                continue
                            language = input("Enter language or type 'B' to go back to main menu: ")
                            if language == 'B':
                                continue
                            noOfCopies = int(input("Enter number of copies or type '-1' to go back to main menu: "))
                            if noOfCopies == -1:
                                continue
                            while noOfCopies < 0:
                                noOfCopies = int(input("Enter number of copies (value more 0 or more): "))
                            availability = input(
                                "Enter availability (Y/N) or type 'B' to go back to main menu: ").upper() == "Y"
                            if availability == 'B':
                                continue
                            author = input("Enter author or type 'B' to go back to main menu: ")
                            if author == 'B':
                                continue
                            genre = input("Enter genre or type 'B' to go back to main menu: ")
                            if genre == 'B':
                                continue
                            add_new_book(user, isbn, title, publisher, language, noOfCopies, availability, author,
                                         genre)
                        except ValueError:
                            print("\n** Invalid input. Please enter a valid number for ISBN and/or number of copies. **")

                    elif typeInput == "3":
                        try:
                            print("\n -- Update a book --\n")
                            isbn = int(input("Enter ISBN of the book to update or type '-1' to go back to main menu: "))
                            if isbn == -1:
                                continue
                            update_book(user, isbn)
                        except ValueError:
                            print("\n** Invalid input. Please enter a valid number for ISBN. **")

                    elif typeInput == "4":
                        try:
                            print("\n -- Delete a book --\n")
                            isbn = int(input("Enter ISBN of the book to delete or type '-1' to go back to main menu: "))
                            if isbn == -1:
                                continue
                            delete_book(user, isbn)
                        except ValueError:
                            print("\n** Invalid input. Please enter a valid number for ISBN. **")
                    elif typeInput == "5":
                        sort_book_publisher(user)

                    elif typeInput == "6":
                        sort_noOfCopies(user)

                    elif typeInput == "7":
                        display_sorted_books_by_title(user)

                    elif typeInput == "8":
                        display_sorted_books_by_language_and_isbn(user)

                    elif typeInput == "9":
                        view_all_users()

                    elif typeInput == "10":
                        reset_password()

                    elif typeInput == "11":
                        delete_user(user)

                    elif typeInput == "12":
                        delete_all_users(user)

                    elif typeInput == "13":
                        print("Logged Out")
                        user = None
                        break

                elif user.role == "librarian":
                    print("\n Welcome to Book Management System's Main Menu")
                    print("\nInput 1 to display all books \n"
                          "Input 2 to add a new book record \n"
                          "Input 3 to update a book record \n"
                          "Input 4 to delete a book record \n"
                          "Input 5 to sort books by publisher \n"
                          "Input 6 to sort books by number of copies \n"
                          "Input 7 to sort books by Title \n"
                          "Input 8 to sort books by Language and then ISBN Num \n"
                          "Input 9 to manage customer requests \n"
                          "Input 10 to log out \n"
                          )
                    typeInput = input("\nEnter your input: ")
                    if typeInput not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
                        print("Invalid input. Please try again.")
                        continue
                    if typeInput == "1":
                        display_all_books(user)
                    elif typeInput == "2":
                        try:
                            isbn = int(input("Enter ISBN or type '-1' to go back  to main page: "))
                            if isbn == -1:
                                continue
                            elif len(str(isbn)) > 13:
                                print("** ISBN must have a maximum of 13 digits. **")
                                continue
                            title = input("Enter book title or type 'B' to go back to main menu: ")
                            if title == 'B':
                                continue
                            publisher = input("Enter publisher or type 'B' to go back to main menu: ")
                            if publisher == 'B':
                                continue
                            language = input("Enter language or type 'B' to go back to main menu: ")
                            if language == 'B':
                                continue
                            noOfCopies = int(input("Enter number of copies or type '-1' to go back to main menu: "))
                            if noOfCopies == -1:
                                continue
                            while noOfCopies < 0:
                                noOfCopies = int(input("Enter number of copies (value more 0 or more): "))
                            availability = input("Enter availability (Y/N) or type 'B' to go back to main menu: ").upper() == "Y"
                            if availability == 'B':
                                continue
                            author = input("Enter author or type 'B' to go back to main menu: ")
                            if author == 'B':
                                continue
                            genre = input("Enter genre or type 'B' to go back to main menu: ")
                            if genre == 'B':
                                continue
                            add_new_book(user, isbn, title, publisher, language, noOfCopies, availability, author,
                                         genre)
                        except ValueError:
                            print("\n** Invalid input. Please enter a valid number for ISBN and/or number of copies. **")

                    elif typeInput == "3":
                        try:
                            print("\n -- Update a book --\n")
                            isbn = int(input("Enter ISBN of the book to update or type '-1' to go back to main menu: "))
                            if isbn == -1:
                                continue
                            update_book(user, isbn)
                        except ValueError:
                            print("\n** Invalid input. Please enter a valid number for ISBN. **")

                    elif typeInput == "4":
                        try:
                            isbn = int(input("Enter ISBN of the book to delete or type '-1' to go back to main menu: "))
                            if isbn == -1:
                                continue
                            delete_book(user, isbn)
                        except ValueError:
                            print("\n** Invalid input. Please enter a valid number for ISBN. **")
                    elif typeInput == "5":
                        sort_book_publisher(user)
                    elif typeInput == "6":
                        sort_noOfCopies(user)
                    elif typeInput == "7":
                        display_sorted_books_by_title(user)
                    elif typeInput == "8":
                        display_sorted_books_by_language_and_isbn(user)
                    elif typeInput == "9":
                        manage_customer_requests(user)
                    elif typeInput == "10":
                        print("Logged Out")
                        user = None
                        break
                elif user.role == "customer":
                    print("\n\nWelcome to Library's Main Menu")
                    print("\nInput 1 to display all books \n"
                          "Input 2 to search for a book by title \n"
                          "Input 3 to sort book by publisher \n"
                          "Input 4 to sort the book by number of copies \n"
                          "Input 5 to sort by Title \n"
                          "Input 6 to sort books by Language and then ISBN Number \n"
                          "Input 7 to borrow a book \n"
                          "Input 8 to view cafe menu \n"
                          "Input 9 to order from cafe \n"
                          "Input 10 to log out \n")
                    typeInput = input("\nEnter your input: ")
                    if typeInput not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
                        print("Invalid input. Please try again.")
                        continue
                    if typeInput == "1":
                        display_all_books(user)

                    elif typeInput == "2":
                        print("\n-- Search a book record --\n")
                        search_title = input("Enter the title of the book you want to search for or type 'B' to go back to main menu: ")
                        if search_title == 'B':
                            continue
                        search_book_by_title(user, search_title)

                    elif typeInput == "3":
                        sort_book_publisher(user)

                    elif typeInput == "4":
                        sort_noOfCopies(user)

                    elif typeInput == "5":
                        display_sorted_books_by_title(user)

                    elif typeInput == "6":
                        display_sorted_books_by_language_and_isbn(user)

                    elif typeInput == "7":
                        try:
                            isbn = int(input("Enter the ISBN of the book you want to borrow or type '-1' to go back to main menu: "))
                            if isbn == -1:
                                continue
                            else:
                                borrow_book(user, isbn)
                        except ValueError:
                            print("\n** Invalid input. Please enter a valid number for ISBN. **")

                    elif typeInput == "8":
                        display_cafe_menu()

                    elif typeInput == "9":
                        order_from_cafe(user)

                    elif typeInput == "10":
                        print("Logged Out")
                        user = None
                        break
        else:
            print("\n** Invalid username or password. Please try again. **")
    elif choice == "2":
        new_user = create_account()
    elif choice == "3":
        print("\n-- Exiting the program. Goodbye! --")
        break
    else:
        print("Invalid input. Please try again.")
