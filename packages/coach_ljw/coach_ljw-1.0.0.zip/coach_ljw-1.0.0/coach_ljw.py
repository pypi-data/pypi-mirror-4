'''
Headfirst Python chaper05 study
I knew data structure of python. - list & set
james.txt -> 2-34,3:21,2.34,2.45,3.01,2:01,2:01,3:10,2-22
julie.txt -> 2.59,2.11,2:11,2:23,3-10,2-23,3:10,3.21,3-21
mikey.txt -> 2:22,3.01,3:01,3.02,3:02,3.02,3:22,2.49,2:38
sarah.txt -> 2:58,2.58,2:39,2-25,2-55,2:54,2.18,2:55,2:55
'''
def sanitize(time_string):
    splitter = '.'
    if '-' in time_string:
        splitter = '-'
    elif ':' in time_string:
        splitter = ':'
    else:
        return time_string
    (min, secs) = time_string.split(splitter)
    return (min + '.' + secs)

def get_coach_data(filename):
    try:
        with open(filename) as f:
            data = f.readline()
        return data.strip().split(',')
    except IOError as ioerr:
        print('File error : ' + str(ioerr))
        return (None)

james = get_coach_data('james.txt')
julie = get_coach_data('julie.txt')
mikey = get_coach_data('mikey.txt')
sarah = get_coach_data('sarah.txt')
    
print(sorted(set([sanitize(t) for t in james]))[0:3])
print(sorted(set([sanitize(t) for t in julie]))[0:3])
print(sorted(set([sanitize(t) for t in mikey]))[0:3])
print(sorted(set([sanitize(t) for t in sarah]))[0:3])
