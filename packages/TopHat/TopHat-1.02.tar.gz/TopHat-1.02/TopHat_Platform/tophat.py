import os, sys
from server import *
def determine_path ():
    """Borrowed from wxglade.py"""
    try:
        root = __file__
        if os.path.islink (root):
            root = os.path.realpath (root)
        return os.path.dirname (os.path.abspath (root))
    except:
        print "I'm sorry, but something is wrong."
        print "There is no __file__ variable. Please contact colm@tophat.ie"
        sys.exit ()
        
def start ():
    print "module is running"
    print determine_path ()
    print "My various data files and so on are:"
    files = [f for f in os.listdir(determine_path())]
    print files
    
if __name__ == "__main__":
		main()   
