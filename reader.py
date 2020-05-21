import fitz

"""open book and return pages for the GUI"""
def open_book(file_name):
    return fitz.open(file_name)

def get_page(page):
    return page.getPixmap()
    