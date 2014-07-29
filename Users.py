import csv, time, re

class Users():
    def __init__(self, writeUsersToCSV = None):
        print 'Initializing'
        if writeUsersToCSV!=None:
            self.retrieveUserCSV()
            self.writeUsersToCSV()
    
    def retrieveUserCSV(self):
        self._usersList = []
        with open('BX-Users.csv', 'r') as infile:
            reader = csv.reader(infile)
            reader.next()
            for row in reader:
                tempDataList = ''.join(row)
                tempData = str(tempDataList).split(';"')
                userID = int(tempData[0])
                d = re.findall(r'[a-zA-Z]+',tempData[1])
                e = [j for j in d if j!='n' and j!='a'] # some locations have value n/a
                try:
                    age = re.findall(r'[0-9]+',tempData[2])[0]
                    location = ' '.join(e)
                except IndexError:   # catch those with NULL age
                    age = None
                    location = ' '.join(e[:-1])
                self._usersList.append((userID, age, location))
                
    def writeUsersToCSV(self):
        userRow = []
        with open('Users.csv', mode='w') as outfile:
            writer = csv.writer(outfile, lineterminator='\n')
            writer.writerow(['User ID', 'Age', 'Location'])
            for userTuple in self._usersList:
                userRow.append(userTuple[0])
                userRow.append(userTuple[1])
                userRow.append(userTuple[2])
                writer.writerow(userRow)
                userRow = []
    
    def addNewUser(self, age = None, location = None):
        try:
            with open('Users.csv', mode='r') as infile:
                reader = csv.reader(infile)
                reader.next()
                tempDataList = []  # ['user id', 'ISBN', 'rating']
                for row in reader:
                    userId = row[0]
                    AGE = row[1]
                    LOCATION = row[2]
                    tempDataList.append((userId, AGE, LOCATION))
                tempDataList.insert(len(tempDataList),(str(int(userId) + 1), age, location))
            userRow = []
            with open('Users.csv', mode='w') as outfile:
                writer = csv.writer(outfile, lineterminator='\n')
                writer.writerow(['User ID', 'Age', 'Location'])
                for userTuple in tempDataList:
                    userRow.append(userTuple[0])
                    userRow.append(userTuple[1])
                    userRow.append(userTuple[2])
                    writer.writerow(userRow)
                    userRow = []
        except IOError:
            print 'ERROR!!!\n'
            print 'Is Users.csv open in your system? If NO, first run Users with any argument other than None type.\n'

if __name__ == '__main__':
    start = time.time()
    user = Users()
    user.addNewUser(21, 'Patna')
    print time.time()-start, 'seconds'