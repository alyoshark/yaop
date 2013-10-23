from yaop import *
class Person(Model):
    name = Attribute(str)

class Kid(Person): # Note that Kid inherits from Person
    age = Attribute(int)

class Student(Kid): # Note that Student inherits from Kid
    grade = Attribute(int)

class Pet(Model):
    name = Attribute(str)
    owner = Attribute(Person)

def main():
    # Creation
    ah_beh = Student(name="Ah Beh", age=15)
    ah_beh.update(grade=5)
    print ah_beh.save()
    dog_lover = Person(name="John")
    johns_id = dog_lover.save()
    bobby = Pet(name="Bobby", owner=johns_id)
    bobby.save()

    # Read
    pets_named_bobby = Pet.search(name="Bobby")
    one_of_bobbies = pets_named_bobby[0]
    # Check if this is John's Bobby
    if one_of_bobbies.owner.value == johns_id:
        print "John finds his Bobby"
    else:
        print "This is not John's Bobby"

    # Update
    ah_beh.update(grade=6)  # Level up ^
    ah_beh.save()
    print ah_beh.grade.value

    # Delete
    ah_beh.remove()
    one_of_bobbies.remove()
    dog_lover.remove()


if __name__ == "__main__":
    main()
