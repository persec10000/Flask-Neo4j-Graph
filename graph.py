from flask import Flask, render_template, Blueprint, flash, request, url_for, redirect
import json
import os
from neo4j import GraphDatabase




import pandas as pd
import json
import csv
import os
import glob
from neo4j import GraphDatabase
import time
from flask import Flask
import numpy as np
from random import randrange
import sys
from flask import Flask, render_template
# pyechart imports
#from pyecharts import options as opts
#from pyecharts.charts import Bar
#from pyecharts.globals import CurrentConfig
#from jinja2 import Markup, Environment, FileSystemLoader
#from pyecharts.charts import Graph, Page
#from pyecharts.faker import Collector
import re


#%%

bp = Blueprint('graph', __name__)  # 2020.07.05, removed the param url_prefix='/', which makes route issue on Ubuntu. 
#bp = Blueprint('graph', __name__, url_prefix='/')

#%%

from flask import jsonify
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', '1'))
@bp.route("/", methods=("GET", "POST"))
def index():
    if request.method == 'POST':
        DOI = request.form['DOI']
        print("index doi:")
        print(DOI)
        for i in range(len(DOI)):
            if DOI[i] == "/":
                DOI = DOI[:i]+"-"+DOI[i+1:]

        return redirect(url_for('graph.search_doi', doi = DOI))
    return render_template("graph/index.html")
#%%
def check_cite_number(url):
    with driver.session() as session:
        result = session.run('MATCH ()-[r:cited]->(n:wiki_graph) WHERE n.url = $url return count(r)', url=url)
        value=result.value()
        return value[0] ## value -> value[0], b/c  value is array have 1 element. 2020.06.30
#%%

@bp.route("/patent", methods=(['GET', 'POST']))
def patent():
    return render_template("graph/patent.html")

@bp.route("/literature", methods=("GET", "POST"))
def literature():
    return render_template("graph/literature.html")

# @bp.route("/<doi>", methods=("GET", "POST"))
# def sidesearch(doi):
#     if request.method == 'POST':
#         DOI = request.form['DOI']
#         print("sidesearch doi:")
#         print(DOI)
#         for i in range(len(DOI)):
#             if DOI[i] == "/":
#                 DOI = DOI[:i]+"-"+DOI[i+1:]
#         return redirect(url_for('graph.search_doi', doi = DOI))

# @bp.route("/<doi>")   
@bp.route("/<doi>", methods=("GET", "POST")) 
def search_doi(doi):
    print ("search doi:")
    print (doi)
    if request.method == 'POST':
        DOI = request.form['DOI']
        for i in range(len(DOI)):
            if DOI[i] == "/":
                DOI = DOI[:i]+"-"+DOI[i+1:]
        return redirect(url_for('graph.search_doi', doi = DOI))
    # return render_template("graph/index.html")

    for i in range(len(doi)):
        if doi[i] == "-":
            doi = doi[:i]+"/"+doi[i+1:]
#%%
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', '1'))
    with driver.session() as session:
        #result = session.run('MATCH p=(n:wiki_graph)-[r:cited*1..4]-() WHERE n.url = $DOI return p skip 12 LIMIT 8', DOI=doi)
        result = session.run('MATCH p=(n:wiki_graph)-[r:cited*1..2]-() WHERE n.url = $DOI return p LIMIT 10', DOI=doi)
        
    #                "MATCH (p:wiki_graph)" +
    #                                 " WHERE p.url = $DOI" +
    #                                 " CALL apoc.path.subgraphNodes(p,{relationshipFilter:'cited',maxLevel:1,uniqueness:'NODE_GLOBAL'}) YIELD node " +
                         
    nodes = []
    links = []
    categories = []

    values = result.values()
    # 2020.07.05 disabled test code
    # print("values:")
    # print(values)
    # print("------------------------------\n\n")

    #print(values)
    #    if values == []:
    #        flash('not exist')
    #        return redirect(url_for('graph.index'))
    for value in values:
        # 2020.07.05 disabled test code
        # print("-- value--\n\n")
        # print(value)
        # print("\n\n")
        try:
            source = [json.loads(str(value[0].start).split("properties=")[1].split(">")[0].replace("'", '\\"').replace('\\', ''))] # parsing string into dict
            temp = str(value[0].end_node).split("properties=")[1].split(">")[0].replace("{\'", '{\"').replace(", \'", ', \"').replace("\':", '\":').replace("\'}", '\"}').replace("\',", '\",').replace(": \'", ': \"')
            target = [json.loads(temp)] # parsing string into dict
        except:
            print(value)
            print("\n\n")
        links.append({"source":str(source[0]["title"]), "target":str(target[0]["title"])})
        
        nodes.append(source[0])
        nodes.append(target[0]) # need to dedup later

    #    nodes = list(set(nodes)) # dedup nodes
    nodes_unique = [i for n, i in enumerate(nodes) if i not in nodes[n + 1:]]
    links_unique = [i for n, i in enumerate(links) if i not in links[n + 1:]]

#    links = list(set(links))
#   
    g_id = 1 # added this valuable for another type of echarts-graph. it is not used for this type of graph.
    for node in nodes_unique:
        #print(node)
        #node['id'] = g_id
        g_id = g_id+1
        node['key']=node['url']
        #print(temp.keys())
        node['name']=node['title']
        node['category']=node['title']
        # node['citation_count']='5'
        node['citation_count']=check_cite_number(node['url'])#temp.get('referenced_by_count', 0) * 5 + temp.get('score', 0) * 5 + 10
        # node['symbolSize'] makes UI error. so I have replaced it with 'citation_count' #2020.06.

        categories.append({'name':node['title']}) # disable => one color, enable => multi - color node
    #return nodes_unique, links_unique, categories

    # 2020.07.05 disabled test code
    # print ("----nodes-----")
    # print (nodes_unique);
    # print ("----links-----")
    # print (links_unique);
    # print ("----categories-----")
    # print (categories);
    return render_template("graph/graph.html", nodes = nodes_unique, links = links_unique, categories = categories)


# %%
