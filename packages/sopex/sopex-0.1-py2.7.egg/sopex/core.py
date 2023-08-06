#!/usr/bin/python
# -*- coding: utf-8 -*-

from chunker import PennTreebackChunker
from extractor import SOPExtractor

chunker = PennTreebackChunker()
extractor = SOPExtractor(chunker)

def extract(sentence):  
  global extractor
  sop_triplet = extractor.extract(sentence)
  return sop_triplet
