class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age


class Carrocinha:
    def __init__(self, city):
        self.dogs = []
        self.city = city
    
    def catch(self, dog):
        self.dogs.append(dog)


dog1 = Dog("MAX", 21)
dog2 = Dog("SPIKE", 12)


ong = Carrocinha("Campinas")

a= 1