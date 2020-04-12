# etymolog

* Martin Užák
* 12 April 2020

I find the meaning of words and the origin thereof fascinating. `etymolog` is a tool to store, retrieve and work with etymological facts. For example this could be looking up the Sanskrit word `tr` and derivation thereof (`./details.py sa tr`):

     => sa:tr = en:stars, to cross over
        + sa:rAtrI {rA+tr} = en:night, sa:naktA [that which gives (rA) the stars (tr)]
       -> pt:trazer   
       -> sa:str = en:star, strewn, scattered, spread  
         -> sa:tara = en:crossing, sa:Kali  
           -> en:Tartary   
         -> en:astral   
         -> en:star   
         -> en:transit 
         
Or producing a dictionary for a language showing the derivations of the words therefrom (`./dict.py sk`):

    * báť sa 
        -> sa:bhaya
    * beda 
        -> sa:bheda
    * biely 
        -> slavic:bel -> sa:bhalu
    * brat 
        -> sa:bhrAtr
    ...

## Pill File Grammar

Etymological data is stored in `.pill` files. They are processed line by line. One line contains one statement that can consist of several expressions. It is not allowed for one statement to span across multiple lines.

Whitespaces on the beginning and end of a line are stripped. Whitespaces between words are normalized to one space.

### Words
A word is the basic unit within a pill. It consists of any number of given alphabetical characters. Example:

    ship

Each word gets assigned to a language. The language is an abbreviation of the language name. The default language is English (``en``) and this can be changed in [config](./config.py). It is used, when no explicit language is set for a word. So the previous example is the same as:

    en:ship

#### Composite words
You can have several words following each other and they will be fused into one:

    big ship (out of wood)

creates one word `big ship (out of wood)` in the default language. Only the first word can have a language explicitly set:

    en:big ship
    
To have two or more different language definitions for a composed word is invalid though:

    en:big de:Schiff     // invalid

The words are stored case-sensitive just as you define them, but they are always looked up case-insensitive. So looking up `Ship` and `ship` will yield the same result.

### Groups
You can have several logically different words in the same statements comprising a group separated by ``,``:

        boat, ship, steam trawler
       
Will create three words. Group make sense to be used in relationships

### Relationships
The value of `etymolog` lies in the ability to define relationships among words. Especially the unidirectional `Derive` is useful as it helps to define the origin of words. 

#### Derivation
Derivation (``->``) indicates that one word has given birth to another one:

    en:pyre -> en:fire

You can have several relationships on one line:

    sa:Pas -> sa:Pasa -> lat:pax -> pacify 
    
Here we say that the word `pacify` is derived from Latin `pax` from Sanskrit word `pasa` which in turn stems from `pas`.

Relations are processed from the left and when one relationship (``sa:Pas -> sa:Pasa``) is used to create another one, the right-most part (``sa:Pasa``) from the one on left is used to create the new one (``sa:Pasa -> lat:pax``).

You can have any number of relationships on one line. You can also combine any relationships you like.
   
#### Equality
Equality defines what would be the translation of a word from one language to another:

    en:ship = de:Schiff

Here is where the groups make sense. If a group is used on the right side of relationship, the relationship will be created for all of its members:

    sa:Pas -> sa:Pasa = rope, cord, tie net, chain, trap, noose, snare

This first defines the derivation of ``sa:Pas`` into ``sa:Pasa``. Then it creates seven `equals` relationships for ``sa:Pasa`` with translation into the default language.

If a group is used on the left side of a relationship, only the right-most part of it will be used. E.g.:

    sa:dvipa -> hindi:Doab, ir:Dobar, cornish:Dofer, celtic:Dubron -> Dubrovnik

Will translate into:

    sa:dvipa -> hindi:Doab
    sa:dvipa -> ir:Dobar
    sa:dvipa -> cornish:Dofer
    sa:dvipa -> celtic:Dubron
    celtic:Dubron -> en:Dubrovnik
    
#### Generic Relation
If there is a link between words yet it is not direct translation (`Equals` relationship) nor derivation (`Derive`) use generic relation ``~``:

    en:pyre ~ sk:pýriť sa, de:Feuer

Which expresses that the two words on the right are somehow related with `pyre` yet it doesn't say why nor how.

### Comments
If you have an idea on "how" or "why" of the relationship or meaning of word, you can use a comment. You put the comment immediately after a word or the sign of a relationship:

    boat [means of transport on water]
    en:pyre ~[person turning red in the face] sk:pýriť sa

If you want to have multiple comments, use multiple statements or put the comments behind each other:

    boat [similar to a ship]
    boat [means of transport on water]
    
    a [b] [c]               // is valid as well
    
### Unions
To express that one word is a composite of two other words, use an union (``{ first_word + ... + last_word }``):

    sa:vi+sa {vi+sa}

This will result in creating a word ``sa:visa`` and creating a corresponding union object for it.

You can have any number of components, e.g.

    sa:svetAsvatara {sveta+asva+tara}

The components are by default in the language of the union. But you can also explicitly set the language for any of them:

    slavic:Dažbog {sa:dadati+bog}

And finally you can combine comments with union statements:

    slavic:Dažbog {sa:dadati+bog} [solar deity]

### Meta

#### EOL Comments

Comments that are for your eyes only and will be ignored by the parser start with ``//`` and end with the the end of the line:

    sa:Rudra -> cs:rudý // červený. Rudra je nahnevaný Šiva
    
#### Embedded comments

Words in parentheses will be ignored, so they can be used as comments:

    pie:k = curvilinear (motion)    
    
Will be the same as:

    pie:k = curvilinear
    
#### Processing Directives

Finally there is a special category of comments that are directives for the parser. They are of the syntax // DIRECTIVE and there must not be any statement before them, i.e. they occupy the wohle line. E.g.

    // SRC http://some.link

Will set the parser's SRC directive to ``http://some.link``. Here is a list of supported directives:

* SRC set's the `source` attribute for all following Relationships and Words.
* NOSRC unsets the `source` attribut for all following entities.
* LANG set's the default language.

These directives are valid from the point where they are encountered until the end-of-the file.

### Tags

Finally you can tag a word. On a line there can be any number of tags, all of which apply to the word preceding it:

    Thames #river #UK
    sa:danu -> danube #river

All tags are case-insensitive and stored in lower case.

## Tools
Above was the description of the grammar. It is implemented in [lexer.py](lexer.py) and [parser.py](parser.py), both of which can be used with a file as argument for testing.

use `parser.py::load_db()` to load the DB. The parser will instantiate the objects and create relationships in memory according to [model.py](model.py). Once this is done you can work on the object model, either with your tools or using the attached ones:

### dump.py
To produce some stats about your DB, use `dump.py`.

### details.py
`details.py` shows the details of a `word` in a `language`.

### dict.py
`dict.py` as seen above lists all the words for a given `language` along with their derivations.

