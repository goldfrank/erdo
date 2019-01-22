# erdo version 0.12
# developed by Joe Goldfrank and last modified on 21 Jan
#
#the wizard can make anything happen
#(Howard and Abbas, Foundations of Decision Analysis, Figure 9.3)

# from __future__ import print_function, division
from copy import deepcopy, copy
from graphviz import Digraph

#float to string
def shorten(x):
    return str(round(x, 2))

# default risk-neutral value function
def risk_neutral(x):
    return(x)

#alternative function for testing only
def risk_double(x):
    return 2*x

#uncertainty node
class Uncertainty_node:
    def __init__(self, name='Uncertainty Node', children=[], verbose=False):
        self.u = 0
        self.val = 0
        self.name = name
        self.children = deepcopy(children)
        self.verbose = verbose
        self.cycled = 0
        self.is_test = False
        self.testval = None

    def clone(self, condition = ' copy', cost=0):
        node = Uncertainty_node(name=self.name + condition)
        for c in self.children:
            node.children.append([c[0].clone(condition = condition, cost=cost),c[1]])
        return node

    def child(self, other_node, prob):
        self.children.append([other_node,prob])


    def utility(self):
        self.u = 0
        self.check = 0
        for i in range(len(self.children)):
            self.check += self.children[i][1]
        if self.check != 1:
            if self.verbose == True:
                print('Uncertainty node \'' + self.name + '\' probabilities do not sum to one, normalizing')
            for i in range(len(self.children)):
                if self.check != 0:
                    self.children[i][1] = self.children[i][1] / self.check
                if self.check == 0:
                    self.children[i][1] = 0
        for i in range(len(self.children)):
            self.u += self.children[i][0].utility() * self.children[i][1]
        return self.u

    def node(self):
        return 'uncertainty'

    def value(self):
        self.val = 0
        self.check = 0
        for i in range(len(self.children)):
            self.check += self.children[i][1]
        if self.check != 1:
            if self.verbose == True: print('Uncertainty node \'' + self.name + '\' probabilities do not sum to one, normalizing')
            for i in range(len(self.children)):
                self.children[i][1] = self.children[i][1] / self.check
        for i in range(len(self.children)):
            self.val += self.children[i][0].value() * self.children[i][1]
        return self.val

    def label(self):
        self.utility()
        if self.is_test == True:
            return (self.name + '\n Expected Utility: ' + shorten(self.u) + '\n Test Value: ' + shorten(self.testval))
        else: return (self.name + '\n Expected Utility: ' + shorten(self.u))

#decision node
class Decision_node:
    def __init__(self, name='Decision Node', children=[]):
        self.val = 0
        self.u = 0
        self.name = name
        self.decision = None
        self.children = deepcopy(children)
        self.is_test = False
        self.is_control = False
        self.testval = None
        self.cost = None

    def clone(self, condition=' copy', cost=0):
        node = Decision_node(name=self.name + condition, children=[])
        for c in self.children:
            node.children.append(c.clone(condition=condition, cost=cost))
        return node

    def child(self, other_node):
        self.children.append(other_node)

    def value(self):
        self.best = 0
        for i in range(len(self.children)):
            if self.children[i].value() >= self.children[0].value(): self.best = i
        self.val = self.children[self.best].value()
        return self.children[self.best].value()

    def utility(self):
        self.best = 0
        for i in range(len(self.children)):
            if self.children[i].utility() >= self.children[0].utility(): self.best = i
        self.u = self.children[self.best].utility()
        self.decision = self.children[self.best].name
        return self.children[self.best].utility()

    def node(self):
        return 'decision'

    def label(self):
        if self.is_test == True: return (self.name + '\n Decision: ' + str(self.decision)  + '\n Expected Utility: ' + shorten(self.u) + '\n Test Value: ' + shorten(self.testval) + '\n Test Cost: ' + shorten(self.cost))
        if self.is_control == True: return (self.name + '\n Decision: ' + str(self.decision)  + '\n Expected Utility: ' + shorten(self.u) + '\n Control Value: ' + shorten(self.testval) + '\n Control Cost: ' + shorten(self.cost))
        return (self.name + '\n Decision: ' + str(self.decision)  + '\n Expected Utility: ' + shorten(self.u))

