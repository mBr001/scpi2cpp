#include "scpi_ifce.hh"

namespace SCPI {

Cmd(int bufferLen)
{
	cmd.reserve(bufferLen);
}

const std::string & str() const
{
	return cmd;
}

}

