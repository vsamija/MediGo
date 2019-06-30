import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from medigo import app, db, bcrypt
from medigo.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from medigo.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required



@app.route("/")
@app.route("/pocetna")
def pocetna():
	image_file = "logo.jpg"
	return render_template('Pocetna.html', title='Pocetna')






@app.route("/zadaci")
@login_required
def zadaci():
	posts = Post.query.all()
	return render_template('zadaci.html', posts=posts)


@app.route("/about")
def about():
	return render_template('About.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('zadaci'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash('Vaš račun je kreiran! Možete se prijaviti','success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Registriraj se', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('zadaci'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('zadaci'))
		else:
			flash('Prijava neuspješna, provjerite email ili lozinku!','danger')
	return render_template('login.html', title='Prijavi se', form=form)



@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('zadaci'))


def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/slike_projekt',picture_fn)
	
	output_size = (125, 125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)


	i.save(picture_path)

	return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Vaš račun je ažuriran!', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static',filename='slike_projekt/' + current_user.image_file)
	return render_template('account.html', title='Accout', image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title=form.title.data, content=form.content.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Zadatak je uspješno dodan!', 'success')
		return redirect(url_for('zadaci'))
	return render_template('create_post.html', title='Novi zadatak', form=form, legend='Novi zadatak')


@app.route("/post/<int:post_id>")
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit()
		flash('Zadatak je ažuriran!', 'success')
		return redirect(url_for('post', post_id=post.id))
	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
	return render_template('create_post.html', title='Uredite zadatak', form=form, legend='Uredite zadatak')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Zadatak je obrisan!', 'success')
	return redirect(url_for('zadaci'))






