#!/usr/bin/env python

from __future__ import print_function

with open('/aml/data/gutenberg-txt.index') as input_file:
    lines = [line.strip() for line in input_file]

##############################################################################
# TEMP: TRIM STUFF
#lines = [line for line in lines if line.startswith('gutenberg-txt/1')]
##############################################################################

with open('hdfs-wordcount.list', 'w') as hdfs_out:
    for line in lines:
        print('hdfs://0potato/user/amcnabb/' + line, file=hdfs_out)

with open('nfs-wordcount.list', 'w') as nfs_out:
    for line in lines:
        print('/aml/data/' + line, file=nfs_out)

with open('hadoop-wordcount.list', 'w') as hadoop_out:
    #all_of_em = ','.join('/user/amcnabb/' + line for line in lines)
    #print(all_of_em, file=hadoop_out)
    for line in lines:
        print('/user/amcnabb/' + line, file=hadoop_out)

# vim: et sw=4 sts=4
