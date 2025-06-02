import sqlite3
import logging
import sys
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


def get_db_connection():
    """This function connects to database with the name `database.db`"""
    global db_connection_count
    try:
        connection = sqlite3.connect('database.db')
        connection.row_factory = sqlite3.Row
        db_connection_count += 1
    except:
        print("The database needs to be initialized first. Please run 'python init_db.py'")
    return connection

def get_post(post_id):
    """Function to get a post using its ID"""
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

#Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
db_connection_count = 0

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info('That article does not exist! - 404 error')
      return render_template('404.html'), 404
    else:
      app.logger.info('Article "{}" retrieved!'.format(post[2]))
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('The "About Us" page was retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('Article "{}" was created!'.format(title))
            return redirect(url_for('index'))
    return render_template('create.html')


@app.route('/healthz')
def healthz():
    response = app.response_class(
        response = json.dumps({"result":"OK - healthy"}),
        status = 200,
        mimetype = 'application/json'
    )
    return response


@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    connection.close()
    response = app.response_class(
        response = json.dumps({"db_connection_count": str(db_connection_count), "post_count": str(post_count)}),
        status = 200,
        mimetype = 'application/json'
    )
    return response

# start the application on port 3111
if __name__ == "__main__":
    # set logger to handle STDOUT and STDERR 
    stdout_handler =  logging.StreamHandler(sys.stdout)
    stderr_handler =  logging.StreamHandler(sys.stdout)
    handlers = [stderr_handler, stdout_handler]
    # format output
    format_output = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"

    logging.basicConfig(format=format_output, level=logging.DEBUG, handlers=handlers)
    #logging.basicConfig(filename='app.log',level=logging.DEBUG)
    app.run(host='0.0.0.0', port='3111')
