import re, time, csv, cPickle as pickle
from math import sqrt
from scipy.cluster.vq import vq, kmeans, whiten
import numpy

class RatingsDictionary():
    def __init__(self):
        self._ratingsdictionary = {}
        self._listOfBooks = []
        self.extractRatings()
        
    def extractRatings(self):
        with open('BX-Book-Ratings.csv', 'r') as infile:
            reader = csv.reader(infile)
            reader.next()
            blist = []
            i = 0
            tempDataList = []  # ['user id', 'ISBN', 'rating']
            for row in reader:
                tempDataList = str(row[0]).split(';"')
                uid = int(tempDataList[0])
                isbn = ''.join(re.findall(r'[0-9]+',tempDataList[1]))
                try:
                    t = tempDataList[2]
                except IndexError:
                    t = -1
                # building the ratings dictionary
                if isbn!='' and t!=-1:
                    rating = int(''.join(re.findall(r'[0-9]+',tempDataList[2])))
                    blist.append(isbn)
                    if uid not in self._ratingsdictionary:
                        self._ratingsdictionary[uid] = {isbn:rating}
                    else: self._ratingsdictionary[uid].update({isbn:rating})
                i+=1
                #if i==10000:
                    #break
            self._listOfBooks = set(blist)
            print len(self._listOfBooks), 'length'
    
    def averageRatings(self, user):
        bookdict = self._ratingsdictionary[user]
        return sum([bookdict[book] for book in bookdict])/len(bookdict)
    
    def createUtilityMatrix(self):
        self._utilityMatrix = {}
        for user in self._ratingsdictionary:
            tempDict = self._ratingsdictionary[user]
            avg = sum([tempDict[book] for book in tempDict])/len(tempDict)
            for book in tempDict:
                bookDict = {book: (tempDict[book] - avg)}
                if user not in self._utilityMatrix:
                    self._utilityMatrix[user] = bookDict
                else: self._utilityMatrix[user].update(bookDict)
        return self._utilityMatrix
    
    def diffUtilityMatrix(self):
        self._dutilityMatrix = {}
        for user in self._ratingsdictionary:
            tempDict = self._ratingsdictionary[user]
            avg = sum([tempDict[book] for book in tempDict])/len(tempDict)
            for book in self._listOfBooks:
                if book not in tempDict:
                    bookDict = {book: 0}
                else:bookDict = {book: (tempDict[book] - avg)}
                if user not in self._dutilityMatrix:
                    self._dutilityMatrix[user] = bookDict
                else: self._dutilityMatrix[user].update(bookDict)
        return self._dutilityMatrix
    
    def sim_cosine(self, user1, user2):
        user1dict = self._utilityMatrix[user1]
        user2dict = self._utilityMatrix[user2]
        sumSq1 = sum([pow(user1dict[book],2) for book in user1dict])
        sumSq2 = sum([pow(user2dict[book],2) for book in user2dict])
        den = sqrt(sumSq1*sumSq2)
        product = 0
        for book in user1dict:
            if book in user2dict:
                product = product + user1dict[book]*user2dict[book]
        num = product
        
        if den == 0: return 0
        else: return float(num)/den
        
    def transformPrefs(self):
        infile = open('diffutilitydictionary.pkl', 'rb')
        prefs = pickle.load(infile)   
        infile.close()
        result={}
        for person in prefs:
            for item in prefs[person]:
                result.setdefault(item,{})
                # Flip item and person
                result[item][person]=prefs[person][item]
        f = open('transformedmatrix.pkl','wb')
        pickle.dump(result, f, pickle.HIGHEST_PROTOCOL)
        f.close()
        return result
        
    def getCosineRecommendations(self, user, n = 10):
        # get users most similar to user
        print 'generating recommendations'
        sim_scoreDict = {}
        user1dict = self._utilityMatrix[user]
        sumSq1 = sum([pow(user1dict[book],2) for book in user1dict])
        for other in self._utilityMatrix: 
            if other == user: continue
            user2dict = self._utilityMatrix[other]
            sumSq2 = sum([pow(user2dict[book],2) for book in user2dict])
            den = sqrt(sumSq1*sumSq2)
            product = 0
            for book in user1dict:
                if book in user2dict:
                    product = product + user1dict[book]*user2dict[book]
            num = product
            if den ==0: score = 0
            else: score = float(num)/den
            
            if score<=0: continue
            sim_scoreDict[other] = score
        
        topSimUsers = sim_scoreDict.keys()
        topSimUsers.sort(reverse = True)
        topSimUsers =  topSimUsers[:n]
        print 'len', len(topSimUsers)
        userAvgRating = self.averageRatings(user)
        print userAvgRating
        total = {}
        g = []
        for book in self._listOfBooks:
            avg = 0
            s = 0
            i = 0
            if book not in self._utilityMatrix[user]:
                for user1 in topSimUsers:
                    if book in self._utilityMatrix[user1]:
                        s += self._utilityMatrix[user1][book] 
                    i+=1
            
            if i==0: avg = 0
            else: avg = float(s)/i
            total[book] = avg + userAvgRating
            if book in self._ratingsdictionary[user]:
                g.append((self._ratingsdictionary[user][book], book))
        g.sort(reverse = True)
        print 'original', g[:n]
        recommendedBooks = [(rating, isbn) for isbn, rating in total.items()]
        recommendedBooks.sort(reverse=True)
        return recommendedBooks[:n]
    
    def matrix_factorization(self, steps=5000, alpha=0.0002, beta=0.02):
        infile = open('utilitydictionary.pkl', 'rb')
        x = pickle.load(infile)   # sparse matrix
        infile.close()
        r = []
        for user in x:
            r.append(x[user].values())
        R = numpy.array(r)
        N = len(R)
        M = len(R[0])
        K = 2
        sf = 0
        ind = 0
        for jh in range(0,N):
            for gh in range(0,M):
                yh = R[jh][gh]
                if yh !=0:
                    sf += R[jh][gh]
                    ind+=1
        fd = sqrt(float(sf)/ind)
        P = numpy.tile(fd, (N,K))
        Q = numpy.tile(fd, (M,K))
        Q = Q.T
        for step in xrange(steps):
            e = 0
            for i in xrange(len(R)):
                for j in xrange(len(R[i])):
                    if R[i][j] > 0:
                        eij = R[i][j] - numpy.dot(P[i,:],Q[:,j])
                        e = e + pow(eij, 2)
                        for k in xrange(K):
                            P[i][k] = P[i][k] + alpha * (2 * eij * Q[k][j] - beta * P[i][k])
                            Q[k][j] = Q[k][j] + alpha * (2 * eij * P[i][k] - beta * Q[k][j])
                            e = e + (beta/2) * ( pow(P[i][k],2) + pow(Q[k][j],2) )
            if e < 0.001:
                break
        return P, Q.T
    
    def generateSVDRecommendations(self):
        nP, nQ = self.matrix_factorization()
        print 'doing'
        nR = numpy.dot(nP, nQ.T)
        print 'done.'
        return nR
    
    def getClusteredMatrix(self):
        infile = open('transformedMatrix.pkl', 'rb')
        x = pickle.load(infile)   
        infile.close()
        r = []
        t = []
        for f in x:
            for g in x[f]:
                t.append(x[f][g])
            r = r + t
            t = []
        features = numpy.array(r)
        #whitened = whiten(features)
        km = kmeans(features, 100)
        f = open('clusteredMatrix.pkl','wb')
        pickle.dump(km, f, pickle.HIGHEST_PROTOCOL)
        f.close()
    
    def printRec(self):
        infile = open('prediction.pkl', 'rb')
        x = pickle.load(infile)   
        infile.close()
        nR = x
        infile = open('utilitydictionary.pkl', 'rb')
        x = pickle.load(infile)   
        infile.close()
        r = []

        for user in x:
            r.append(x[user].values())
        R = numpy.array(r)
        l = nR[10]
        ll = numpy.array(l).reshape(-1).tolist()
        q = R[10]
        lq = numpy.array(q).reshape(-1).tolist()
        print 'nR', ll
        print 'R', lq
    
    def sim_pearson(self, ratingsDictionary,user1,user2):
        # Get the list of mutually rated items
        similarityDict={}
        for item in ratingsDictionary[user1]:
            if item in ratingsDictionary[user2]: similarityDict[item]=1
        # Find the number of elements
        n=len(similarityDict)
        # if they are no ratings in common, return 0
        if n==0: return 0
        # Add up all the preferences
        sum1=sum([ratingsDictionary[user1][item] for item in similarityDict])
        #print 'sum1', sum1
        sum2=sum([ratingsDictionary[user2][item] for item in similarityDict])
        #print 'sum2', sum2
        # Sum up the squares
        sum1Sq=sum([pow(ratingsDictionary[user1][item],2) for item in similarityDict])
        #print 'sum1Sq', sum1Sq
        sum2Sq=sum([pow(ratingsDictionary[user2][item],2) for item in similarityDict])
        #print 'sum2Sq', sum2Sq
        # Sum up the products
        pSum=sum([ratingsDictionary[user1][item]*ratingsDictionary[user2][item] for item in similarityDict])
        #print 'psum', pSum
        # Calculate Pearson score
        num=(n*pSum)-(sum1*sum2)
        #print 'num', num
        den=(n-1)*sqrt((sum1Sq-pow(sum1,2))*(sum2Sq-pow(sum2,2)))
        #print 'den', den
        if den==0: return 0
        r=float(num)/den
        return r

    def topCosineMatches(self, prefs,person,n = 5,similarity = sim_cosine):
        # Sort the list so the highest scores appear at the top
        scores = []
        for other in prefs:
            if other!=person:
                #e = similarity(prefs, person, other)
                q = similarity(person, other)
                if q != 0:
                    scores.append((q, other))
        scores.sort( )
        scores.reverse( )
        return scores[0:n]
    
    def topPearsonMatches(self, prefs,person,n = 5,similarity = sim_pearson):
        # Sort the list so the highest scores appear at the top
        scores = []
        for other in prefs:
            if other!=person:
                q = similarity(prefs, person, other)
                if q != 0:
                    scores.append((q, other))
        scores.sort( )
        scores.reverse( )
        return scores[0:n]
    
    def getPearsonRecommendations(self, prefs, user, similarity = sim_pearson, n = 5):
        totals={}
        simSums={}
        for other in prefs:
            # don't compare me to myself
            if other==user: continue
            sim=similarity(prefs,user,other)
            
            # ignore scores of zero or lower
            if sim<=0: continue
            for item in prefs[other]:
                # only score books I haven't rated yet
                if item not in prefs[user] or prefs[user][item]==0:
                    # Similarity * Score
                    totals.setdefault(item,0)
                    totals[item]+=prefs[other][item]*sim
                    # Sum of similarities
                    simSums.setdefault(item,0)
                    simSums[item]+=sim
            # Create the normalized list
            rankings=[(total/simSums[item],item) for item,total in totals.items()]
            # Return the sorted list
            rankings.sort( )
            rankings.reverse( )
            return rankings[:n]
    
    def getRecommendations(self, prefs, user, similarity = sim_cosine, n = 5):
        totals={}
        simSums={}
        for other in prefs:
            # don't compare me to myself
            if other==user: continue
            sim=similarity(user,other)
            
            # ignore scores of zero or lower
            if sim<=0: continue
            for item in prefs[other]:
                # only score books I haven't seen yet
                if item not in prefs[user] or prefs[user][item]==0:
                    # Similarity * Score
                    totals.setdefault(item,0)
                    totals[item]+=prefs[other][item]*sim
                    # Sum of similarities
                    simSums.setdefault(item,0)
                    simSums[item]+=sim
            # Create the normalized list
            rankings=[(total/simSums[item],item) for item,total in totals.items()]
            # Return the sorted list
            rankings.sort( )
            rankings.reverse( )
            return rankings[:1000]
        
    
    
