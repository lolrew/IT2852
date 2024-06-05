import logging
import shelve
from tabulate import tabulate
# Configure logging
# this uses book_management.log to track all the logs such as adding and viewing
# and time and date are also recorded
logging.basicConfig(filename='book_management.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role


# Sample user data for users to access in
# admin, librarian and user are the username
# admin123, librarian123, and user123 are the passwords
# roles are assigned so that for example if users wanna add a new record,
# they can't as they don't have permissions to do it.
users = [
    User("admin", "admin123", "admin"),  # a means admin
    User("librarian", "librarian123", "librarian"),  # l means librarian
    User("customer", "customer123", "customer")
]


def create_account():
    """
    Allows users to create a new account.

    Returns:
        User object: Returns the newly created User object.
    """
    while True:
        try:
            username = input("\nEnter a new username or type 'B' to go back to go back to Welcome Page:")

            if username == "B":
                break

            # Check if the username already exists
            # raise ValueError("Username already exists. Please try again."): This line raises a ValueError exception with the message "Username already exists. Please try again." if the entered username already exists in the list of users.
            # raise ValueError("Invalid role. Please enter 'admin' or 'librarian'."): This line raises a ValueError exception with the message "Invalid role. Please enter 'admin' or 'librarian'." if the entered role is not either "admin" or "librarian".
            # raise is like a check to see if they are possible errors like having an invalid role

            # The any() function returns True if any item in an iterable are true, otherwise it returns False and
            # if the iterable object is empty, the any() function will return False.
            # if any() function to check if any existing user has a username that matches the username entered by the user trying to create a new account.
            # This check ensures that the new username being entered is unique and does not already exist in the list of users.

            if any(user.username == username for user in users):
                raise ValueError("\n** Username already exists. Please try again. **")

            password = input("Enter a password or type 'B' to go back to Welcome Page: ")

            if password == "B":
                break

            role = input(
                "Enter a role (admin / librarian / customer) or type others to go back to Welcome Page: ").lower()

            # Check if the role is valid
            if role not in ["admin", "librarian", "customer"]:
                raise ValueError("\n** Invalid role. Please try again. **")

            user = User(username, password, role)  # getting from the class meaning
            users.append(user)  # for each time user creates an account, this users array will be appended

            # Save the new user to shelve
            with shelve.open('book_management_db') as db:
                db['users'] = users

            print("Account created successfully.")
            return user
        except ValueError as ve:
            print(ve)  # this is if there is an error then it will throw out an exception


def authenticate(username, password):
    """
    Authenticates the user based on the provided username and password.

    Args:
        username (str): The username entered by the user.
        password (str): The password entered by the user.

    Returns:
        User object: Returns the User object if authentication is successful, otherwise returns None.
    """
    for user in users:
        if user.username == username and user.password == password:
            return user
    return None


def is_admin(user):
    """
    Checks if the user has admin privileges.

    Args:
        user (User object): The user object.

    Returns:
        bool: True if the user is an admin, otherwise False.
    """
    return user.role == "admin"


class Book:
    # constructor
    def __init__(self, ISBN_Num, title, Publisher, Language, NumberOfCopies, Availability, author, genre):
        # Initialize the book object with the provided attributes
        ## Instance variables
        self._title = title
        self._isbn = ISBN_Num
        self._publisher = Publisher
        self._language = Language
        self._noOfCopies = NumberOfCopies
        self._availability = Availability
        self._author = author
        self._genre = genre

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


# Initialize shelve for storing user and book data
# with shelve.open('book_management_db') as db: Opens a shelve database file named 'book_management_db'. The with statement ensures that the database is properly closed after the operations are completed.

# if 'users' not in db: Checks if the 'users' key is not already present in the database.
# db['users'] = users: If the 'users' key is missing, it initializes it with the value of users, which should be a predefined variable containing user data.

# if 'books' not in db: Checks if the 'books' key is not already present in the database.
# db['books'] = {}: If the 'books' key is missing, it initializes it with an empty dictionary to store book data.

with shelve.open('book_management_db') as db:
    if 'users' not in db:
        db['users'] = users
    if 'books' not in db:  # Use 'books' for consistency
        db['books'] = {}

    # Load user and book data
    users = db['users']
    booklist = db['books']


def display_all_books(user):
    """
    Displays all book records if the user is authorized.

    Args:
        user (User object): The user object.
    """

    # This function is responsible for displaying all the information about all the books in the system.
    # It iterates over the booklist and prints detailed information about each book. This function is
    # typically used when the user wants to view all the books in the system, such as when an admin or
    # librarian or customer accesses the system.

    print("\n-- These are all the book records --\n")
    if is_admin(user) or user.role in ["librarian",
                                       "customer"]:  # check if only admin, librarian, or customer can access
        table = []
        headers = ["ISBN", "Title", "Publisher", "Language", "Number of Copies", "Availability", "Author", "Genre"]

        for k, v in booklist.items():  # k = key, v = value, .items() means getting both key and value pairs
            table.append([
                k,
                v.get_title(),
                v.get_publisher(),
                v.get_language(),
                v.get_noOfCopies(),
                v.get_availability(),
                v.get_author(),
                v.get_genre()
            ])

        print(tabulate(table, headers, tablefmt="grid"))
        logging.info(f"{user.username} viewed all books.")  # logs the info to book_management.log
    else:
        print("Unauthorized access.")


def add_new_book(user, isbn, title, publisher, language, noOfCopies, availability, author, genre):
    """
    Adds a new book record if the user is authorized.

    Args:
        user (User object): The user object.
        isbn (int): The ISBN of the book.
        title (str): The title of the book.
        publisher (str): The publisher of the book.
        language (str): The language of the book.
        noOfCopies (int): The number of copies of the book.
        availability (bool): The availability of the book.
        author (str): The author of the book.
        genre (str): The genre of the book.
    """
    try:
        if not (is_admin(user) or user.role == "librarian"):
            raise PermissionError("Unauthorized access.")

        if isbn in booklist:
            raise ValueError("ISBN must be unique.")

        for book in booklist.values():
            if book.get_title() == title:
                raise ValueError("\n** ISBN already exist for the same book title. **")

        myBook = Book(isbn, title, publisher, language, noOfCopies, availability, author, genre)
        booklist[isbn] = myBook

        # Save the updated booklist to the shelve database
        with shelve.open('book_management_db') as db:
            db['books'] = booklist

        print('\n-- Book added successfully. --')
        logging.info(f"{user.username} added a new book '{title}' with ISBN: {isbn}.")
    except (PermissionError, ValueError) as e:
        print(e)


def update_book(user, isbn, new_title, new_publisher, new_language, new_noOfCopies, new_availability, new_author,
                new_genre):
    """
    Updates an existing book record if the user is authorized and the ISBN exists.

    Args:
        user (User object): The user object.
        isbn (int): The ISBN of the book to be updated.
        new_title (str): The new title of the book.
        new_publisher (str): The new publisher of the book.
        new_language (str): The new language of the book.
        new_noOfCopies (int): The new number of copies of the book.
        new_availability (bool): The new availability of the book.
        new_author (str): The new author of the book.
        new_genre (str): The new genre of the book.
    """
    try:
        if is_admin(user) or user.role == "librarian":
            if isbn not in booklist:
                print("\n** Book not found. **")

            elif isbn in booklist:
                book = booklist[isbn]
                book._title = new_title
                book._publisher = new_publisher
                book._language = new_language
                book._noOfCopies = new_noOfCopies
                book._availability = new_availability
                book._author = new_author
                book._genre = new_genre

            # Save the updated booklist to the shelve database
            with shelve.open('book_management_db') as db:
                db['books'] = booklist

                print("Book updated successfully.")
                logging.info(f"{user.username} updated book with ISBN: {isbn}.")
        else:
            raise PermissionError("Unauthorized access.")
    except PermissionError as e:
        print(e)


def delete_book(user, isbn):
    """
    Deletes an existing book record if the user is authorized.

    Args:
        user (User object): The user object.
        isbn (int): The ISBN of the book to be deleted.
    """
    try:
        if not (is_admin(user) or user.role == "librarian"):
            raise PermissionError("Unauthorized access.")

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


# asc order using bubble sort
def sort_book_publisher(user):
    """
    Sorts books by publisher if the user is authorized.

    Args:
        user (User object): The user object.
    """

    def get_publisher(book):
        return book.get_publisher()

    try:
        print("\n---------------------------------------------------------------")
        # Check if the user is an admin, librarian, or customer
        if is_admin(user) or user.role in ["librarian", "customer"]:
            # Open the shelve database
            with shelve.open('book_management_db') as db:
                booklist = db.get('books', {})

                # Convert the booklist values to a list for sorting
                books = list(booklist.values())

                # Sort books using Bubble Sort Algorithm in Ascending Order by Publisher
                n = len(books)
                for i in range(n - 1):
                    for j in range(0, n - i - 1):
                        if get_publisher(books[j]) > get_publisher(books[j + 1]):
                            books[j], books[j + 1] = books[j + 1], books[j]

                # Prepare the table
                headers = ["ISBN", "Title", "Publisher", "Language", "Number of Copies", "Availability", "Author", "Genre"]
                table = []

                # Add sorted books to the table
                for book in books:
                    table.append([
                        book.get_isbn(),
                        book.get_title(),
                        book.get_publisher(),
                        book.get_language(),
                        book.get_noOfCopies(),
                        book.get_availability(),
                        book.get_author(),
                        book.get_genre()
                    ])

                # Print the sorted books in table format
                print(tabulate(table, headers, tablefmt="grid"))
                logging.info(f"{user.username} sorted books by publisher in ascending order.")
        else:
            raise PermissionError("Unauthorized access.")
    except PermissionError as e:
        print(e)


"""def search_book_by_isbn(isbn):

    #Searches for a book by ISBN.

    #Args:
        #isbn (int): The ISBN of the book to be searched.

    with shelve.open('book_management_db') as db:
        booklist = db.get('books', {})
        for book in booklist.values():
            if book.get_isbn() == isbn:
                print(
                    f'ISBN: {book.get_isbn()} | Title: {book.get_title()} | Publisher: {book.get_publisher()} | Language: {book.get_language()} | Number of Copies: {book.get_noOfCopies()} | Availability: {book.get_availability()} | Author: {book.get_author()} | Genre: {book.get_genre()}')
                return
        print("Book not found.")"""


def search_book_by_title(user, title):
    """
    Searches for a book by title and prints the record in a table format.

    Args:
        user (User object): The user object.
        title (str): The title of the book to be searched.
    """
    with shelve.open('book_management_db') as db:
        booklist = db.get('books', {})

        # Collect search results into a list of lists
        search_results = []
        headers = ["ISBN", "Title", "Publisher", "Language", "Number of Copies", "Availability", "Author", "Genre"]

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
                    book.get_genre()
                ])

        # If there are search results, print them in a table format
        if search_results:
            print("\n-- Search Results --\n")
            print(tabulate(search_results, headers, tablefmt="grid"))
        else:
            print("\n** Book not found. **")


