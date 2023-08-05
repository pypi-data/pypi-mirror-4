from AllocineObject import *

class Person(AllocineObject):
  def __unicode__(self):
    if "name" in self.__dict__:
      if "given" in self.name and "family" in self.name:
        return "%s %s" % (self.name["given"], self.name["family"])
      elif "given" in self.name:
        return self.name["given"]
      elif "family" in self.name:
        return self.name["family"]
      else:
        return str(self.__dict__.keys())
    else:
      return str(self.__dict__.keys())