#value node
class Value_node:
    def __init__(self, val, u=risk_neutral, name='Value Node'):
        if not isinstance(val, (int, float)): raise TypeError('Value node: \'val\' expected an int or float')
        if not callable(u): raise TypeError('Value node: \'u\' expected a function')
        self.val = val
        self.ufunc = u
        self.u = u(val)
        self.name = name
    def utility(self): return self.u
    def value(self): return self.val
    def node(self): return 'value'
    def label(self):
        return (self.name + '\n Utility: ' + shorten(self.u))
    def clone(self, condition = ' copy', cost=0):
        node = Value_node(self.val-cost, name=self.name + condition, u=self.ufunc)
        return node

def add_to_graph(graph, node):
    #check current node type and set shape
    current_node = node
    if current_node.node() == 'decision': graph.attr('node', shape='box')
    if current_node.node() == 'uncertainty': graph.attr('node', shape='ellipse')
    if current_node.node() == 'value': graph.attr('node', shape='octagon')
    #graph.attr('node', shape='underline')
    graph.node(current_node.name, label=current_node.label())
    if current_node.node() == 'value':
        return
    if len(current_node.children) > 0:
        for i in range(len(current_node.children)):
            if current_node.node() == 'uncertainty':
                add_to_graph(graph, current_node.children[i][0])
                graph.edge(current_node.name, current_node.children[i][0].name, label=shorten(current_node.children[i][1]))
            else:
                add_to_graph(graph, current_node.children[i])
                graph.edge(current_node.name, current_node.children[i].name, label='')
    return

def create_graph(top_node, filename='decision_tree'):
    top_node.utility()
    current_node = top_node
    g = Digraph('Decision Tree', filename=filename)
    g.attr(rankdir='LR', size='8,5')
    add_to_graph(g, top_node)
    g.view()

def wave_wand(current, node):
    if current.node() == 'uncertainty':
        for c in current.children:
            if c[0].name[0:len(node)] == node:
                for c in current.children:
                    if c[0].name[0:len(node)] == node: c[1] = 1
                    else: c[1] = 0
                return
            else: wave_wand(c[0], node)
        return
    if current.node() == 'decision':
        for c in current.children:
            wave_wand(c, node)
        return
    if current.node() == 'value': return

def summon_the_wizard(target_graph, target_node, wizard_name='Summon The Wizard', paythewizard=0, condition='Wizard'):
    #the wizard can make *anything* happen
    new = []
    new.append(target_graph.clone(condition = " | " + condition))
    new.append(target_graph.clone(condition = " | No " + condition))
    if isinstance(target_node, str):
        wave_wand(new[0], target_node)
        wizard = Decision_node(name=str(wizard_name) + '?')
        wizard.child(new[0])
        wizard.child(new[1])
        wizard.is_control = True
        wizard.cost = paythewizard
        wizard.testval = (new[0].utility()-new[1].utility())
        return wizard
    if isintance(target_node, (tuple, list)):
        for t in target_node:
            wave_wand(new[0], t)
        wizard = Decision_node(name=str(wizard_name) + '?')
        wizard.is_control = True
        wizard.cost = paythewizard
        wizard.testval = (new[0].utility()-new[1].utility())
        wizard.child(new[0])
        wizard.child(new[1])
        return wizard

def add_control(target_graph, target_node, name='Control', cost=0, condition='Control'):
    return summon_the_wizard(target_graph, target_node, wizard_name=name, paythewizard=cost, condition=condition)

