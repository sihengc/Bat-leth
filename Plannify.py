import itertools
from PlanElementGraph import Action, PlanElementGraph
from Graph import Edge
from clockdeco import clock
from Reuse import ReuseLib
from Flaws import Flaw
from Element import Operator

@clock
def Plannify(RQ, GL):
	#An ActionLib for steps in RQ - ActionLib is a container w/ all of its possible instances as ground steps
	print('... Processing {}'.format(RQ.name))
	print('...ActionLibs')
	Libs = [ActionLib(i, RS, GL) for i, RS in enumerate([Action.subgraph(RQ, step) for step in RQ.Steps])]

	#A World is a combination of one ground-instance from each step
	Worlds = productByPosition(Libs)

	print('...Planets')
	#A Planet is a plan s.t. all steps are "arg_name consistent", but a step may not be equiv to some ground step
	Planets = [PlanElementGraph.Actions_2_Plan(W) for W in Worlds if isArgNameConsistent(W)]

	print('...Linkify')
	#Linkify installs orderings and causal links from RQ/decomp to Planets, rmvs Planets which cannot support links
	has_links = Linkify(Planets, RQ, GL)

	print('...Groundify')
	#Groundify is the process of replacing partial steps with its ground step, and removing inconsistent planets
	Plans = Groundify(Planets, GL, has_links)

	print('...returning consistent plans')
	return [Plan for Plan in Plans if Plan.isInternallyConsistent()]

@clock
def Unify(U, V, B = None):
	if B is None:
		B = set()
	#Create library of possible U-steps to reuse steps in V
	Reuse = [[u for u in U.Steps if u.stepnumber == v.stepnumber].append(v) for v in V.Steps]

	#Create step lists where either "u" is reused to unify with "v" or "v" is added
	Worlds = itertools.product(*Reuse)

	#Create new U-Plans to Integrate V info (links and orderings) or add v-steps not reused (or both)
	Plans = [U.Integrate(W, V) for W in Worlds]

	return [Plan for Plan in Plans if Plan.isInternallyConsistent()]


def partialUnify(PS, _map):
	if _map is False:
		return False
#	NS = PS.deepcopy()
	import copy
	NS = copy.deepcopy(PS)
	effects = [edge.sink for edge in NS.edges if edge.label == 'effect-of']
	for elm in effects:
		if elm in _map:
			g_elm = _map[elm]
			elm.merge(g_elm)
			elm.replaced_ID = g_elm.replaced_ID

	NSE = list(NS.elements)
	for elm in NSE:
		if elm in _map:
			g_elm = _map[elm]
			elm.merge(g_elm)
			elm.replaced_ID = g_elm.replaced_ID
			if elm.replaced_ID == -1:
				# this is an object/constant
				ge = copy.deepcopy(g_elm)
				ge.replaced_ID = ge.ID
				NS.assign(elm, ge)
				#elm.replaced_ID = g_elm.ID
				#elm.ID = g_elm.ID
	NS.root.stepnumber = PS.root.stepnumber
	return NS

def isArgNameConsistent(Partially_Ground_Steps):
	"""
		@param Partially_Ground_Steps <-- partially ground required steps (PGRS), reach required step associated with ground step
	"""
	arg_name_dict = {}

	for PGS in Partially_Ground_Steps:
		for elm in PGS.elements:
			if not elm.arg_name is None:
				if elm.arg_name in arg_name_dict.keys():
					if not elm.isConsistent(arg_name_dict[elm.arg_name]):
						return False
				else:
					arg_name_dict[elm.arg_name] = elm
	return True

def productByPosition(Libs):
	return itertools.product(*[list(Libs[T.position]) for T in Libs])

