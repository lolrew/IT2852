import logging
import shelve
# Configure logging
#this uses book_management.log to track all the logs such as adding and viewing
#and time and date are also recorded
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
    User("admin", "admin123", "admin"), #a means admin
    User("librarian", "librarian123", "librarian") #l means librarian
]


def create_account():
    """
    Allows users to create a new account.

    Returns:
        User object: Returns the newly created User object.
    """
    while True:
        try:
            username = input("Enter a new username: ")

            # Check if the username already exists
            # raise ValueError("Username already exists. Please try again."): This line raises a ValueError exception with the message "Username already exists. Please try again." if the entered username already exists in the list of users.
            # raise ValueError("Invalid role. Please enter 'admin' or 'librarian'."): This line raises a ValueError exception with the message "Invalid role. Please enter 'admin' or 'librarian'." if the entered role is not either "admin" or "librarian".
            # raise is like a check to see if they are possible errors like having an invalid role

            # The any() function returns True if any item in an iterable are true, otherwise it returns False and
            # if the iterable object is empty, the any() function will return False.
            # if any() function to check if any existing user has a username that matches the username entered by the user trying to create a new account.
            # This check ensures that the new username being entered is unique and does not already exist in the list of users.

            if any(user.username == username for user in users):
                raise ValueError("Username already exists. Please try again.")

            password = input("Enter a password: ")

            role = input("Enter a role (admin / librarian): ").lower()
            # Check if the role is valid
            if role not in ["admin", "librarian"]:
                raise ValueError("Invalid role. Please enter 'a' which means admin or 'l' which means librarian.")
            user = User(username, password, role) # getting from the class meaning
            users.append(user) # for each time user creates an account, this users array will be appended

            #Save the new user to shelve
            with shelve.open('book_management_db') as db:
                db['users'] = users

            print("Account created successfully.")
            return user
        except ValueError as ve:
            print(ve) #this is if there is an error then it will throw out an exception


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
with shelve.open('book_management_db') as db:
    if 'users' not in db:
        db['users'] = users
    if 'books' not in db:    # Use 'books' for consistency
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

    #This function is responsible for displaying all the information about all the books in the system.
    # It iterates over the booklist and prints detailed information about each book. This function is
    # typically used when the user wants to view all the books in the system, such as when an admin or
    # ibrarian accesses the system.

    if is_admin(user) or user.role == "librarian": #check if only admin or librarian role can access
        for k, v in booklist.items(): # k = key, v = value
            print(
                f' ISBN: {k} \n Title: {v.get_title()} \n Publisher: {v.get_publisher()} \n Language: {v.get_language()}\n Number of Copies: {v.get_noOfCopies()}\n Availability: {v.get_availability()}\n Author: {v.get_author()}\n Genre: {v.get_genre()}\n\n')
        logging.info(f"{user.username} viewed all books.") #goes back to the book_management.log and display the info there.
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
        if not is_admin(user):
            raise PermissionError("Unauthorized access.")

        if isbn in booklist:
            raise ValueError("ISBN must be unique.")

        for book in booklist.values():
            if book.get_title() == title:
                raise ValueError("ISBN already exist for the same book title.")
        myBook = Book(isbn, title, publisher, language,noOfCopies, availability, author, genre)
        booklist[isbn] = myBook

        # Save the updated booklist to the shelve database
        with shelve.open('book_management_db') as db:
            db['books'] = booklist

        print('Book added successfully.')
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
        if is_admin(user):
            if isbn not in booklist:
                print("Book not found.")
            elif isbn in booklist:
                book = booklist[isbn]
                book._title = new_title
                book._publisher = new_publisher
                book._language = new_language
                book._noOfCopies = new_noOfCopies
                book._availability = new_availability
                book._author = new_author
                book._genre = new_genre
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
        if not is_admin(user):
            raise PermissionError("Unauthorized access.")

        if isbn not in booklist:
            raise ValueError("Book not found.")

        del booklist[isbn]

        # Save the updated booklist to the shelve database
        with shelve.open('book_management_db') as db:
            db['books'] = booklist

        print('Books deleted successfully')
        logging.info(f"{user.username} deleted book with ISBN: {isbn}.")
    except (ValueError, PermissionError) as e:
        print(e)

