from __future__ import absolute_import
from __future__ import print_function
import sys
import os
from bidict import bidict
from optparse import OptionParser
from collections import deque
from copy import deepcopy
import pandas as pd
import graph_tool.all as gt
import logging
# the next line can be removed after installation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pyverilog.utils.version
from pyverilog.vparser.parser import parse
import pyverilog.vparser.ast as pvast

logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)

def workTheTree(t):
    # inputs = set([])
    # outputs = set([])
    inputs = []
    outputs = []
    modules = []

    def showChidren(t,dict_={}):
        # print(type(t))
            # if nodes[-1]:
        if(type(t) == pvast.Input):
            # print (dir(t))
            # print (t.name)
            inputs.append(t.name)
            # print ("    {}".format(t))
            # print ("    {}".format(t.children()))
        if(type(t) == pvast.Output):
            outputs.append(t.name)
        if(type(t) == pvast.ModuleDef):
            print(t.name)
            print(t.paramlist.params)
            print([x.name for x in t.portlist.ports])
            print()
            modules.append(t)

        for i in t.children():
            showChidren(i)
    showChidren(t)
    # print(inputs)
    # print(outputs)
    print(modules)


class KnownModule(object):
    known_modules = {}
    def __init__(self,defin):
        wire_dict = {}
        self.unnamed_instance_number = 0
        self.nodes = []
        self.inputs = []
        self.outputs = []
        self.mod_def = defin
        self.wires  = []
        self.inner_modules = {}
        self.nametomodule = {}
        self.edgelist = []
        edgelist2 = []
        self.graph = gt.Graph()
        logger.info(defin.name)
        self.node_name = self.graph.new_vertex_property("object")
        self.snode_name = self.graph.new_vertex_property("string")
        # self.strnode_name = self.graph.new_vertex_property("object")
        # print(defin.paramlist.params)
        # print([x.name for x in defin.portlist.ports])
        self.ports = bidict({x.name:i for i,x in enumerate(defin.portlist.ports)})
        # self.ports.update({i:x.name for i,x in enumerate(defin.portlist.ports)})
        logging.info(self.ports)
        # print([x for x in defin.items])-

        for item in defin.items:
            if(type(item) == pvast.Decl):
                for decl in item.list:
                    if(type(decl) == pvast.Input):
                        # print("Input: {}".format(decl.name))
                        # self.inputs.append(self.ports[decl.name])
                        self.inputs.append(decl.name)
                    if(type(decl) == pvast.Output):
                        # print("Output: {}".format(decl.name))
                        self.outputs.append(decl.name)
                    if(type(decl) == pvast.Wire):
                        self.wires.append(decl.name)
                    self.nodes.append(decl.name)
                    # if(type(decl) == pvast.Output):

            if(type(item) == pvast.InstanceList):
                # print(dir(item))
                # print(item.instances)
                for instance in item.instances:
                    # pass

                    logger.debug("{}({})".format(instance.module,",".join([repr(x.argname) for x in instance.portlist])))
                    mod = self.known_modules[instance.module]
                    if instance.name == '':
                        instance.name = "_un_{}".format(str(self.unnamed_instance_number).zfill(3))
                        self.unnamed_instance_number +=1
                    logger.debug(instance.name)
                    self.nametomodule[instance.name] = instance.module
                    self.inner_modules.setdefault(instance.module,set([]))
                    self.inner_modules[instance.module].add(instance.name)
                    # if(instance.name == ''):
                    # self.inner_modules[instance.name] = (deepcopy(mod))

                    # print(mod)
                    # print([(x,y) for (x,y) in zip(mod.mod_def.portlist.ports,instance.portlist)])
                    # print([((instance.name,x.name),repr(y.argname)) for (x,y) in zip(mod.mod_def.portlist.ports,instance.portlist)])
                    # self.edgelist.extend([((instance.name,x.name),repr(y.argname),x.name in mod.outputs,repr(y.argname) in self.outputs) for (x,y) in zip(mod.mod_def.portlist.ports,instance.portlist)])
                    # self.edgelist.extend([((instance.name,x.name),repr(y.argname)) for (x,y) in zip(mod.mod_def.portlist.ports,instance.portlist)])
                    for (x,y) in zip(mod.mod_def.portlist.ports,instance.portlist):
                        # print (x.name,y.argname)
                        ymod = None
                        if repr(y.argname) in self.inputs:
                            ymod = 'inputs'
                        if repr(y.argname) in self.outputs:
                            ymod = 'outputs'
                        elif repr(y.argname) in self.wires:
                            ymod = 'wires'

                        conntuple = None
                        if x.name in mod.inputs:
                            # print("{} -> {}".format((ymod,repr(y.argname)),(instance.name,x.name)))
                            # xnode = self.graph.add_vertex()
                            # ynode = self.graph.add_vertex()
                            conntuple = ((ymod,repr(y.argname)),(instance.name,x.name))
                        elif x.name in mod.outputs:
                            # print("{} -> {}".format((instance.name,x.name),(ymod,repr(y.argname))))
                            # if ymod == 'wires':
                                # wire_dict[repr(y.argname)] = (instance.name,x.name)
                            conntuple = ((instance.name,x.name),(ymod,repr(y.argname)))

                        # if conntuple[0][0] == 'wires':
                            # conntuple[0] = wire_dict.pop(conntuple[0][1])
                        # print ("{} is conntuple and {} is what im looking at".format(conntuple,conntuple[1][0]))
                        if conntuple[1][0] == 'wires':
                            wire_dict[conntuple[1][1]] = conntuple[0]
                        else:
                            edgelist2.append(conntuple)


                        # if ymod == 'wires':
                            # If last element appended was a wire, then store it in a dict and reuse it wherever it is used as an input
                            # last_element = self.e
                            # wire_dict[repr(y.argname)] = edgelist2[-1][1]
                            # pass
                    # print(mod.mod_def.portlist.ports)
                    # print(instance.portlist)-

                    # for x,y in edgelist2:
                        # if x[0] == 'wires':

        logger.debug("\n-\n-")
        # print (self.wires)
        logger.debug(wire_dict)
        logger.debug("edgelist")
        self.edgelist = []
        for x,y in edgelist2:
            a,b = x,y
            if x[0] == 'wires':
                a = wire_dict[x[1]]
            self.edgelist.append((a,b))
            node_a = self.graph.add_vertex()
            self.node_name[node_a] = a
            self.snode_name[node_a] = str(a)
            node_b = self.graph.add_vertex()
            self.node_name[node_b] = b
            self.snode_name[node_b] = str(b)
            self.graph.add_edge(node_a,node_b)

        # print(self.edgedict)
        # node_name = g.new_vertex_property("string")
        # for x,y in self.edgelist:
            # g.add
        logger.info("\n"+"\n".join((str(x) for x in self.edgelist)))
        logger.info("\n\n")
        # print("\n".join([repr(x) for x in self.edgelist]))
        logger.debug(self.graph.get_vertices())
        logger.debug(self.graph.get_edges())
        logger.debug("")
        logger.debug("Property map is")
        logger.debug(self.node_name)
        # print({k:v for k,v in self.node_name})
        # gt.graph_draw(self.graph)
        # gt.graph_draw(self.graph, vertex_text=self.snode_name, vertex_font_size=12)
        # if not self.edgelist:



        # print(self.nodes)
        # print(self.nodes)
        # if self.edgelist:
            # df = pd.DataFrame(self.edgelist)
            # print(df)
            # for i,group in df.groupby(0):
                # print(group)
                # print()
        # node_level = {}
        # for i in self.inputs:
        #     node_level[i] = 0
        # for mod,node in self.edgelist:
        #     # pd.
        #     level = node_level.get(node,None)
        #     if level is None:
        #         pass


        self.known_modules[self.mod_def.name] = self

        # print(self.inputs)
        # print(self.outputs)


