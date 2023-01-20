import requests
from bs4 import BeautifulSoup
import re
from PIL import Image
import shutil 
import random
import os
import pandas as pd
import datetime
from math import trunc


# https://github.com/maria-antoniak/goodreads-scraper/blob/master/get_books.py

############## these are from above repo
def get_isbn(soup):
    try:
        isbn = re.findall(r'nisbn: [0-9]{10}' , str(soup))[0].split()[1]
        return isbn
    except:
        return "isbn not found"

def get_num_pages(soup):
    if soup.find('span', {'itemprop': 'numberOfPages'}):
        num_pages = soup.find('span', {'itemprop': 'numberOfPages'}).text.strip()
        return int(num_pages.split()[0])
    return ''

def get_year_first_published(soup):
    year_first_published = soup.find('nobr', attrs={'class':'greyText'})
    if year_first_published:
        year_first_published = year_first_published.string
        if year_first_published is not None:
            return re.search('([0-9]{3,4})', year_first_published).group(1)
        else:
            return ''
    else:
        return ''

def get_cover_image_uri(soup):
    series = soup.find('img', id='coverImage')
    if series:
        series_uri = series.get('src')
        return series_uri
    else:
        return ""

def get_genres(soup):
    genres = []
    for node in soup.find_all('div', {'class': 'left'}):
        current_genres = node.find_all('a', {'class': 'actionLinkLite bookPageGenreLink'})
        current_genre = ' > '.join([g.text for g in current_genres])
        if current_genre.strip():
            genres.append(current_genre)
    return genres
################## below is my code, but core elements from above

def get_average_rating(soup):
    average_rating = soup.find('span', {'itemprop': 'ratingValue'})
    if average_rating:
        return average_rating.text.strip()
    else:
        return ''

def get_number_ratings(soup):
    average_rating = soup.find('meta', {'itemprop': 'ratingCount'})
    if average_rating:
        return average_rating['content'].strip()
    else:
        return ''
def get_title(soup):
    title = soup.find('h1', {'id': 'bookTitle'})
    if title:
        return ' '.join(title.text.split())    
    else:
        return ''

###################

class Book:

    def __init__(self,book_ID_number):
        url = "https://www.goodreads.com/book/show/" + str(book_ID_number)
        page = requests.get(url)
        self.soup = BeautifulSoup(page.content, "html.parser")
        
        self.ID_number = book_ID_number
        self.isbn = get_isbn(self.soup)
        self.num_pages = get_num_pages(self.soup)
        self.year_first_published = get_year_first_published(self.soup)
        self.cover_image_url = get_cover_image_uri(self.soup)
        self.genres = get_genres(self.soup)
        self.average_rating = get_average_rating(self.soup)
        self.number_ratings = get_number_ratings(self.soup)
        self.title = get_title(self.soup)

    def check_exists(self):
        if self.isbn == "isbn not found":
            return False
        else:
            return True
    
    def to_dict(self):

        return {
            "ID_number" : self.ID_number,
            "isbn" : self.isbn,
            "num_pages" : self.num_pages,
            "year_first_published" : self.year_first_published,
            "cover_imgae_url" : self.cover_image_url,
            "genres" : self.genres,
            "average_rating" : self.average_rating,
            "number_ratings" : self.number_ratings,
            "title" : self.title
        }
        


def get_book_info(ID_number):
    # also saves image to file
    book = Book(ID_number)
    book_exists = book.check_exists()
    if book_exists and book.cover_image_url != "":
        print("Book {ID} is called <<{title}>> with average rating {rating}".format(ID = str(ID_number), title = book.title,rating = book.average_rating))
        res = requests.get(book.cover_image_url, stream = True)
        if res.status_code == 200:
            with open("images/"+str(ID_number)+".png",'wb') as f:
                shutil.copyfileobj(res.raw, f)
            print('\tImage {ID} sucessfully Downloaded'.format(ID = str(ID_number)))
            return book
        else:
            print('Image Couldn\'t be retrieved')
            return None
    else:
        print("Book {ID} not found".format(ID = str(ID_number)))
        #print(book.soup)
        return None


def get_n_unused_IDs(lower, upper, num_samples):
    # excludes images already found and present
    filenames = os.listdir("images/")
    # filenames are in the form "xxxx.png"
    exclude = []
    for filename in filenames:
        exclude.append(int(filename.split(".")[0]))
    chosen_IDs = []
    while len(chosen_IDs) < num_samples:
        ID = random.randint(lower, upper+1)
        if ID not in exclude:
            chosen_IDs.append(ID)
    return chosen_IDs

def get_one_unused_ID(lower, upper, exclude):
    i = 0
    while i < 100:
        ID = random.randint(lower, upper+1)
        if ID not in exclude:
            return ID
        i += 1
    return None

def get_n_books(n):

    filenames = os.listdir("images/")
    # filenames are in the form "xxxx.png"
    exclude = []
    for filename in filenames:
        exclude.append(int(filename.split(".")[0]))
    books = []
    n_checked = 0
    while(len(books)<n):
        #after ~3000 books I opened this from 3m to 60m as my range to get newer books
        ID_number = get_one_unused_ID(1,6000000,exclude)
        book_info = get_book_info(ID_number)
        if book_info is not None:
            books.append(book_info)
        n_checked +=1
    return books, n_checked

def add_to_csv(dataframe,filename):
    filepath = 'book_data/{f}.csv'.format(f = filename)
    if not os.path.exists(filepath):
        os.makedirs('book_data', exist_ok=True)  
        dataframe.to_csv(filepath)
    else:
        dataframe.to_csv(filepath, mode = "a", header = False)

def find_and_add_n_books_to_file(n_books, filename):    
    start_time = datetime.datetime.now()
    books, n_checked = get_n_books(n_books)
    dataframe = pd.DataFrame.from_records([book.to_dict() for book in books])
    add_to_csv(dataframe,filename)
    end_time = datetime.datetime.now()
    timespan = end_time - start_time
    print("Saved {n} books to file, which took {t}s".format(n = n_books, t = timespan.seconds))
    print("{checked} books were checked".format(checked = n_checked))


def main():
    n_books = 100 # number of books to find
    n_cycle = 20

    filename = "data"
    n_cycles = trunc(n_books/n_cycle)
    remainder = n_books % n_cycles
    
    if n_cycles >0:
        for i in range(n_cycles):
            find_and_add_n_books_to_file(n_cycle, filename)
            print("")
            print("Status: [{n_added}/{n_total}]".format(n_added = n_cycle*(i+1), n_total = n_books))
            print("")
    if remainder >0:
        find_and_add_n_books_to_file(remainder)
        print("")
        print("Status: [{n_added}/{n_total}]".format(n_added = n_books, n_total = n_books))
        print("")




if __name__ == "__main__":
    main()