def sort_book_publisher(user):
    """
    Sorts books by publisher if the user is authorized.

    Args:
        user (User object): The user object.
    """

    def get_publisher(book):
        return book.get_publisher()

    try:
        if is_admin(user) or user.role == "librarian":
            with shelve.open('book_management_db') as db:
                booklist = db.get('books', {})
                books_by_publisher = sorted(booklist.values(), key=get_publisher)
                print("Books sorted by publisher:")
                for book in books_by_publisher:
                    print(f'ISBN: {book.get_isbn()} | Title: {book.get_title()} | Publisher: {book.get_publisher()} | Language: {book.get_language()} | Number of Copies: {book.get_noOfCopies()} | Availability: {book.get_availability()} | Author: {book.get_author()} | Genre: {book.get_genre()}')
                logging.info(f"{user.username} sorted books by publisher.")
        else:
            raise PermissionError("Unauthorized access.")
    except PermissionError as e:
        print(e)

            # n: Represents the total number of elements in the list to be sorted.
            #Helps determine the length of the list and the number of iterations needed to sort it.

            # i: Represents the current iteration of the outer loop. It ranges from 0 to n-1.
            # Tracks the progress of the outer loop. After each iteration of the outer loop, the largest element moves
            # to its correct position at the end of the list, so subsequent iterations can ignore the
            # last i elements that are already sorted.

            # j: Represents the index of the current element being considered within the inner loop. It ranges from 0 to n-i-1 in each iteration of the outer loop.
            # Represents the current position within the unsorted portion of the list.
            # It helps compare adjacent elements and perform swapping if necessary during each
            # iteration of the inner loop.
"""
            n = len(books)
            for i in range(n):
                swapped = False
                for j in range(0, n-i-1):
                    publisher_j = books[j].get_publisher()
                    publisher_j_plus_1 = books[j+1].get_publisher()
                    if publisher_j > publisher_j_plus_1:
                        # Swap books
                        books[j], books[j+1] = books[j+1], books[j]
                        swapped = True
                if not swapped:
                    break
            for book in books:
                print_book_info(book)
            logging.info(f"{user.username} sorted books by publisher.")
        else:
            raise PermissionError("Unauthorized access.")
    except PermissionError as pe:
        print(pe)"""

def search_book_by_isbn(isbn):
    """
    Searches for a book by ISBN.

    Args:
        isbn (int): The ISBN of the book to be searched.
    """
    with shelve.open('book_management_db') as db:
        booklist = db.get('books', {})
        for book in booklist.values():
            if book.get_isbn() == isbn:
                print(
                    f'ISBN: {book.get_isbn()} | Title: {book.get_title()} | Publisher: {book.get_publisher()} | Language: {book.get_language()} | Number of Copies: {book.get_noOfCopies()} | Availability: {book.get_availability()} | Author: {book.get_author()} | Genre: {book.get_genre()}')
                return
        print("Book not found.")

def search_book_by_title(title):
    """
    Searches for a book by title.

    Args:
        title (str): The title of the book to be searched.
    """
    with shelve.open('book_management_db') as db:
        booklist = db.get('books', {})
        for book in booklist.values():
            if book.get_title().lower() == title.lower():
                print(
                    f'ISBN: {book.get_isbn()} | Title: {book.get_title()} | Publisher: {book.get_publisher()} | Language: {book.get_language()} | Number of Copies: {book.get_noOfCopies()} | Availability: {book.get_availability()} | Author: {book.get_author()} | Genre: {book.get_genre()}')
                return
        print("Book not found.")

