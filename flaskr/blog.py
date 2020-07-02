from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    """Show all the posts, most recent first."""
    db = get_db()
    posts = db.execute(
        'SELECT  p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user  u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    
    print(posts)
    
    likes = db.execute(
        'SELECT * from likes'
    ).fetchall()
    
    return render_template('blog/index.html', posts=posts, likes=likes)
    
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        
        if not title:
            error = 'Title is required.'
            
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?,?,?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
                
    return render_template('blog/create.html')

@bp.route('/<int:id>/like', methods=('POST',))   
@login_required 
def like(id):
    """If not done already, like a  post for the current user."""
    post = get_post(id)
    db = get_db()
    """
    user_like = db.execute(
        'SELECT * FROM likes WHERE'
        ' post_id = ? AND user_id = ?',
        (post, g.user['id'])
    )
    .fetchone()
    """
    
    like = get_like(id)
    error = None
    if like:
        error = 'Post already liked by user'
    if error is not None:
        flash(error)
    else:
        db.execute(
            'INSERT INTO likes (post_id, user_id)'
            ' VALUES (?,?)',
            (post['author_id'], g.user['id'])
        )
        db.commit   ()
           
    return redirect(url_for('blog.index'))
    
@bp.route('/<int:id>/unlike', methods=('POST',))   
@login_required 
def unlike(id):
    """If not done already, like a  post for the current user."""
    post = get_post(id)
    db = get_db()
   
    db.execute(
        'DELETE FROM likes WHERE (post_id, user_id) == '
        '(?,?)',
        (id, g.user['id'])
    )
    db.commit()
           
    return redirect(url_for('blog.index'))
    
def get_like(id):
    """Check if a user liked a post"""
    post = get_post(id)
    like = get_db().execute(
        'SELECT * FROM likes'
        ' WHERE post_id = ? AND user_id = ?',
        (post['author_id'], g.user['id'])
        ).fetchone()
        
    return like
            

def get_post(id, check_author=True):
            post = get_db().execute(
                'SELECT p.id, title, body, created, author_id, username'
                ' FROM post p JOIN user u ON p.author_id = u.id'
                ' WHERE p.id = ?',
                (id,)
            ).fetchone()
            
            if post is None:
                abort(404, "Post id [0] doesn't exist.".format(id))
                
            if check_author and post['author_id'] != g.user['id']:
                abort(403)
                
            return post
            
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        
        if not title:
            error = 'Title is required.'
            
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
            
    return render_template('blog/update.html', post=post)
        
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
