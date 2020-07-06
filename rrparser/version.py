"""
Created on June 23 2020

@author: Joan Hérisson

"""


from os.path import dirname

with open(dirname(__file__) + '/../release/RELEASE.md', 'r') as f:
    __version__ = f.readline().split()[0]
