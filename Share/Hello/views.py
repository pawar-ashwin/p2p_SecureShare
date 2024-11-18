# views.py
import datetime
import os
import socket
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from pymongo import MongoClient
from django.contrib import messages
from django.http import JsonResponse
import random
from django.views.decorators.http import require_GET
from django.utils.html import escape
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import redirect
from django.contrib import messages
from bson import ObjectId

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

        # Render the dashboard with popular files
        return render(request, 'user.html', {
            'username': username,
            'share_path': user.get('share_path', ''),
            'popular_files': popular_files_list  # Pass the list of popular files
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
    
    # Iterate through all users who have a non-empty 'share_path'
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
                # Extend the all_files list with user file info
                all_files.extend([{"username": user["username"], "file": file} for file in user_files_from_db])
            except Exception as e:
                print(f"Error accessing files for user {user['username']}: {e}")
    
    # If there are any files, randomly select a few for display
    if all_files:
        random_files = random.sample(all_files, min(len(all_files), 12))  # Limit to 12 random files
    else:
        random_files = []

    return random_files

@require_GET
def search_files(request):
    if 'username' in request.session:
        username_main = request.session['username']
        user_main = users_collection.find_one({"username": username_main})
        share_path_main = user_main.get('share_path', '')
        
        # Get the search query from the GET parameters
        query = request.GET.get('query', '').strip()  # Get the search query
        query = escape(query)  # Escape to prevent XSS
        
        # List to store search results
        search_results = []

        # Iterate through all users' data to search their files
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
        
        # Render the search results in the template
        return render(request, 'user.html', {
            'search_results': search_results, 
            'query': query, 
            'username': username_main, 
            'share_path': share_path_main
        })
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
    if 'username' in request.session:
        username = request.session['username']
        requests_cursor = db.file_requests.find({'owner': username, 'status': 'Pending'})
        
        # Convert MongoDB cursor to list, renaming `_id` to `request_id`
        requests = [
            {
                "request_id": str(req["_id"]),  # Rename `_id` to `request_id`
                "requester": req["requester"],
                "filename": req["filename"]
            }
            for req in requests_cursor
        ]

        # Pass the modified requests list to the template
        return render(request, 'file_requests.html', {'requests': requests})
    else:
        return redirect('home')


from datetime import datetime

def chat_view(request, username):
    if 'username' not in request.session:
        return redirect('home')

    current_user = request.session['username']

    # Fetch messages between the current user and the selected user
    messages = list(db.chats.find({
        '$or': [
            {'sender': current_user, 'receiver': username},
            {'sender': username, 'receiver': current_user}
        ]
    }).sort('timestamp', -1))  # Sort messages by timestamp, newest first

    # Format messages for rendering
    for message in messages:
        message['timestamp'] = message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')

    return render(request, 'chat.html', {
        'messages': messages,
        'receiver': username,
        'current_user': current_user,
    })


@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        sender = request.session['username']
        receiver = data['receiver']
        message = data['message']

        # Insert the new message into the database
        db.chats.insert_one({
            'sender': sender,
            'receiver': receiver,
            'message': message,
            'timestamp': datetime.now()
        })

        return JsonResponse({'message': 'Message sent!'})


def fetch_messages(request):
    if 'username' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    current_user = request.session['username']
    receiver = request.GET.get('receiver')

    # Fetch messages between the current user and the selected user
    messages = list(db.chats.find({
        '$or': [
            {'sender': current_user, 'receiver': receiver},
            {'sender': receiver, 'receiver': current_user}
        ]
    }).sort('timestamp', -1))  # Sort messages by timestamp, newest first

    # Format messages for response
    formatted_messages = []
    for message in messages:
        formatted_messages.append({
            'sender': message['sender'],
            'receiver': message['receiver'],
            'message': message['message'],
            'timestamp': message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        })

    return JsonResponse({'messages': formatted_messages})


#signout API
def signout(request):
    # Clear the session to log the user out
    request.session.flush()

    # display logout message
    messages.success(request, 'You have successfully logged out.')

    # Redirect to the home page
    return redirect('home')

@csrf_exempt
@require_POST
def approve_request(request):
    data = json.loads(request.body)
    request_id = data.get('request_id')

    if request_id:
        db.file_requests.update_one(
            {'_id': ObjectId(request_id)},
            {'$set': {'status': 'Approved'}}
        )
        return JsonResponse({'status': 'success', 'message': 'Request approved.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request ID.'})

@csrf_exempt
@require_POST
def decline_request(request):
    data = json.loads(request.body)
    request_id = data.get('request_id')

    if request_id:
        db.file_requests.update_one(
            {'_id': ObjectId(request_id)},
            {'$set': {'status': 'Declined'}}
        )
        return JsonResponse({'status': 'success', 'message': 'Request declined.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request ID.'})

def my_requests(request):
    if 'username' in request.session:
        username = request.session['username']
        user = users_collection.find_one({"username": username})
        share_path_main = user.get('share_path', '')
        requests_cursor = db.file_requests.find({'requester': username})
        
        # Convert cursor to list and rename fields
        requests = [
            {
                "owner": req["owner"],
                "filename": req["filename"],
                "status": req["status"],
                "request_id": str(req["_id"])
            }
            for req in requests_cursor
        ]

        return render(request, 'my_requests.html', {'requests': requests, 'username': username, 'share_path': share_path_main})
    else:
        return redirect('home')


# Function to download the file
def download_file(request, owner, filename):
    if 'username' in request.session:
        requester = request.session['username']
        print(filename)
        print(owner)
        
        # Find the owner's share path from MongoDB
        owner = users_collection.find_one({"username": owner})
        if not owner:
            return JsonResponse({"status": "error", "message": "Owner not found."})
        
        # Owner's server details
        SERVER_HOST = "192.168.1.80"  # Replace with the owner's IP
        SERVER_PORT = 5001  # Port used by the owner's server

        try:
            # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            #     client_socket.connect((SERVER_HOST, SERVER_PORT))
            #     client_socket.send(filename.encode())

            #     # Check server response
            #     response = client_socket.recv(1024).decode()
            #     if response == "FOUND":
            #         # Save the file to the requester's system
            #         save_path = os.path.join("D:\P2P_Downloads", filename)
            #         with open(save_path, "wb") as f:
            #             while chunk := client_socket.recv(1024):
            #                 f.write(chunk)
            #         return JsonResponse({"status": "success", "message": f"File downloaded to {save_path}"})
            #     else:
            #         return JsonResponse({"status": "error", "message": "File not found on the owner's system."})

            # Create a socket object
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect to the server
            client_socket.connect((SERVER_HOST, SERVER_PORT))

            # Get the filename from the user
            file_to_request = filename

            # Send the filename to the server
            client_socket.send(file_to_request.encode())
            save_path = os.path.join("D:\\P2P_Downloads",filename)

            # Open the file to write the received content in binary mode
            # Open the file to write the received content in binary mode
            with open(save_path, "wb") as file:
                while True:
                    # Receive file data in chunks
                    data = client_socket.recv(1024)
                    if not data:
                        break  # If no data is received, the file transfer is complete
                    file.write(data)
                print(f"[*] File '{file_to_request}' received and saved as {file_to_request}'.")

            # Close the socket only after the file is fully received
            client_socket.close()
            
        except Exception as e:
            print(f"Error during file transfer: {e}")
            return JsonResponse({"status": "error", "message": "Error during file transfer."})
    else:
        return redirect('home')
