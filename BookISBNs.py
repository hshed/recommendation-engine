import csv, time, re

class BookISBNs():
    def __init__(self, writeBooksToCSV = None):
        print 'Initializing'
        if writeBooksToCSV != None:
            self.retrieveBookCSV()
            self.writeBooksToCSV()
                
    def retrieveBookCSV(self):
        print'Reading BX-Books.csv'
        self._bookList = []
        with open('BX-Books.csv', 'r') as infile:
            reader = csv.reader(infile)
            reader.next()
            tempDataList = []  # ['user id', 'ISBN', 'rating']
            for row in reader:
                try:
                    tempDataList = str(row[0]).split(';"')
                    author = str(' '.join(re.findall(r'[a-zA-z0-9]+',tempDataList[2])))
                except IndexError: # done because of discrepancies in the csv file
                    tempDataList = str(' '.join(row)).split(';"')
                    author = str(' '.join(re.findall(r'[a-zA-z0-9]+',tempDataList[2])))
                isbn = ''.join(re.findall(r'[0-9]+',tempDataList[0]))
                book = str(' '.join(re.findall(r'[a-zA-z0-9]+',tempDataList[1])))
                
                self._bookList.append((isbn, book, author))
    
    def writeBooksToCSV(self):
        bookRow = []
        print 'Writing BookISBNs.csv'
        with open('BookISBNs.csv', mode='w') as outfile:
            writer = csv.writer(outfile, lineterminator='\n')
            writer.writerow(['ISBN', 'Book Title', 'Author'])
            for bookTuple in self._bookList:
                bookRow.append(bookTuple[0])
                bookRow.append(bookTuple[1])
                bookRow.append(bookTuple[2])
                writer.writerow(bookRow)
                bookRow = []
    
    def addNewBook(self, ISBN, BookTitle, Author):
        try:
            with open('BookISBNs.csv', mode='r') as infile:
                reader = csv.reader(infile)
                reader.next()
                tempDataList = []  # ['user id', 'ISBN', 'rating']
                for row in reader:
                    isbn = row[0]
                    book = row[1]
                    author = row[2]
                    tempDataList.append((isbn, book, author))
            tempDataList.insert(0,(ISBN, BookTitle, Author))
            bookRow = []
            with open('BookISBNs.csv', mode='w') as outfile:
                writer = csv.writer(outfile, lineterminator='\n')
                writer.writerow(['ISBN', 'Book Title', 'Author'])
                for bookTuple in tempDataList:
                    bookRow.append(bookTuple[0])
                    bookRow.append(bookTuple[1])
                    bookRow.append(bookTuple[2])
                    writer.writerow(bookRow)
                    bookRow = [] 
        except IOError:
            print 'ERROR!!!\n'
            print 'Is BookISBNs.csv open in your system? If NO, first run BookISBNs with any argument other than None type.\n'
        

if __name__ == '__main__':
    start = time.time()
    book = BookISBNs(1)
    book.addNewBook(1000001, 'A time travel', 'Hrishikesh Kumar')
    print time.time()-start, 'seconds'
                
            