# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

ARTICLES_DIR = 'articles'
if not os.path.exists(ARTICLES_DIR):
    os.makedirs(ARTICLES_DIR)

# Hardcoded admin credentials (replace with more secure method in production)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password'

def get_articles():
    articles = []
    for filename in os.listdir(ARTICLES_DIR):
        if filename.endswith('.json'):
            with open(os.path.join(ARTICLES_DIR, filename), 'r') as f:
                article = json.load(f)
                articles.append(article)
    return sorted(articles, key=lambda x: x['date'], reverse=True)

@app.route('/')
def home():
    articles = get_articles()
    return render_template('home.html', articles=articles)

@app.route('/article/<string:id>')
def article(id):
    filename = f"{id}.json"
    filepath = os.path.join(ARTICLES_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            article = json.load(f)
        return render_template('article.html', article=article)
    return "Article not found", 404

@app.route('/admin')
def admin():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    articles = get_articles()
    return render_template('admin/dashboard.html', articles=articles)

@app.route('/admin/add', methods=['GET', 'POST'])
def add_article():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        id = str(int(datetime.now().timestamp()))
        article = {
            'id': id,
            'title': title,
            'content': content,
            'date': date
        }
        with open(os.path.join(ARTICLES_DIR, f"{id}.json"), 'w') as f:
            json.dump(article, f)
        flash('Article added successfully', 'success')
        return redirect(url_for('admin'))
    return render_template('admin/add_article.html')

@app.route('/admin/edit/<string:id>', methods=['GET', 'POST'])
def edit_article(id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    filepath = os.path.join(ARTICLES_DIR, f"{id}.json")
    if request.method == 'POST':
        article = {
            'id': id,
            'title': request.form['title'],
            'content': request.form['content'],
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(filepath, 'w') as f:
            json.dump(article, f)
        flash('Article updated successfully', 'success')
        return redirect(url_for('admin'))
    else:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                article = json.load(f)
            return render_template('admin/edit_article.html', article=article)
    return "Article not found", 404

@app.route('/admin/delete/<string:id>')
def delete_article(id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    filepath = os.path.join(ARTICLES_DIR, f"{id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
        flash('Article deleted successfully', 'success')
    return redirect(url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)