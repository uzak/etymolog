# etymolog

I find the meaning and origin of words is fascinating. `etymolog` is a tool to support me in my explorations. It stores the facts in files called `pills` (see [db](/db)). These can be loaded using the parser. After that you can work with them in python code.

* TODO - explain pills
* TODO - explain usage
* TODO - explain two types of comments

## Relationships

* = equals: Words carry the same meaning, yet the sound is different.
* ~ related: Words have similar sound but the meaning doesn't definitely indicate derivation.
* -> derivation: There is a similarity in the meaning and sound of the words indicating one being the origin of the other.
* \+ union: The combination of two words is treated like a new word.

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
