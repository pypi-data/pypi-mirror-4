import codecs    

def cp1147_search_function(s):
    if s!='cp1147': return None
    try:                
         import cp1147
    except ImportError:
         return None
    codec = cp1147.Codec()
    return (codec.encode, codec.decode, cp1147.StreamReader,cp1147.StreamWriter)

codecs.register(cp1147_search_function)
