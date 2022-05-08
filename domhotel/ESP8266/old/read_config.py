def read_config(filename) :
    try:
        file = open(filename, "r")
        stringa = file.readline()
        file.close()
        return stringa
    except:
        return ""
        