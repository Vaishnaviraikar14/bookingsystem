import sqlite3
import hashlib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Initialize the SQLite database
conn = sqlite3.connect('cinema.db')
c = conn.cursor()

# Create users table if not exists
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT 0
)
''')

# Create screens table if not exists
c.execute('''
CREATE TABLE IF NOT EXISTS screens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    capacity INTEGER NOT NULL
)
''')

# Create movies table with screen_id
c.execute('''
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    genre TEXT NOT NULL,
    showtime TEXT NOT NULL,
    screen_id INTEGER NOT NULL,
    FOREIGN KEY (screen_id) REFERENCES screens(id)
)
''')

# Create bookings table if not exists
c.execute('''
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    movie_id INTEGER,
    seats_booked INTEGER,
    total_price REAL,
    status TEXT DEFAULT 'confirmed',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (movie_id) REFERENCES movies(id)
)
''')
conn.commit()

# Create food items table if not exists
c.execute('''
CREATE TABLE IF NOT EXISTS food_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL
)
''')
conn.commit()

# Create orders table if not exists
c.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    food_item_id INTEGER,
    quantity INTEGER NOT NULL,
    total_price REAL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (food_item_id) REFERENCES food_items(id)
)
''')
conn.commit()

# Function for admin panel
def admin_panel():
    while True:
        print("\nAdmin Panel:")
        print("1. Screen Management")
        print("2. Booking Management")
        print("3. Food Menu Management")
        print("4. Exit Admin Panel")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            screen_management()
        elif choice == '2':
            booking_management()
        elif choice == '3':
            food_menu_management()
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

# Screen Management
def screen_management():
    while True:
        print("\nScreen Management:")
        print("1. Add Screen")
        print("2. View Screens")
        print("3. Delete Screen")
        print("4. Back")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            add_screen()
        elif choice == '2':
            view_screens()
        elif choice == '3':
            delete_screen()
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

def add_screen():
    name = input("Enter screen name: ")
    capacity = int(input("Enter screen capacity: "))

    c.execute('INSERT INTO screens (name, capacity) VALUES (?, ?)', (name, capacity))
    conn.commit()
    print("Screen added successfully!")

def view_screens():
    c.execute('SELECT * FROM screens')
    screens = c.fetchall()

    if screens:
        print("\n=== Screens ===")
        for screen in screens:
            print(f"ID: {screen[0]}, Name: {screen[1]}, Capacity: {screen[2]}")
    else:
        print("No screens available.")

def delete_screen():
    view_screens()
    screen_id = int(input("Enter the ID of the screen to delete: "))

    c.execute('DELETE FROM screens WHERE id=?', (screen_id,))
    conn.commit()
    print("Screen deleted successfully!")

# Booking Management
def booking_management():
    while True:
        print("\nBooking Management:")
        print("1. View Bookings")
        print("2. Cancel Booking")
        print("3. Back")

        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            view_bookings()
        elif choice == '2':
            cancel_booking()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 3.")

def view_bookings():
    c.execute('''
    SELECT bookings.id, users.name, movies.title, bookings.seats_booked, bookings.total_price, bookings.status, bookings.timestamp
    FROM bookings
    JOIN users ON bookings.user_id = users.id
    JOIN movies ON bookings.movie_id = movies.id
    ''')
    bookings = c.fetchall()

    if bookings:
        print("\n=== Bookings ===")
        for booking in bookings:
            print(
                f"ID: {booking[0]}, User: {booking[1]}, Movie: {booking[2]}, Seats: {booking[3]}, Total Price: ${booking[4]:.2f}, Status: {booking[5]}, Timestamp: {booking[6]}")
    else:
        print("No bookings available.")

def cancel_booking():
    view_bookings()
    booking_id = int(input("Enter the ID of the booking to cancel: "))

    c.execute('UPDATE bookings SET status="cancelled" WHERE id=?', (booking_id,))
    conn.commit()
    print("Booking cancelled successfully!")

