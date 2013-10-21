YAOP
====
### Yet Another ORM in Python

### (WARNING: Highly untested!!!)

- Focus on the retrieval of objects when serialized into database.

- Supports only SQLite3.

- Supports only types of INTEGER and TEXT.

- Use cases under construction.

### Creating of table and entry now works as follows:

(bear with me being too lazy to format the text into proper markdown syntax for
code highlighting)

    $ python
    from yaop import *
    class Person(Model):
        name = Attribute(str, unique=True)
        age = Attribute(int)
    
    x = Person(name="Xiao Ming", age=10)
    x.save()
    Executed: insert into Person(age,name) values(10,"XiaoMing")


Another tested use case with empty database.
This is a much more meaningful example as this maps inheritance into relational
database.

    $ python
    from yaop import *
    class Person(Model):
        name = Attribute(str)
    
    class Kid(Person): # Note that Kid inherits from Person
        age = Attribute(int)
    
    class Student(Kid): # Note that Student inherits from Kid
        grade = Attribute(int)
    
And here are the use cases for foreign keys, as well as searches. Note that only
equality search is supported.

    class Pet(Model):
        name = Attribute(str)
        owner = Attribute(Person)
    
    xm = Person(name="Xiao Ming")
    xmid = xm.save()
    >> Executed: insert into Person(name) values("Xiao Ming")

    xmid
    >> 1

    wangxingren = Pet(name="Bobby", owner=xmid)
    wangxingren.save()
    >> Executed: insert into Pet(owner,name) values(1,"Bobby")
    >> 1

    wangxingren.Id
    >> 1

    bobby = Pet.search(name="Bobby")
    bobby = bobby[0]
    bobby.name.value
    >> u'Bobby'

    bobby.owner.value
    >> 1

    bobby.Id
    >> 1
