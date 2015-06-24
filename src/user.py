class User:
    def __init__(self,id="",name="", org=None):
        if org == None: return
        self.id = id
        self.name = name
        self.key = self.to_key(org.id, id)
        self.organization = org
        
    @staticmethod
    def to_key(org,id):
        return 'organization:%s:user:%s' % (org,id) 