# Food Menu Management
def food_menu_management():
    while True:
        print("\nFood Menu Management:")
        print("1. Add Food Item")
        print("2. View Food Menu")
        print("3. Delete Food Item")
        print("4. Back")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            add_food_item()
        elif choice == '2':
            view_food_menu()
        elif choice == '3':
            delete_food_item()
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

def add_food_item():
    name = input("Enter food item name: ")
    price = float(input("Enter food item price: "))

    c.execute('INSERT INTO food_items (name, price) VALUES (?, ?)', (name, price))
    conn.commit()
    print("Food item added successfully!")

def view_food_menu():
    c.execute('SELECT * FROM food_items')
    food_items = c.fetchall()

    if food_items:
        print("\n=== Food Menu ===")
        for item in food_items:
            print(f"ID: {item[0]}, Name: {item[1]}, Price: ${item[2]:.2f}")
    else:
        print("No food items available.")

def delete_food_item():
    view_food_menu()
    food_item_id = int(input("Enter the ID of the food item to delete: "))

    c.execute('DELETE FROM food_items WHERE id=?', (food_item_id,))
    conn.commit()
    print("Food item deleted successfully!")

def register():
    print("=== Register ===")
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    try:
        c.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, hashed_password))
        conn.commit()
        print("Registration successful!")
    except sqlite3.IntegrityError:
        print("Error: Email already exists!")

def login():
    print("=== Login ===")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    c.execute('SELECT * FROM users WHERE email=? AND password=?', (email, hashed_password))
    user = c.fetchone()

    if user:
        print(f"Login successful! Welcome, {user[1]}!")
        return user
    else:
        print("Error: Invalid email or password!")
        return None

def display_movies():
    c.execute('''
    SELECT movies.id, movies.title, movies.genre, movies.showtime, screens.name
    FROM movies
    JOIN screens ON movies.screen_id = screens.id
    ''')
    movies = c.fetchall()

    if movies:
        print("\n=== Available Movies ===")
        for movie in movies:
            print(f"ID: {movie[0]}, Title: {movie[1]}, Genre: {movie[2]}, Showtime: {movie[3]}, Screen: {movie[4]}")
    else:
        print("No movies available.")

def select_movie():
    display_movies()
    movie_id = input("\nEnter the ID of the movie you want to watch: ")
    return movie_id

def display_seats(movie_id):
    c.execute(
        'SELECT movies.id, movies.title, movies.genre, movies.showtime, screens.name, screens.capacity FROM movies JOIN screens ON movies.screen_id = screens.id WHERE movies.id=?',
        (movie_id,))
    movie = c.fetchone()

    if movie:
        print(
            f"\n=== Movie Details ===\nID: {movie[0]}\nTitle: {movie[1]}\nGenre: {movie[2]}\nShowtime: {movie[3]}\nScreen: {movie[4]}\nCapacity: {movie[5]}")
        c.execute('SELECT SUM(seats_booked) FROM bookings WHERE movie_id=?', (movie_id,))
        seats_booked = c.fetchone()[0] or 0
        available_seats = movie[5] - seats_booked
        print(f"Available Seats: {available_seats}")
    else:
        print("Movie not found.")

def reserve_seats(user, movie_id):
    display_seats(movie_id)
    seats = int(input("Enter the number of seats you want to reserve: "))

    c.execute('SELECT capacity FROM screens JOIN movies ON screens.id = movies.screen_id WHERE movies.id=?',
              (movie_id,))
    screen_capacity = c.fetchone()[0]

    c.execute('SELECT SUM(seats_booked) FROM bookings WHERE movie_id=?', (movie_id,))
    seats_booked = c.fetchone()[0] or 0

    available_seats = screen_capacity - seats_booked

    if seats > available_seats:
        print(f"Only {available_seats} seats are available.")
        send_email(user[2], "Seat Availability Alert",
                   f"Only {available_seats} seats are available for the selected movie.")
        return

    total_price = seats * 10.0  # Assume each seat costs $10.0

    c.execute('INSERT INTO bookings (user_id, movie_id, seats_booked, total_price) VALUES (?, ?, ?, ?)',
              (user[0], movie_id, seats, total_price))
    conn.commit()
    print("Seats reserved successfully!")

    send_email(user[2], "Booking Confirmation",
               f"Your booking for {seats} seats has been confirmed. Total price: ${total_price:.2f}")

