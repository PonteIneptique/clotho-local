#Workflow of Clotho Pipeline

This documents aims to explain the structure required by the pipeline and provides generic informations about the steps. If you aim to integrate one of your export function or a new discovery service, you might want to look there.

##Query corpus initialization

This steps defines a list of lemma for which Clotho will search. The class called by our command line tool should have a `search(self, query: str)` function. The query should return a list of `Data.Models.lang.Lemma` Objects (which basic integration can be seen in `Data.Models.lang.Lemma`)

```python
#Example
LemmaSearchInstance = Linguistic.Perseus.MySQL.Lemma()
LemmaSearchInstance.search("habeo") 
# -> List(Data.Models.lang.Lemma(uid = None, "habeo", definition = None))
```

##Search for occurences

This steps will use a list of lemma to search for each occurences it can find. The class here should have a function search which takes a `Lemma` object as source : `search(self, lemma: Data.Models.lang.Lemma)`. It should returns a list of `Data.Models.documents.Occurence` object

```python
#Example
OccurenceSearchInstance = Linguistic.Perseus.MySQL.Occurence()
OccurenceSearchInstance.search(Data.Models.lang.Lemma(uid = None, "habeo", definition = None))
# -> List(Data.Models.documents.Occurence)
```

##Filtering occurences
**TODO**

```python
#Example
# -> Data.Models.documents.Occurence()
```

##Contextualisation of occurences
This **optionnal step** aims to provide services which will take an Occurence() object and strip it texts to what the user needs. For example, this could reduce the occurence to a grammatical Sentence or to a n-word window. This class should have a strip() function which takes a Lemma() and an Occurence instance as parameter and returns an Occurence

The Contextualiser itself can take a n parameters in some case as well as a FormFinder class or Object (Linguistic.Lemma.form.Finder)

```python
#2-Word window example
Contextualiser = Linguistic.Contextualiser.WordsWindow(n = 2, FormFinderClass = Services.Perseus.MySQL.LatinFormFinder)
Contextualiser.strip(Data.Models.documents.Occurence(), Data.Models.lang.Lemma(), Linguistic.Lemma.form.Finder)
# -> Data.Models.documents.Occurence()
```

##Lemmatisation of occurences
This step aims to transform an occurence Text to a list of Forms, with the same order than in the text. The class object should have a `parse` function which takes a `Data.Models.documents.Occurence` parameter. It should returns a list of `Data.Models.lang.Form`

```python
#Example
Lemmatizer = Linguistic.Perseus.MySQL.Lemmatizer()
Lemmatizer.parse(Data.Models.documents.Occurence())
# -> List(Data.Models.lang.Form())
```

##Grouping Occurence
An `OccurenceSet` instance is an object which takes two parameters : a Lemma and a list of Occurences. This means to regroup data together so it's treated as a group. 

```python
#Example
OccurenceSet = Data.Models.documents.OccurenceSet(lemma = Data.Models.lang.Lemma(...), occurences = [Data.Models.documents.Occurence(), Data.Models.documents.Occurence(), ...])
```

##Exporter
The exporter is the real aim of the whole pipeline. It offers to the user a way to treat collected data. For example, exporting data to json, plain text, or create graph about those data. They are based on `Exporter.common.Model` and takes at least two parameters : Exporter.common.Model(List(OccurenceSet)). `self.write()` is the function to export / write.

```python
#Example
OccurenceSet1 = Data.Models.documents.OccurenceSet(lemma = Data.Models.lang.Lemma(...), occurences = [Data.Models.documents.Occurence(), Data.Models.documents.Occurence(), ...])
OccurenceSet2 = Data.Models.documents.OccurenceSet(lemma = Data.Models.lang.Lemma(...), occurences = [Data.Models.documents.Occurence(), Data.Models.documents.Occurence(), ...])

ExporterInstance = Exporter.Raws.RCorpus([OccurenceSet1, OccurenceSet2])
ExporterInstance.write()
```