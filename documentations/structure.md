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

##Contextualisation of occurences
This **optionnal step** aims to provide services which will take an Occurence() object and strip it texts to what the user needs. For example, this could reduce the occurence to a grammatical Sentence or to a n-word window. This class should have a strip() function which takes a Lemma() and an Cccurence as parameter and returns an Occurence

```python
#2-Word window example
Contextualiser = Linguistic.Contextualiser.WordsWindow(n = 2)
Contextualiser.strip(Data.Models.documents.Occurence(), Data.Models.lang.Lemma())
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