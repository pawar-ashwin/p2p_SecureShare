from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from pymongo import MongoClient
from django.contrib import messages

# MongoDB connection setup
mongo_uri = "mongodb+srv://sowmyamutya20:hyB1Mq5ODLBssNDl@logincredentials.oalqb.mongodb.net/?retryWrites=true&w=majority&appName=loginCredentials"
client = MongoClient(mongo_uri, ssl=True)

try:
    client.admin.command('ping')
    print("Connection successful")
except Exception as e:
    print("Connection failed:", e)

# Define the users_collection
db = client['users']  
users_collection = db['loginCredentials']  

class HomePage(TemplateView):
    template_name = 'home.html'

class AboutPage(TemplateView):
    template_name = 'about.html'

def signup(request):
    if request.method == 'POST':
        new_email = request.POST.get('newEmail')
        new_username = request.POST.get('newUsername')
        new_password = request.POST.get('newPassword')
        
        # Check if data is being captured correctly
        print(f"Email: {new_email}, Username: {new_username}, Password: {new_password}")
        
        # Check if the user already exists
        if users_collection.find_one({'username': new_username}):
            messages.error(request, 'Username already exists!')
            return redirect('home')  # Redirect back to home page (signup modal will still be there)
        
        # Insert new user into the database
        try:
            result = users_collection.insert_one({
                'email': new_email,
                'username': new_username,
                'password': new_password  # Ideally, hash the password before storing
            })
            print("Insertion result:", result)
            messages.success(request, 'Signup successful! You can now log in.')
        except Exception as e:
            print("Error inserting into database:", e)
            messages.error(request, 'Failed to register. Please try again.')

        return redirect('home')  # Redirect to home page after successful signup
    
    # Remove the `render('signup.html')` part
    return redirect('home')  # Redirect to home page for GET request



def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if the user exists in the database
        user = users_collection.find_one({'username': username, 'password': password})
        
        if user:
            request.session['username'] = username  # Store the username in the session
            messages.success(request, 'Login successful!')
            return redirect('user_dashboard')  # Redirect to the user dashboard after login
        else:
            messages.error(request, 'Invalid credentials! Please try again.')
            return redirect('home')  # Redirect back to the home page if login fails
    
    # Remove the `render('login.html')` part
    return redirect('home')  # Redirect to home page for GET request

def user_dashboard(request):
    if 'username' in request.session:
        username = request.session['username']
        return render(request, 'user.html', {'username': username})
    else:
        return redirect('home')