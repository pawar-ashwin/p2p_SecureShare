# views.py

import os
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from pymongo import MongoClient
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
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
                'password': new_password,  # Ideally, hash the password before storing
                'share_path' : ''
            })
            print("Insertion result:", result)
            messages.success(request, 'Signup successful! You can now log in.')
        except Exception as e:
            print("Error inserting into database:", e)
            messages.error(request, 'Failed to register. Please try again.')

        return redirect('home')  # Redirect to home page after successful signup
    
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
            print("Message set: Login successful!") 
            return redirect('user_dashboard')  # Redirect to the user dashboard after login
        else:
            messages.error(request, 'Invalid credentials! Please try again.')
            return redirect('home')  # Redirect back to the home page if login fails
    
    return redirect('home')  # Redirect to home page for GET request

def user_dashboard(request):
    if 'username' in request.session:
        username = request.session['username']
        user = users_collection.find_one({"username": username})

        return render(request, 'user.html', {'username': username, "share_path" : user['share_path']})
    else:
        return redirect('home')

# New profile view
def user_profile(request):
    if 'username' in request.session:
        username = request.session['username']
        
        # Fetch user details from the database
        user = users_collection.find_one({'username': username})
        
        if user:
            return render(request, 'profile.html', {
                'username': user['username'],
                'email': user['email'],
                'share_path': user.get('share_path', '')  # Default to an empty string if not set
            })
        else:
            messages.error(request, 'User not found.')
            return redirect('home')
    else:
        return redirect('home')
    
def update_share_path(request):
    if request.method == 'POST' and 'username' in request.session:
        username = request.session['username']
        new_share_path = request.POST.get('share_path')

        # Update share path in MongoDB if provided
        if new_share_path or new_share_path == "":
            try:
                result = users_collection.update_one(
                    {'username': username},
                    {'$set': {'share_path': new_share_path}}
                )

                if result.modified_count > 0:
                    return JsonResponse({'status': 'success', 'message': 'Share path updated successfully.'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'No changes made to the share path.'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Error updating share path: {str(e)}'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid share path provided.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized request.'})
    

def update_email(request):
    if request.method == 'POST' and 'username' in request.session:
        username = request.session['username']
        new_email = request.POST.get('email')

        # Check if a new email is provided
        if new_email:
            try:
                # Update the email in MongoDB
                result = users_collection.update_one(
                    {'username': username},
                    {'$set': {'email': new_email}}
                )
                
                if result.modified_count > 0:
                    return JsonResponse({'status': 'success', 'message': 'Email updated successfully.'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'No changes made to the email.'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Error updating email: {str(e)}'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid email provided.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized request.'})


def my_files(request):
    if 'username' in request.session:
        username = request.session['username']
        user = users_collection.find_one({"username": username})
        share_path = user.get('share_path', '')

        files = []
        if share_path and os.path.isdir(share_path):
            try:
                # List all files in the share path directory
                files = os.listdir(share_path)
            except Exception as e:
                messages.error(request, f"Error accessing files: {e}")
        else:
            messages.error(request, "Invalid or empty share path.")

        return render(request, 'userfiles.html', {'files': files, 'username': username, 'share_path': share_path})
    else:
        return redirect('home')

#signout API
def signout(request):
    # Clear the session to log the user out
    request.session.flush()

    # display logout message
    messages.success(request, 'You have successfully logged out.')

    # Redirect to the home page
    return redirect('home')