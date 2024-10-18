from pymongo import MongoClient

# MongoDB connection
client = MongoClient('mongodb+srv://Ashwin:OPX0TdrZPdov0OlG@cluster0.seexzfd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')  # Update with your MongoDB URI
db = client['P2P-FS']  # Your MongoDB database name
users_collection = db['users']  # Collection for user data
