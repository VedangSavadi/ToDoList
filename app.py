from flask import Flask, render_template, request, redirect, url_for,flash,session
import requests
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_oidc import OpenIDConnect
from flask_session import Session 
import stripe
from flask import jsonify
import json
from flask_graphql import GraphQLView
import graphene
from flask.views import MethodView
import os

stripe.api_key = "sk_test_51OS1PoSJKGxc59SvYZiPwkJTgBYuFeRlpoQYaOFKyXswMrfLKIgt5OMN3vo8GiSMaPAFZ1gbt6fDaZdfpgh1SzGk00g4VTkIWL"  # this is test key


app = Flask(__name__)
app.static_url_path = ''
app.static_folder = 'static'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)
app.secret_key = 'vedangsapp'
# Flask-OIDC configuration for Keycloak
app.config.update({
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',  # Path to your client_secrets.json file
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
})

oidc = OpenIDConnect(app)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    image_path = db.Column(db.String(200))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    is_pro = db.Column(db.Boolean, default=False)

# Function to create tables within the application context
def create_tables():
    with app.app_context():
        db.drop_all()
        db.create_all()

@app.route('/logout', methods=['POST'])
def logout():
    if oidc.user_loggedin:
        oidc.logout()
    return redirect(oidc.client_secrets['issuer'] + '/protocol/openid-connect/logout?redirect_uri=' + url_for('logout', _external=True))


@app.route('/', methods=['GET', 'POST'])
@oidc.require_login
def index():
    if request.method == 'GET':
        todos = ToDo.query.order_by(ToDo.timestamp.desc()).all()
        user = oidc.user_getfield('preferred_username')
        emailid = oidc.user_getfield('email')
        existing_user = User.query.filter_by(username=user).first()
        # existing_email = User.query.filter_by(email = emailid).first()

        if existing_user is None:
            new_user = User(username=user , email=emailid)
            db.session.add(new_user)
            db.session.commit()

        return render_template('index.html', todos=todos, current_user=User.query.filter_by(username=oidc.user_getfield('preferred_username')).first())

    elif request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
         # Check if the user is Pro and an image was uploaded
        if oidc.user_loggedin and oidc.user_getfield('is_pro') and 'image' in request.files:
            image_filename = images.save(request.files['image'])
            new_todo = ToDo(title=title, description=description, image_path=image_filename)
        else:
            # Create a ToDo without an image if the user is not Pro or no image is uploaded
            new_todo = ToDo(title=title, description=description)
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for('index'))

        

from flask_uploads import UploadSet, configure_uploads , IMAGES
# Configure image uploads
app.config['UPLOADED_IMAGES_DEST'] = 'static/uploads'
images = UploadSet('images', IMAGES)
configure_uploads(app, images)
@app.route('/add', methods=['POST'])
@oidc.require_login
def add_todo():
    title = request.form['title']
    description = request.form['description']
    current_user = User.query.filter_by(username=oidc.user_getfield('preferred_username')).first()
    # Check if the user is Pro to allow image upload
    if current_user.is_pro and 'image' in request.files:
        image_filename = images.save(request.files['image'])
        new_todo = ToDo(title=title, description=description, image_path=image_filename)
    else:
        new_todo = ToDo(title=title, description=description)

    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for('index'))



@app.route('/delete/<int:id>')
@oidc.require_login
def delete_todo(id):
    todo_to_delete = ToDo.query.get_or_404(id)
    # Check if the To-Do item has an associated image
    if todo_to_delete.image_path:
        # Delete the associated image file
        image_path = os.path.join(app.config['UPLOADED_IMAGES_DEST'], todo_to_delete.image_path)
        if os.path.exists(image_path):
            os.remove(image_path)
    db.session.delete(todo_to_delete)
    db.session.commit()
    return redirect(url_for('index'))
    

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@oidc.require_login
def edit_todo(id):
    todo = ToDo.query.get_or_404(id)

    if request.method == 'POST':
        todo.title = request.form['title']
        todo.description = request.form['description']

        # Handle image update logic
        if 'image' in request.files:
            # Delete existing image if present
            if todo.image_path:
                existing_image_path = os.path.join(app.config['UPLOADED_IMAGES_DEST'], todo.image_path)
                if os.path.exists(existing_image_path):
                    os.remove(existing_image_path)
            
            # Save and update the new image
            new_image_filename = images.save(request.files['image'])
            todo.image_path = new_image_filename

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', todo=todo, current_user=User.query.filter_by(username=oidc.user_getfield('preferred_username')).first())


    
YOUR_DOMAIN = 'http://localhost:5000'

@app.route('/create-checkout-session', methods=['POST'])
@oidc.require_login
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Image upload service',
                },
                'unit_amount': 100,
            },
            'quantity': 1,
        }],
        mode='payment',
            success_url=YOUR_DOMAIN + '/success.html',
            cancel_url=YOUR_DOMAIN + '/cancel.html',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

@app.route('/success.html')
@oidc.require_login
def payment_success():
    user = User.query.filter_by(username=oidc.user_getfield('preferred_username')).first()
    if user:
        user.is_pro = True
        db.session.commit()
        flash('Payment successful!', 'payment_success')
    return redirect(url_for('index'))

@app.route('/cancel.html')
@oidc.require_login
def payment_unsuccessful():
    flash('Payment unsuccessful', 'payment_failure')
    return redirect(url_for('index'))

@app.route('/checkout.html')
@oidc.require_login
def checkout():
    return render_template('checkout.html')


# Consolidated GraphQL schema and queries
class UserType(graphene.ObjectType):
    id = graphene.Int()
    username = graphene.String()
    email = graphene.String()
    is_pro = graphene.String()

class ToDoType(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    description = graphene.String()
    timestamp = graphene.DateTime()
    image_path = graphene.String()




class Query(graphene.ObjectType):
    user = graphene.Field(UserType)
    todos = graphene.List(ToDoType)

    def resolve_user(self, info):
        if oidc.user_loggedin:
            user = User.query.filter_by(username=oidc.user_getfield('preferred_username')).first()
            # user = User.query.all()
            return user
        return None
    
    def resolve_todos(self, info):
        return ToDo.query.all()



schema = graphene.Schema(query=Query,types=[ToDoType,UserType])

# Define a custom view function for GraphQL protected by OIDC
class SecureGraphQLView(GraphQLView):
    # Override the dispatch_request method to enforce OIDC authentication
    @oidc.require_login
    def dispatch_request(self):
        return super(SecureGraphQLView, self).dispatch_request()

# Use the custom SecureGraphQLView for your /graphql endpoint
app.add_url_rule('/graphql', view_func=SecureGraphQLView.as_view('graphql', schema=schema, graphiql=True))


# Run the function to create tables when the script runs
if __name__ == '__main__':
    create_tables()
    app.run(debug=True)