# etymolog

I find the meaning and origin of words is fascinating. `etymolog` is a tool to support me in my explorations. It stores the facts in files called `pills` (see [db](/db)). These can be loaded using the parser. After that you can work with them in python code.

* TODO - explain pills
* TODO - explain usage

## Relationships

* = equals
* -> gives birth to
* ~ related
* \+ union 

## Object Model

    en = World.language("en")           # get or create language
    
    word = en.word("boat")              # get or add
    word.comments                       # all comments
    word.comment("small ship")          # get or create a comment
    word.rels                           # all relationships
    
    rel = World.rel("~", word1, word2)   # w1 ~ w2 (or w2 ~ w1)
    rel.comments
    rel.comment("so they say")
    
    World.rels("->", "~")                # only ~, -> rels
    word.rels("->")