def getmodules(t):
    # print(dir(t))
    modules = []
    # print(t.description)
    # print("\n".join([repr(x) for x in t.description.definitions]))
    for defin in t.description.definitions:
        modules.append(KnownModule(defin))
        # print(defin.default_nettype)
        # defin.show()
        # print(defin)
        # print()
    return modules

def main():
    INFO = "Verilog code parser"
    VERSION = pyverilog.utils.version.VERSION
    USAGE = "Usage: python example_parser.py file ..."

    def showVersion():
        print(INFO)
        print(VERSION)
        print(USAGE)
        sys.exit()

    optparser = OptionParser()
    optparser.add_option("-v","--version",action="store_true",dest="showversion",
                         default=False,help="Show the version")
    optparser.add_option("-I","--include",dest="include",action="append",
                         default=[],help="Include path")
    optparser.add_option("-D",dest="define",action="append",
                         default=[],help="Macro Definition")
    (options, args) = optparser.parse_args()

    filelist = args
    if options.showversion:
        showVersion()

    for f in filelist:
        if not os.path.exists(f): raise IOError("file not found: " + f)

    if len(filelist) == 0:
        showVersion()

    ast, directives = parse(filelist,
                            preprocess_include=options.include,
                            preprocess_define=options.define)

    # print(ast.children()[0].children()[0].children())
    # showChidren(ast)
    # workTheTree(ast)
    getmodules(ast)

    for lineno, directive in directives:
        print('Line %d : %s' % (lineno, directive))
        
if __name__ == '__main__':
    main()
