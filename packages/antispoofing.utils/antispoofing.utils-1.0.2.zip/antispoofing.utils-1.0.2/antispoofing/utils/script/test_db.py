#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Thu Jan 17 14:35:08 CET 2013

"""Simple program that tests which databases are available"""

import os
import sys
import bob
import numpy
import argparse

def main():

  import antispoofing.utils.db 

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

  antispoofing.utils.db.Database.create_parser(parser)

  args = parser.parse_args()

  import ipdb; ipdb.set_trace()
  #######################
  # Loading the database objects
  #######################
  database = args.cls(args)

  trainReal, trainAttack = database.get_train_data()
  develReal, develAttack = database.get_devel_data()
  testReal, testAttack = database.get_test_data()

if __name__ == "__main__":
  main()
