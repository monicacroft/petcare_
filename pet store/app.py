from flask import Flask, render_template,request,flash,redirect
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import UserMixin
import requests
import json

app = Flask(__name__)
app.secret_key = '17171717'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///petcare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()

class Pet(db.Model): #ბაზისთვის შექმნილი ცხოველის კლასი, რა ექნება  ბაზაში:აიდი , სახელი,სქესი,აღწერა.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    description = db.Column(db.String(255))
    



    @staticmethod
    def get_all(): #ამოაქვს ბაზიდან ყველა ჩაწერილი ცხოველი. AVAILABLE PETS-ში რაც ჩანს 
        return Pet.query.all()
    
    def get_by_id(pet_id):#იღებს ბაზიდან ცხოველს აიდის მიხედვით რომელიც  გამოიყენება  კონკრეტული ცხ. დეტალების გამოსატანად

        return Pet.query.get(pet_id) 



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


def initialize_db(app):
    db.init_app(app)
    with app.app_context():
        if not os.path.exists('petcare.db'):
            db.create_all()
            print("Database created successfully!")
def user_is_registered(username):
    user = User.query.filter_by(username=username).first()
    return user is not None

@app.route('/')#პირველი გვერდი
def home():
    return render_template('home.html')

@app.route('/store', methods=['GET', 'POST'])#petstore
def pet_store():
    


    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        description = request.form['description']
        
        pet = Pet(name=name, gender=gender, description=description)
        db.session.add(pet)
        db.session.commit()
        flash('Pet added successfully!', 'success')
        return redirect('/store')

    pets = Pet.get_all()
    return render_template('pet_store.html', pets=pets)



@app.route('/detail_pet/<int:pet_id>')#დეტალურად რასაც გამოაქვს ცხოველზე ინფორმაცია
def detail_pet(pet_id):
    pet = Pet.get_by_id(pet_id)
    return render_template('detail_pet.html', pet=pet)

@app.route('/contract/<int:pet_id>')
def contract(pet_id):
   
    pet = Pet.query.get(pet_id)

    return render_template('contract.html', pet=pet)

@app.route('/confirm_adopt/<int:pet_id>', methods=['POST']) #ცხოველის აყვანაზე რაც ხდება ეს აკეთებს
def confirm_adopt(pet_id):
    answer = request.form['answer']

    if answer == 'yes':
        
        pet = Pet.query.get(pet_id)

        if pet:
            flash('Congratulations! You have adopted the pet.', 'success')
        else:
            flash('Pet not found.', 'error')
    else:
        flash('Adoption process canceled.', 'info')

    return redirect('/store')

@app.route('/donate', methods=['GET', 'POST'])#დონაცია
def donate():
    if request.method == 'POST':
        donation_amount = request.form['donation_amount']
       
        return render_template('donate.html', donation_amount=donation_amount)
    
    return render_template('donate.html')

@app.route('/register', methods=['GET', 'POST'])#რეგისტრაცია
def registration():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username is already taken.', 'error')
            return redirect('/register')

    
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect('/store')

    return render_template('registration.html')
    

@app.route('/delete_pet/<int:pet_id>', methods=['POST'])#ცხოველის წაშლა აიდის მიხედვით
def delete_pet(pet_id):
    pet = Pet.query.get(pet_id)
    if pet:
        db.session.delete(pet)
        db.session.commit()
        flash('Pet deleted successfully!', 'success')
    else:
        flash('Pet not found.', 'error')
    return redirect('/store')


@app.route('/pets', methods=['GET', 'POST'])
def get_pets():
   
    response = requests.get('https://petstore.swagger.io/v2/pet/findByStatus?status=available')

    if response.status_code == 200:
       
        json_data = json.loads(response.text)

        return render_template('pets.html', pets=json_data)
    else:
        return "Error: Failed to retrieve data from the API"




if __name__ == '__main__':  
    initialize_db(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
