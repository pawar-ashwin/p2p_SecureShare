from django.shortcuts import render
from utils.db import get_collection

# Access the `messages` collection from the `users` database
messages_collection = get_collection('users', 'messages')


def chat_room(request, username):
    # Get the current user
    user = request.user.username
    receiver = username  # Receiver is passed as a username

    # Query for messages between the current user and the receiver
    messages = list(messages_collection.find({
        '$or': [
            {'sender': user, 'receiver': receiver},
            {'sender': receiver, 'receiver': user}
        ]
    }).sort("timestamp"))

    # Render the template with the receiver's username and messages
    return render(request, 'messaging/room.html', {
        'receiver': receiver,
        'messages': messages
    })
