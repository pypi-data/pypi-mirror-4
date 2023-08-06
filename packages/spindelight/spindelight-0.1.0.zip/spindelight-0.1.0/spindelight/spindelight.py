# Spin Delight

from random import randrange
from re import sub
from sys import argv, exit
import itertools


def init(filename):
    
    # Open the file specified and copy all the words
    with open(filename, 'r') as file:
        string = sub(r'[^a-z0-9]+', ' ', file.read().lower()).split()
    
    # Return string
    return string


def generate_dict(words):

    key = []
    values = {}

    # Creating the dictionary
    [key.append(word) for word in words if word not in key]
    for word in key:
        limit = len(words) - 1
        values[word] = [words[i+1] for i in range(limit + 1) if word == words[i] and i != limit]  

    # Return the keys and the dictionary
    return key, values


def generate_key(key,i,values):

    value = values[i]
    if len(value) == 0:
        y2 = []
    else:
        n = randrange(0,len(value))
        y2 = str(value[n])   
    return y2


def generate_unique(y1,key,values,cnt,mx):

    lst = []
    y2 = generate_key(key,y1,values)
    while y1 == y2:
        y2 = generate_key(key,y1,values)
    lst = list(set(values[y1]).intersection(values[y2]))

    if len(lst) == 0:
        y2 = []

    return y2


def generate_sent(key,values):
    
    x = []
    i = 0
    cnt = [0 for i in key]
    mx = [len(i) for i in key]

    y1 = key[randrange(0,len(key))]
    y2 = generate_unique(y1,key,values,cnt,mx)

    while 1:
        for i in range(len(values[y1])):
            if len(y2) != 0:
                break
            else:
                y2 = generate_unique(y1,key,values,cnt,mx)
        if i == len(values[y1]) - 1:
            y1 = key[randrange(0,len(key))]
        else:
            break

    # Generating the sentence
    while 1:
        x.append(y1)
        j = x.index(y1)
        if len(y2) == 0:
             break
        y1 = y2
        y2 = generate_unique(y1,key,values,cnt,mx)
        for i in range(len(values[y1])):
            if y2 == x[j]:
                y2 = generate_unique(y1,key,values,cnt,mx)
            elif len(y2) != 0:
                break
            else:
                y2 = generate_unique(y1,key,values,cnt,mx)
            
    # Formating the sentence
    string = ''
    for i in range(len(x)):
        string += str(x[i])
        if i != len(x) - 1:
            string += ' '
    string = string.capitalize() + '.'
    return string


def main():

    if len(argv) > 3:
        print('Usage: ' + argv[0] + ' [filename] [Number of paragraphs]')
        print('Example: '+ argv[0] + 'text.txt 2')
        exit(0)
    else:
        sen = 5
        if len(argv) == 3:
            filename = argv[1]
            sen = int(argv[2])
        elif len(argv) == 2:
            try:
                sen = int(argv[1])
                filename = 'text.txt'
            except ValueError:
                filename = argv[1]
        else:
            filename = 'text.txt'

        string = init(filename)                  # Function to parse the words from the file
        key, values = generate_dict(string)      # Function to generate the list from the words
        strng = ''

        for i in range(sen):
            for i in range(10):
                z = generate_sent(key,values)    
                while len(z) < 50:
                    z = generate_sent(key,values)
                strng += z + ' '
            strng += '\n\n'

        print(strng)
            
        
if __name__ == '__main__':
    main()
