def sanitize(time_string):
    if '-' in time_string:
        splitter = '-'
    elif ':' in time_string:
        splitter = ':'
    else:
        return(time_string)
    (mins, secs) = time_string.split(splitter)
    return(mins + '.' + secs)

class AthleteList(list):
    def __init__(self, a_name, a_dob=None, a_times=[]):
        list.__init__([])
        self.name = a_name
        self.dob = a_dob
        self.extend(a_times)
        
    def top3(self):
        return(sorted(set([sanitize(t) for t in self]))[0:3])

def getFileContent(fileName):
    try:
        with open(fileName) as f:
            data = f.readline()
        templ = data.strip().split(",")
        return(AthleteList(templ.pop(0), templ.pop(0), templ))
    except IOError as ioerr:
        print("There was an error with the file: " + str(ioerr) + "\nPlease correct it and try again")
        return(None)
try:
    james = getFileContent("james2.txt")
    julie = getFileContent("julie2.txt")
    mikey = getFileContent("mikey2.txt")
    sarah = getFileContent("sarah2.txt")

    print(james.name + "'s fastest times are: " + str(james.top3()))
    print(julie.name + "'s fastest times are: " + str(julie.top3()))
    print(mikey.name + "'s fastest times are: " + str(mikey.top3()))
    print(sarah.name + "'s fastest times are: " + str(sarah.top3()))
except TypeError as err:
    pass
except NameError:
    pass
