
parser ParserDescription:

#	ignore:      '\\\r?\n'
	token COMMENT: "[#].*?\r?\n"
	token EOF:   "$"
	token CC:    '[A-Z][A-Z][A-Z]'
	token IC:    '[A-Z][A-Z][A-Z]?[A-Z]?[a-z]*[0-9]*'
	token NAME:  '[a-zA-Z_][a-zA-Z0-9_]*'
	token TYPE:  '<[a-zA-Z_][a-zA-Z0-9_]*>'
	token AT:    '[@]'
	token CHLIST:'\\([@]'
	token LP:    '\\('
	token RP:    '\\)'
	token LT:    '<'
	token GT:    '>'
	token LSB:   '\\['
	token RSB:   '\\]'
	token LCB:   '{'
	token RCB:   '}'
	token OR:    '[|]'
	token TABS:  '[\t]*'
	token EOL:   '[ \t]*\r?\n'
	token WS:    '[ \t]'
	token WSS:   '[ \t]*'
	token STAR:  '[*]'
	token PLUS:  '[+]'
	token QUEST: '[?]'
	token COMMA: '[,]'
	token STAR:  '[*]'
	token COLON: '[:]'

	rule SCPI:
	    	Commands EOF
		{{ return Commands }}

	rule Commands: {{ commands = [] }}
		( COMMENT | EOL | ( Command EOL {{ commands.append(Command) }} ) )*
	    	( Command {{ commands.append(Command) }} )?
	    	{{ return commands }}

	rule Command:
		CCommand {{ return CCommand }} |
		ICommand {{ return ICommand }}

	rule CCommand: {{ command = {} }}
		STAR CC Query
		{{ command["name"] = CC }}
		{{ command["query"] = Query }}
		{{ command["type"] = "CC" }}
		{{ return command }}

	rule ICommand: {{ command = {} }}
		TABS ICommandTree Query
		( WS+ ( ICommandParams
			{{ command["params"] = ICommandParams }} )? )?
		{{ command["indent"] = len(TABS) }}
		{{ command["query"] = Query }}
		{{ command["tree"] = ICommandTree }}
		{{ command["type"] = "IC" }}
		{{ return command }}

	rule ICommandTree:
		ICommandBranch {{ command = ICommandBranch }}
		( ICommandTree {{ command["sub"] = ICommandTree }} )?
		{{ return command }}

	rule ICommandBranch: {{ command = {} }}
		( ( ICommandName {{ command["name"] = ICommandName }} ) |
		( LSB ICommandName RSB
			{{ command["name"] = ICommandName }}
			{{ command["optional"] = True }} ) )
		{{ return command }}

	rule ICommandName:
		COLON IC
		{{ return IC }}

	rule ICommandParams: {{ params = [] }}
		( ( ICommandParam {{ params.append(ICommandParam) }} |
			ICommandParamOpt {{ params.append(ICommandParamOpt) }}
			)
			( ICommandParamNext
				{{ params.append(ICommandParamNext) }} |
			  ICommandParamNextOpt
				{{ params.append(ICommandParamNextOpt) }} )*
			)?
		{{ return params }}

	rule ICommandParam:
		ChannelList {{ return ChannelList }} |
		ParamValueList {{ return ParamValueList }} |
		ICommandParamOne {{ return ICommandParamOne }}

	rule ICommandParamOpt: {{ param = {} }}
		LSB WSS ICommandParams RSB WSS
		{{ param["type"] = "optional" }}
		{{ param["subparams"] = ICommandParams }}
		{{ return param }}

	rule ICommandParamNext:
		COMMA WSS ICommandParam
		{{ return ICommandParam }}

	rule ICommandParamNextOpt: {{ param = {} }}
		LSB WSS COMMA WSS ICommandParams RSB WSS
		{{ param["type"] = "optional" }}
		{{ param["subparams"] = ICommandParams }}
		{{ return param }}

	rule ICommandParamOne: {{ param = {} }}
		"1" WSS
		{{ param["type"] = "const" }}
		{{ param["value"] = "1" }}
		{{ return param }}

	rule ICommandSub:
		(ICommand {{ return ICommand }} )?
		{{ return None }}

	rule Query:
		( QUEST {{ return True }} )?
		{{ return False }}

	rule ValueList: {{ values = [] }}
		(LCB WSS
		( TYPE WSS {{ values.append(TYPE) }} )
		( OR WSS TYPE WSS {{ values.append(TYPE) }} )*
		RCB WSS)?
		{{ return values }}

	rule ChannelList: {{ param = {} }}
		{{ param["type"] = "channels" }}
		CHLIST ParamValueType RP WSS
		{{ param["value type"] = ParamValueType }}
		{{ return param }}

	rule ParamValueList: {{ param = {} }}
		{{ param["type"] = "list" }}
		{{ param["values special"] = [] }}
		LCB WSS
		( ( ParamValueType
			{{ param["value type"] = ParamValueType }} ) |
		  ( ParamValueSpecial
			{{ param["values special"].append(ParamValueSpecial) }} )
		)
		( OR WSS ParamValueSpecial
			{{ param["values special"].append(ParamValueSpecial) }} )*
		RCB WSS
		{{ return param }}

	rule ParamValueSpecial:
		NAME WSS {{ return NAME }}

	rule ParamValueType:
		LT NAME GT WSS {{ return NAME }}

