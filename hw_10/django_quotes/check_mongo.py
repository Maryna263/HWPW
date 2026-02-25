from pymongo import MongoClient

client = MongoClient("mongodb+srv://29072025pmv_db_user:bZuhdb6b0rvANCAq@cluster0.ozprlhm.mongodb.net/?retryWrites=true&w=majority")
db = client.hw_8 

print("\n--- Приклад одного автора ---")
author = db.authors.find_one()
print(author)

print("\n--- Приклад однієї цитати ---")
quote = db.quotes.find_one()
print(quote)