
test:
	python3 scpi2cpp.py
	#@echo "=========== HH ==========="
	#@cat gen/testdevice.hh
	#@echo "=========== CC ==========="
	#@cat gen/testdevice.cpp
	#@echo "==========="
	#g++ -c gen/testdevice.cpp -o gen/testdevice.o

