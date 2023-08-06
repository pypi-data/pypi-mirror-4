"""a module that make a file which have a line of numbers to a class"""
def sanitize(time_string):
    """a function that make the different separators same as ':'"""
    if '-' in time_string:
        splitter = '-'
    elif  ':' in time_string:
        splitter = ':'
    else:
        return(time_string)
    (mins,secs)=time_string.split(splitter)
    return(mins+'.'+secs)

class AthleteList(list):
    """a class  carry on list and it has 2 attributes and a function"""
    def __init__(self,a_name=None,a_dob=None,a_times=[]):
        list.__init__([])
        self.name=a_name
        self.dob=a_dob
        self.extend(a_times)

    def top3(self):
        return(sorted(set([sanitize(t) for t in self]))[0:3])
    
