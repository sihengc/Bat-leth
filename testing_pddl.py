from PlanElementGraph import *

print('-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_')
op_excavate = Operator(id = 71, type = 'Action', name = 'excavate', num_args = 3, instantiated = True)

p1 = Literal(id=72, type='Condition', name= 'alive', 			num_args = 1, truth = True)
p2 = Literal(id=73, type='Condition', name= 'at', 				num_args = 2, truth = True)
p3 = Literal(id=74, type='Condition', name= 'burried', 			num_args = 2, truth = True)
p4 = Literal(id=75, type='Condition', name= 'knows-location', 	num_args = 3, truth = True)

e1 = Literal(id=76, type='Condition', name='burried',	num_args=2,	 truth = False)
e2 = Literal(id=77, type='Condition', name='has', 		num_args=2,	 truth = True)

consent = 	Actor(id=78,	 		type='actor',	 arg_pos_dict = {71 :	1})
item = 		Argument(id = 79, 	type='var',		 arg_pos_dict=	{71 :  2})
place = 	Argument(id = 80, 	type='var',		 arg_pos_dict=	{71:  3})

edge0 = Edge(op_excavate, consent, 'actor-of')
edge1 = Edge(op_excavate, p1,	 	'precond-of')
edge2 = Edge(op_excavate, p2, 		'precond-of')
edge3 = Edge(op_excavate, p3, 		'precond-of')
edge4 = Edge(op_excavate, p4, 		'precond-of')

edge5 = Edge(op_excavate, e1, 'effect-of')
edge6 = Edge(op_excavate, e2, 'effect-of')

edge7 = Edge(	p1, consent, 'first-arg')
edge8 = Edge(	p2, consent, 'first-arg')
edge9 = Edge(	p4, consent, 'first-arg')
edge10 = Edge(	e2, consent, 'first-arg')

edge12 = Edge(p2, item, 'sec-arg')
edge13 = Edge(p3, item, 'first-arg')
edge14 = Edge(p4, item, 'sec-arg')
edge15 = Edge(e1, item, 'first-arg')
edge16 = Edge(e2, item, 'sec-arg')

edge17 = Edge(p2, place, 'sec-arg')
edge18 = Edge(p3, place, 'sec-arg')
edge19 = Edge(p4, place, 'third-arg')
edge20 = Edge(e1, place, 'sec-arg')

excavate_elements = {op_excavate, p1, p2, p3, p4, e1, e2, consent, item, place}
excavate_edges = {edge0, edge1, edge2, edge3, edge4, edge5, edge6, edge7, edge8, edge9, edge10, \
					edge12, edge13, edge14,edge15, edge16,edge17, edge18, edge19, edge20}

					
op_kill = Operator(id = 4111, name = 'kill', type = 'Action', num_args = 4, executed = None, instantiated = True)
pre_kill_1 = Literal(id = 4112, name = 'alive', type = 'Condition', num_args = 1, truth = True)
pre_kill_2 = Literal(id = 4113, name = 'at', type = 'Condition', num_args = 2, truth = True)
pre_kill_3 = Literal(id = 4114, name='has', type = 'Condition', num_args = 2, truth = True)
pre_kill_4 = Literal(id = 4115, name = 'alive', type = 'Condition', num_args = 1, truth = True)
pre_kill_5 = Literal(id = 4116, name = 'at', type = 'Condition', num_args = 2, truth = True)
eff_kill_1 = Literal(id=4117, name='alive', type = 'Condition', num_args = 1, truth = False)
killer = Actor(id = 4118, name = None, type = 'actor', arg_pos_dict = {4111:1})
weapon = Argument(id=4119, type = 'var', arg_pos_dict = {4111:2})
victim = Actor(id = 4120, name = None, type = 'actor', arg_pos_dict = {4111:3})
place1 = Actor(id = 4121, name = None, type = 'var', arg_pos_dict = {4111:4})

