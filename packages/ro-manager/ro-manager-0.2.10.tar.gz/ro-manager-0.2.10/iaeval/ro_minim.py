# ro_minim.py

"""
Research Object minimum information model access functions
"""

import re
import urllib
import urlparse
import logging

log = logging.getLogger(__name__)

import rdflib
import rdflib.namespace
from uritemplate import uritemplate

from rocommand import ro_manifest
from rocommand import ro_namespaces
from rocommand.ro_namespaces import RDF, RDFS

minimnsuri = rdflib.URIRef("http://purl.org/minim/minim#")
MINIM      = ro_namespaces.makeNamespace(minimnsuri,
            [ "Constraint", "Model", "Requirement", "RequirementRule"
            , "SoftwareEnvironmentRule", "DataRequirementRule", "ContentMatchRequirementRule"
            , "hasConstraint" 
            , "forTarget", "forTargetTemplate", "forPurpose", "onResource", "onResourceTemplate", "toModel"
            , "hasMustRequirement", "hasShouldRequirement", "hasMayRequirement", "hasRequirement"
            , "derives", "reports", "isDerivedBy"
            , "show", "showpass", "showfail", "showmiss", "seq"
            , "aggregates"
            , "command", "response"
            , "forall", "orderby", "exists", "aggregatesTemplate", "isLiveTemplate"
            , "minimallySatisfies", "nominallySatisfies", "fullySatisfies"
            # Result properties
            , "satisfied", "missingMay", "missingShould", "missingMust"
            , "testedConstraint", "testedPurpose", "testedTarget"
            , "minimUri", "modelUri"
            , "tryRequirement", "tryMessage"
            ])

resultnsuri = rdflib.URIRef("http://www.w3.org/2001/sw/DataAccess/tests/result-set#")
RESULT      = ro_namespaces.makeNamespace(resultnsuri,
            [ "binding", "variable", "value"
            ])

def getElementUri(minimbase, elemname):
    """
    Returns URI of element in Minim file
    
    minimbase   is the URI of the Minim file containing the required element
    elemname    is the relative URI of the element - commonly a fragment identifier
    """
    return rdflib.URIRef(urlparse.urljoin(str(minimbase), elemname))

def readMinimGraph(minimuri):
    """
    Read Minim file, return RDF Graph.
    """
    minimgraph = rdflib.Graph()
    minimgraph.parse(minimuri, format="xml")
    return minimgraph

def getConstraints(minimgraph):
    for (target, constraint) in minimgraph.subject_objects(predicate=MINIM.hasConstraint):
        # @@TODO: use property of constraint for this, one day
        c = {'target': target, 'uri': constraint}
        c['target_t']   = minimgraph.value(subject=constraint, predicate=MINIM.forTargetTemplate)
        c['purpose']    = minimgraph.value(subject=constraint, predicate=MINIM.forPurpose)
        c['resource']   = minimgraph.value(subject=constraint, predicate=MINIM.onResource)
        c['resource_t'] = minimgraph.value(subject=constraint, predicate=MINIM.onResourceTemplate)
        c['model']      = minimgraph.value(subject=constraint, predicate=MINIM.toModel)
        yield c
    return

def getConstraint(minimgraph, rouri, target_ref, purpose_regex_string):
    """
    Find constraint matching supplied RO, target and purpose regex
    
    Constraint is returned with:
    targetro_actual  -> URI of resource
    targetres_actual -> URI of target if supplied, else subject of minium:hasConstraint
    resource_actual  -> explicit onResource URI, or expansion of onResourceTemplate with RO URI
    """
    def mkstr(u):
        return u and str(u)
    log.debug("getConstraint: rouri %s, target_ref %s"%(rouri, target_ref))
    target       = target_ref and ro_manifest.getComponentUri(rouri, target_ref)
    log.debug("               target_uri %s"%(target))
    purpose      = purpose_regex_string and re.compile(purpose_regex_string)
    templatedict = {'targetro': urllib.unquote(str(rouri))}
    for c in getConstraints(minimgraph):
        log.debug("- test: target %s purpose %s"%(c['target'],c['purpose']))
        log.debug("- purpose %s, c['purpose'] %s"%(purpose_regex_string, c['purpose']))
        if not purpose or purpose.match(c['purpose']):
            c['targetro_actual']   = mkstr(rouri)
            c['targetres_actual']  = mkstr(target or c['target'])
            c['onresource_actual'] = ( mkstr(c['resource']) or 
                                      (c['resource_t'] and uritemplate.expand(c['resource_t'], templatedict))
                                     )
            if not target:
                # No target specified in request, match any (first) constraint
                return c
            if target == c['target']:
                # Match explicit target specification (subject of minim:hasConstraint)
                return c    
            log.debug("- target %s, c['target_t'] %s"%(target, c['target_t']))
            if target and c['target_t']:
                log.debug("- expand %s"%(uritemplate.expand(c['target_t'], templatedict)))
                if str(target) == uritemplate.expand(c['target_t'], templatedict):
                    # Target matches expanded template from constraint description
                    return c
    return None