if __name__ == '__main__':
    start = time.time()
    rd = RatingsDictionary()
    #rdict = rd._ratingsdictionary
    #print 'similarity', rd.sim_pearson(rdict, 276747, 11676)
    #print 'Top Matches:', rd.topPearsonMatches(rdict, 276747, 10, rd.sim_pearson)
    #print rd.getPearsonRecommendations(rdict, 11676, rd.sim_pearson, 100)
    rd.createUtilityMatrix()
    #print rd.sim_cosine(276747, 11676)
    #print rd.averageRatings(276747)
    #print 'Top Matches', rd.topCosineMatches(rdict, 276747, 10, rd.sim_cosine)
    print rd.getCosineRecommendations(11676, 100)
    '''util = rd.diffUtilityMatrix()
    print 'Saving the dictionary into .pkl file...'
    f = open('diffutilitydictionary.pkl','wb')
    pickle.dump(util, f, pickle.HIGHEST_PROTOCOL)
    f.close()'''
    #rd.transformPrefs()
    #print 'Saved as ratingsdictionary.pkl'
    '''ut = rd.generateRecommendations()
    f = open('prediction.pkl','wb')
    pickle.dump(ut, f, pickle.HIGHEST_PROTOCOL)
    f.close()'''
    #print rd.averageRatings(276747)
    #rd.printRec()
    #rd.getClusteredMatrix()
    '''infile = open('clusteredMatrix.pkl', 'rb')
    x = pickle.load(infile)   
    infile.close()
    print len(x)
    print x
    '''
    print 'took', time.time() - start, 'seconds'
