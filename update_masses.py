import urllib.request
import json

BASE_URL = "https://nssdc.gsfc.nasa.gov"
TABLE_URL = "https://nssdc.gsfc.nasa.gov/nmc/spacecraftSearch.do"

def isChiffre(a):
	return a >= '0' and a <= '9'

def isNombre(mot):
	for a in mot:
		if not isChiffre(a):
			return False
	return True

def findNextLi(currentIndex, page): # currentIndex: index du dernier <td>
	try:
		index = page.index("<li>", currentIndex)
		return index
	except ValueError:
		return -1

def findNextLiCloser(currentIndex, page):
	try:
		index = page.index("</li>", currentIndex)
		return index
	except ValueError:
		return -1 #Normalement l'erreur ne devrait pas se produire.

def findNextTd(currentIndex, page): # currentIndex: index du dernier <td>
	try:
		index = page.index("<td>", currentIndex)
		return index
	except ValueError:
		return -1

def findNextTdCloser(currentIndex, page):
	try:
		index = page.index("</td>", currentIndex)
		return index
	except ValueError:
		return -1 #Normalement l'erreur ne devrait pas se produire.

def getLinkNameAndURL(currentIndex, page):
	urlIndex = page.index('"', currentIndex)+1
	ret_url = BASE_URL+page[urlIndex:page.index('"', urlIndex+1)]
	name_index = page.index('>', urlIndex)+1
	ret_name = page[name_index:page.index('<', name_index+1)]
	return ret_name, ret_url

def getNextTdContent(currentIndex, page):
	nextTd = findNextTd(currentIndex, page)+4
	nextCloser = findNextTdCloser(nextTd, page)

	if(nextTd == 3 or nextCloser == -1):
		return "", nextTd+1

	return page[nextTd:nextCloser], nextTd+1

def getMassInPage(sub_page):
	try:
		sub_index_begin = sub_page.index("Mass:</strong>")+22
		sub_index_end = sub_page.index("kg", sub_index_begin)-8
		return sub_page[sub_index_begin:sub_index_end]
	except ValueError:
		return "0"

def getUNameInPage(sub_page):
	try:
		start_index = sub_page.index("Alternate Names")
		while True:
			nextLi = findNextLi(start_index, sub_page)
			nextCloser = findNextLiCloser(nextLi, sub_page)
			start_index = nextCloser

			if nextLi == -1 or nextCloser == -1:
				return '0'
			if not isNombre(sub_page[nextLi+4:nextCloser]):
				continue

			return sub_page[nextLi+4:nextCloser] 

	except ValueError:
		return "0"

def getUNameAndMass(sub_url):
	try:
		sub_httpresponse = urllib.request.urlopen(sub_url)
	except (urllib.error.URLError, TimeoutError):
		print("exception")
		return "0", "0"
	sub_page = str(sub_httpresponse.read())
	return getUNameInPage(sub_page), getMassInPage(sub_page)

httpresponse = urllib.request.urlopen("https://nssdc.gsfc.nasa.gov/nmc/spacecraftSearch.do")
page = str(httpresponse.read())

index = 0 #page.index("<td>")

content = "a"
i = 0

toWrite = ""

while content:
	i += 1
	print(i)
	content, index = getNextTdContent(index, page)
	if not content:
		break
	name, url = getLinkNameAndURL(index, page)
	uname, mass = getUNameAndMass(url)

	if uname == "0" or mass == "0": # En cas d'erreur sur le lien, ou si le nom n'a pas été spécifié.
		if(url == ""):
			print("Empty URL, finishing.")
			break
		content, index = getNextTdContent(index, page)
		if not content:
			break

		content, index = getNextTdContent(index, page)
		if not content:
			break
		continue
	toWrite += uname+" "+mass+" "
	
	content, index = getNextTdContent(index, page)
	if not content:
		break
	toWrite += content+" "
	content, index = getNextTdContent(index, page)
	if not content:
		break

	toWrite += content+"\n"

fichier = open("masses.txt", "w")
fichier.write(toWrite)
fichier.close()




#
#	Update JSON
#

def parseName(name):
	return name[2:4]+name[5:]

fichierMasses = open('masses.txt')

masses = dict()

for ligne in fichierMasses:
	mots = ligne.split(" ")
	masses[parseName(mots[2])] = str(int(float(mots[1])))+" kg"

fichierMasses.close()



fichier = open('TLE.json', 'r')

l = json.load(fichier)

for tle in l:
	if tle['INTLDES'] in masses:
		tle['OBJECT_MASS'] = masses[tle['INTLDES']]
	else:
		tle['OBJECT_MASS'] = 'Unknown'

fichier.close()

fichier = open('TLE.json', 'w')
json.dump(l, fichier)
fichier.close()