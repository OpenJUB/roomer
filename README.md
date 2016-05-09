# Roomer
[![Build Status](https://travis-ci.com/kuboschek/roomer.svg?token=36dBHFWEizPXoaPLRT7Q&branch=master)](https://travis-ci.com/kuboschek/roomer)

Room allocation, redone in Django for more structure and sanity.

## Structure

At the moment, there are three apps:
* ```roomer``` has the core models of the project, and the base URLconf
* ```collegechooser``` has the college chooser views and models
* ```roommates``` has the roommate management views
