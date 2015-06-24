class Organization:
    def __init__(self,id="",name=""):
        self.id = id
        self.name = name
        self.key = self.to_key(id) 

    @staticmethod
    def to_key(id):
        return 'organization:%s' % id
