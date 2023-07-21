from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Temporary storage for user data (replace with a database in production)
users = []

# Data model for User
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username is already taken
        if any(user.username == username for user in users):
            flash('Username already taken. Please choose a different username.', 'danger')
            return redirect(url_for('register'))

        # Create a new user and add it to the list (temporary storage)
        new_user = User(username, password)
        users.append(new_user)

        flash('Registration successful. You can now login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists and the password is correct
        user = next((user for user in users if user.username == username), None)
        if user and user.password == password:
            # Simulate user login by setting a session variable (replace with proper session management)
            flash('Login successful. Welcome, {}!'.format(username), 'success')
            return redirect(url_for('home'))

        flash('Invalid username or password. Please try again.', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')

# Home route
@app.route('/')
def home():
    return "Hacker News Clone"

if __name__ == '__main__':
    app.run(debug=True)
