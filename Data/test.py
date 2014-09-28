import Models
import MySQL

Con = MySQL.Connection(path = "../")

SchemeTable = Models.storage.Table("morph", fields = [
						Models.storage.Field("id_morph", {"int" : "11"}, "NOT NULL AUTO_INCREMENT"),
						Models.storage.Field("lemma_morph", {"varchar" : "100"}, "CHARACTER SET utf8 DEFAULT NULL"),
						Models.storage.Field("form_morph", {"varchar" :"100"}, "CHARACTER SET utf8 DEFAULT NULL")
					], keys = [
					"PRIMARY KEY (`id_morph`)"
					])

t = MySQL.Table(SchemeTable, Con)

print t.check(True)