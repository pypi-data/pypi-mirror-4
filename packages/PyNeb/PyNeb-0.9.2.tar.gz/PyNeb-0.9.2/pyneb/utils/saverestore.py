import cPickle
def save(file_,*args,**kwargs):
    """
    Save the value of some data in a file.
    Usage: save('misdatos.pypic','a',b=b)
    """
    f=open(file_,"wb")
    dico = kwargs
    for name in args:
        dico[name] = eval(name)
    cPickle.dump(dico,f,protocol=2)
    f.close
def restore(file_):
    """
    Read data saved with save function.
    Usage: datos = restore('misdatos.pypic')
    """
    f=open(file_,"rb")
    result = cPickle.load(f)
    f.close
    return result
