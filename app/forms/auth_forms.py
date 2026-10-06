from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class RegisterForm(FlaskForm):
    """Formulário de cadastro de novo usuário."""

    nome = StringField('Nome', validators=[
        DataRequired(message="Informe seu nome."),
        Length(min=2, max=50, message="Nome deve ter entre 2 e 50 caracteres.")
    ])

    email = StringField('Email', validators=[
        DataRequired(message="Informe seu e-mail."),
        Email(message="Informe um e-mail válido.")
    ])

    senha = PasswordField('Senha', validators=[
        DataRequired(message="Digite uma senha."),
        Length(min=6, message="A senha deve ter pelo menos 6 caracteres.")
    ])

    consentimento = BooleanField(
        'Estou ciente de que as análises da IA têm caráter apenas estatístico e informativo.',
        validators=[DataRequired(message="Você precisa aceitar os termos.")]
    )

    submit = SubmitField('Criar Conta')

class LoginForm(FlaskForm):
    """Formulário de autenticação de usuário."""

    email = StringField('Email', validators=[
        DataRequired(message="Informe seu e-mail."),
        Email(message="Informe um e-mail válido.")
    ])

    senha = PasswordField('Senha', validators=[
        DataRequired(message="Digite sua senha.")
    ])

    submit = SubmitField('Entrar')
