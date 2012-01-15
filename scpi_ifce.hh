#pragma once

namespace SCPI {

class Cmd {
	std::string cmd;
public:
	Cmd(int bufferLen=65532);
	const std::string &str() const;
};

}