def sort_noOfCopies(user):
    def get_noOfCopies(book):
        return book.get_noOfCopies()

    try:
        if is_admin(user) or user.role == "librarian":
            with shelve.open('book_management_db') as db:
                booklist = db.get('books', {}).values()
                books_by_noOfCopies = sorted(booklist, key=get_noOfCopies, reverse=True)
                print("Books sorted by number of copies:")
                for book in books_by_noOfCopies:
                    print(
                        f'ISBN: {book.get_isbn()} | Title: {book.get_title()} | Publisher: {book.get_publisher()} | Language: {book.get_language()} '
                        f'| Number of Copies: {book.get_noOfCopies()} | Availability: {book.get_availability()} | Author: {book.get_author()} '
                        f'| Genre: {book.get_genre()}')
                logging.info(f"{user.username} sorted books by number of copies.")
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




# Main loop
while True:

    # Welcome message
    print("Welcome to the Book Management System!")

    print("\nInput 1 to log in \nInput 2 to create a new account \nInput 3 to exit")
    choice = input("\nEnter your choice: ")

    if choice == "1":
        print("Please log in or press 'B' on username or password to go back to Welcome Page.")
        username = input("Enter username: ")
        if username.upper() == 'B':  # If 'B' is entered, go back to the main menu
            continue
        password = input("Enter password: ")
        if password.upper() == 'B':
            continue

        user = authenticate(username, password)
        if user:
            print(f"Welcome, {user.username}!")
            while True:
                if is_admin(user):
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
                            print("Input 'B' to go back to main page")

                            isbn = int(input("Enter ISBN: "))

                            title = input("Enter book title: ")
                            if title == 'B':
                                continue

                            publisher = input("Enter publisher: ")
                            if publisher == 'B':
                                continue

                            language = input("Enter language: ")
                            if language == 'B':
                                continue

                            noOfCopies = int(input("Enter number of copies: "))

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
                            print("Invalid input. Please enter a valid number for ISBN and number of copies.")
                    elif typeInput == "3":
                        try:
                            print("Input 'B' to go back main page")

                            isbn = int(input("Enter ISBN of the book to update: "))

                            new_title = input("Enter new title: ")
                            if new_title == 'B':
                                continue

                            new_publisher = input("Enter new publisher: ")
                            if new_publisher == 'B':
                                continue

                            new_language = input("Enter new language: ")
                            if new_language == 'B':
                                continue

                            new_noOfCopies = int(input("Enter new number of copies: "))

                            new_availability = input("Enter new availability (Y/N): ").upper() == "Y"
                            if new_availability == 'B':
                                continue

                            new_author = input("Enter new author: ")
                            if new_author == 'B':
                                continue

                            new_genre = input("Enter new genre: ")
                            if new_genre == 'B':
                                continue

                            update_book(user, isbn, new_title, new_publisher, new_language, new_noOfCopies,
                                        new_availability,
                                        new_author, new_genre)
                        except ValueError:
                            print("Invalid input. Please enter a valid number for ISBN and number of copies.")
                    elif typeInput == "4":
                        try:
                            print("Input 'B' to go back to main page")
                            isbn = int(input("Enter ISBN of the book to delete: "))
                            delete_book(user, isbn)
                        except ValueError:
                            print("Invalid input. Please enter a valid number for ISBN.")
                    elif typeInput == "5":
                        sort_book_publisher(user)
                    elif typeInput == "6":
                        sort_noOfCopies(user)
                    elif typeInput == "7":
                        print("Logged Out")
                        user = None  # Reset user
                        break
                else:
                    print("\nInput 1 to display all books \n"
                          "Input 2 to sort books by publisher \n"
                          "Input 3 to sort books by number of copies \n"
                          "Input 4 to log out \n")
                    typeInput = input("\nEnter your input: ")

                    # Input validation
                    if typeInput not in ["1", "2", "3", "4"]:
                        print("Invalid input. Please try again.")
                        continue

                    if typeInput == "1":
                        display_all_books(user)
                    elif typeInput == "2":
                        sort_book_publisher(user)
                    elif typeInput == "3":
                        sort_noOfCopies(user)
                    elif typeInput == "4":
                        print("Logged Out")
                        user = None  # Reset user
                        break
        else:
            print("Invalid username or password. Please try again.")
    elif choice == "2":
        new_user = create_account()
    elif choice == "3":
        print("Exiting the program. Goodbye!")
        break
    else:
        print("Invalid input. Please try again.")

