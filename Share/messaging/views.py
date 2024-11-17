from django.shortcuts import render
from utils.db import get_collection

# Access the `messages` collection from the `users` database
messages_collection = get_collection('users', 'messages')

def chat_room(request, username):
    user = request.user.username # The logged-in user
    receiver = username  # The receiver is passed as a parameter

    # Query for messages between the current user and the receiver
    messages = list(messages_collection.find({
        '$or': [
            {'sender': user, 'receiver': receiver},
            {'sender': receiver, 'receiver': user}
        ]
    }).sort("timestamp"))  # Sort messages by timestamp (ascending)

    # Render the template with the receiver's username and messages
    return render(request, 'messaging/room.html', {
        'receiver': receiver,
        'messages': messages
    })