def Linkify(Planets, RQ, GL):
	#Planets are plans containing steps which may not be ground steps from story_GL
	orderings = RQ.OrderingGraph.edges
	if len(orderings) > 0:
		for Planet in Planets:
			GtElm = Planet.getElementById
			try:
				Planet.OrderingGraph.edges = {Edge(GtElm(ord.source.ID), GtElm(ord.sink.ID),'<') for ord in orderings}
			except:
				raise AttributeError('why can I not use add ordering here?')

	links = RQ.CausalLinkGraph.edges
	if len(links) == 0:
		return False

	removable = set()
	for link in links:
		for i, Planet in enumerate(Planets):
			src = Planet.getElementById(link.source.ID)
			snk = Planet.getElementById(link.sink.ID)
			cond = Planet.getElementById(link.label.ID)

			if src.stepnumber not in GL.ante_dict[snk.stepnumber]:
				removable.add(i)
				continue

			if not GL.hasConsistentPrecondition(GL[snk.stepnumber],cond):
				removable.add(i)
				continue

			Planet.CausalLinkGraph.addEdge(src, snk, cond)
			Planet.OrderingGraph.addEdge(src,snk)

		Planets[:] = [Planet for i, Planet in enumerate(Planets) if i not in removable]
		removable = set()
		if len(Planets) == 0:
			raise ValueError('no Planet could support links in {}'.format(RQ.name))

	return True


def Groundify(Planets, GL, has_links):

	for Planet in Planets:
		for step in Planet.Steps:
			Step = Action.subgraph(Planet, step)
			Planet.UnifyActions(Step, GL[step.stepnumber])

	if not has_links:
		#we're done
		return Planets

	Discovered_Planets = []
	for Plan in Planets:
		Libs = [LinkLib(i,link,GL) for i, link in enumerate(Plan.CausalLinkGraph.edges)]

		#LW = [plan1 [link1.condition, link2.condition,..., link-n.condition],
			#  plan2 [link1.condition, link2.condition, ..., link-m.condition],
		    #  plan-k [l1,...,lz]]
		LW = productByPosition(Libs)

		for lw in LW:
			NP = Plan.deepcopy()
			for _link in lw:
				pre_token = GL.getConsistentPrecondition(Action.subgraph(NP, _link.sink), _link.label)
				if _link.label == pre_token:
					continue
				pre_link = NP.RemoveSubgraph(pre_token)
				pre_link.sink = _link.label
				NP.edges.add(pre_link)

			Discovered_Planets.append(NP)

	return Discovered_Planets


class ActionLib:

	def __init__(self, i, RS, GL):
		#RS.root.stepnumber = stepnum
		self.position = i
		RS.root.position = i
		self.RS = RS
		self.root = RS.root
		self._cndts = []
		for gs in GL:
			if not gs.root.isConsistent(self.RS.root):
				continue
			elm_maps = gs.findConsistentSubgraph(self.RS)
			if len(elm_maps) == 0:
				continue
			for map in elm_maps:
				if len(map) == 0:
					self.RS.root.merge(gs.root)
					self.RS.root.replaced_ID = gs.root.replaced_ID
				self.append(partialUnify(self.RS, map), gs.stepnumber)
		if len(self) == 0:
			raise ValueError('no gstep compatible with RS {}'.format(self))

	def __len__(self):
		return len(self._cndts)

	def __getitem__(self, position):
		return self._cndts[position]

	def __setitem__(self, key, value):
		self._cndts[key] = value

	def append(self, item, stepnum):
		item.root.stepnumber = stepnum
		self._cndts.append(item)

	@property
	def edges(self):
		return self.RS.edges

	@property
	def elements(self):
		return self.RS.elements

	def __contains__(self, item):
		return item in self._cndts

	def __repr__(self):

		return self.RS.__repr__()




