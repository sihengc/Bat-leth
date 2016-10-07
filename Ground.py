
import itertools
import copy
from collections import namedtuple, defaultdict
from PlanElementGraph import Condition, Action
from clockdeco import clock
from ElementGraph import ElementGraph
from Element import Argument
from Element import Operator

#GStep = namedtuple('GStep', 'action pre_dict pre_link')
Antestep = namedtuple('Antestep', 'action eff_link')

def groundStoryList(operators, objects, obtypes):
	stepnum = 0
	gsteps = []
	for op in operators:
		op.updateArgs()
		cndts = [[obj for obj in objects if arg.typ == obj.typ or arg.typ in obtypes[obj.typ]] for arg in op.Args]
		tuples = itertools.product(*cndts)
		for t in tuples:
			legaltuple = True
			for (u,v) in op.nonequals:
				if t[u] == t[v]:
					legaltuple = False
					break
			if not legaltuple:
				continue
			gstep = copy.deepcopy(op)
			gstep._replaceInternals()
			gstep.root.stepnumber = stepnum
			gstep.root.arg_name = stepnum
			stepnum+=1
			gstep.replaceArgs(t)
			gsteps.append(gstep)
	return gsteps

def groundDiscList(operators, SGL):
	from Plannify import Plannify
	#For each ground subplan in Subplans, make a copy of DO s.t. each
	gsteps = []
	stepnum = 0
	for op in operators:
		Subplans = Plannify(next(iter(op.subgraphs)), SGL)
		for sp in Subplans:
			GDO = copy.deepcopy(op)
			for elm in sp.elements:
				ex_elms = iter(op.elements)
				for ex_elm in ex_elms:
					if elm.arg_name == ex_elm.arg_name and elm.arg_name is not None:
						if elm.typ in {'Action','Condition'}:
							EG = eval(elm.typ).subgraph(sp,elm)
						else:
							EG = elm
						GDO.assign(ex_elm, EG)
			GDO.ground_subplan = sp
			GDO.root.stepnumber = stepnum
			stepnum+=1
			gsteps.append(GDO)

	return gsteps

import pickle

@clock
def upload(GL, name):
	afile = open(name,"wb")
	pickle.dump(GL, afile)
	afile.close()

@clock
def reload(name):
	afile = open(name,"rb")
	GL = pickle.load(afile)
	afile.close()
	return GL

def isStoryElement(elm):
	return isinstance(elm, ElementGraph) or isinstance(elm, Argument)

