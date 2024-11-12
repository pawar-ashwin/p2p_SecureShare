# views.py
import datetime
import os
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from pymongo import MongoClient
from django.contrib import messages
from django.http import JsonResponse
import random
from django.views.decorators.http import require_GET
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
import json
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
                'share_path' : '',
                'My_files':[]
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

# def user_dashboard(request):
#     if 'username' in request.session:
#         username = request.session['username']
#         user = users_collection.find_one({"username": username})

#         return render(request, 'user.html', {'username': username, "share_path" : user['share_path']})
#     else:
#         return redirect('home')

def user_dashboard(request):
    if 'username' in request.session:
        username = request.session['username']
        user = users_collection.find_one({"username": username})
        # Get popular files from other users' shared paths
        popular_files_list = popular_files()

        # Render the dashboard with popular files only
        return render(request, 'user.html', {
            'username': username,
            "share_path" : user['share_path'],
            "popular_files": popular_files_list
        })
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

        # Initialize an empty list to store files from the directory
        files = []

        if share_path and os.path.isdir(share_path):
            try:
                # List all files in the share path directory
                current_files = set(os.listdir(share_path))

                # Get the files already stored in the database
                stored_files = set(user.get('My_files', []))

                # Identify new files by subtracting stored files from current files
                new_files = current_files - stored_files

                # If new files are found, update the user's My_files in MongoDB
                if new_files:
                    # Combine the existing and new files without duplicates
                    updated_files_list = list(stored_files | new_files)
                    users_collection.update_one(
                        {"username": username},
                        {"$set": {"My_files": updated_files_list}}
                    )
                else:
                    # If no new files, keep the existing stored files
                    updated_files_list = list(stored_files)

                # Use the updated or existing My_files list to render the view
                files = updated_files_list

            except Exception as e:
                messages.error(request, f"Error accessing files: {e}")
        else:
            messages.error(request, "Invalid or empty share path.")

        return render(request, 'userfiles.html', {'files': files, 'username': username, 'share_path': share_path})
    else:
        return redirect('home')



def popular_files():
    """
    Fetches random files from all users' share paths for the 'Popular Files on the Network' section.
    """
    all_files = []
    all_users = users_collection.find({"share_path": {"$ne": ""}})  # Users with non-empty share paths

    # for i in all_users:
    #     print(i['username'])
    #     print()
    #     print(i['My_files'])
    #     print("=====================================================")


    for user in all_users:
        user_files_from_db = user.get("My_files", [])
        print(user_files_from_db)
        
        # Verify the path exists and is a directory
        if user_files_from_db:
            try:
                # Get all files in the user's share path
                user_files = user_files_from_db
                all_files.extend([{"username": user["username"], "file": file} for file in user_files])
            except Exception as e:
                print(f"Error accessing files in {user_files_from_db}: {e}")
    
    # Randomly select up to 10 files for display
    random_files = random.sample(all_files, min(len(all_files), 12))
    return random_files

@require_GET
def search_files(request):
    if 'username' in request.session:
        username_main = request.session['username']
        user_main = users_collection.find_one({"username": username_main})
        share_path_main = user_main.get('share_path', '')
        query = request.GET.get('query', '').strip()  # Get the search query
        query = escape(query)  # Escape to prevent XSS

        # Search across all users' shared files
        search_results = []
        for user in users_collection.find({}):
            username = user['username']
            share_path = user.get('share_path', '')
            files_from_db = user.get('My_files', [])
            # print("I AM COMING HERE!");
            if files_from_db:
                try:
                    # Filter files that match the query
                    files = [f for f in files_from_db if query.lower() in f.lower()]
                    for file_name in files:
                        search_results.append({'username': username, 'file': file_name, "share_path" : share_path})
                except Exception as e:
                    print(f"Error accessing files for {username}: {e}")
                    continue

        return render(request, 'user.html', {'search_results': search_results, 'query': query, 'username': username_main, 'share_path': share_path_main})
    else:
        return redirect('home')
    

@csrf_exempt
def request_file(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        requester = request.session['username']
        owner = data['owner']
        filename = data['filename']

        db.file_requests.insert_one({
            'requester': requester,
            'owner': owner,
            'filename': filename,
            'status': 'Pending'
        })

        return JsonResponse({'message': 'File request sent successfully!'})

def file_requests(request):
    username = request.session['username']
    requests = db.file_requests.find({'owner': username, 'status': 'Pending'})

    return render(request, 'file_requests.html', {'requests': requests})

def chat_view(request, username):
    current_user = request.session['username']
    messages = db.chats.find({
        '$or': [
            {'sender': current_user, 'receiver': username},
            {'sender': username, 'receiver': current_user}
        ]
    })

    return render(request, 'chat.html', {'messages': messages, 'receiver': username})

@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        sender = request.session['username']
        receiver = data['receiver']
        message = data['message']

        db.chats.insert_one({
            'sender': sender,
            'receiver': receiver,
            'message': message,
            'timestamp': datetime.now()
        })

        return JsonResponse({'message': 'Message sent!'})


#signout API
def signout(request):
    # Clear the session to log the user out
    request.session.flush()

    # display logout message
    messages.success(request, 'You have successfully logged out.')

    # Redirect to the home page
    return redirect('home')