class LinkLib:

	def __init__(self, position, link, GL):
		"""
		@param position: in list of links of Planet
		@param link: ground steps
		@param Plan: Plan containing link
		@param GL: ground step library """

		self.position = position
		self.source = link.source
		self.sink = link.sink
		self.condition = link.label

		#LinkLib is a library of potential conditions, just 1 if already specified
		self._links = []

		if not link.label.arg_name is None:
			#linked-by
			self._links = [Edge(link.source, link.sink, self.condition)]
		else:
			# add new condition for each potential condition
			self._links = GL.getPotentialEffectLinkConditions(link.source, link.sink)
			#self._links = story_GL.getPotentialLinkConditions(link.source, link.sink)

	def __len__(self):
		return len(self._links)

	def __getitem__(self, position):
		return self._links[position]

	def __repr__(self):
		return '{}-- link-pos {} --> {}'.format(self.source, self.position, self.sink)


@clock
def Unify(story, other, GL):
	#self is story, other is ground subplan, which may have elements/IDs already in story.

	SSteps = set(story.Steps)
	Uni_Libs = [ReuseLib(i, s_add, SSteps) for i, s_add in enumerate(other.Steps)]
	Uni_Worlds = itertools.product(*Uni_Libs)
	# for ul  in Uni_Libs:
	# 	if len(ul._cndts) > 1:
	# 		pass

	New_Plans = set()
	for UW in Uni_Worlds:
		new_plan = story.deepcopy()

		#For each step not already in story, add
		AddNewSteps(UW, other, SSteps, new_plan)

		for ord in other.OrderingGraph.edges:
			new_plan.OrderingGraph.addEdge(UW[ord.source.position], UW[ord.sink.position])

		for link in other.CausalLinkGraph.edges:
			if UW[link.sink.position] not in SSteps:
				#If its a new step, then there aren'tany flaws to remove
				AddLink(link, new_plan, UW, remove_flaw=False)
			else:
				#if its already in plan, then remove flaw for tat dependency.
				AddLink(link, new_plan, UW, remove_flaw=True)

		#Add new flaws for other steps
		for step in UW:
			if step not in SSteps:
				AddNewFlaws(GL, step, new_plan)

		if new_plan.isInternallyConsistent():
			New_Plans.add(new_plan)

	return New_Plans

def AddNewSteps(UW, other, SSteps, new_plan):
	for step in UW:
		if step not in SSteps:
			S_new = Action.subgraph(other, step).deepcopy()
			S_new.root.arg_name = step.stepnumber
			# move pieces
			new_plan.elements.update(S_new.elements)
			new_plan.edges.update(S_new.edges)
			# place in order
			new_plan.OrderingGraph.addEdge(new_plan.initial_dummy_step, S_new.root)
			new_plan.OrderingGraph.addEdge(S_new.root, new_plan.final_dummy_step)

def AddNewFlaws(GL, step, new_plan):
	Step = Action.subgraph(new_plan, step)
	# Step = Action.subgraph(new_plan, new_plan.getElmByRID(step.replaced_ID))

	for pre in Step.preconditions:
		#this is a hack, if the precondition has two operator parents, then its in a causal link
		cndts = {edge for edge in new_plan.edges if isinstance(edge.source, Operator) and edge.sink == pre}
		if len(cndts) == 0:
			raise ValueError('wait, no edge for this preconditon? impossible!')
		if len(cndts) < 2:
			new_plan.flaws.insert(GL, new_plan, Flaw((step, pre), 'opf'))

	new_plan.flaws.addCndtsAndRisks(GL, step)

def AddLink(link, new_plan, UW, remove_flaw=True):

	Source = Action.subgraph(new_plan, UW[link.source.position])
	new_d = Source.getElmByRID(link.label.replaced_ID)
	if new_d is None:
		Sink = Action.subgraph(new_plan, UW[link.sink.position])
		new_d = Sink.getElmByRID(link.label.replaced_ID)
		# if new_d is None:
		# 	raise ValueError('here')
	new_plan.CausalLinkGraph.addEdge(UW[link.source.position], UW[link.sink.position], new_d)

	if remove_flaw:
		flaws = new_plan.flaws.flaws
		f = Flaw((UW[link.sink.position], new_d), 'opf')
		if f in flaws:
			new_plan.flaws.remove(f)