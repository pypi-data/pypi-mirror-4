import pickle

#Code to pickle up the given data

def pickle_data(obj,file='PicTemp.txt'):
    try :
        with open(file,'wb') as pic :
            pic.seek(0)
            try :
                pickle.dump(obj,pic)
            except pickle.PickleError as picError :
                print("Pickle Error : "+str(picError))
    except IOError as IOErr :
        print("IO Error : "+str(IOErr))

#Code to unpickle the pickled data and write it to the shell/to a file

def unpickle_data(file,fileout=False,wfile='UnPicTemp.txt'):
    try :
        with open(file,'rb') as unpic :
            unpic.seek(0)
            try :
                decode = pickle.load(unpic)
            except pickle.PickleError as picError :
                print("Pickle Error : "+str(picError))
        if fileout == True :
            try :
                with open(wfile,'w') as write :
                    write.seek(0)
                    print(decode,file=write)
            except IOError as IOerr:
                print("IO Error : "+IOerr)
        elif fileout == False :
            print(decode)
    except IOError as IOErr :
        print("IO Error : "+str(IOError))






