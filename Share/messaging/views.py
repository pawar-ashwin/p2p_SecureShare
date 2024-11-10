from django.shortcuts import render
from utils.db import get_collection

# Access the `messages` collection from the `users` database
messages_collection = get_collection('users', 'messages')

def chat_room(request, username):
    user = request.user.username
    messages = list(messages_collection.find({
        '$or': [
            {'sender': user, 'receiver': username},
            {'sender': username, 'receiver': user}
        ]
    }).sort("timestamp"))

    return render(request, 'messaging/room.html', {
        'receiver': username,
        'messages': messages
    })
