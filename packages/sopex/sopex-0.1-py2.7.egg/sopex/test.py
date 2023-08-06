#!/usr/bin/python
# -*- coding: utf-8 -*-

import core

def do_test():  
  sentences = [
    'Monkeys are destroying the garden.',
    'No man can serve two masters.',
    'When students travel to US, they usually go by air.',    
    'The Earth revolves around the sun.',
    'Honesty is the best policy.',
    'John F. Kennedy was elected as US President in 1960.',
    'The quick brown fox jumps over the lazy dog.',
    'A rare black squirrel has become a regular visitor to a suburban garden',
    'As with every Sony PDA before it, the NR70 series is equipped with Sony\'s own memory stick expansion.'
  ]
  for sentence in sentences:
    sop_triplet = core.extract(sentence)
    print '%s --[%s]--> %s' % (sop_triplet.subject, sop_triplet.predicate, sop_triplet.object)
