# etymolog

I find the meaning of words and the origin thereof fascinating. `etymolog` is a tool to store, retrieve and work with etymological facts. These facts are contained in files called `pills` (see [db](/db)) and contain words in different languages and relationships among them. They can be loaded using the [parser](./parser.py). After that you can work with them in python code or use one of the enclosed [tools](#Tools).

## Pill File Grammar

Etymological facts are stored in `.pill` files. They are processed line by line. One line contains one statement that can consist of several expressions. It is not allowed for one statement to span across multiple lines.

Whitespaces on the beginning and end of a line are stripped. Whitespaces between words are normalized to one space.

### Words
A word is the basic unit within a pill. It consists of any number of given alphabetical characters:

    ship

Each word gets assigned to a language. The language is an abbreviation of the language name. The default language is English (``en``) and this can be changed in [config](./config.py). It is used, when no explicit language is set for a word:

    en:ship

#### Composite words
You can have several words following each other and they will be fused into one:

    big ship 

creates one word `big ship` in the default language. Only the first word can have a language explicitly set:

    en:big ship
    
To have two or more different language definitions for a composed word is invalid though:

    en:big de:Schiff     // invalid

The words are stored case-sensitive just as you define them, but they are always looked up case-insensitive. So looking up `Ship` and `ship` will yield the same result.

### Groups
You can have several logically different words in the same statements comprising a group separated by ``;``:

    boat; ship; steam trawler
   
Will create three words. Group make sense to be used in relationships

### Relationships
The value of `etymolog` lies in the ability to define relationships among words. Especially the unidirectional `Derive` is useful as it helps to define the origin of words. Both `Equals` and `Related` are bidirectional, i.e. `a = b` will be the same as `b = a`.

#### Derivation
Derivation (``->``) indicates that one word has given birth to another one:

    en:pyre -> en:fire

You can have several relationships on one line:

    sa:Pas -> sa:Pasa -> lat:Pacify 
    
Here we say that the Latin word `pacify` is derived from Sanskrit word `pasa` which in turn stems from `pas`.

Relations are processed from the left and when one relationship (``sa:Pas -> sa:Pasa``) is used to create another one, the right-most part (``sa:Pasa``) from the one on left is used to create the new one (``sa:Pasa -> lat:Pacify``).

You can have any number of relationships on one line. You can also combine any relationships you like.
   
#### Equality
Equality defines what would be the translation of a word from one language to another:

    en:ship = de:Schiff

Here is where the groups make sense. If a group is used on the right side of relationship, the relationship will be created for all of its members:

    sa:Pas -> sa:Pasa = rope; cord; tie net; chain; trap; noose; snare

This first defines the derivation of ``sa:Pas`` into ``sa:Pasa``. Then it creates seven `equals` relationships for ``sa:Pasa`` with translation into the default language.

If a group is used on the left side of a relationship, only the right-most part of it will be used. E.g.:

    sa:dvipa -> hindi:Doab; ir:Dobar; cornish:Dofer; celtic:Dubron -> Dubrovnik

Will translate into:

    sa:dvipa -> hindi:Doab
    sa:dvipa -> ir:Dobar
    sa:dvipa -> cornish:Dofer
    sa:dvipa -> celtic:Dubron
    celtic:Dubron -> en:Dubrovnik
    
#### Generic Relation
If there is a link between words yet it is not direct translation (`Equals` relationship) nor derivation (`Derive`) use generic relation ``~``:

    en:pyre ~ sk:pýriť sa; de:Feuer

Which expresses that the two words on the right are somehow related with `pyre` yet it doesn't say why nor how.

### Comments
If you have an idea on "how" or "why" of the relationship or meaning of word, you can use a comment. You put the comment immediately after a word or the sign of a relationship:

    boat [means of transport on water]
    en:pyre ~[person turning red in the face] sk:pýriť sa

If you want to have multiple comments, use multiple statements:

    boat [similar to a ship]
    boat [means of transport on water]
    
### Unions
To express that one word is a composite of two other words, use an union (``+``):

    sa:vi + sa

This will result in creating a word ``sa:visa`` and creating a corresponding union object for it.

If a word's transcription is different from the composite word's, use the following syntax:

    sa:vyasa [vi+asa]
    
The words in brackets have the same language as the word they define. 

    sa:vyasa [sk:vy+asa]             // invalid

### Meta

#### EOL Comments

Comments that are for your eyes only and will be ignored by the parser start with ``//`` and end with the the end of the line:

    sa:Rudra -> cz:rudý // červený. Rudra je nahnevaný Šiva
    
    
#### Inline Comments

Comments within a series of words are enclosed in ``()``:

    sa:tantra = instrument (tra) to expand (tan) your consciousness

Yields the same data as:

    sa:tantra = instrument to expand your consciousness

#### Processing Directives

Finally there is a special category of comments that are directives for the parser. They are of the syntax // DIRECTIVE and there must not be any statement before them, i.e. they occupy the wohle line. E.g.

    // SRC http://some.link

Will set the parser's SRC directive to ``http://some.link``. Here is a list of supported directives:

* SRC set's the `source` attribute for all following Relationships and Words.
* LANG set's the default language.

All directives are valid from the point where they are encountered until the end-of-the file.

### Tags

Finally you can tag a word. On a line there can be any number of tags, all of which apply to the word preceding it:

    Thames #river #UK
    sa:danu -> danube #river

All tags are case-insensitive and stored in lower case.

## Tools
### dump.py
TODO

### details.py
TODO

### dict.py
TODO

## Object Model

    en = World.language("en")           # get or create language
    
    word = en.add_word("boat")
    word.comments                       # all comments
    word.comment("small ship")          # get or create a comment
    
    rel = Derived.add(w1, w2)
    rel == Derived.get(w1)
    rel in Derived.All
    rel.comments
    rel.comment("so they say")
