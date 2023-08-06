import coinor.pulp as pulp

from dipapi import DipAPI

from _dippy import *

from collections import defaultdict

class DipError(Exception):
    """
    Dip Exception
    """

_Solve = Solve
def Solve(prob, params=None):
    """
    Solve a DipProblem instance, returning a solution object

    @param prob A DipProblem instance to solve
    @param params A dictionary of parameters to pass to DIP
    """

    # params is a dictionary, keys are strings, values are
    # strings or dictionaries

    # if value is a dictionary, key is a section, and items
    # of dictionary are names/values

    # if value is a string, then section is NULL and key is name
    # for these parameters we also assign them to the 'DECOMP'
    # section as a convenience

    # the dictionary is converted into a dictionary of
    # strings indexed by (section, name) tuples

    processed = {}
    if params is None:
        params = {}

    if prob.branch_method == None:
        params['pyBranchMethod'] = '0'
    if prob.post_process == None:
        params['pyPostProcess'] = '0'
    if prob.relaxed_solver == None:
        params['pyRelaxedSolver'] = '0'
    if prob.is_solution_feasible == None:
        params['pyIsSolutionFeasible'] = '0'
    
    if (prob.generate_cuts == None) and (prob.generate_cuts_from_node == None):
        params['pyGenerateCuts'] = '0'

    if prob.generate_cuts != None:
        prob.gen_cuts = True
    else:
        prob.gen_cuts = False
    if prob.generate_cuts_from_node != None:
        prob.gen_cuts_node = True
    else:
        prob.gen_cuts_node = False
    
    if prob.heuristics == None:
        params['pyHeuristics'] = '0'
    if prob.init_vars == None:
        params['pyInitVars'] = '0'
    if prob.is_solution_feasible == None:
        params['pyIsSolutionFeasible'] = '0'

    for key, value in params.items():
        valid_types = (basestring, int, float)
        if not isinstance(key, basestring):
            raise DipError("Bad key in parameter dictionary, expecting string")
        if isinstance(value, dict):
            section = key
            for name, param_val in value.items():
                if not isinstance(param_val, valid_types):
                    raise DipError("Bad value '%s' in parameter dictionary, expecting string or number" % param_val)
                processed[(section, name)] = str(param_val)
        elif isinstance(value, valid_types):
            # add this parameter to both the 'None' section and the 'DECOMP' section
            processed[(None, key)] = str(value)
            processed[('DECOMP', key)] = str(value)
        else:
            raise DipError("Bad value '%s' in parameter dictionary, expecting string" % value)

    # DIP only solves minimisation problems
    if prob.sense == pulp.LpMaximize:
        raise DipError("DIP assumes a minimize objective, but DipProblem has maximize objective.\n" +
                       "Use prob.sense = pulp.LpMinimize and prob.objective *= -1 to remedy")
    
    # DIP only allows non-negative variables. This is difficult
    # to transform automatically, so request re-formulation
    for v in prob.variables():
        if v.lowBound < 0:
            raise DipError("Variable %s has negative lower bound, please re-formulate using sum of non-negative variables" % v.name)
        
    # call the Solve method from _dippy
    try:
        status, message, solList, dualList = _Solve(prob, processed)
        # solList  is a list of (col_name, value) pairs
        # dualList is a list of (row_name, value) pairs
    except:
        print "Error returned from _dippy"
        raise

    if solList is None:
      solution = None
    else:
      solDict = dict(solList)
      setVars = set(prob.variables())
      setSolVars = set(solDict.keys())
      diff = setVars.symmetric_difference(setSolVars)
      if len(diff) > 0:
          raise DipError("Solution and variable list don't match in dippy.Solve")

      solution = solDict
      for v in prob.variables():
        v.varValue = solution[v]
        
    if dualList is None:
        duals = None
    else:
        dualDict = dict([(c.getName(), v) for (c, v) in dualList])
        setCons = set(prob.constraints)
        setDualCons = set(dualDict.keys())
        diff = setCons.symmetric_difference(setDualCons)
        if len(diff) > 0:
            raise DipError("Duals and constraint list don't match in dippy.Solve")

        duals = dualDict

    # return status, message, solution and duals
    return status, message, solution, duals

