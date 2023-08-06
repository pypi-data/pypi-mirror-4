def read_file():
    filename = input("Please input the dir of the document:")
    fp = open(filename,'r')
    print(fp.readlines(), end = '')
    fp.seek(0)
    fp.close()
