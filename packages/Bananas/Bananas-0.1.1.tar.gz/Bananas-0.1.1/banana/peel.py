class Peel(object):
    
    def __init__(self):
        self.has_peel = True
        
    def throw(self):
        print "You threw your banana peel."
        self.has_peel = False