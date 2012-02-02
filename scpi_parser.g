
parser ParserDescription:

#	ignore:      '\\\r?\n'
	token COMMENT: "[#].*?\r?\n"
	token EOF:   "$"
	token CC:    '[*][A-Z][A-Z][A-Z]'
	token IC:    ':[A-Z][A-Z][A-Z]?[A-Z]?[a-z]*[0-9]*'
	token TYPE:  '<[a-zA-Z_][a-zA-Z0-9_]*>'
	token AT:    '[@]'
	token CHLIST:'\\([@]'
	token LP:    '\\('
	token RP:    '\\)'
	token LB:    '\\['
	token RB:    '\\]'
	token OR:    '[|]'
	token TABS:  '[\t]*'
	token EOL:   '[ \t]*\r?\n'
	token WS:    '[ \t]'
	token STAR:  '[*]'
	token PLUS:  '[+]'
	token QUEST: '[?]'
	token COLON: ':'

	rule SCPI:
	    	Commands EOF
		{{ return Commands }}

	rule Commands: {{ commands = [] }}
		( COMMENT | EOL | ( Command {{ commands.append(Command) }} EOL ) )*
	    	( Command {{ commands.append(Command) }} )?
	    	{{ return commands }}

	rule Command:
		CCommand {{ return CCommand }} |
		ICommand {{ return ICommand }}

	rule CCommand: {{ command = {} }}
		CC Query
		{{ command['name'] = CC }}
		{{ command['query'] = Query }}
		{{ return command }}

	rule ICommand: {{ command = {} }}
		TABS ICommandName ICommandSub Query ICommandParams
		{{ command['indent'] = len(TABS) }}
		{{ command.update(ICommandName) }}
		{{ command['child'] = ICommandSub }}
		{{ command['query'] = Query }}
		{{ command['params'] = ICommandParams }}
		{{ return command }}

	rule ICommandName: {{ command = {} }}
		( IC {{ command['name'] = IC }} |
		LB IC RB {{ command['name'] = IC; command['optional'] = True }} )
		{{ return command }}

	rule ICommandParams: {{ params = [] }}
		( WS+ ( ICommandParam {{ params.append(ICommandParam) }})?
		( WS* ICommandParam "[ \t]*," {{ params.append(ICommandParam) }})*
			)?
		{{ return params }}

	rule ICommandParam: {{ param = {} }}
		ChannelList
		{{ return ChannelList }}

	rule ICommandSub:
		{{ ICommand = None }}
		ICommand?
		{{ return ICommand }}

	rule Query:
		{{ QUEST = False }}
		QUEST?
		{{ return bool(QUEST) }}


	rule ChannelList:
		CHLIST ParamType RP
		{{ return ParamType }}

	rule ParamType:
		TYPE
		{{ return TYPE }}