def display_food_menu():
    c.execute('SELECT * FROM food_items')
    food_items = c.fetchall()

    if food_items:
        print("\n=== Food Menu ===")
        for item in food_items:
            print(f"ID: {item[0]}, Name: {item[1]}, Price: ${item[2]:.2f}")
    else:
        print("No food items available.")

def add_to_cart(user):
    while True:
        display_food_menu()
        food_item_id = int(input("\nEnter the ID of the food item you want to add to cart (0 to exit): "))

        if food_item_id == 0:
            break

        quantity = int(input("Enter the quantity: "))

        c.execute('SELECT * FROM food_items WHERE id=?', (food_item_id,))
        food_item = c.fetchone()

        if food_item:
            total_price = quantity * food_item[2]
            c.execute('INSERT INTO orders (user_id, food_item_id, quantity, total_price) VALUES (?, ?, ?, ?)',
                      (user[0], food_item_id, quantity, total_price))
            conn.commit()
            print("Food item added to cart successfully!")
        else:
            print("Invalid food item ID.")

def checkout(user):
    c.execute('SELECT * FROM orders WHERE user_id=?', (user[0],))
    orders = c.fetchall()

    if orders:
        total_amount = sum(order[4] for order in orders)
        print("\n=== Order Summary ===")
        for order in orders:
            print(f"Food Item: {order[1]}, Quantity: {order[3]}, Total Price: ${order[4]:.2f}")

        print(f"\nTotal Amount: ${total_amount:.2f}")

        confirm = input("Confirm checkout (yes/no): ").lower()
        if confirm == 'yes':
            # Place your checkout logic here (e.g., payment processing, etc.)
            c.execute('DELETE FROM orders WHERE user_id=?', (user[0],))
            conn.commit()
            print("Checkout successful! Enjoy your movie.")
        else:
            print("Checkout cancelled.")
    else:
        print("No items in the cart.")

def send_email(to_email, subject, body):
    from_email = "vaishnaviraikar1403@gmail.com"
    from_password = "Vaishnavi2001"
    smtp_server = "smtp.example.com"
    smtp_port = 587

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print(f"Email sent successfully to {to_email}")
    except smtplib.SMTPException as e:
        print(f"Failed to send email. Error: {e}")


def main():
    user = None  # Initialize user variable

    while True:
        print("\n=== Movie Booking System ===")
        print("1. Register")
        print("2. Login")
        print("3. Display Movies")
        print("4. Select Movie")
        print("5. Reserve Seats")
        print("6. Confirm Booking")
        print("7. Display Food Menu")
        print("8. Add to Cart")
        print("9. Checkout")
        print("10. Admin Panel")
        print("11. Exit")

        choice = input("Enter your choice (1-11): ")

        if choice == '1':
            register()
        elif choice == '2':
            user = login()
            if user:
                if user[3] == 1:  # Check if user is admin
                    admin_panel()
        elif choice == '3':
            display_movies()
        elif choice == '4':
            movie_id = select_movie()
        elif choice == '5':
            if user:
                if 'movie_id' in locals():
                    reserve_seats(user, movie_id)
                else:
                    print("Please select a movie first.")
            else:
                print("Please login first.")
        elif choice == '6':
            # Confirm booking functionality can be implemented here
            pass
        elif choice == '7':
            display_food_menu()
        elif choice == '8':
            if user:
                add_to_cart(user)
            else:
                print("Please login first.")
        elif choice == '9':
            if user:
                checkout(user)
            else:
                print("Please login first.")
        elif choice == '10':
            if user and user[4] == 1:  # Check if user is admin
                admin_panel()
            else:
                print("Access denied. Admin rights required.")
        elif choice == '11':
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 11.")

    conn.close()
    print("Thank you for using the Movie Booking System!")

if __name__ == "__main__":
    main()