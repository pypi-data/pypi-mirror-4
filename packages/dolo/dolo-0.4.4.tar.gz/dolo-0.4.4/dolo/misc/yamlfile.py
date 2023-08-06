from __future__ import division

from dolo.symbolic.symbolic import Variable,Parameter,Shock,Equation
from dolo.symbolic.model import Model
from collections import OrderedDict
import yaml
import sympy
import re

def iteritems(d):
    return zip(d.keys(), d.values())

def parse_yaml_text(txt,verbose=False):
    '''
Imports the content of a modfile into the current interpreter scope
'''
    txt = txt.replace('..','-')
    txt = txt.replace('--','-')
    txt = txt.replace('^','**')
    raw_dict = yaml.load(txt)

    if verbose == True:
        print('YAML file successfully parsed')

    declarations = raw_dict['declarations']
    # check
    if 'variables' not in declarations:
        variables_groups = OrderedDict()
        for vtype in declarations.keys():
            if vtype not in ('shocks','parameters'):
                variables_groups[vtype] = [Variable(vn) for vn in declarations[vtype]]
        variables_ordering = sum(variables_groups.values(),[])
    else:
        vnames = declarations['variables']
        variables_ordering = [Variable(vn) for vn in vnames]
        variables_groups = None

    parameters_ordering = [Parameter(vn) for vn in declarations['parameters']]

    shocks_ordering = [Shock(vn) for vn in declarations['shocks']]

    context = [(s.name,s) for s in variables_ordering + parameters_ordering + shocks_ordering]
    context = dict(context)

    from dolo.symbolic.symbolic import timeshift as TS
    context['TS'] = TS
    if 'horrible_hack' in raw_dict:
        tt = raw_dict['horrible_hack']
        exec(raw_dict['horrible_hack'],context)


    # add some common functions
    for f in [sympy.log, sympy.exp,
              sympy.sin, sympy.cos, sympy.tan,
              sympy.asin, sympy.acos, sympy.atan,
              sympy.sinh, sympy.cosh, sympy.tanh,
              sympy.pi, sympy.sign]:
        context[str(f)] = f
    context['sqrt'] = sympy.sqrt

    import re
    # we recognize two kinds of equations:
    # lhs = rhs
    # lhs | comp where comp is a complementarity condition

    equations = []
    equations_groups = OrderedDict()
    raw_equations = raw_dict['equations']
    if isinstance(raw_equations,dict): # tests whether there are groups of equations
        for groupname in raw_equations.keys():
            equations_groups[groupname] = []
            for raw_eq in raw_equations[groupname]: # Modfile is supposed to represent a global model. TODO: change it
                teqg = raw_eq.split('|')
                teq = teqg[0]
                if '=' in teq:
                    lhs,rhs = str.split(teq,'=')
                else:
                    lhs = teq
                    rhs = '0'
                try:
                    lhs = eval(lhs,context)
                    rhs = eval(rhs,context)
                except Exception as e:
                    print('Error parsing equation : ' + teq)
                    print( str(e) )
                    raise e

                eq = Equation(lhs,rhs)
                eq.tag(eq_type=groupname)
                if len(teqg)>1:
                    comp = teqg[1]
                    eq.tag(complementarity=comp)
                equations.append(eq)
                #equations_groups[groupname].append( eq )
    else:
        for teq in raw_equations:
            if '=' in teq:
                lhs,rhs = str.split(teq,'=')
            else:
                lhs = teq
                rhs = '0'
            try:
                lhs = eval(lhs,context)
                rhs = eval(rhs,context)
            except Exception as e:
                print('Error parsing equations : ' + teq)
                print(str(e))
            eq = Equation(lhs,rhs)
            equations.append(eq)
        equations_groups = None

    parameters_values = {}
    init_values = {}
    covariances = None
    if 'calibration' in raw_dict:
        calibration = raw_dict['calibration']
        if 'parameters' in calibration:
            parameters_values = [ (Parameter(k), eval(str(v),context)) for k,v in iteritems(calibration['parameters']) ]
            parameters_values = dict(parameters_values)
        #steady_state = raw_dict['steady_state']
        if 'steady_state' in calibration:
            init_values = [ (Variable(vn), eval(str(value),context)) for vn,value in iteritems(calibration['steady_state']) ]
            init_values = dict(init_values)
        if 'covariances' in calibration:
            context['sympy'] = sympy
            covariances = eval('sympy.Matrix({0})'.format( calibration['covariances'] ), context)
        else:
            covariances = None # to avoid importing numpy

    model_dict = {
        'variables_ordering': variables_ordering,
        'parameters_ordering': parameters_ordering,
        'shocks_ordering': shocks_ordering,
        'variables_groups': variables_groups,
        'equations_groups': equations_groups,
        'equations': equations,
        'parameters_values': parameters_values,
        'init_values': init_values,
        'covariances': covariances
    }

    if 'model_type' in raw_dict:
        model_dict['model_type'] = raw_dict['model_type']
    model_dict['original_data'] = raw_dict

    model = Model(**model_dict)
    model.check_consistency(auto_remove_variables=False)
    return model

def yaml_import(filename,verbose=False):
    '''Imports model defined in specified file'''
    import os
    basename = os.path.basename(filename)
    fname = re.compile('(.*)\.yaml').match(basename).group(1)
    f = open(filename)
    txt = f.read()
    model = parse_yaml_text(txt,verbose=verbose)
    model['name'] = fname
    return model
