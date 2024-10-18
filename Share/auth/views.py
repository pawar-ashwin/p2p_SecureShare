import bcrypt
from django.http import JsonResponse
from .mongodb import users_collection

# SIGNUP API
def signup(request):
    if request.method == 'POST':
        data = request.POST
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Check if user already exists
        existing_user = users_collection.find_one({"username": username})
        if existing_user:
            return JsonResponse({'error': 'Username already exists'}, status=400)

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert user data into MongoDB
        users_collection.insert_one({
            "username": username,
            "email": email,
            "password": hashed_password
        })

        return JsonResponse({'message': 'User registered successfully'})

# LOGIN API
def login(request):
    if request.method == 'POST':
        data = request.POST
        username = data.get('username')
        password = data.get('password')

        # Find user by username
        user = users_collection.find_one({"username": username})
        if user:
            # Check password
            if bcrypt.checkpw(password.encode('utf-8'), user['password']):
                return JsonResponse({'message': 'Login successful'})
            else:
                return JsonResponse({'error': 'Invalid password'}, status=400)
        else:
            return JsonResponse({'error': 'User not found'}, status=404)

