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
