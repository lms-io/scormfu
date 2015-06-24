class Registration:
    def __init__(self,id="",name="", org=None, course=None):
        if org == None: return
        self.id = id
        self.name = name
        self.key = self.to_key(org.id, id) 
        self.organization = org 
        self.course = course 
        
    @staticmethod
    def to_key(org,id):
        return 'organization:%s:registration:%s' % (org,id) 