class DipProblem(pulp.LpProblem, DipAPI):

    def __init__(self, *args, **kwargs):
        # callback functions can be passed to class constructor as keyword arguments
        self.branch_method = kwargs.pop('branch_method', None)
        self.post_process = kwargs.pop('post_process', None)
        self.relaxed_solver = kwargs.pop('relaxed_solver', None)
        self.is_solution_feasible = kwargs.pop('is_solution_feasible', None)
        self.generate_cuts = kwargs.pop('generate_cuts', None)
        self.generate_cuts_from_node = kwargs.pop('generate_cuts_from_node', None)
        self.heuristics = kwargs.pop('heuristics', None)
        self.init_vars = kwargs.pop('init_vars', None)

        super(DipProblem, self).__init__(*args, **kwargs)
        self._subproblem = []
        self.relaxation = RelaxationCollection(self)

    def deepcopy(self):
        # callback functions can be passed to class constructor as keyword arguments
        dipcopy = DipProblem(name = self.name, sense = self.sense)
        dipcopy.branch_method = self.branch_method
        dipcopy.is_solution_feasible = self.is_solution_feasible
        dipcopy.generate_cuts = self.generate_cuts
        dipcopy.heuristics = self.heuristics
        dipcopy.init_vars = self.init_vars

        # This code is taken from pulp.py and needs to be coordinated
        # with pulp.py to avoid errors
        if dipcopy.objective != None:
            dipcopy.objective = self.objective.copy()
        dipcopy.constraints = {}
        for k,v in self.constraints.iteritems():
            dipcopy.constraints[k] = v.copy()
        dipcopy.sos1 = self.sos1.copy()
        dipcopy.sos2 = self.sos2.copy()

        dipcopy._subproblem = self._subproblem[:]
        for k in self.relaxation.keys():
            dipcopy.relaxation[k] = self.relaxation[k].copy()

        return dipcopy
    
    def variables(self):
        """
        Returns a list of the problem variables
        Overrides LpProblem.variables()
        
        Inputs:
            - none
        
        Returns:
            - A list of the problem variables
        """
        variables = {}
        if self.objective:
            variables.update(self.objective)
        for c in self.constraints.itervalues():
            variables.update(c)
        for p in sorted(self.relaxation.keys()):
            for c in self.relaxation[p].constraints.itervalues():
                variables.update(c)
        variables = list(variables)
        variables = sorted(variables, key=lambda variable: variable.name)
        
        return variables

    def getObjective(self):
        """
        Return objective as a dictionary with LpVariables as keys
        and (non-zero) coefficients as values
        """
        return self.objective

    def getRows(self, problem=None):
        """
        Return constraints as a list of dictionaries with LpVariables as keys
        and (non-zero) coefficients as values. Constraints also have
        getName, getLb and getUb methods (i.e., a LpConstraint)

        problem = None implies the master problem, otherwise problem
        is a subproblem
        """

        if problem is None:
            problem = self

        for n, c in problem.constraints.iteritems():
            if c.name == None:
                c.name = n
        constraints = problem.constraints.values()

        return constraints

    def getCols(self, problem=None):
        """
        Returns a list of variables. Variables have getName, getLb,
        getUb and isInteger methods

        problem = None implies the master problem, otherwise problem
        is a subproblem
        """

        if problem is None:
            variables = self.variables()
        else:
            variables = {}
            for c in problem.constraints.itervalues():
                variables.update(c)
            variables = list(variables)
            variables = sorted(variables, key=lambda variable: variable.name)

        return variables

    def getRelaxsAsDict(self):
        """
        Returns the relaxation subproblems as a dictionary with keys as
        defined by the user and values as subproblems
        """
        return self.relaxation.dict

    def writeRelaxed(self, block, filename, mip = 1):
        """
        Write the given block into a .lp file.
        
        This function writes the specifications (NO objective function,
        constraints, variables) of the defined Lp problem to a file.
        
        Inputs:
            - block -- the key to the block to write
            - filename -- the name of the file to be created.          
                
        Side Effects:
            - The file is created.
        """
        relaxation = self.relaxation[block]
        f = file(filename, "w")
        f.write("\\* "+relaxation.name+" *\\\n")
        f.write("Subject To\n")
        ks = relaxation.constraints.keys()
        ks.sort()
        for k in ks:
            f.write(relaxation.constraints[k].asCplexLpConstraint(k))
        vs = relaxation.variables()
        vs.sort()
        # Bounds on non-"positive" variables
        # Note: XPRESS and CPLEX do not interpret integer variables without 
        # explicit bounds
        if mip:
            vg = [v for v in vs if not (v.isPositive() and \
                                        v.cat == pulp.LpContinuous) \
                and not v.isBinary()]
        else:
            vg = [v for v in vs if not v.isPositive()]
        if vg:
            f.write("Bounds\n")
            for v in vg:
                f.write("%s\n" % v.asCplexLpVariable())
        # Integer non-binary variables
        if mip:
            vg = [v for v in vs if v.cat == pulp.LpInteger and \
                                   not v.isBinary()]
            if vg:
                f.write("Generals\n")
                for v in vg: f.write("%s\n" % v.name)
            # Binary variables
            vg = [v for v in vs if v.isBinary()]
            if vg:
                f.write("Binaries\n")
                for v in vg: f.write("%s\n" % v.name)
        f.write("End\n")
        f.close()
        
    def chooseBranchSet(self, xhat):
        """
        Finds the best branch for a fractional solution

        Inputs:
        xhat (list of (LpVariable, value) tuples) = list of solution values for all variables

        Output:
        down_lb, down_ub, up_lb, up_ub (tuple of (LpVariable, value) dictionaries) =
        lower and upper bounds for down branch, lower and upper bounds for up branch
        """

        if not self.branch_method:
            return None

        xhatDict = dict(xhat)
        setVars = set(self.variables())
        setXhatVars = set(xhatDict.keys())
        diff = setVars.symmetric_difference(setXhatVars)
        if len(diff) > 0:
            raise DipError("Solution and variable list don't match in chooseBranchSet")

        return self.branch_method(self, xhatDict)

    def decipherNode(self, output):
        outputDict = dict(output)
        if "xhat" in outputDict.keys():
            xhat = outputDict["xhat"]
            outputDict["xhat"] = dict(xhat)
        if "bounds" in outputDict.keys():
            bounds = outputDict["bounds"]
            outputDict["bounds"] = dict(bounds)
            
        return outputDict

    def postProcessNode(self, node):
        """
        Returns information from the node that has just been processed.

        Inputs:
        output (list of (parameter, value) tuples) = list of output values from the node
        """
        if self.post_process:

            nodeDict = self.decipherNode(node)
                
            self.post_process(self, nodeDict)

    def solveRelaxed(self, key, redCostX, convexDual):
        """
        Returns solutions to the whichBlock relaxed subproblem

        Inputs:  
        key (Python Object) = key of relaxed subproblem to be solved
        redCostX (list of (LpVariable, value) tuples) = list of reduced costs for all variables
        convexDual (float) = dual for convexity constraint for this relaxed subproblem

        Output:
        varList (list of (cost, reduced cost, (LpVariable, value) dictionaries)) =
        solution for this relaxed subproblem expressed as a cost, reduced cost and
        dictionary of non-zero values for variables
        """

        # transform redCostX into a dictionary
        redCostDict = dict(redCostX)
        setVars = set(self.variables())
        setRedCostVars = set(redCostDict.keys())
        diff = setVars.symmetric_difference(setRedCostVars)
        if len(diff) > 0:
            print diff
            raise DipError("Reduced cost and variable list don't match in solveRelaxed")

        return self.relaxed_solver(self, key, redCostDict, convexDual)

    def isUserFeasible(self, sol, tol):
        """
        Lets the user decide if an integer solution is really feasible

        Inputs:
        sol (list of (LpVariable, value) tuples) = list of solution values for all variables
        tol (double) = zero tolerance

        Outputs:
        (boolean) = false if not feasible (generate cuts) or true if feasible
        """
        if not self.is_solution_feasible:
            return None

        solDict = dict(sol)
        setVars = set(self.variables())
        setSolVars = set(solDict.keys())
        diff = setVars.symmetric_difference(setSolVars)
        if len(diff) > 0:
            raise DipError("Solution and variable list don't match in isUserFeasible")

        return self.is_solution_feasible(self, solDict, tol)

    def generateCuts(self, node):
        """
        Lets the user generate cuts to remove fractional "pieces" of xhat

        Inputs:
        node (list of (string, object) tuples) = list of node properties

        Output:
        cutList (list of LpConstraints) =
        cuts for this fractional solution expressed as a list LpConstraints,
        i.e., a dictionary with LpVariables as keys and (non-zero) coefficients
        as values with getName, getLb and getUb bound methods
        """
        if (not self.gen_cuts) and (not self.gen_cuts_node):
            return None

        nodeDict = self.decipherNode(node)
        xhatDict = nodeDict["xhat"]
        setVars = set(self.variables())
        setXhatVars = set(xhatDict.keys())
        diff = setVars.symmetric_difference(setXhatVars)
        if len(diff) > 0:
            raise DipError("Solution and variable list don't match in generateCuts")

        # Generate a list of cuts as LpConstraints
        if self.gen_cuts:
            cuts = self.generate_cuts(self, xhatDict)
        else:
            cuts = []

        if self.gen_cuts_node:
            cuts.extend(self.generate_cuts_from_node(self, nodeDict))
                
        return cuts

    def solveHeuristics(self, xhat, costX):
        """
        Lets the user generate (heuristic) solutions from a fractional solution

        Inputs:
        xhat  (list of (LpVariable, value) tuples) = list of solution values for all variables
        costX (list of (LpVariable, value) tuples) = list of costs for all variables

        Outputs:
        solList (list of (LpVariable, value) dictionaries) =
        solutions found from this fractional solution expressed as a
        dictionary of non-zero values for variables
        """

        if not self.heuristics:
            return None

        # transform xhat into a dictionary
        xhatDict = dict(xhat)
        setVars = set(self.variables())
        setXhatVars = set(xhatDict.keys())
        diff = setVars.symmetric_difference(setXhatVars)
        if len(diff) > 0:
            raise DipError("Solution and variable list don't match in solveHeuristics")

        # transform costs into a dictionary
        costDict = dict(costX)
        setCostVars = set(costDict.keys())
        diff = setVars.symmetric_difference(setCostVars)
        if len(diff) > 0:
            raise DipError("Cost and variable list don't match in solveHeuristics")

        return self.heuristics(self, xhatDict, costDict)

    def generateInitVars(self):
        """
        Returns initial solutions to relaxed subproblems

        Inputs:
        None

        Output:
        varList (list of (subproblem key, (cost, (LpVariable, value) dictionaries))) =
        initial solutions for the relaxed subproblems expressed as a cost and
        dictionary of non-zero values for variables
        """

        if not self.init_vars:
            return None

        return self.init_vars(self)
    
class RelaxationCollection(object):
    """
    A simple defaultdict for holding relaxation problems
    """
    PROBLEM_CLASS = pulp.LpProblem


    def __init__(self, parent):
        self.parent = parent
        self.dict = {}

    def __getitem__(self, name):
        if name not in self.dict:
            self.dict[name] = self.PROBLEM_CLASS()
        return self.dict[name]

    def __setitem__(self, name, value):
        self.dict[name] = value

    def keys(self):
        return self.dict.keys()

    def values(self):
        return self.dict.values()