# desc order using Insertion Sort
def sort_noOfCopies(user):
    """
    Sorts books by the number of copies in descending order if the user is authorized.

    Args:
        user (User object): The user object.
    """

    def get_noOfCopies(book):
        return book.get_noOfCopies()

    try:
        print("\n---------------------------------------------------------------")
        if is_admin(user) or user.role in ["librarian", "customer"]:
            with shelve.open('book_management_db') as db:
                booklist = list(db.get('books', {}).values())

                # Insertion Sort Algorithm in Descending Order by Number of Copies
                for i in range(1, len(booklist)):
                    current_book = booklist[i]
                    j = i - 1
                    while j >= 0 and get_noOfCopies(booklist[j]) < get_noOfCopies(current_book):
                        booklist[j + 1] = booklist[j]
                        j -= 1
                    booklist[j + 1] = current_book

                # Prepare the table
                headers = ["ISBN", "Title", "Publisher", "Language", "Number of Copies", "Availability", "Author", "Genre"]
                table = []

                # Add sorted books to the table
                for book in booklist:
                    table.append([
                        book.get_isbn(),
                        book.get_title(),
                        book.get_publisher(),
                        book.get_language(),
                        book.get_noOfCopies(),
                        book.get_availability(),
                        book.get_author(),
                        book.get_genre()
                    ])

                # Print the sorted books in table format
                print(tabulate(table, headers, tablefmt="grid"))
                logging.info(f"{user.username} sorted books by number of copies in descending order.")
        else:
            raise PermissionError("Unauthorized access.")
    except PermissionError as e:
        print(e)


