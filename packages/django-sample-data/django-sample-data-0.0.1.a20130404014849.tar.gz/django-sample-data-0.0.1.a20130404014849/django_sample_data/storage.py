import codecs
import os
import random

cd = os.path.dirname( __file__ )

STORAGE =  os.path.join( cd ,'data')


def load_data( language, filename):
    filepath = os.path.join( STORAGE, language, filename)
    return load_file(filepath)

def load_file( *files, **kwargs ):
    alls = []
    for filename in files:
        f = codecs.open( os.path.join( STORAGE, filename ), "r", "utf-8" )
        alls.extend( f.read().splitlines() )

    random.shuffle( alls )
    return alls
