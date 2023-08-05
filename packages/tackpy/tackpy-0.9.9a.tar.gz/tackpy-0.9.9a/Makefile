
TESTDIR = testoutput

.PHONY : default
default:
	@echo To install tackpy run \"./setup.py install\" or \"make install\"
	@echo

.PHONY: install
install:
	./setup.py install

.PHONY: dist
dist:
	./setup.py sdist

.PHONY : clean
clean:
	rm -f `find . -name *.pyc`
	rm -rf build
	rm -rf dist
	rm -rf $(TESTDIR)

# Variables for testing
TESTDIR = testoutput
EXEC = ./tack.py
CERT1 = ./testdata/serverX509Cert.pem
CERT2 = ./testdata/serverX509Cert.der

.PHONY: test
test:
	rm -rf $(TESTDIR)
	mkdir $(TESTDIR)
	$(EXEC) genkey -p asdf > $(TESTDIR)/TACK_Key1.pem 
	$(EXEC) genkey -x -p asdf > $(TESTDIR)/TACK_Key2.pem 
	$(EXEC) genkey -p asdf -o $(TESTDIR)/TACK_Key3.pem 
	$(EXEC) sign -k $(TESTDIR)/TACK_Key1.pem -p asdf -c $(CERT1) > $(TESTDIR)/TACK1.pem	
	cat $(TESTDIR)/TACK_Key1.pem | $(EXEC) sign -k- -p asdf -c $(CERT2) -o $(TESTDIR)/TACK2.pem		
	$(EXEC) sign -x -k $(TESTDIR)/TACK_Key1.pem -p asdf -c $(CERT1) -m2 -o $(TESTDIR)/TACK3.pem			
	$(EXEC) sign -k $(TESTDIR)/TACK_Key1.pem -p asdf -c $(CERT1) -o $(TESTDIR)/TACK4.pem			
	$(EXEC) sign -x -k $(TESTDIR)/TACK_Key1.pem -p asdf -e 2030-06-06Z -c $(CERT2) -o $(TESTDIR)/TACK5.pem
	cat $(CERT1) | $(EXEC) sign -k $(TESTDIR)/TACK_Key1.pem -p asdf -g2 -m2 -c- -o $(TESTDIR)/TACK6.pem
	cat $(CERT2) | $(EXEC) sign -k $(TESTDIR)/TACK_Key1.pem -p asdf -m250 -g251 -c - -o $(TESTDIR)/T6 -e 2013-01-02Z -n 3@1d
	$(EXEC) pack -t $(TESTDIR)/TACK3.pem > $(TESTDIR)/TACK_Ext3.pem
	cat $(TESTDIR)/TACK3.pem $(TESTDIR)/TACK4.pem > $(TESTDIR)/TACK3_4.pem
	$(EXEC) pack -t $(TESTDIR)/TACK3_4.pem > $(TESTDIR)/TACK_Ext3_4.pem
	$(EXEC) unpack -E $(TESTDIR)/TACK_Ext3_4.pem -o $(TESTDIR)/TACK_Ext3_4_Unpack.txt
	$(EXEC) view $(TESTDIR)/TACK_Key1.pem > $(TESTDIR)/TACK_View_Key1.txt
	cat $(TESTDIR)/TACK1.pem | $(EXEC) view - > $(TESTDIR)/TACK_View1.txt
	$(EXEC) v $(CERT1) > $(TESTDIR)/TACK_View_Cert1.txt
	cat $(CERT2) | $(EXEC) v - > $(TESTDIR)/TACK_View_Cert2.txt
	$(EXEC) v $(TESTDIR)/TACK_Ext3.pem > $(TESTDIR)/TACK_View_TACK_Ext3.txt 
	@echo OK