def get_noOfCopies(book):
    return book.noOfCopies


def print_book_info(book):
    """
    Prints information about a book.

    Args:
        book (Book object): The Book object containing information about the book.
    """

    # This function, on the other hand, is responsible for printing information about a single book.
    # It takes a Book object as input and prints detailed information about that particular book.
    # This function is more general-purpose and can be used to print information about a single book
    # in various contexts, not just when displaying all books. It provides flexibility in printing
    # book information for individual books as needed throughout the program.

    print(
        f' ISBN: {book.get_isbn()}\n Title: {book.get_title()}\n Publisher: {book.get_publisher()}\n Language: {book.get_language()}\n Number of Copies: {book.get_noOfCopies()}\n Availability: {book.get_availability()} Author: {book.get_author()}\n Genre: {book.get_genre()}\n\n')


def borrow_book(user, isbn):
    """
    Allows a customer to borrow a book if its availability is 'Yes' and number of copies is greater than 0.

    Args:
        user (User object): The user object.
        isbn (int): The ISBN of the book to be borrowed.
    """
    try:
        if user.role != "customer":
            raise PermissionError("\n** Only customers can borrow books. **")

        if isbn not in booklist:
            raise ValueError("\n** Book not found. **")

        book = booklist[isbn]
        if book.get_availability() == "No":
            print("\n** This book is not available for borrowing. **")
            return

        if book.get_noOfCopies() == 0:
            print("\n** This book is out of stock. **")
            return

        # Prompt the user to input the number of copies to borrow
        num_copies_to_borrow = int(input("Enter the number of copies you want to borrow: "))
        if num_copies_to_borrow <= 0:
            print("\n** Invalid number of copies. **")
            return

        # Check if the requested number of copies is available
        if num_copies_to_borrow > book.get_noOfCopies():
            print("\n** Not enough copies available. **")
            return

        # Reduce the number of copies available
        book._noOfCopies -= num_copies_to_borrow
        if book.get_noOfCopies() == 0:
            book._availability = False  # If no copies are available, set availability to False

        # Update the booklist in the database
        with shelve.open('book_management_db') as db:
            db['books'] = booklist

        print("-- Books borrowed successfully. --")
        logging.info(f"{user.username} borrowed {num_copies_to_borrow} copies of book with ISBN: {isbn}.")
    except (PermissionError, ValueError) as e:
        print(e)


