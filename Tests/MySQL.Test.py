import sys
sys.path.append("..")
from Data import Models
from Data import MySQL

Con = MySQL.Connection()

SchemeTable = Models.storage.Table("morph", fields = [
						Models.storage.Field("id_morph", {"int" : "11"}, "NOT NULL AUTO_INCREMENT"),
						Models.storage.Field("lemma_morph", {"varchar" : "100"}, "CHARACTER SET utf8 DEFAULT NULL"),
						Models.storage.Field("form_morph", {"varchar" :"100"}, "CHARACTER SET utf8 DEFAULT NULL")
					], keys = [
					"PRIMARY KEY (`id_morph`)"
					])

t = MySQL.Table(SchemeTable, Con) 

#Just in case
if t.check():
	t.drop()

assert t.check() == False , "Table should not exist"

assert t.create(), "Table can't be created" # -> True

assert t.create() == False, "It shouldn't be possible to create twice a table"# -> False

assert t.insert({"lemma_morph" : "lascivus", "form_morph" : "lascivi"}) == 1, "Insert should work and return UID 1" # -> 1
assert t.insert({"lemma_morph" : "lascivus", "form_morph" : "lascivus"}) == 2, "Insert should work and return UID 2" # -> 2

assert u'lascivus' == t.select()[1]["form_morph"], "Select doesn't work properly"
assert u'lascivus' == t.select([Models.storage.Condition("form_morph", "lascivus")])[0]["form_morph"], "Select with condition not working properly"
assert u'lascivus' not in t.select([Models.storage.Condition("form_morph", "lascivus")], ["id_morph"])[0], "Select with condition and field limitationnot working properly"
assert  2 == int(t.select([Models.storage.Condition("form_morph", "lascivus")], ["id_morph"])[0]["id_morph"]), "Select with condition and field not working properly"

assert t.length() == 2, "Length of table should be two" # -> 2

assert t.delete([Models.storage.Condition("form_morph", "lascivus")])
assert t.length() == 1, "Length of table should be one" # -> 1

assert t.insert({"lemma_morph" : "lascivus", "form_morph" : "lascivi"}) == 3, "Insert should work and return UID 1" # -> 1
assert t.delete(limit = 50), "Delete should return true"
assert t.length() == 0, "Length of table should be 0" # -> 0

assert t.drop(), "Table should be dropped and return True" # -> True
assert t.insert({"lemma_morph" : "lascivus", "form_morph" : "lascivus"}) == False, "Insert shouldn't work for a dropped Table"# -> False
assert t.length() == 0, "Length of table should be 0 as it was deleted"# -> 0
assert t.drop() == False, "Table shouldn't be dropped again as it doesn't exist anymore"# -> False