def uncertainty_check(e, unc):
    e = e
    found = 0
    if e.node() == 'decision':
        #print('d - checking ' + str(e.name))
        for c in e.children:
            if c.name[0:len(unc)] == unc:
                #print('found ' + c.name[0:len(unc)])
                found = 1
                if len(c.children) != 2: raise AttributeError('Uncertainty to be tested must only have two possibilities')
                else:
                    negstring = " | \"" + (c.children[0][0].name.split('|')[0]) + "\""
                    posstring = " | \"" + (c.children[1][0].name.split('|')[0]) + "\""
                    negprob = c.children[0][1]
                    posprob = c.children[1][1]
                    return [negstring, posstring, negprob, posprob]
            #for c in e.children:
            temp = uncertainty_check(c, unc)
            if temp != False:
                return temp
    elif e.node() == 'uncertainty':
        #print('u - checking ' + str(e.name))
        for c in e.children:
            if c[0].name[0:len(unc)] == unc:
                #print('found ' + c[0].name[0:len(unc)])
                found = 1
                if len(c[0].children) != 2: raise AttributeError('Uncertainty to be tested must only have two possibilities')
                else:
                    negstring = " | \"" + (c[0].children[0][0].name.split('|')[0]) + "\""
                    posstring = " | \"" + (c[0].children[1][0].name.split('|')[0]) + "\""
                    negprob = c[0].children[0][1]
                    posprob = c[0].children[1][1]
                    return [negstring, posstring, negprob, posprob]
        if found == 0:
            #print ('not found ' + str(e.name))
            for c in e.children:
                #print(c[0].name)
                temp = uncertainty_check(c[0], unc)
                if temp != False:
                    return temp
    elif e.node() == 'value':
        #print('Value node ' + str(e.name))
        return False
    return False

def uncertainty_mod(e, unc, neg, pos):
    found = 0
    if e.node() == 'decision':
        #print('d - checking ' + str(e.name))
        for c in e.children:
            if c.name[0:len(unc)] == unc:
                #print('found ' + c.name[0:len(unc)])
                found = 1
                if len(c.children) != 2: raise AttributeError('Uncertainty to be tested must only have two possibilities')
                else:
                    #print('doing it')
                    #print('before: ' +str(c.children[0][1]))
                    c.children[0][1] = neg
                    c.children[1][1] = pos
                    #print('after: ' +str(c.children[0][1]))
                    return True
            temp = uncertainty_mod(c, unc, pos, neg)
            if temp != False:return temp
    elif e.node() == 'uncertainty':
        #print('u - checking ' + str(e.name))
        for c in e.children:
            if c[0].name[0:len(unc)] == unc:
                #print('found! ' + c[0].name[0:len(unc)])
                found = 1
                if len(c[0].children) != 2: raise AttributeError('Uncertainty to be tested must only have two possibilities')
                else:
                    #print('doing it')
                    #print('before: ' +str(c[0].children[0][1]))
                    c[0].children[0][1] = neg
                    c[0].children[1][1] = pos
                    #print('after: ' +str(c[0].children[0][1]))
                    return True
        if found == 0:
            #print ('not found ' + str(e.name))
            for c in e.children:
                ##print(c[0].name)
                temp = uncertainty_mod(c[0], unc, neg, pos)
                if temp != False: return temp
    elif e.node() == 'value':
        #print('Value node ' + str(e.name))
        return False
    return False