kill_edges = {	Edge(op_kill, pre_kill_1, 'precond-of'),\
				Edge(op_kill, pre_kill_2, 'precond-of'),\
				Edge(op_kill, pre_kill_3, 'precond-of'),\
				Edge(op_kill, pre_kill_4, 'precond-of'),\
				Edge(op_kill, pre_kill_5, 'precond-of'),\
				Edge(op_kill, eff_kill_1, 'effect-of'),\
				Edge(op_kill, killer, 	  'actor-of'),\
				Edge(pre_kill_1, killer, 'first-arg'),\
				Edge(pre_kill_2, killer, 'first-arg'),\
				Edge(pre_kill_2, place1, 'sec-arg'),\
				Edge(pre_kill_3, killer, 'first-arg'),\
				Edge(pre_kill_3, weapon, 'sec-arg'),\
				Edge(pre_kill_4, victim, 'first-arg'),\
				Edge(pre_kill_5, victim, 'first-arg'),\
				Edge(pre_kill_5, place1, 'sec-arg'),\
				Edge(eff_kill_1, killer, 'first-arg')}
				
kill_elements = {op_kill, pre_kill_2, pre_kill_1, pre_kill_3, pre_kill_4, pre_kill_5, eff_kill_1, weapon, place1, victim, killer}
	

example2 = Operator(id = 2111, type= 'Action') #kill
te = Literal(id = 2112, type='Condition', name='alive', truth= False, num_args = 1)
killer_actor = 	Actor(id=2113, 			type='actor',			arg_pos_dict={2111 : 1})


example = Operator(id = 111, type= 'Action') #excavate
example_p1 =		Literal(id=112, 		type='Condition', 		name='alive', 			num_args = 1,		truth = True)
example_e1 = 		Literal(id=116, 		type = 'Condition', 	name='has', 			num_args = 2,		truth = True)
example_e3 = 		Literal(id=113, 		type = 'Condition', 	name='has', 								truth = True)
ex_const_element = 	Literal(id=114, 		type ='Condition',		name='knows-location', 	num_args = 3,		truth = False)
example_item = 		Argument(id=115,		type='var', 			arg_pos_dict={})
example_actor = 	Actor(id=117, 			type='actor',			arg_pos_dict={})


example_edge5 = Edge(example,	 example_e3, 	'effect-of')


example_elements = 	{	example, \
						example2,\
						te,\
						example_p1, \
						example_e1, \
					#	example_e3,\
						example_actor, \
						example_item,\
						ex_const_element,\
						killer_actor
						}
						
						
example_edges = 	{	Edge(example,	 example_p1, 	'precond-of'),\
						Edge(example,	 example_e1, 	'effect-of'),\
						Edge(example_p1, example_actor, 'first-arg'),\
						Edge(example_e1, example_actor, 'first-arg'),\
						Edge(example_e1, example_item, 	'sec-arg'),\
						Edge(example2,	 te, 			'effect-of'),\
						Edge(te, 		 killer_actor, 'first-arg')\
						}

						
example_constraints = {	Edge(example, ex_const_element, 'precond-of'),\
						Edge(ex_const_element, example_actor,	'first-arg'),\
						Edge(ex_const_element, example_item, 	'sec-arg')}
						
						
Excavate_operator =			Action(	id = 200,\
							type_graph = 'Action', \
							name = 'excavate', \
							Elements = excavate_elements, \
							root_element = op_excavate,\
							Edges = excavate_edges)
							
Kill_operator =				Action(	id = 3001,\
							type_graph = 'Action', \
							name = 'kill', \
							Elements = kill_elements, \
							root_element = op_kill,\
							Edges = kill_edges)
							
P1 = 	PlanElementGraph(id = 5432,\
		Elements=example_elements,\
		Edges=example_edges,\
		Constraints=example_constraints)
		
P2 = P1.copyGen()

kill_clone_9000 = Kill_operator.makeCopyFromID(9000, 1)
excavate_clone_7000 = Excavate_operator.makeCopyFromID(7000,1)

plans = P2.rInstantiate({2111, 111},{kill_clone_9000,excavate_clone_7000})
plan = plans.pop()
plan.print_plan()
plan.updatePlan()