def view_all_users():
    """
    Displays all users in a table format.
    """
    headers = ["Username", "Role"]
    table = []

    print("\n-- List of all users: --\n")
    for user in users:
        table.append([user.username, user.role])

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


# Main loop
while True:

    # Welcome message
    print("\n\nWelcome to the Book Management System!")

    print("\nInput 1 to log in \nInput 2 to create a new account \nInput 3 to exit")
    choice = input("\nEnter your choice: ")

    if choice == "1":
        print("\n-- Please log in or press 'B' on username or password to go back to Welcome Page. --\n")
        username = input("Enter username: ")
        if username.upper() == 'B':  # If 'B' is entered, go back to the main menu
            continue
        password = input("Enter password: ")
        if password.upper() == 'B':
            continue

        user = authenticate(username, password)
        if user:
            while True:
                print(f"\n\nWelcome, {user.username}!! :)")
                if user.role == "admin":
                    print("\n-- Welcome to Book Management System's Main Menu --")
                    print("\nWhat would you like to do today?\n")
                    print("\nInput 1 to display all books \n"
                          "Input 2 to add a new book record \n"
                          "Input 3 to update a book record \n"
                          "Input 4 to delete a book record \n"
                          "Input 5 to sort books by publisher \n"
                          "Input 6 to sort books by number of copies \n"
                          "Input 7 to view all users \n"
                          "Input 8 to reset user password \n"
                          "Input 9 to log out \n"

                          )
                    typeInput = input("\nEnter your input: ")

                    # Input validation
                    if typeInput not in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
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

                            # Validate ISBN
                            elif len(str(isbn)) > 13:
                                print("\n** ISBN must have a maximum of 13 digits. **")
                                continue

                            title = input("Enter book title or type 'B' to go back to main menu: ")
                            if title == 'B':
                                continue

                            publisher = input("Enter publisher or type 'B' to go back to main menu:: ")
                            if publisher == 'B':
                                continue

                            language = input("Enter language or type 'B' to go back to main menu: ")
                            if language == 'B':
                                continue

                            noOfCopies = int(input("Enter number of copies or type '-1' to go back to main menu: "))
                            if noOfCopies == -1:
                                continue
                            while noOfCopies < 0:
                                # print("must be a value 0 or more.")
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
                            print(
                                "\n** Invalid input. Please enter a valid number for ISBN and/or number of copies. **")
                            #print("** ISBN must have a maximum of 13 digits. **\n")

                    elif typeInput == "3":
                        try:
                            print("\n -- Update a book --\n")
                            isbn = int(input("Enter ISBN of the book to update or type '-1' to go back to main menu: "))

                            if isbn == -1:
                                continue

                            new_title = input("Enter new title or type 'B' to go back to main menu: ")
                            if new_title == 'B':
                                continue

                            new_publisher = input("Enter new publisher or type 'B' to go back to main menu: ")
                            if new_publisher == 'B':
                                continue

                            new_language = input("Enter new language or type 'B' to go back to main menu: ")
                            if new_language == 'B':
                                continue

                            new_noOfCopies = int(
                                input("Enter new number of copies or type '-1' to go back to main menu: "))
                            if new_noOfCopies == -1:
                                continue
                            while new_noOfCopies < 0:
                                # print("must be a value 0 or more.")
                                new_noOfCopies = int(input("Enter number of copies (value more 0 or more): "))

                            new_availability = input(
                                "Enter new availability (Y/N) or type 'B' to go back to main menu:").upper() == "Y"
                            if new_availability == 'B':
                                continue

                            new_author = input("Enter new author or type 'B' to go back to main menu: ")
                            if new_author == 'B':
                                continue

                            new_genre = input("Enter new genre or type 'B' to go back to main menu: ")
                            if new_genre == 'B':
                                continue

                            update_book(user, isbn, new_title, new_publisher, new_language, new_noOfCopies,
                                        new_availability,
                                        new_author, new_genre)
                        except ValueError:
                            print(
                                "\n** Invalid input. Please enter a valid number for ISBN and/or number of copies. **")
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

                    elif typeInput == '7':
                        view_all_users()

                    elif typeInput == '8':
                        reset_password()

                    elif typeInput == "9":
                        print("Logged Out")
                        user = None  # Reset user
                        break




                # LIBRARIAN
                elif user.role == "librarian":
                    # Librarian options
                    print("\n Welcome to Book Management System's Main Menu")
                    print("\nInput 1 to display all books \n"
                          "Input 2 to add a new book record \n"
                          "Input 3 to update a book record \n"
                          "Input 4 to delete a book record \n"
                          "Input 5 to sort books by publisher \n"
                          "Input 6 to sort books by number of copies \n"
                          "Input 7 to log out \n"
                          )
                    typeInput = input("\nEnter your input: ")

                    # Input validation
                    if typeInput not in ["1", "2", "3", "4", "5", "6", "7"]:
                        print("Invalid input. Please try again.")
                        continue

                    if typeInput == "1":
                        display_all_books(user)

                    elif typeInput == "2":
                        try:
                            isbn = int(input("Enter ISBN or type '-1' to go back  to main page: "))
                            if isbn == -1:
                                continue
                            # Validate ISBN
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
                                # print("must be a value 0 or more.")
                                noOfCopies = int(input("Enter number of copies (value more 0 or more): "))

                            availability = input("Enter availability (Y/N): ").upper() == "Y"
                            if availability == 'B':
                                continue

                            author = input("Enter author: ")
                            if author == 'B':
                                continue

                            genre = input("Enter genre: ")
                            if genre == 'B':
                                continue

                            add_new_book(user, isbn, title, publisher, language, noOfCopies, availability, author,
                                         genre)
                        except ValueError:
                            print(
                                "\n** Invalid input. Please enter a valid number for ISBN and/or number of copies. **")
                    elif typeInput == "3":
                        try:
                            isbn = int(input("Enter ISBN of the book to update: "))

                            new_title = input("Enter new title or type 'B' to go back to main menu: ")
                            if new_title == 'B':
                                continue

                            new_publisher = input("Enter new publisher or type 'B' to go back to main menu: ")
                            if new_publisher == 'B':
                                continue

                            new_language = input("Enter new language or type 'B' to go back to main menu: ")
                            if new_language == 'B':
                                continue

                            new_noOfCopies = int(
                                input("Enter new number of copies or type '-1' to go back to main menu: "))
                            if new_noOfCopies == -1:
                                continue
                            while new_noOfCopies < 0:
                                # print("must be a value 0 or more.")
                                new_noOfCopies = int(input("Enter number of copies (value more 0 or more): "))

                            new_availability = input(
                                "Enter new availability (Y/N) or type 'B' to go back to main menu: ").upper() == "Y"
                            if new_availability == 'B':
                                continue

                            new_author = input("Enter new author or type 'B' to go back to main menu: ")
                            if new_author == 'B':
                                continue

                            new_genre = input("Enter new genre or type 'B' to go back to main menu: ")
                            if new_genre == 'B':
                                continue

                            update_book(user, isbn, new_title, new_publisher, new_language, new_noOfCopies,
                                        new_availability,
                                        new_author, new_genre)
                        except ValueError:
                            print(
                                "\n** Invalid input. Please enter a valid number for ISBN and/or number of copies. **")
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
                        print("Logged Out")
                        user = None  # Reset user
                        break


                # customer
                elif user.role == "customer":
                    print("\n\nWelcome to Library's Main Menu")
                    print("\nInput 1 to display all books \n"
                          "Input 2 to search for a book by title \n"
                          "Input 3 to sort book by publisher \n"
                          "Input 4 to sort the book by number of copies \n"
                          "Input 5 to borrow a book \n"
                          "Input 6 to log out \n")
                    typeInput = input("\nEnter your input: ")

                    # Input validation
                    if typeInput not in ["1", "2", "3", "4", "5", "6"]:
                        print("Invalid input. Please try again.")
                        continue

                    if typeInput == "1":
                        display_all_books(user)

                    elif typeInput == "2":
                        print("\n-- Search a book record --\n")
                        search_title = input(
                            "Enter the title of the book you want to search for or type 'B' to go back to main menu: ")
                        if search_title == 'B':
                            continue
                        search_book_by_title(user, search_title)

                    elif typeInput == "3":
                        sort_book_publisher(user)

                    elif typeInput == "4":
                        sort_noOfCopies(user)

                    elif typeInput == "5":
                        try:
                            isbn = int(input(
                                "Enter the ISBN of the book you want to borrow or type '-1' to go back to main menu: "))
                            if isbn == -1:
                                continue
                            else:
                                borrow_book(user, isbn)

                        except ValueError:
                            print("\n** Invalid input. Please enter a valid number for ISBN. **")

                    elif typeInput == "6":
                        print("Logged Out")
                        user = None  # Reset user
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

