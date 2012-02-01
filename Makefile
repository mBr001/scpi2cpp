
YAPPS2 = yapps2-2.1.1-17.1/yapps2.py

test: scpi_parser.py
	python3 scpi2cpp.py
	#@echo "=========== HH ==========="
	#@cat gen/testdevice.hh
	#@echo "=========== CC ==========="
	#@cat gen/testdevice.cpp
	#@echo "==========="
	#g++ -c gen/testdevice.cpp -o gen/testdevice.o

scpi_parser.py: scpi_parser.g
	python ${YAPPS2} $^ $@

