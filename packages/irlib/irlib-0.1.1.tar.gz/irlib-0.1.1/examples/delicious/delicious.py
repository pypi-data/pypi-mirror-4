# Using IR to answer your question
# Not so smart question and answer system

import os, sys
import random

import cProfile
import pstats

# Adding this to path to be able to import irlib
sys.path.append('../../')

from irlib.preprocessor import Preprocessor
from irlib.matrix import Matrix, Stats
from irlib.metrics import Metrics

def main(filename='delicious.txt'):
    
    mx = Matrix()
    fd = open(filename,'r')
    
    for line in fd.readlines()[0:2000]:
        items = line.split('\t')
        if len(items) < 23:
            # Skip this line!
            continue
        url = items[0]
        popularity = items[1]
        date = items[2]
        tags = [items[i].lower() for i in range(3,len(items)) if i % 2]
        #print url, tags
        try:
            mx.add_doc(doc_id=url,
                doc_terms=tags,
                frequency=False, do_padding=True)
        except:
            print items
            raise
    mx.do_padding()    
    fd.close()
    print mx
 
    
    stats = mx.get_stats()
    print stats
    
    fd = open('tf.csv', 'w')
    tf = stats.get_terms_freq()
    for i in range(len(tf[0])):
        fd.write('%s, %f\n' % (tf[0][i], tf[1][i]))
    fd.close()


if __name__ == "__main__":

    if True:
        cProfile.run('main()','my_prof')
        p = pstats.Stats('my_prof')
        #p.sort_stats('time').print_stats(15)
        p.sort_stats('time').print_stats(15)
    else:     
        main()

