from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL, Length
from flask_ckeditor import CKEditor, CKEditorField
from datetime import datetime
from flask_ckeditor import CKEditor

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy()
db.init_app(app)

# CKEditor
ckeditor = CKEditor(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


# FORM
class PostForm(FlaskForm):
    blog_post_title = StringField(label="Blog Post title", validators=[DataRequired(), Length(min=8)])
    subtitle = StringField(label='Subtitle', validators=[DataRequired()])
    author = StringField(label="Your name", validators=[DataRequired()])
    image_url = StringField(label="Blog Image URL", validators=[DataRequired(), URL()])
    blog_content = CKEditorField('Body')
    submit = SubmitField(label="Submit post")


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost).order_by(BlogPost.title))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route('/post/<post_id>')
def show_post(post_id):
    requested_post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    return render_template("post.html", post=requested_post)


@app.route("/new-post", methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if request.method == 'POST' and form.validate_on_submit():
        blog_post_title = form.blog_post_title.data
        subtitle = form.subtitle.data
        author = form.author.data
        image_url = form.image_url.data
        blog_content = form.blog_content.data
        new_post = BlogPost(
            title=blog_post_title,
            subtitle=subtitle,
            date=datetime.today().strftime('%B %d,%Y'),
            body=blog_content,
            author=author,
            img_url=image_url,
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form=form)


@app.route("/edit-post/<post_id>", methods=['GET', 'POST'])
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    form = PostForm(
        blog_post_title=post.title,
        subtitle=post.subtitle,
        author=post.author,
        image_url=post.img_url,
        blog_content=post.body,
    )
    if request.method == 'POST' and form.validate_on_submit():
        post.title = form.blog_post_title.data
        post.subtitle = form.subtitle.data
        post.author = form.author.data
        post.img_url = form.image_url.data
        post.body = form.blog_content.data
        db.session.commit()
        return redirect(url_for('show_post', post_id=post.id))
    return render_template('make-post.html', from_page='edit', form=form)


@app.route("/delete/<post_id>")
def delete_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
