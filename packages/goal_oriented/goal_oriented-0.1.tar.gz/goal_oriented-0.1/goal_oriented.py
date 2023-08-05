#!/usr/bin/env python

# Author: Emanuele Acri
# email: crossbower@gmail.com
# BSD License - January 2013

"""
Tested for:
- 2.4+
- 2.5+
- 2.6+

This module provides a simple facility to the goal-oriented programming paradigm.

In goal-oriented programming, the programmer subdivides the problem in minor goals,
with dependencies between them, and just pass them to a scheduler that will
execute them asyncronously and in the correct order.

In this implementation every goal function receives three arguments:
name    -- the unique name of the goal
args    -- the results from its dependencies
results -- a dictionary where it can write a return value
           (readable by subcessive goals)

The test cointained in the module file illustrates how the module must be used. 
"""


from threading import Thread
from time import sleep


# just a little utility
usleep = lambda x: sleep(x/1000000.0)


def schedule_goals(**goals):

    """This function schedule and executes the goals in the correct order.
       
       Accept a variable number of goals as arguments, in this form:
       goal_name = { options dictionary }

       The options dictionary for a goal can contain the following keys:
       target -- the function to execute
       deps   -- the goals on with the function is dependent (Default: [])
       """

    threads = {}
    results = {}

    # I like concise set operations...
    for goal, opts in goals.items():
        opts['deps'] = 'deps' in opts and frozenset(opts['deps']) or frozenset([])

    todo = set(goals.keys())
    runn = set([])
    done = set([])

    # start goals
    while todo:

        # get goals to launch
        curr = todo

        # keep goals with all dependencies met
        curr = [goal for goal in curr if goals[goal]['deps'] <= done]

        # try to run these goals
        for goal in curr:
        
            # get dependencies return values (used as arguments)
            args = dict([(name, result) for name, result in results.items() \
                         if name in goals[goal]['deps']])

            # run task
            threads[goal] = Thread(name=goal, target=goals[goal]['target'], args=(goal,args,results))
            threads[goal].start()
            runn.add(goal)

        # join completed goals
        for goal in runn:
            if not threads[goal].isAlive():
                threads[goal].join()
                done.add(goal)

        # update goal sets
        runn -= done
        todo -= runn | done

        # sleep a little bit
        usleep(1000)


def test():
    
    """Test for the module"""
    
    def goal1(name, args, results):
        print name, args
        sleep(1)
        results[name] = name + " completed!"

    def goal2(name, args, results):
        print name, args
        sleep(2)
        results[name] = name + " completed!"

    def goal3(name, args, results):
        print name, args
        sleep(2)
        results[name] = name + " completed!"

    def goal4(name, args, results):
        print name, args
        sleep(1)
        results[name] = name + " completed!"

    def goal5(name, args, results):
        print name, args
        sleep(3)
        results[name] = name + " completed!"

    def goal6(name, args, results):
        print name, args
        sleep(1)
        results[name] = name + " completed!"

    # goals to run and their dependencies
    schedule_goals( goal1 = { 'target': goal1 },
                    goal2 = { 'target': goal2 },
                    goal3 = { 'target': goal3, 'deps': ['goal1', 'goal2'] },
                    goal4 = { 'target': goal4, 'deps': ['goal3'] },
                    goal5 = { 'target': goal5, 'deps': ['goal2'] },
                    goal6 = { 'target': goal6 } )

if __name__ == "__main__":
    test()
