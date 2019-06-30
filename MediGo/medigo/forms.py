from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from medigo.models import User


class RegistrationForm(FlaskForm):
	username = StringField('Korisničko ime', validators=[DataRequired(), Length(min=4, max=20)])

	email = StringField('Email', validators=[DataRequired(), Email()])

	password = PasswordField('Lozinka', validators=[DataRequired(), Length(min=6, max=20)])
	confirm_password = PasswordField('Potvrda lozinke', validators=[DataRequired(), Length(min=6, max=20), EqualTo('password')])

	submit = SubmitField ('Registriraj se')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('Korisničko ime već postoji. Molimo odaberite drugo!')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('Email adresa već postoji. Molimo odaberite drugu!')


class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])

	password = PasswordField('Lozinka', validators=[DataRequired(), Length(min=6, max=20)])
	remember = BooleanField('Zapamti')
	submit = SubmitField ('Prijavi se')


class UpdateAccountForm(FlaskForm):
	username = StringField('Korisničko ime', validators=[DataRequired(), Length(min=4, max=20)])

	email = StringField('Email', validators=[DataRequired(), Email()])
	picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
	submit = SubmitField ('Ažuriraj')

	def validate_username(self, username):
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('Korisničko ime već postoji. Molimo odaberite drugo!')

	def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('Email adresa već postoji. Molimo odaberite drugu!')


class PostForm(FlaskForm):
	title = StringField('Naziv', validators=[DataRequired()])
	content = TextAreaField('Opis', validators = [DataRequired()])
	submit = SubmitField('Spremi')


