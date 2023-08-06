#!/usr/bin/env python

import argparse
import os
import chef

api = None

class NoNodesFound(Exception):
    pass

def main(args):

    node_query = chef.Node(args.query,api=api)
    if node_query.exists:
        nodes = [node_query]
    else:
        if args.all:
            node_query = chef.Search("node","roles:%s AND chef_environment:%s" % (args.query,args.environment),api=api)
        else:
            node_query = chef.Search("node","roles:%s AND chef_environment:%s" % (args.query,args.environment),rows=args.num+args.offset,api=api)
    

        if len(node_query)==0:
            raise NoNodesFound
    
        nodes = [n.object for n in node_query[args.offset:len(node_query)]]

    attr_recurse = args.a.split(".")
    for attr in attr_recurse:
        nodes = filter(lambda x: x,[n.get(attr) for n in nodes])

    command_args = ["%s@%s" % (args.user,n) for n in nodes]

    if args.forwardagent:
        if len(nodes)==1:
            command_args+=["-A"]
        else:
            command_args+= ["--ssh_args","-A"]

    print " ".join(command_args)

    if not nodes:
        print "No Nodes Found"
        return 1

    if len(nodes)==1:
        os.execvp("ssh",["blah blah blah"] + command_args)
    else:
        os.execvp("csshx",["blah blah blah"]+command_args)
    

def list_roles(args):
    chef_roles = chef.Search("role","name:*",api=api)
    for role in chef_roles:
        print role.get("name")

def run():
    global api
    api = chef.autoconfigure()
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("query",type=str,help='Server role to ssh into')
    arg_parser.add_argument("--num",type=int,default=1,help='Number of servers to ssh into')
    arg_parser.add_argument("--offset",type=int,default=0,help='Offset servers')
    arg_parser.add_argument("--all",action="store_true",default=False,help='Number of servers to ssh into')
    arg_parser.add_argument("--environment",type=str,default="production",help='Server Environment')
    arg_parser.add_argument("--user",type=str,default="ubuntu",help='SSH user')
    arg_parser.add_argument("-a",type=str,default="ipaddress",help='Server Environment')
    arg_parser.add_argument("-A","--forwardagent",action="store_true",default=False,help='Forward your ssh agent')
    args = arg_parser.parse_args()

    #Hacky way to make first argument both a directive and a variable 
    if args.query == "list":
        list_roles(args)
    else:
        main(args)
        
