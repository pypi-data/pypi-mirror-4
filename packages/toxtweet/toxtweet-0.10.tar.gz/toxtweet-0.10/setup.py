#!/usr/bin/env python

from distutils.core import setup

setup(name='toxtweet',
      version='0.10',
      description='ToxTweet- Tools for Toxicovigliance on Twitter',
      author='Michael Chary',
      author_email='mac389@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',
      py_modules=['better_twitter_search','classifying','crawler','FK','languageclassifier','lexdiv','loadTweets','main','medgraph','parser','readabilitytests','similarity','syllables_en','textanalyzer','twitterQuery','urlextracter','visualize_networks']
     )