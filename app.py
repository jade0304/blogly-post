import re
from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "abc123"
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()



@app.route('/')
def root():
    """Show recent list of posts, most-recent first."""

    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template("posts/homepage_post.html", posts=posts)


@app.errorhandler(404)
def page_not_found(e):
    """Show 404 NOT FOUND page."""

    return render_template('404.html'), 404


@app.route('/users')
def user_listing():
    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('listing.html', users=users)

@app.route('/users/new', methods=["GET"])
def users_new_form():
    """Show a form to create a new user"""

    return render_template('create_user.html')

@app.route('/users/new', methods=['POST'])
def create_new_user():
    """submit the form for creating a new user"""
    fname = request.form['first_name']
    lname = request.form['last_name']
    img = request.form['img_url'] or None
    
    new_user = User(first_name=fname, last_name=lname, image_url=img)
    db.session.add(new_user)
    db.session.commit()
    return redirect('/users')

@app.route('/users/<int:user_id>')
def user_detail(user_id):
    """show detail about a specific user"""
    user = User.query.get_or_404(user_id)
    return render_template('user_detail.html', user=user)


@app.route('/users/<int:user_id>/edit')
def edit_user(user_id):
    """Show form to edit existing user"""
    user = User.query.get_or_404(user_id)

    return render_template('edit_user.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=['POST'])
def update_user(user_id):
    """submit the form for updating user info"""
    user = User.query.get_or_404(user_id)

    fname = request.form['first_name']
    lname = request.form['last_name']
    img = request.form['img_url']
    
    user.first_name = fname
    user.last_name = lname
    user.image_url = img

    db.session.add(user)
    db.session.commit()
    return redirect('/users')

@app.route('/users/<user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete an existing user."""
    user = User.query.get_or_404(user_id)
    
    db.session.delete(user)
    db.session.commit()
    return redirect('/users')

# ****************************************************************

@app.route('/users/<int:user_id>/posts/new')
def show_post_form(user_id):
    """Show post for that user."""
    user = User.query.get_or_404(user_id)

    return render_template('posts/add_post.html', user=user)

@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def handle_add_form(user_id):
    """handle form submission"""
    user = User.query.get_or_404(user_id)
    new_post = Post(title=request.form['title'],
                    content=request.form['content'],
                    user=user)
    
    db.session.add(new_post)
    db.session.commit()

    flash(f"Post '{new_post.title}' added.")
    return redirect(f'/users/{user_id}')
    
    
@app.route('/posts/<int:post_id>')
def show_post(post_id):
    """show post with edit and delete button"""
    
    post = Post.query.get_or_404(post_id)
    return render_template('posts/show_post.html', post=post)
        
    
@app.route('/posts/<int:post_id>/edit')
def edit_post(post_id):
    """show form to edit a post, and to cancle"""
    
    post = Post.query.get_or_404(post_id)
    return render_template('edit_post.html', post=post)

      
@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def handle_edit_post(post_id):
    """handle editing of a post. Redirect back to post view"""
    
    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']
    
    db.session.add(post)
    db.session.commit()
    flash(f"Post '{post.title}' edited.")
    
    return redirect(f'/users/{post.user_id}')


@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def delete_post(post_id):
    """Handle form submission for deleting existing post"""
    
    post = Post.query.get_or_404(post_id)
    
    db.session.delete(post)
    db.session.commit()
    
    flash(f"Post '{post.title} deleted'")
    return redirect(f'/users/{post.user_id}')