class GLib:

	def __init__(self, operators, objects, obtypes, init_action, goal_action, storyGL=None):


		if storyGL is not None:
			self._gsteps = groundDiscList(operators, storyGL)

			#init_actions = discotize(init_action)
			#goal_actions = discotize(goal_action)
		else:
			self._gsteps = groundStoryList(operators, objects, obtypes)

		#init at [-2]
		init_action.root.stepnumber =len(self._gsteps)
		init_action._replaceInternals()
		init_action.replaceInternals()
		self._gsteps.append(init_action)
		#goal at [-1]
		goal_action.root.stepnumber= len(self._gsteps)
		goal_action._replaceInternals()
		goal_action.replaceInternals()
		self._gsteps.append(goal_action)

		#dictionaries
		self.initDicts()

		#load dictionaries
		self.loadAll()
		print('{} ground steps created'.format(len(self)))

		print('uploading')
		if storyGL is not None:
			upload(self, 'DGL')
		else:
			upload(self, 'SGL')


	def initDicts(self):
		self.pre_dict = defaultdict(set)
		self.ante_dict = defaultdict(set)
		self.id_dict = defaultdict(set)
		self.eff_dict = defaultdict(set)
		self.threat_dict = defaultdict(set)


	def loadAll(self):
		for _step in self._gsteps:
			#print('preprocessing step {}....'.format(_step))
			pre_tokens = _step.preconditions
			for _pre in pre_tokens:
				#print('preprocessing precondition {} of step {}....'.format(_pre, _step))
				self.loadAnteSteps(_step, _pre)

	def loadAnteSteps(self, _step, _pre):
		Precondition = Condition.subgraph(_step, _pre)
		for gstep in self._gsteps:
			# Defense pattern
			count = 0
			for _eff in gstep.effects:
				# Defense 2
				if not _eff.isConsistent(_pre):
					# Defense 2.1

					if not _eff.isOpposite(_pre):
						continue
					# Defense 2.2
					Effect = Condition.subgraph(gstep, _eff)
					if Effect.Args != Precondition.Args:
						continue

					self.threat_dict[_step.stepnumber].add(gstep.stepnumber)
					continue


				# Defense 3
				Effect = Condition.subgraph(gstep,_eff)
				if Effect.Args != Precondition.Args:
					continue

				# Create antestep
				antestep = copy.deepcopy(gstep)
				eff_link = antestep.RemoveSubgraph(_eff)
				antestep.replaceInternals()

				self.pre_dict[_pre.replaced_ID].add(Antestep(antestep, eff_link))
				self.id_dict[_pre.replaced_ID].add(antestep.stepnumber)
				self.eff_dict[_pre.replaced_ID].add(eff_link.sink.replaced_ID)
				count += 1

			if count > 0:
				self.ante_dict[_step.stepnumber].add(gstep.stepnumber)

	def makeGoal(self, objects, goal_action):
		from Plannify import DiscLib

		#story_elements = {elm for dgl in self for elm in dgl.elements if isStoryElement(elm)}
		DiscLibs = [DiscLib(elm, self) for elm in goal_action.elements if isStoryElement(elm)]
		DiscWorlds = itertools.product(DiscLibs)

	def getPotentialLinkConditions(self, src, snk):
		from Graph import Edge
		cndts = []
		for pre in self[snk.stepnumber].preconditions:
			if not src.stepnumber in self.id_dict[pre.replaced_ID]:
				continue

			cndts.add(Edge(src,snk,copy.deepcopy(pre)))
		return cndts

	def getPotentialEffectLinkConditions(self, src, snk):
		from Graph import Edge
		cndts = []
		for eff in self[src.stepnumber].effects:
			for pre in self[snk.stepnumber].preconditions:
				if not eff.replaced_ID in self.id_dict[pre.replaced_ID]:
					continue
				cndts.add(Edge(src, snk, copy.deepcopy(eff)))

		return cndts

	def getConsistentEffect(self, S_Old, precondition):
		effect_token = None
		for eff in S_Old.effects:
			if eff.replaced_ID in self.eff_dict[precondition.replaced_ID]:
				effect_token = eff
				break
		if effect_token == None:
			raise AttributeError('story_GL.eff_dict empty but id_dict has antecedent')
		return effect_token

	def hasConsistentPrecondition(self, Sink, effect):
		for pre in Sink.preconditions:
			if effect.replaced_ID in self.eff_dict[pre.replaced_ID]:
				return True
		return False

	def getConsistentPrecondition(self, Sink, effect):
		pre_token = None
		for pre in Sink.preconditions:
			if effect.replaced_ID in self.eff_dict[pre.replaced_ID]:
				pre_token = pre
				break
		if pre_token == None:
			raise AttributeError('effect {} not in story_GL.eff_Dict for Sink {}'.format(effect, Sink))
		return pre_token

	def __len__(self):
		return len(self._gsteps)

	def __getitem__(self, position):
		return self._gsteps[position]

	def __contains__(self, item):
		return item in self._gsteps

	def __repr__(self):
		return 'Grounded Step Library: \n' +  str([step.__repr__() for step in self._gsteps])


		#what if we limit to just those elements which are args in a DGL?
			#idea: iterate through DGL and identify all story-elements. Then, those story-elements become the problem
	#  objects. Then, for each problem object in goal state, create world for each possible goal world. Basically,
	# just take the story element in the goal condition, and see which DGL story elements


from pddlToGraphs import parseDomAndProb
from Flaws import FlawLib


if __name__ ==  '__main__':
	domain_file = 'domains/ark-domain.pddl'
	problem_file = 'domains/ark-problem.pddl'

	operators, objects, object_types, initAction, goalAction = parseDomAndProb(domain_file, problem_file)

	from Planner import preprocessDomain, obTypesDict
	FlawLib.non_static_preds = preprocessDomain(operators)
	obtypes = obTypesDict(object_types)

	print("creating ground actions......\n")
	GL = GLib(operators, objects, obtypes, initAction, goalAction)

	print('\n')
	print(GL)

	# for gstep in story_GL:
	# 	print(gstep)
	# 	pre_tokens = gstep.getPreconditionsOrEffects('precond-of')
	# 	print('antes:')
	# 	for pre in pre_tokens:
	# 		print('pre: {} of step {}....\n'.format(pre, gstep))
	# 		for ante in gstep.pre_dict[pre]:
	# 			print(ante.action)
	# 		print('\n')
	# 	print('\n')
