#NAME: Aryaman Ladha, Akhil Vinta
#EMAIL: ladhaaryaman@ucla.edu, akhil.vinta@gmail.com
#ID: 805299802, 405288527
TAR = tar
TARFLAGS = -czvf
TAREXT = gz
submission-files = README Makefile lab3b.py executable.sh

default: lab3b
clean:
	rm -f *.o lab3b-805299802.$(TAR).$(TAREXT) lab3b
dist: lab3b-805299802.tar.gz
lab3b-805299802.tar.gz: default
	$(TAR) $(TARFLAGS) $@ $(submission-files)
lab3b: lab3b.py executable.sh
	rm -f lab3b
	chmod +x executable.sh
	ln executable.sh lab3b
	chmod +x lab3b