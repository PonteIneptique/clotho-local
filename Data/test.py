import Models
import MySQL

Con = MySQL.Connection(path = "../")

SchemeTable = Models.storage.Table("testing", [
		Models.Field("id_test", {"int" : "11"}, "AUTO_INCREMENT"),
		Models.Field("text_test", {"varchar" : "100"})
	], ["PRIMARY KEY id_test"])

print SchemeTable.fields
t = MySQL.Table(SchemeTable)
print t
print t.fields[0].toString()