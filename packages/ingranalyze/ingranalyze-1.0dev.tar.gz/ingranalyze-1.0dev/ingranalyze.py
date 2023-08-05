#!python
# Copyright (c) 2012, Sven Thiele <sthiele78@gmail.com>
#
# This file is part of ingranalyze.
#
# ingranalyze is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ingranalyze is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ingranalyze.  If not, see <http://www.gnu.org/licenses/>.import random
# -*- coding: utf-8 -*-
import os
from optparse import OptionParser
from bioasp import asp
from __ingranalyze__ import query, utils, bioquali

#from bioasp.misc import *
#import tempfile
#from bioasp.data import op


if __name__ == '__main__':
    usage = "usage: %prog [options] networkfile observationfile" 
    parser = OptionParser(usage)


    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error("incorrect number of arguments")

    net_string = args[0]
    obs_string = args[1]

      
    print '\nReading network',net_string, '...',
    net = bioquali.readGraph(net_string)
    print 'done.'

    print '\nReading observations',obs_string, '...',
    mu = bioquali.readProfile(obs_string)
    print 'done.'

    print '\nComputing input nodes ...',
    inputs = query.guess_inputs(net)
    print 'done.'

    print '\nTesting empty network for consistency ...',
    consistent = query.is_consistent(net)
    print 'done.'

    if consistent: print '   The empty network is consistent.'
    else:
      print '   The empty network is inconsistent.'

      empty_net = net.union(inputs)
      print '\nTesting empty network plus input nodes for consistency ...',
      consistent = query.is_consistent(empty_net)
      print 'done.'
      if consistent: print '   The empty network is consistent.'
      else:
	print '   The empty network is still inconsistent.'
	
	choice= raw_input('\nDo you want to compute the minimal inconsistent cores? y/n ')
	if choice=="y": 
	  print '\nComputing minimal inconsistent cores (mic\'s) ...',
	  mics = query.get_minimal_inconsistent_cores(empty_net)
	  print 'done.\n'
	  count = 1
	  oldmic = 0
	  for mic in mics:
	      if oldmic != mic: 
		print 'mic '+str(count)+':'
		utils.print_mic(mic.to_list(),net.to_list(),[])
		count+=1
		oldmic= mic

	print "\nWhich repair mode do you want to perform ?"
	print "[1] flip observed variations"
	print "[2] flip influences"
	print "[3] define network nodes as inputs"
	print "[4] define network nodes as input in an experiment (to use only in case of multiple experiments)"
	print "[5] add influences"
	repairchoice= raw_input('\nChoose repair mode 1-5:')
	repair_options= asp.TermSet()
	print '\nCompute repair options ...',
	if repairchoice=="1":                    
	  print 'repair mode: flip observed variations ...',
	  repair_options = query.get_repair_options_flip_obs(empty_net)
	  print 'done.'
	if repairchoice=="2":                    
	  print 'repair mode: flip influences ...',
	  repair_options = query.get_repair_options_flip_edge(empty_net)
	  print 'done.'
	if repairchoice=="3":                    
	  print 'repair mode: define network nodes as inputs ...',
	  repair_options = query.get_repair_options_make_node_input(empty_net)
	  print 'done.'
	if repairchoice=="4":
	  print 'repair mode: define network nodes as input in an experiment ...',
	  repair_options = query.get_repair_options_make_obs_input(empty_net)
	  print 'done.'                    
	if repairchoice=="5":
	  print 'repair mode: add influence ...',
	  repair_options = query.get_repair_options_add_edges(empty_net)
	  print 'done.'                    
      
	if not (repairchoice in ["1","2","3","4","5"]) : print "ERROR", exit(0)

	print '\nCompute minimal numbers of necessary repair operations ...',
	optimum = query.get_minimum_of_repairs(empty_net,repair_options) 
	print 'done.'    
	
	print '   The data set can be repaired with minimal', optimum[0],'operations.'
	
	do_repair= raw_input('\nDo you want to compute all possible repair sets? Y/n:')
	if do_repair=="Y":

	  print '\nComputing all repair sets with size', optimum[0],'...'
	  models = query.get_minimal_repair_sets(empty_net,repair_options,optimum[0])
	  print 'done.'
	
	  count = 1
	  oldmodel = 0
	  for model in models:
	    if oldmodel != model: 
	      oldmodel = model
	      repairs = model.to_list()
	      print '  repair',count,':'
	      for r in repairs : print str(r.arg(0)),
	      print ' '
	      count+=1
	
	print '\nComputing predictions that hold under all repair sets size', optimum[0],'...',
	model = query.get_predictions_under_minimal_repair(optimum[0],empty_net,repair_options)
	print 'done.'
	predictions = model.to_list()
	print ( str(len(predictions)) + ' predictions found:')
	utils.print_predictions(predictions)

    if consistent: #if network is consistent add data
      net_with_data = net.union(mu).union(inputs)
      print '\nTesting network with data for consistency ...',
      consistent = query.is_consistent(net_with_data)
      print "done."
      if consistent: 
	print '   The network and data are consistent.'
	
	print '\nComputing predictions under consistency ...',
	model = query.get_predictions_under_consistency(net_with_data)
	print 'done.'
	predictions = model.to_list()
	#predictions.sort()
	print ( str(len(predictions)) + ' predictions found:')
	utils.print_predictions(predictions)
	
	
      else:
	print '   The network and the data are inconsistent.'
	
	choice= raw_input('\nDo you want to compute the minimal inconsistent cores? y/n ')
	if choice=="y": 
	  print '\nComputing minimal inconsistent cores (mic\'s) ...',
	  mics = query.get_minimal_inconsistent_cores(net_with_data)
	  print 'done.'
	  count = 1
	  oldmic = 0    
	  for mic in mics:
	    if oldmic != mic: 
	      print 'mic '+str(count)+':'
	      utils.print_mic(mic.to_list(),net.to_list(),mu.to_list())
	      count+=1
	      oldmic= mic
	    

	print "\nWhich repair mode do you want to perform ?"
	print "[1] flip observed variations"
	print "[2] flip influences"
	print "[3] define network nodes as inputs"
	print "[4] define network nodes as input in an experiment (to use only in case of multiple experiments)"
	print "[5] add influences"
	repairchoice= raw_input('\nChoose repair mode 1-5:')
	repair_options= asp.TermSet()
	print '\nCompute repair options ...',
	if repairchoice=="1":
	  print 'repair mode: flip observed variations ...',
	  repair_options = query.get_repair_options_flip_obs(net_with_data)
	  print 'done.'
	if repairchoice=="2":                    
	  print 'repair mode: flip influences ...',    
	  repair_options = query.get_repair_options_flip_edge(net_with_data)
	  print 'done.'
	if repairchoice=="3":                    
	  print 'repair mode: define network nodes as inputs ...',
	  repair_options = query.get_repair_options_make_node_input(net_with_data)
	  print 'done.'
	if repairchoice=="4":                    
	  print 'repair mode: define network nodes as input in an experiment ...',
	  repair_options = query.get_repair_options_make_obs_input(net_with_data)
	  print 'done.'
	if repairchoice=="5":                    
	  print 'repair mode: add influence ...',
	  repair_options = query.get_repair_options_add_edges(net_with_data)
	  print 'done.'
      
	if not (repairchoice in ["1","2","3","4","5"]) : print "ERROR", exit(0)

	print '\nCompute minimal numbers of necessary repair operations ...',
	optimum = query.get_minimum_of_repairs(net_with_data, repair_options)
	print 'done.'
	    
	print '   The data set can be repaired with minimal', optimum[0],'operations.'
	  
	do_repair= raw_input('\nDo you want to compute all possible repair sets? Y/n:')
	if do_repair=="Y":

	  print '\nComputing all repair sets with size', optimum[0],'...',
	  models = query.get_minimal_repair_sets(net_with_data, repair_options, optimum[0])
	  print "done."
	  count = 1
	  oldmodel = 0
	  for model in models:
	    if oldmodel != model: 
	      oldmodel = model
	      repairs = model.to_list()
	      print "  repair",count,':'
	      for r in repairs : print str(r.arg(0)),
	      print ' '
	      count+=1

	#print 'Computing subset minimal repairs ...'
	#print '\n', query.subset_minimal_repair_flip_obs(net_with_data)
	
	print '\nComputing predictions that hold under all repair sets size', optimum[0],'...',
	model = query.get_predictions_under_minimal_repair(net_with_data, repair_options, optimum[0])
	print "done."
	predictions = model.to_list()
	#predictions.sort()
	print ( str(len(predictions)) + ' predictions found:')
	utils.print_predictions(predictions)

    utils.clean_up()  
