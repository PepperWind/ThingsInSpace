import json

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