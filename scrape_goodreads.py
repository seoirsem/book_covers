import requests
from bs4 import BeautifulSoup
import re
from PIL import Image
import shutil 
import random
import os


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
        return re.search('([0-9]{3,4})', year_first_published).group(1)
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
        return None


def define_range(lower, upper, num_samples):
    # excludes images already found and present
    filenames = os.listdir("images/")
    # filenames are in the form "xxxx.png"
    exclude = []
    for filename in filenames:
        exclude.append(int(filename.split(".")[0]))
    ID_range = range(lower, upper+1)
    chosen_IDs = []
    while len(chosen_IDs) < num_samples:
        ID = random.randint(lower, upper+1)
        if ID not in exclude:
            chosen_IDs.append(ID)
    return chosen_IDs

book_dict = {}
ID_numbers = define_range(1,300000,15)
for ID_number in ID_numbers:
    book_info = get_book_info(ID_number)
    if book_info is not None:
        book_dict[ID_number] = book_info


print(book_dict)