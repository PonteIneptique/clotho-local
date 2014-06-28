import codecs
import json

with codecs.open("group-1.json") as f:
	data = json.load(f)
	f.close()

for term in data:
	print term +"\t"+str(len(data[term]))