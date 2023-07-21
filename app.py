from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions on the filesystem

# Function to get a database connection
def get_db_connection():
    connection = sqlite3.connect('hackernews.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to create database tables
def create_tables():
    with app.open_resource('schema.sql', mode='r') as f:
        connection = get_db_connection()
        connection.cursor().executescript(f.read())
        connection.commit()
        connection.close()

# Call create_tables() to create the tables
create_tables()

# Data model for User
class User:
    def __init__(self, username, password):
        self.id = None
        self.username = username
        self.password = password

    def create_user(self):
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO user (username, password) VALUES (?, ?)',
                           (self.username, self.password))
            connection.commit()
            self.id = cursor.lastrowid
        return self

    @staticmethod
    def find_by_username(username):
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM user WHERE username = ?', (username,))
            user_data = cursor.fetchone()
            if user_data:
                user = User(user_data['username'], user_data['password'])
                user.id = user_data['id']
                return user
        return None
    @classmethod
    def get_user_by_id(cls, user_id):
        users = [
            User(1, 'john_doe', 'john@example.com', 'hashed_password_1', '2023-07-21 12:34:56'),
            User(2, 'jane_smith', 'jane@example.com', 'hashed_password_2', '2023-07-20 09:15:25'),
            # Add more user objects as needed...
        ]
        for user in users:
            if user.user_id == user_id:
                return user

        return None

        for user in users:
            if user.user_id == user_id:
                return user

        return None

# Data model for Post
class Post:
    def __init__(self, title, content, user_id):
        self.id = None
        self.title = title
        self.content = content
        self.created_at = None
        self.user_id = user_id

    def create_post(self):
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO post (title, content, user_id) VALUES (?, ?, ?)',
                           (self.title, self.content, self.user_id))
            connection.commit()
            self.id = cursor.lastrowid
        return self

    @staticmethod
    def get_all_posts():
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM post ORDER BY created_at DESC')
            posts_data = cursor.fetchall()
            posts = []
            for post_data in posts_data:
                post = Post(post_data['title'], post_data['content'], post_data['user_id'])
                post.id = post_data['id']
                post.created_at = post_data['created_at']
                posts.append(post)
            return posts

    @staticmethod
    def get_post_by_id(post_id):
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM post WHERE id = ?', (post_id,))
            post_data = cursor.fetchone()
            if post_data:
                post = Post(post_data['title'], post_data['content'], post_data['user_id'])
                post.id = post_data['id']
                post.created_at = post_data['created_at']
                return post
            return None

# Data model for Comment
class Comment:
    def __init__(self, text, post_id, user_id):
        self.id = None
        self.text = text
        self.created_at = None
        self.post_id = post_id
        self.user_id = user_id

    def create_comment(self):
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO comment (text, post_id, user_id) VALUES (?, ?, ?)',
                           (self.text, self.post_id, self.user_id))
            connection.commit()
            self.id = cursor.lastrowid

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username is already taken
        existing_user = User.find_by_username(username)
        if existing_user:
            flash('Username already taken. Please choose a different username.', 'danger')
            return redirect(url_for('register'))

        # Create a new user and save it to the database
        user = User(username, password)
        user.create_user()

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists and the password is correct
        user = User.find_by_username(username)
        if user and user.password == password:
            session['user_id'] = user.id  # Simulate user login by setting a session variable
            flash('Login successful. Welcome, {}!'.format(username), 'success')
            return redirect(url_for('home'))

        flash('Invalid username or password. Please try again.', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')

# Route for user logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Home route
@app.route('/')
def home():
    posts = Post.get_all_posts()
    return render_template('index.html', posts=posts)

    
@app.route('/create_post', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        flash('You must be logged in to create a new post. Please login or register.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        post_title = request.form['post_title']
        post_content = request.form['post_content']

        post = Post(post_title, post_content, user_id)
        post.create_post()

        flash('Post created successfully!', 'success')
        return redirect(url_for('home'))
    
@app.route('/add_comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session:
        flash('You must be logged in to add a comment. Please login or register.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        comment_text = request.form['comment_text']

        comment = Comment(comment_text, post_id, user_id)
        comment.create_comment()

        flash('Comment added successfully!', 'success')
        return redirect(url_for('home'))
    
@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.get_post_by_id(post_id)
    if post is None:
        flash('Post not found.', 'danger')
        return redirect(url_for('home'))

    return render_template('view_post.html', post=post)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('You must be logged in to view your profile.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.get_user_by_id(user_id)
    if user is None:
        flash('User not found.', 'danger')
        return redirect(url_for('home'))

    return render_template('profile.html', user=user)

@app.route('/account_settings', methods=['GET', 'POST'])
def account_settings():
    if 'user_id' not in session:
        flash('You must be logged in to access account settings.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.get_user_by_id(user_id)
    if user is None:
        flash('User not found.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        new_username = request.form['new_username']
        new_password = request.form['new_password']

        # Validate and update the username and password
        if not new_username:
            flash('Username cannot be empty.', 'danger')
        elif not new_password:
            flash('Password cannot be empty.', 'danger')
        else:
            user.update_profile(new_username, new_password)
            flash('Account settings updated successfully!', 'success')
            return redirect(url_for('profile'))

    return render_template('account_settings.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)