def getModels(minimgraph, modeluri=None):
    for (model, p, o) in minimgraph.triples( (modeluri, RDF.type, MINIM.Model) ):
        m = {'uri': model}
        m['label']   = minimgraph.value(subject=model, predicate=RDFS.label)
        m['comment'] = minimgraph.value(subject=model, predicate=RDFS.comment)
        yield m
    return

def getModel(minimgraph, modeluri):
    for m in getModels(minimgraph, modeluri=modeluri):
        return m
    return None

def getRequirements(minimgraph, modeluri):
    def matchRequirement((s, p, o), reqp, reqval):
        req = None
        if p == reqp:
            req = (
                { 'uri':    o
                , 'model':  s
                , 'level':  reqval
                , 'label':  minimgraph.value(subject=o, predicate=RDFS.label)
                })
            ruleuri = minimgraph.value(subject=o, predicate=MINIM.isDerivedBy)
            assert ruleuri, "Requirement %s has no minim:isDerivedBy rule"%(str(o))
            rule = (
                { 'derives':    minimgraph.value(subject=ruleuri, predicate=MINIM.derives) 
                , 'show':       minimgraph.value(subject=ruleuri, predicate=MINIM.show) 
                , 'showpass':   minimgraph.value(subject=ruleuri, predicate=MINIM.showpass)
                , 'showfail':   minimgraph.value(subject=ruleuri, predicate=MINIM.showfail)
                , 'showmiss':   minimgraph.value(subject=ruleuri, predicate=MINIM.showmiss)
                })
            # Create field used for sorting checklist items
            req['seq'] = str( minimgraph.value(subject=s, predicate=MINIM.seq) or
                              rule['show'] or
                              rule['showpass'] )
            ruletype = minimgraph.value(subject=ruleuri, predicate=RDF.type)
            if ruletype == MINIM.DataRequirementRule:
                rule['aggregates']  = minimgraph.value(subject=ruleuri, predicate=MINIM.aggregates)
                req['datarule'] = rule
            elif ruletype == MINIM.SoftwareEnvironmentRule:
                rule['command']  = minimgraph.value(subject=ruleuri, predicate=MINIM.command)
                rule['response'] = minimgraph.value(subject=ruleuri, predicate=MINIM.response)
                req['softwarerule'] = rule
            elif ruletype == MINIM.ContentMatchRequirementRule:
                rule['forall']   = minimgraph.value(subject=ruleuri, predicate=MINIM.forall)
                rule['orderby']  = minimgraph.value(subject=ruleuri, predicate=MINIM.orderby)
                rule['exists']   = minimgraph.value(subject=ruleuri, predicate=MINIM.exists)
                rule['template'] = minimgraph.value(subject=ruleuri, predicate=MINIM.aggregatesTemplate)
                rule['islive']   = minimgraph.value(subject=ruleuri, predicate=MINIM.isLiveTemplate)
                req['contentmatchrule'] = rule
            else:
                assert False, "Unrecognized rule type %s for requirement %s"%(str(ruletype), str(o))
        return req
    for stmt in minimgraph.triples( (modeluri, None, None) ):
        pred_level_list = (
            [ (MINIM.hasMustRequirement, "MUST")
            , (MINIM.hasShouldRequirement, "SHOULD")
            , (MINIM.hasMayRequirement, "MAY")
            ])
        for (pred, level) in pred_level_list:
            r = matchRequirement(stmt, pred, level)
            if r:
                yield r
                break
    return

# End.