#uncertainty must be one or two levels below the decision
def add_test(decision, uncertainty, truepos=1, trueneg=1, testname='Test', cost=0):
    posstring = ''
    negstring = ''

    if isinstance(uncertainty, str):
        temp = uncertainty_check(decision, uncertainty)
        if temp != False: negstring, posstring, negprob, posprob = temp
        else:
            #print(temp)
            raise AttributeError('Uncertainty node does not exist within specified decision')

        # compute marginal probabilities for test
        # format: test_reality
        pos_pos = posprob * truepos
        neg_pos = posprob * (1-truepos)
        neg_neg = negprob * trueneg
        pos_neg = negprob * (1-trueneg)

        #bayesian inference
        if (pos_pos + pos_neg) == 0:
            pos_postest, neg_postest = 0,0
        else:
            pos_postest = pos_pos / (pos_pos + pos_neg)
            neg_postest = pos_neg / (pos_pos + pos_neg)
        if (neg_pos + neg_neg) == 0:
            pos_negest, neg_negtest = 0,0
        else:
            pos_negtest = neg_pos / (neg_pos + neg_neg)
            neg_negtest = neg_neg / (neg_pos + neg_neg)
        prob_postest = (pos_pos + pos_neg) / (pos_pos + neg_pos + neg_neg + pos_neg)
        prob_negtest = (neg_pos + neg_neg) / (pos_pos + neg_pos + neg_neg + pos_neg)

        new = []
        new.append(decision.clone(condition = negstring))
        new.append(decision.clone(condition = posstring))
        new.append(decision.clone(condition = ' | No Test'))
        #print('--making modifications--')

        '''for c in new[0].children:
            if c.name[0:len(uncertainty)] == uncertainty:
                c.children[0][1] = neg_negtest
                c.children[1][1] = pos_negtest'''
        uncertainty_mod(new[0], uncertainty, neg_negtest, pos_negtest)
        uncertainty_mod(new[1], uncertainty, neg_postest, pos_postest)
        #print(new[0].children[1].children[1][0].children[0][1])
        '''for c in new[1].children:
            if c.name[0:len(uncertainty)] == uncertainty:
                c.children[0][1] = neg_postest
                c.children[1][1] = pos_postest'''

        new_uncertain = Uncertainty_node(name=testname, children=[[new[0], prob_negtest],[new[1], prob_postest]])
        test_decision = Decision_node(name="Test Decision", children=[new_uncertain, new[2]])

        if new_uncertain.utility() - new[2].utility() > 0: test_value = new_uncertain.utility() - new[2].utility()
        else: test_value = 0
        new[0] = (decision.clone(condition = negstring, cost=cost))
        new[1] = (decision.clone(condition = posstring, cost=cost))
        '''for c in new[0].children:
            if c.name[0:len(uncertainty)] == uncertainty:
                c.children[0][1] = neg_negtest
                c.children[1][1] = pos_negtest

        for c in new[1].children:
            if c.name[0:len(uncertainty)] == uncertainty:
                c.children[0][1] = neg_postest
                c.children[1][1] = pos_postest'''
        uncertainty_mod(new[0], uncertainty, neg_negtest, pos_negtest)
        uncertainty_mod(new[1], uncertainty, neg_postest, pos_postest)
        new_uncertain = Uncertainty_node(name=testname, children=[[new[0], prob_negtest],[new[1], prob_postest]])
        test_decision = Decision_node(name="Test Decision", children=[new_uncertain, new[2]])
        test_decision.is_test = True
        test_decision.testval = test_value
        test_decision.cost = cost
        return test_decision
    elif isinstance(uncertainty, (list, tuple)):
        temp = uncertainty_check(decision, uncertainty[0])
        if temp != False: negstring, posstring, negprob, posprob = temp
        else:
            #print(temp)
            raise AttributeError('Uncertainty node does not exist within specified decision')

        # compute marginal probabilities for test
        # format: test_reality
        pos_pos = posprob * truepos
        neg_pos = posprob * (1-truepos)
        neg_neg = negprob * trueneg
        pos_neg = negprob * (1-trueneg)

        #bayesian inference
        if (pos_pos + pos_neg) == 0:
            pos_postest, neg_postest = 0,0
        else:
            pos_postest = pos_pos / (pos_pos + pos_neg)
            neg_postest = pos_neg / (pos_pos + pos_neg)
        if (neg_pos + neg_neg) == 0:
            pos_negest, neg_negtest = 0,0
        else:
            pos_negtest = neg_pos / (neg_pos + neg_neg)
            neg_negtest = neg_neg / (neg_pos + neg_neg)
        prob_postest = (pos_pos + pos_neg) / (pos_pos + neg_pos + neg_neg + pos_neg)
        prob_negtest = (neg_pos + neg_neg) / (pos_pos + neg_pos + neg_neg + pos_neg)

        new = []
        new.append(decision.clone(condition = negstring))
        new.append(decision.clone(condition = posstring))
        new.append(decision.clone(condition = ' | No Test'))
        #print('--making modifications--')

        '''for c in new[0].children:
            if c.name[0:len(uncertainty)] == uncertainty:
                c.children[0][1] = neg_negtest
                c.children[1][1] = pos_negtest'''
        for u in uncertainty:
            uncertainty_mod(new[0], u, neg_negtest, pos_negtest)
            uncertainty_mod(new[1], u, neg_postest, pos_postest)
        #print(new[0].children[1].children[1][0].children[0][1])
        '''for c in new[1].children:
            if c.name[0:len(uncertainty)] == uncertainty:
                c.children[0][1] = neg_postest
                c.children[1][1] = pos_postest'''

        new_uncertain = Uncertainty_node(name=testname, children=[[new[0], prob_negtest],[new[1], prob_postest]])
        test_decision = Decision_node(name="Test Decision", children=[new_uncertain, new[2]])

        if new_uncertain.utility() - new[2].utility() > 0: test_value = new_uncertain.utility() - new[2].utility()
        else: test_value = 0
        new[0] = (decision.clone(condition = negstring, cost=cost))
        new[1] = (decision.clone(condition = posstring, cost=cost))
        '''for c in new[0].children:
            if c.name[0:len(uncertainty)] == uncertainty:
                c.children[0][1] = neg_negtest
                c.children[1][1] = pos_negtest

        for c in new[1].children:
            if c.name[0:len(uncertainty)] == uncertainty:
                c.children[0][1] = neg_postest
                c.children[1][1] = pos_postest'''
        for u in uncertainty:
            uncertainty_mod(new[0], u, neg_negtest, pos_negtest)
            uncertainty_mod(new[1], u, neg_postest, pos_postest)
        new_uncertain = Uncertainty_node(name=testname, children=[[new[0], prob_negtest],[new[1], prob_postest]])
        test_decision = Decision_node(name="Test Decision", children=[new_uncertain, new[2]])
        test_decision.is_test = True
        test_decision.testval = test_value
        test_decision.cost = cost
        return test_decision


#test case
#party problem from Howard and Abbas
#with examples of control and testing
'''from erdo import *

sun_o = Value_node(1, name='Sunshine | Outdoors')
rain_o = Value_node(0, name='Rain | Outdoors')
outdoors = Uncertainty_node(name='Outdoors')
outdoors.child(sun_o, .4)
outdoors.child(rain_o, .6)
sun_p = Value_node(.95, name='Sunshine | Porch')
rain_p = Value_node(.32, name='Rain | Porch')
porch = Uncertainty_node(name='Porch')
porch.child(sun_p, .4)
porch.child(rain_p, .6)
sun_i = Value_node(.57, name='Sunshine | Indoors')
rain_i = Value_node(.67, name='Rain | Indoors')
indoors = Uncertainty_node(name='Indoors')
indoors.child(sun_i, .4)
indoors.child(rain_i, .6)
party = Decision_node(name='Party Location?')
party.child(outdoors)
party.child(porch)
party.child(indoors)
#test = add_test(party, ('Outdoors','Porch','Indoors'), trueneg = .9, truepos = .9, cost=.05)
wizard = summon_the_wizard(party, 'Rain')
create_graph(wizard,filename='party_problem')
#create_graph(party, filename='party')
'''
