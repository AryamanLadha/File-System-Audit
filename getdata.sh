TEST=1
for i in csv err
do
    `wget www.cs.ucla.edu/classes/cs111/Samples/P3B-test_$(TEST).$(i)`
done