#include "scpi_ifce.hh"

namespace SCPI {

class CmdBuilder
{
	int bufferLen;

public:
	CmdBuilder(int bufferLen) : bufferLen(bufferLen) {};
};


}

