import re
import logging
import copy
import smtplib
import os
from email.mime.text import MIMEText
import chef
from fabric.api import env
import sys
import requests
import json
import argparse

class BadChefParametersException(Exception):
    pass

class BadFabricParameters(Exception):
    pass


class ChefFab(object):

    def _parse_tasks_and_set(self):
        #Parse arguments and get tasks
        parser = argparse.ArgumentParser(description='Fabric tasks.')
        parser.add_argument('tasks', metavar='N', type=str, nargs='+',
                            help='tasks to be run')
        parser.add_argument("--set",type=str,required=False)
        args, unknown = parser.parse_known_args()

        return (args.tasks,args.set)

    def __init__(self,*args,**config):
        #initialize pychef
        self.api = chef.autoconfigure()
        self.config = config

        #Parse tasks and set
        self.tasks,self.setdata = self._parse_tasks_and_set()
        
        #Validation Fabric Environment
        self._validate()

        #Initialize Event Data
        self.event_payload = {
            'what' : json.dumps(self.tasks),
            'data' : self.setdata,
            'tags' : [env.get("role") or env.get("names") or env.get("name")]
            }

        #Determine and limit hosts
        def resolve_node_attr(node,dot_notation_str):
            node_data = copy.copy(node)
            for attr in dot_notation_str.split("."):
                if not node_data.get(attr):
                    raise BadChefParametersException("attr %s does not exist for node %s" % (dot_notation_str,node.name))
                node_data = node_data.get(attr)
                
            return node_data
                

        self.node_data_map = dict([(resolve_node_attr(node,config.get("ipaddress_attr","ipaddress")),node) for node in self._get_nodes()])
        env.hosts = self.node_data_map.keys()
        
        if env.get("start") or env.get("stop"):
            env.hosts = env.hosts[int(env.start) or 0:int(env.stop) or len(env.hosts)]

        if self.config.get("event_type"):
            for task in self.tasks:
                self.post_event(task,self.config.get("event_type"))

    def post_event(self,task_name,event_type):
        '''Post an event that this is happening. 
           Currently Graphite is the only
           event aggregate that implements this interface
           '''

        if event_type == "graphite":
            self._post_to_graphite()
        elif event_type == "email":
            self._post_to_email()
        else:
            logging.error("Invalid event type: %s" % event_type)
                
    def _post_to_graphite(self):
        if not self.config.get("graphite_events_endpoint"):
            logging.error("Error! Graphite event specified, but you haven't specified your graphite endpoint")
            return

        try:
            headers = {'content-type': 'application/json'}
            res = requests.post(self.config.get("graphite_events_endpoint"),
                                data=json.dumps(self.event_payload),
                                headers=headers)
            
        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout) as e:
            print "Error connecting to graphite to post event"
            print "Continuing anyway..."

    def _post_to_email(self):
        if not self.config.get("email_event_recipient") or \
                not self.config.get("sendgrid_username") or \
                not self.config.get("sendgrid_password"):
            logging.error("Error! Email event specified, but you don't have the right constants configured in py")
            return
            
        msg = MIMEText("\n".join(["%s: %s" % (key,value) for key,value in self.event_payload.items()]))
        msg['Subject'] = 'cheffab alert: %s on %s' % (self.event_payload['what'],self.event_payload['data'])
        msg['From'] = "root@localhost"
        msg['To'] = self.config.get("email_event_recipient")

        try:
            s = smtplib.SMTP(host='smtp.sendgrid.net',port=587)

            s.login(self.config.get("sendgrid_username"),
                    self.config.get("sendgrid_password"))

            s.sendmail("root@localhost", 
                       [self.config.get("email_event_recipient")], 
                       msg.as_string())
            s.quit()

        except smtplib.SMTPException:
            logging.error("Failed to send email event for %s" % self.event_payload['what'])

    def _validate(self):
        if (not env.get("name") and 
            not env.get("names") and 
            (not env.get("environment") or not env.get("role"))):
            raise BadChefParametersException("Missing parameters. Please include both role and environment")

    def _get_nodes(self):
        #Single name specified, should only return one node
        if env.get("name"):
            query_s = 'name:%s' % env.get("name")
    
        #Else if names are specified, choose all those
        elif env.get("names"):
            query_s = " OR ".join(["name:%s" % name for name in env.get("names")])

        
        #Else, distinguish by role and environment.
        elif env.get("role") and env.get("environment"):
            query_s = 'roles:%s AND chef_environment:%s' % (env.get("role"),env.get("environment"))

        else:
            raise Exception("Error, need at least a role and environment to choose nodes.")

        nodes = chef.Search('node', q=query_s,api=self.api)
        return sorted([node.object for node in nodes],key= lambda x: x.name)
