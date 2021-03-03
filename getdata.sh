#!/bin/bash
for TEST in 1 2 3 4 5 6 7 8 9 10 11
do
    for i in csv err
    do
        wget www.cs.ucla.edu/classes/cs111/Samples/P3B-test_$(TEST).$(i)
    done
done