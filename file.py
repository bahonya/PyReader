import json 
from drive import Drive
from os import path

#drive = Drive()
#drive.auth()
#books = drive.list_books()
#for book in books:
#    book['progress'] = 0
    
def write_progress(books):
    with open("progress.json", "w") as write_file:
        json.dump(books, write_file, ensure_ascii=False)
        
def read_progress():
    with open("progress.json", "r") as read_file:
        return json.load(read_file)
    
def progress_exists():
    return path.exists('progress.json')
    
print(progress_exists())    
#books = read_progress()
#print(books[0]['progress'])