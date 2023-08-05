# -*- coding: utf-8 -*-

import re

static=( [u'\\&',u'&'],	
			[u'``',u'“'],
			[u'\\$',u'$'],	
			[u'\\%',u'%'],	
			[u'\\#',u'#'],	
			[u'\\_',u'_'],	
			[u'\\%',u'%'],	
			[u'\\{',u'{'],	
			[u'\\}',u'}'],	
			[u'\\S',u'§'],	
			[u'~', unicode('\xC2\xA0', 'utf-8')], # Non-break space
			[u'\\P',u'¶'],	
			[u'\\copyright',u'©'],
			[u'\\pounds',u'£'],
			[u'?`',u'¿'],
			[u'!`',u'¡'],
			[u"''", u'"'],
			[u"\\`{A}", u"À"], # LATIN CAPITAL LETTER A WITH GRAVE
			[u"\\'{A}", u"Á"],# LATIN CAPITAL LETTER A WITH ACUTE
			[u"\\'A", u"Á"],# LATIN CAPITAL LETTER A WITH ACUTE
			[u"\\^{A}", u"Â"],# LATIN CAPITAL LETTER A WITH CIRCUMFLEX
			[u"\\~{A}", u"Ã"],# LATIN CAPITAL LETTER A WITH TILDE
			[u"\\~A", u"Ã"],# LATIN CAPITAL LETTER A WITH TILDE
			[u'\\"{A}', u"Ä"],# LATIN CAPITAL LETTER A WITH DIAERESIS
			[u'\\"A', u"Ä"],# LATIN CAPITAL LETTER A WITH DIAERESIS
			[u"\\r{A}", u"Å"],# LATIN CAPITAL LETTER A WITH RING ABOVE
			[u"\\AE", u"Æ"],# LATIN CAPITAL LETTER AE
			[u"\\c{C}", u"Ç"],# LATIN CAPITAL LETTER C WITH CEDILLA
			[u"\\`{E}", u"È"],# LATIN CAPITAL LETTER E WITH GRAVE
			[u"\\'{E}", u"É"],# LATIN CAPITAL LETTER E WITH ACUTE
			[u"\\'E", u"É"],# LATIN CAPITAL LETTER E WITH ACUTE
			[u"\\^{E}", u"Ê"],# LATIN CAPITAL LETTER E WITH CIRCUMFLEX
			[u'\\"{E}', u"Ë"],# LATIN CAPITAL LETTER E WITH DIAERESIS
			[u'\\"E', u"Ë"],# LATIN CAPITAL LETTER E WITH DIAERESIS
			[u"\\`{I}", u"Ì"],# LATIN CAPITAL LETTER I WITH GRAVE
			[u"\\'{I}", u"Í"],# LATIN CAPITAL LETTER I WITH ACUTE
			[u"\\'I", u"Í"],# LATIN CAPITAL LETTER I WITH ACUTE
			[u"\\^{I}", u"Î"],# LATIN CAPITAL LETTER I WITH CIRCUMFLEX
			[u'\\"{I}', u"Ï"],# LATIN CAPITAL LETTER I WITH DIAERESIS
			[u'\\"I', u"Ï"],# LATIN CAPITAL LETTER I WITH DIAERESIS
			[u"\\DH", u"Ð"],# LATIN CAPITAL LETTER ETH
			[u"\\~{N}", u"Ñ"],# LATIN CAPITAL LETTER N WITH TILDE
			[u"\\`{O}", u"Ò"],# LATIN CAPITAL LETTER O WITH GRAVE
			[u"\\'{O}", u"Ó"],# LATIN CAPITAL LETTER O WITH ACUTE
			[u"\\'O", u"Ó"],# LATIN CAPITAL LETTER O WITH ACUTE
			[u"\\^{O}", u"Ô"],# LATIN CAPITAL LETTER O WITH CIRCUMFLEX
			[u"\\~{O}", u"Õ"],# LATIN CAPITAL LETTER O WITH TILDE
			[u"\\~O", u"Õ"],# LATIN CAPITAL LETTER O WITH TILDE
			[u'\\"{O}', u"Ö"],# LATIN CAPITAL LETTER O WITH DIAERESIS
			[u'\\"O', u"Ö"],# LATIN CAPITAL LETTER O WITH DIAERESIS
			[u"\\texttimes", u"×"],#MULTIPLICATION SIGN
			[u"\\O", u"Ø"],# LATIN CAPITAL LETTER O WITH STROKE
			[u"\\`{U}", u"Ù"],# LATIN CAPITAL LETTER U WITH GRAVE
			[u"\\'{U}", u"Ú"],# LATIN CAPITAL LETTER U WITH ACUTE
			[u"\\'U", u"Ú"],# LATIN CAPITAL LETTER U WITH ACUTE
			[u"\\^{U}", u"Û"],# LATIN CAPITAL LETTER U WITH CIRCUMFLEX
			[u'\\"{U}', u"Ü"],# LATIN CAPITAL LETTER U WITH DIAERESIS
			[u'\\"U', u"Ü"],# LATIN CAPITAL LETTER U WITH DIAERESIS
			[u"\\'{Y}", u"Ý"],# LATIN CAPITAL LETTER Y WITH ACUTE
			[u"\\TH", u"Þ"],# LATIN CAPITAL LETTER THORN
			[u"{\\ss}", u"ß"],# LATIN SMALL LETTER SHARP S
			[u"\\ss", u"ß"],
			[u'\\"s', u"ß"],
			[u'\\"s', u"ß"],
			[u"\\`{a}", u"à"],# LATIN SMALL LETTER A WITH GRAVE
			[u"\\'{a}", u"á"],# LATIN SMALL LETTER A WITH ACUTE
			[u"\\'a", u"á"],# LATIN SMALL LETTER A WITH ACUTE
			[u"\\^{a}", u"â"],# LATIN SMALL LETTER A WITH CIRCUMFLEX
			[u"\\^a", u"â"],# LATIN SMALL LETTER A WITH CIRCUMFLEX
			[u"\\~{a}", u"ã"],# LATIN SMALL LETTER A WITH TILDE
			[u"\\~a", u"ã"],# LATIN SMALL LETTER A WITH TILDE
			[u'\\"{a}', u"ä"],# LATIN SMALL LETTER A WITH DIAERESIS
			[u'\\"a', u"ä"],# LATIN SMALL LETTER A WITH DIAERESIS
			[u"\\r{a}", u"å"],# LATIN SMALL LETTER A WITH RING ABOVE
			[u"\\ae", u"æ"],# LATIN SMALL LETTER AE
			[u"\\c{c}", u"ç"],# LATIN SMALL LETTER C WITH CEDILLA
			[u"\\`{e}", u"è"],# LATIN SMALL LETTER E WITH GRAVE
			[u"\\`e", u"è"],# LATIN SMALL LETTER E WITH GRAVE
			[u"\\'{e}", u"é"],# LATIN SMALL LETTER E WITH ACUTE
			[u"\\'e", u"é"],# LATIN SMALL LETTER E WITH ACUTE
			[u"\\^{e}", u"ê"],# LATIN SMALL LETTER E WITH CIRCUMFLEX
			[u'\\"{e}', u"ë"],# LATIN SMALL LETTER E WITH DIAERESIS
			[u'\\"e', u"ë"],# LATIN SMALL LETTER E WITH DIAERESIS
			[u"\\`{i}", u"ì"],#uATIN SMALL LETTER I WITH GRAVE
			[u"\\`i", u"ì"],#uATIN SMALL LETTER I WITH GRAVE
			[u"\\'{i}", u"í"],# LATIN SMALL LETTER I WITH ACUTE
			[u"\\'i", u"í"],# LATIN SMALL LETTER I WITH ACUTE
			[u"\\^{i}", u"î"],# LATIN SMALL LETTER I WITH CIRCUMFLEX
			[u'\\"{i}', u"ï"],# LATIN SMALL LETTER I WITH DIAERESIS
			[u"\\dh", u"ð"],# LATIN SMALL LETTER ETH
			[u"\\~{n}", u"ñ"],# LATIN SMALL LETTER N WITH TILDE
			[u"\\`{o}", u"ò"],# LATIN SMALL LETTER O WITH GRAVE
			[u"\\'{o}", u"ó"],# LATIN SMALL LETTER O WITH ACUTE
			[u"\\'o", u"ó"],# LATIN SMALL LETTER O WITH ACUTE
			[u"\\'o", u"ó"],# LATIN SMALL LETTER O WITH ACUTE
			[u"\\^{o}", u"ô"],# LATIN SMALL LETTER O WITH CIRCUMFLEX
			[u"\\~{o}", u"õ"],# LATIN SMALL LETTER O WITH TILDE
			[u"\\~o", u"õ"],# LATIN SMALL LETTER O WITH TILDE
			[u'\\"{o}', u"ö"],# LATIN SMALL LETTER O WITH DIAERESIS
			[u'\\"o', u"ö"],# LATIN SMALL LETTER O WITH DIAERESIS
			[u"\\textdiv", u"÷"],#DIVISION SIGN
			[u"\\o", u"ø"],# LATIN SMALL LETTER O WITH STROKE
			[u"\\`{u}", u"ù"],# LATIN SMALL LETTER U WITH GRAVE
			[u"\\'{u}", u"ú"],# LATIN SMALL LETTER U WITH ACUTE
			[u"\\'u", u"ú"],# LATIN SMALL LETTER U WITH ACUTE
			[u"\\^{u}", u"û"],# LATIN SMALL LETTER U WITH CIRCUMFLEX
			[u'\\"{u}', u"ü"],# LATIN SMALL LETTER U WITH DIAERESIS
			[u'\\"u', u"ü"],# LATIN SMALL LETTER U WITH DIAERESIS
			[u'\\"u', u"ü"],# LATIN SMALL LETTER U WITH DIAERESIS
			[u"\\'{y}", u"ý"],# LATIN SMALL LETTER Y WITH ACUTE
			[u"\\th", u"þ"],# LATIN SMALL LETTER THORN
			[u'\\"{y}', u"ÿ"],# LATIN SMALL LETTER Y WITH DIAERESIS
			[u"\\={A}", u"Ā"],# LATIN CAPITAL LETTER A WITH MACRON
			[u"\\={a}", u"ā"],# LATIN SMALL LETTER A WITH MACRON
			[u"\\u{A}", u"Ă"],# LATIN CAPITAL LETTER A WITH BREVE
			[u"\\u{a}", u"ă"],# LATIN SMALL LETTER A WITH BREVE
			[u"\\k{A}", u"Ą"],# LATIN CAPITAL LETTER A WITH OGONEK
			[u"\\k{a}", u"ą"],# LATIN SMALL LETTER A WITH OGONEK
			[u"\\'{C}", u"Ć"],# LATIN CAPITAL LETTER C WITH ACUTE
			[u"\\'{c}", u"ć"],# LATIN SMALL LETTER C WITH ACUTE
			[u"\\^{C}", u"Ĉ"],# LATIN CAPITAL LETTER C WITH CIRCUMFLEX
			[u"\\^{c}", u"ĉ"],# LATIN SMALL LETTER C WITH CIRCUMFLEX
			[u"\\.{C}", u"Ċ"],# LATIN CAPITAL LETTER C WITH DOT ABOVE
			[u"\\.{c}", u"ċ"],# LATIN SMALL LETTER C WITH DOT ABOVE
			[u"\\v{C}", u"Č"],# LATIN CAPITAL LETTER C WITH CARON
			[u"\\v{c}", u"č"],# LATIN SMALL LETTER C WITH CARON
			[u"\\v{D}", u"Ď"],# LATIN CAPITAL LETTER D WITH CARON
			[u"\\v{d}", u"ď"],# LATIN SMALL LETTER D WITH CARON
			[u"\\DJ", u"Đ"],# LATIN CAPITAL LETTER D WITH STROKE
			[u"\\dj", u"đ"],# LATIN SMALL LETTER D WITH STROKE
			[u"\\={E}", u"Ē"],# LATIN CAPITAL LETTER E WITH MACRON
			[u"\\={e}", u"ē"],# LATIN SMALL LETTER E WITH MACRON
			[u"\\u{E}", u"Ĕ"],# LATIN CAPITAL LETTER E WITH BREVE
			[u"\\u{e}", u"ĕ"],# LATIN SMALL LETTER E WITH BREVE
			[u"\\.{E}", u"Ė"],# LATIN CAPITAL LETTER E WITH DOT ABOVE
			[u"\\.{e}", u"ė"],# LATIN SMALL LETTER E WITH DOT ABOVE
			[u"\\k{E}", u"Ę"],# LATIN CAPITAL LETTER E WITH OGONEK
			[u"\\k{e}", u"ę"],# LATIN SMALL LETTER E WITH OGONEK
			[u"\\v{E}", u"Ě"],# LATIN CAPITAL LETTER E WITH CARON
			[u"\\v{e}", u"ě"],# LATIN SMALL LETTER E WITH CARON
			[u"\\^{G}", u"Ĝ"],# LATIN CAPITAL LETTER G WITH CIRCUMFLEX
			[u"\\^{g}", u"ĝ"],# LATIN SMALL LETTER G WITH CIRCUMFLEX
			[u"\\u{G}", u"Ğ"],# LATIN CAPITAL LETTER G WITH BREVE
			[u"\\u{g}", u"ğ"],# LATIN SMALL LETTER G WITH BREVE
			[u"\\.{G}", u"Ġ"],# LATIN CAPITAL LETTER G WITH DOT ABOVE
			[u"\\.{g}", u"ġ"],# LATIN SMALL LETTER G WITH DOT ABOVE
			[u"\\c{G}", u"Ģ"],# LATIN CAPITAL LETTER G WITH CEDILLA
			[u"\\c{g}", u"ģ"],# LATIN SMALL LETTER G WITH CEDILLA
			[u"\\^{H}", u"Ĥ"],# LATIN CAPITAL LETTER H WITH CIRCUMFLEX
			[u"\\^{h}", u"ĥ"],# LATIN SMALL LETTER H WITH CIRCUMFLEX
			[u"\\={H}", u"Ħ"],# LATIN CAPITAL LETTER H WITH STROKE
			[u"\\={h}", u"ħ"],# LATIN SMALL LETTER H WITH STROKE
			[u"\\~{I}", u"Ĩ"],# LATIN CAPITAL LETTER I WITH TILDE
			[u"\\~{i}", u"ĩ"],# LATIN SMALL LETTER I WITH TILDE
			[u"\\={I}", u"Ī"],# LATIN CAPITAL LETTER I WITH MACRON
			[u"\\={i}", u"ī"],# LATIN SMALL LETTER I WITH MACRON
			[u"\\u{I}", u"Ĭ"],# LATIN CAPITAL LETTER I WITH BREVE
			[u"\\u{i}", u"ĭ"],# LATIN SMALL LETTER I WITH BREVE
			[u"\\k{I}", u"Į"],# LATIN CAPITAL LETTER I WITH OGONEK
			[u"\\k{i}", u"į"],# LATIN SMALL LETTER I WITH OGONEK
			[u"\\.{I}", u"İ"],# LATIN CAPITAL LETTER I WITH DOT ABOVE
			[u"\\i", u"ı"],# LATIN SMALL LETTER DOTLESS I
			[u"\\IJ", u"Ĳ"],# LATIN CAPITAL LIGATURE IJ
			[u"\\ij", u"ĳ"],# LATIN SMALL LIGATURE IJ
			[u"\\^{J}", u"Ĵ"],# LATIN CAPITAL LETTER J WITH CIRCUMFLEX
			[u"\\^{j}", u"ĵ"],# LATIN SMALL LETTER J WITH CIRCUMFLEX
			[u"\\c{K}", u"Ķ"],# LATIN CAPITAL LETTER K WITH CEDILLA
			[u"\\c{k}", u"ķ"],# LATIN SMALL LETTER K WITH CEDILLA
			[u"ĸ", u"ĸ"],# LATIN SMALL LETTER KRA
			[u"\\'{L}", u"Ĺ"],# LATIN CAPITAL LETTER L WITH ACUTE
			[u"\\'{l}", u"ĺ"],# LATIN SMALL LETTER L WITH ACUTE
			[u"\\c{L}", u"Ļ"],# LATIN CAPITAL LETTER L WITH CEDILLA
			[u"\\c{l}", u"ļ"],# LATIN SMALL LETTER L WITH CEDILLA
			[u"\\v{L}", u"Ľ"],# LATIN CAPITAL LETTER L WITH CARON
			[u"\\v{l}", u"ľ"],# LATIN SMALL LETTER L WITH CARON
			[u"\\.{L}", u"Ŀ"],# LATIN CAPITAL LETTER L WITH MIDDLE DOT
			[u"\\.{l}", u"ŀ"],# LATIN SMALL LETTER L WITH MIDDLE DOT
			[u"\\L", u"Ł"],# LATIN CAPITAL LETTER L WITH STROKE
			[u"\\l", u"ł"],# LATIN SMALL LETTER L WITH STROKE
			[u"\\'{N}", u"Ń"],# LATIN CAPITAL LETTER N WITH ACUTE
			[u"\\'{n}", u"ń"],# LATIN SMALL LETTER N WITH ACUTE
			[u"\\c{N}", u"Ņ"],# LATIN CAPITAL LETTER N WITH CEDILLA
			[u"\\c{n}", u"ņ"],# LATIN SMALL LETTER N WITH CEDILLA
			[u"\\v{N}", u"Ň"],# LATIN CAPITAL LETTER N WITH CARON
			[u"\\v{n}", u"ň"],# LATIN SMALL LETTER N WITH CARON
			[u"\\nument{149}", u"ŉ"],# LATIN SMALL LETTER N PRECEDED BY APOSTROPHE
			[u"\\NG", u"Ŋ"],# LATIN CAPITAL LETTER ENG
			[u"\\ng", u"ŋ"],# LATIN SMALL LETTER ENG
			[u"\\={O}", u"Ō"],# LATIN CAPITAL LETTER O WITH MACRON
			[u"\\={o}", u"ō"],# LATIN SMALL LETTER O WITH MACRON
			[u"\\u{O}", u"Ŏ"],# LATIN CAPITAL LETTER O WITH BREVE
			[u"\\u{o}", u"ŏ"],# LATIN SMALL LETTER O WITH BREVE
			[u"\\'{O}", u"Ő"],# LATIN CAPITAL LETTER O WITH DOUBLE ACUTE
			[u"\\'{o}", u"ő"],# LATIN SMALL LETTER O WITH DOUBLE ACUTE
			[u"\\OE", u"Œ"],# LATIN CAPITAL LIGATURE OE
			[u"\\oe", u"œ"],# LATIN SMALL LIGATURE OE
			[u"\\'{R}", u"Ŕ"],# LATIN CAPITAL LETTER R WITH ACUTE
			[u"\\'{r}", u"ŕ"],# LATIN SMALL LETTER R WITH ACUTE
			[u"\\c{R}", u"Ŗ"],# LATIN CAPITAL LETTER R WITH CEDILLA
			[u"\\c{r}", u"ŗ"],# LATIN SMALL LETTER R WITH CEDILLA
			[u"\\v{R}", u"Ř"],# LATIN CAPITAL LETTER R WITH CARON
			[u"\\v{r}", u"ř"],# LATIN SMALL LETTER R WITH CARON
			[u"\\'{S}", u"Ś"],# LATIN CAPITAL LETTER S WITH ACUTE
			[u"\\'{s}", u"ś"],# LATIN SMALL LETTER S WITH ACUTE
			[u"\\^{S}", u"Ŝ"],# LATIN CAPITAL LETTER S WITH CIRCUMFLEX
			[u"\\^{s}", u"ŝ"],# LATIN SMALL LETTER S WITH CIRCUMFLEX
			[u"\\c{S}", u"Ş"],# LATIN CAPITAL LETTER S WITH CEDILLA
			[u"\\c{s}", u"ş"],# LATIN SMALL LETTER S WITH CEDILLA
			[u"\\v{S}", u"Š"],# LATIN CAPITAL LETTER S WITH CARON
			[u"\\v{s}", u"š"],# LATIN SMALL LETTER S WITH CARON
			[u"\\c{T}", u"Ţ"],# LATIN CAPITAL LETTER T WITH CEDILLA
			[u"\\c{t}", u"ţ"],# LATIN SMALL LETTER T WITH CEDILLA
			[u"\\v{T}", u"Ť"],# LATIN CAPITAL LETTER T WITH CARON
			[u"\\v{t}", u"ť"],# LATIN SMALL LETTER T WITH CARON
			[u"\\={T}", u"Ŧ"],# LATIN CAPITAL LETTER T WITH STROKE
			[u"\\={t}", u"ŧ"],# LATIN SMALL LETTER T WITH STROKE
			[u"\\~{U}", u"Ũ"],# LATIN CAPITAL LETTER U WITH TILDE
			[u"\\~{u}", u"ũ"],# LATIN SMALL LETTER U WITH TILDE
			[u"\\={U}", u"Ū"],# LATIN CAPITAL LETTER U WITH MACRON
			[u"\\={u}", u"ū"],# LATIN SMALL LETTER U WITH MACRON
			[u"\\u{U}", u"Ŭ"],# LATIN CAPITAL LETTER U WITH BREVE
			[u"\\u{u}", u"ŭ"],# LATIN SMALL LETTER U WITH BREVE
			[u"\\r{U}", u"Ů"],# LATIN CAPITAL LETTER U WITH RING ABOVE
			[u"\\r{u}", u"ů"],# LATIN SMALL LETTER U WITH RING ABOVE
			[u"\\'{U}", u"Ű"],# LATIN CAPITAL LETTER U WITH DOUBLE ACUTE
			[u"\\'{u}", u"ű"],# LATIN SMALL LETTER U WITH DOUBLE ACUTE
			[u"\\k{U}", u"Ų"],# LATIN CAPITAL LETTER U WITH OGONEK
			[u"\\k{u}", u"ų"],# LATIN SMALL LETTER U WITH OGONEK
			[u"\\^{W}", u"Ŵ"],# LATIN CAPITAL LETTER W WITH CIRCUMFLEX
			[u"\\^{w}", u"ŵ"],# LATIN SMALL LETTER W WITH CIRCUMFLEX
			[u"\\^{Y}", u"Ŷ"],# LATIN CAPITAL LETTER Y WITH CIRCUMFLEX
			[u"\\^{y}", u"ŷ"],# LATIN SMALL LETTER Y WITH CIRCUMFLEX
			[u'\\"{Y}', u"Ÿ"],# LATIN CAPITAL LETTER Y WITH DIAERESIS
			[u"\\'{Z}", u"Ź"],# LATIN CAPITAL LETTER Z WITH ACUTE
			[u"\\'{z}", u"ź"],# LATIN SMALL LETTER Z WITH ACUTE
			[u"\\.{Z}", u"Ż"],# LATIN CAPITAL LETTER Z WITH DOT ABOVE
			[u"\\.{z}", u"ż"],# LATIN SMALL LETTER Z WITH DOT ABOVE
			[u"\\v{Z}", u"Ž"],# LATIN CAPITAL LETTER Z WITH CARON
			[u"\\v{z}", u"ž"],# LATIN SMALL LETTER Z WITH CARON
		)
		
# Helper function to re-generate the mapping table
def printMappingTable():
	pattern="DeclareUnicodeCharacter{(\S+)}{(\S+)}"
	# Peter Mac OS X 10.6
	data=open("/Library/TeX/Distributions/.DefaultTeX/Contents/AllTexmf/texmf-dist/source/latex/base/utf8ienc.dtx").readlines()
	# generate mapping dictionary from Latex sources
	mapping={}
	for line in data:
		prog=re.compile(pattern)
		result=prog.search(line)
		if result:
			latex=result.group(2)
			latex=latex.replace("@tabacckludge","")
			mapping[int('0x'+result.group(1),16)]=latex
	# add manual additions
	for k,v in static:
		if ord(v) not in mapping:
			print "%s : %s missing in Latex"%(k,v)
			mapping[ord(v)]=k
	sortmap=[ (k,mapping[k]) for k in sorted(mapping.keys())]
	for k,v in sortmap:
		v=v.replace("\\","\\\\")
		if "'" in v:
			print '%u:"%s",'%(k,v),
		else:
			print "%u:'%s',"%(k,v),
		print "\t# character "+unichr(k)

printMappingTable()