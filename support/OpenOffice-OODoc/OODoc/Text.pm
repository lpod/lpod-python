#----------------------------------------------------------------------------
#
#	$Id : Text.pm 2.236 2009-02-18 JMG$
#
#	Created and maintained by Jean-Marie Gouarne
#	Copyright 2009 by Genicorp, S.A. (www.genicorp.com)
#
#-----------------------------------------------------------------------------

package OpenOffice::OODoc::Text;
use	5.008_000;
use	OpenOffice::OODoc::XPath	2.229;
our	@ISA		= qw ( OpenOffice::OODoc::XPath );
our	$VERSION	= 2.236;

#-----------------------------------------------------------------------------
# synonyms

BEGIN	{
	*findElementsByContent		= *selectElementsByContent;
	*replaceAll			= *selectElementsByContent;
	*findTextContent		= *selectTextContent;
	*getHeaderList			= *getHeadingList;
	*getHeaderTextList		= *getHeadingTextList;
	*getBibliographyElements	= *getBibliographyMarks;
	*bibliographyElementContent	= *bibliographyEntryContent;
	*setBibliographyElement		= *setBibliographyMark;
	*bookmarkElement		= *setBookmark;
	*removeBookmark			= *deleteBookmark;
	*getHeader			= *getHeading;
	*getHeaderContent		= *getHeadingContent;
	*getHeaderText			= *getHeadingText;
	*getOutlineLevel		= *getLevel;
	*setOutlineLevel		= *setLevel;
	*getSections			= *getSectionList;
	*getChapter			= *getChapterContent;
	*getParagraphContent		= *getParagraphText;
	*createTextBox			= *createTextBoxElement;
	*getTextBox			= *getTextBoxElement;
	*getTextBoxElements		= *getTextBoxElementList;
	*getList			= *getItemList;
	*getColumn			= *getTableColumn;
	*getRow				= *getTableRow;
	*getHeaderRow			= *getTableHeaderRow;
	*getCell			= *getTableCell;
	*getSheet			= *getTable;
	*selectTableByName		= *getTableByName;
	*getSheetByName			= *getTableByName;
	*getTableContent		= *getTableText;
	*normalizeTable			= *normalizeSheet;
	*normalizeTables		= *normalizeSheets;
	*expandSheet			= *expandTable;
	*insertColumn			= *insertTableColumn;
	*deleteColumn			= *deleteTableColumn;
	*replicateRow			= *replicateTableRow;
	*insertRow			= *insertTableRow;
	*appendRow			= *appendTableRow;
	*deleteRow			= *deleteTableRow;
	*appendHeader			= *appendHeading;
	*insertHeader			= *insertHeading;
	*removeHeader			= *removeHeading;
	*deleteHeading			= *removeHeading;
	*getNote			= *getNoteElement;
	*getNoteList			= *getNoteElementList;
	*getHeadingText			= *getHeadingContent;
	*getUserFieldElement		= *getUserField;
	*cellType			= *fieldType;
	*cellValueAttributeName		= *fieldValueAttributeName;
	*cellCurrency			= *fieldCurrency;
	*getStyle			= *textStyle;
	*setStyle			= *textStyle;
	}

#-----------------------------------------------------------------------------
# default text style attributes

our	%DEFAULT_TEXT_STYLE	=
	(
	references	=>
		{
		'style:name'			=> undef,
		'style:family'			=> 'paragraph',
		'style:parent-style-name'	=> 'Standard',
		'style:next-style-name'		=> 'Standard',
		'style:class'			=> 'text'
		},
	properties	=>
		{
		}
	);

#-----------------------------------------------------------------------------
# default delimiters for flat text export

our	%DEFAULT_DELIMITERS	=
	(
	'text:footnote-citation'	=>
		{
		begin	=>	'[',
		end	=>	']'
		},
	'text:note-citation'		=>
		{
		begin	=>	'[',
		end	=>	']'
		},
	'text:footnote-body'		=>
		{
		begin	=>	'{NOTE: ',
		end	=>	'}'
		},
	'text:note-body'		=>
		{
		begin	=>	'{NOTE: ',
		end	=>	'}'
		},
	'text:span'			=>
		{
		begin	=>	'<<',
		end	=>	'>>'
		},
	'text:list-item'		=>
		{
		begin	=>	'- ',
		end	=>	''
		},
	);

#-----------------------------------------------------------------------------

our $ROW_REPEAT_ATTRIBUTE       = 'table:number-rows-repeated';
our $COL_REPEAT_ATTRIBUTE       = 'table:number-columns-repeated';

#-----------------------------------------------------------------------------

sub	fieldType
	{
	my $self	= shift;
	my $field	= shift		or return undef;
	my $newtype	= shift;
	my $prefix	= $self->{'opendocument'} ? 'office' : 'table';
	my $attribute	= $prefix . ':value-type';
	my $oldtype	= $field->att($attribute);
	unless (defined $newtype)
		{
		return $oldtype;
		}
	else
		{
		if (($newtype eq 'date') || ($newtype eq 'time'))
			{
			$field->del_att($prefix . ':value');
			}
		else
			{
			$field->del_att($prefix . ':date-value');
			$field->del_att($prefix . ':time-value');
			}
		return $field->set_att($attribute, $newtype);
		}
	}

sub	fieldValueAttributeName
	{
	my $self	= shift;
	my $field	= shift		or return undef;

	my $value_type	= ref $field ?
				$self->fieldType($field)	:
				$field;
	my $attribute	= "";
	my $prefix	= $self->{'opendocument'} ? 'office' : 'table';
	if	(
			($value_type eq 'string')	||
			($value_type eq 'date')		||
			($value_type eq 'time')
		)
		{
		$attribute = $prefix . ':' . $value_type . '-value';
		}
	else
		{
		$attribute = $prefix . ':value';
		}
	return $attribute;
	}

#-----------------------------------------------------------------------------
# constructor

sub	new
	{
	my $caller	= shift;
	my $class	= ref($caller) || $caller;
	my %options	=
		(
		level_attr	=> 'text:outline-level',
		paragraph_style	=> 'Standard',
		heading_style	=> 'Heading_20_1',
		use_delimiters	=> 'on',
		field_separator	=> ';',
		line_separator	=> "\n",
		max_rows	=> 32,
		max_cols	=> 26,
		delimiters	=>
			{ %OpenOffice::OODoc::Text::DEFAULT_DELIMITERS },
		@_
		);
	$options{heading_style} = $options{header_style}
		if $options{header_style};

	my $object	= $class->SUPER::new(%options);

	if ($object)
		{
		bless $object, $class;
		unless ($object->{'opendocument'})
			{
			$object->{'level_attr'}		= 'text:level';
			$object->{'heading_style'}	= 'Heading 1';
			}
		}
	return $object;
	}

#-----------------------------------------------------------------------------
# getText() method adaptation for complex elements
# and text output "enrichment"
# (overrides getText from OODoc::XPath)

sub	getText
	{
	my $self	= shift;
	my $element	= $self->getElement(@_);
	return undef	unless ($element && $element->isElementNode);

	my $text	= undef;
	my $begin_text	= '';
	my $end_text	= '';

	my $line_break	= $self->{'line_separator'} || '';
	if ($self->{'use_delimiters'} && $self->{'use_delimiters'} eq 'on')
		{
		my $name	= $element->getName;
		$begin_text	=
		    defined $self->{'delimiters'}{$name}{'begin'}	?
		        $self->{'delimiters'}{$name}{'begin'}		:
			($self->{'delimiters'}{'default'}{'begin'} || '');
		$end_text	=
		    defined $self->{'delimiters'}{$name}{'end'}		?
		        $self->{'delimiters'}{$name}{'end'}		:
			($self->{'delimiters'}{'default'}{'end'} || '');
		}

	$text	= $begin_text;

	if	($element->isParagraph)
		{
		my $t = $self->SUPER::getText($element);
		$text .= $t if defined $t;
		}
	elsif	($element->isItemList)
		{
		return $self->getItemListText($element);
		}
	elsif	(
		$element->isListItem		||
		$element->isNoteBody		||
		$element->isTableCell		||
		$element->isSection		||
		$element->isTextBox
		)
		{
		$element = $element->first_child('draw:text-box')
			if ($element->hasTag('draw:frame'));
		my @paragraphs = $element->children(qr '^text:(p|h)$');
		while (@paragraphs)
			{
			my $p = shift @paragraphs;
			my $t = $self->SUPER::getText($p);
			$text .= $t if defined $t;
			$text .= $line_break if @paragraphs;
			}
		}
	elsif	($element->isNote)
		{
		my $b = $element->selectChildElement
				('text:(|foot|end)note-body');
		return $self->getText($b);
		}
	elsif	($element->isTable)
		{
		$text .= $self->getTableContent($element);
		}
	else
		{
		my $t = $self->SUPER::getText($element);
		$text .= $t if defined $t;
		}

	$text	.= $end_text;

	return $text;
	}

#-----------------------------------------------------------------------------
# use or don't use delimiters for flat text output

sub	outputDelimitersOn
	{
	my $self	= shift;
	$self->{'use_delimiters'}	= 'on' ;
	}

sub	outputDelimitersOff
	{
	my $self	= shift;
	$self->{'use_delimiters'}	= 'off';
	}

sub	defaultOutputTerminator
	{
	my $self	= shift;
	my $delimiter	= shift;
	$self->{'delimiters'}{'default'}{'end'} = $delimiter
		if defined $delimiter;
	return $self->{'delimiters'}{'default'}{'end'};
	}

#-----------------------------------------------------------------------------
# setText() method adaptation for complex elements
# overrides setText from OODoc::XPath

sub	setText
	{
	my $self	= shift;
	my $path	= shift;
	my $pos		= (ref $path) ? undef : shift;
	my $element	= $self->getElement($path, $pos);
	return undef	unless $element;

	return $self->SUPER::setText($element, @_) if $element->isParagraph;

	my $line_break	= $self->{'line_separator'} || '';
	if	($element->isItemList)
		{
		my @text	= @_;
		foreach my $line (@text)
			{
			$self->appendItem($element, text => $line);
			}
		return wantarray ? @text : join $line_break, @text;
		}
	elsif	($element->isListItem)
		{
		return $self->setItemText($element, @_);
		}
	elsif	($element->isTableCell)
		{
		return $self->updateCell($element, @_);
		}
	elsif	(
		$element->isNoteBody		||
		$element->isTableCell		||
		$element->isSection
		)
		{
		$element->cut_children;
		return $self->appendParagraph
			(
			attachment	=> $element,
			text		=> shift,
			@_
			);
		}
	elsif	($element->isTextBox)
		{
		return $self->setTextBoxContent($element, shift);
		}
	elsif	($element->isNote)
		{
		my $b = $element->selectChildElement
				('text:(|foot|end)note-body');
		return $self->setText($b, @_);
		}
	else
		{
		return $self->SUPER::setText($element, @_);
		}
	}

#-----------------------------------------------------------------------------
# get the whole text content of the document in a readable (non-XML) form
# result is a list of strings or a single string

sub	getTextContent
	{
	my $self	= shift;
	return $self->selectTextContent('.*', @_);
	}

#-----------------------------------------------------------------------------
# get/set the text:id attribute of a given element

sub	textId
	{
	my $self	= shift;
	my $element	= shift		or return undef;
	return $element->textId(@_);
	}

#-----------------------------------------------------------------------------
# selects headings, paragraph & list item elements matching a given pattern
# returns a list of elements
# if $action is defined, it's treated as a reference to a callback procedure
# to be executed for each node matching the pattern, with the node as arg.

sub	selectElementsByContent
	{
	my $self	= shift;
	my $pattern	= shift;

	my $context = $self->{'context'}->isa('OpenOffice::OODoc::Element') ?
			$self->{'context'} : $self->{'body'};


	my @elements	= ();
	foreach my $element ($context->getChildNodes)
		{
		next if
			(
				(! $element->isElementNode)
				||
				($element->isSequenceDeclarations)
			);
		push @elements, $element
			if (
				(! $pattern)
				||
				($pattern eq '.*')
				||
				(defined $self->_search_content
					($element, $pattern, @_, $element))
			   );
		}

	return @elements;
	}

#-----------------------------------------------------------------------------

sub	selectElementByTextId
	{
	my $self	= shift;
	my $id		= $self->inputTextConversion(shift) or return undef;
	return $self->getNodeByXPath("//*[\@text:id=\"$id\"]");
	}

#-----------------------------------------------------------------------------
# select the 1st element matching a given pattern

sub	selectElementByContent
	{
	my $self	= shift;
	my $pattern	= shift;

	my $context = $self->{'context'}->isa('OpenOffice::OODoc::Element') ?
			$self->{'context'} : $self->{'body'};

	foreach my $element ($context->getChildNodes)
		{
		next if
			(
				(! $element->isElementNode)
				||
				($element->isSequenceDeclarations)
			);
		return $element
			if (
				(! $pattern)
				||
				($pattern eq '.*')
				||
				(defined $self->_search_content
					($element, $pattern, @_, $element))
			   );
		}
	return undef;
	}

#-----------------------------------------------------------------------------
# selects texts matching a given pattern, with optional replacement on the fly
# returns the whole text content
# result is a list of strings or a single string

sub	selectTextContent
	{
	my $self	= shift;
	my $pattern	= shift;

	my $line_break	= $self->{'line_separator'} || '';
	my @lines	= ();

	my $context = $self->{'context'}->isa('OpenOffice::OODoc::Element') ?
			$self->{'context'} : $self->{'body'};

	foreach my $element ($context->getChildNodes)
		{
		next if
			(
				(! $element->isElementNode)
				||
				($element->isSequenceDeclarations)
			);
		push @lines, $self->getText($element)
			    if (
				(! $pattern)
				||
				($pattern eq '.*')
				||
				(defined $self->_search_content
					($element, $pattern, @_, $element))
			       );
		}
	return wantarray ? @lines : join $line_break, @lines;
	}

#-----------------------------------------------------------------------------
# get the list of text elements

sub	getTextElementList
	{
	my $self	= shift;

	my $context = $self->{'context'}->isa('OpenOffice::OODoc::Element') ?
			$self->{'context'} : $self->{'body'};

	return $self->selectChildElementsByName
			(
			$context,
			qr '^t(ext:(h|p|.*list|table.*)|able:.*)$',
			@_
			);
	}

#-----------------------------------------------------------------------------
# get the list of paragraph elements

sub	getParagraphList
	{
	my $self	= shift;
	return $self->getDescendants('text:p', @_)
	}

#-----------------------------------------------------------------------------
# get the paragraphs as a list of strings

sub	getParagraphTextList
	{
	my $self	= shift;

	return $self->getTextList('//text:p', @_);
	}

#-----------------------------------------------------------------------------
# get the list of heading elements

sub	getHeadingList
	{
	my $self	= shift;
	my %opt		= @_;
	my $path	= undef;

	unless ($opt{'level'})
		{
		return $self->getDescendants('text:h', $opt{'context'});
		}
	else
		{
		$path	=	'//text:h[@' . $self->{'level_attr'}	.
				'="' . $opt{'level'} . '"]';
		}
	return $self->getElementList($path, $opt{'context'});
	}

#-----------------------------------------------------------------------------
# get the headings as a list of strings

sub	getHeadingTextList
	{
	my $self	= shift;
	my @nodes	= $self->getHeadingList(@_);
	if (wantarray)
		{
		my @list = ();
		foreach my $node (@nodes)
			{
			push @list, $self->getText($node);
			}
		return @list;
		}
	else
		{
		my $text = "";
		my $separator = $self->{'line_separator'} || '';
		foreach my $node (@nodes)
			{
			$text .= $self->getText($node);
			$text .= $separator;
			}
		return $text;
		}
	}

#-----------------------------------------------------------------------------
# get the list of span elements (i.e. text elements distinguished from their
# containing paragraph by any kind of attribute such as font, color, etc)

sub	getSpanList
	{
	my $self	= shift;
	return $self->getDescendants('text:span', @_);
	}

#-----------------------------------------------------------------------------
# get the span elements as a list of strings

sub	getSpanTextList
	{
	my $self	= shift;

	return $self->getTextList('//text:span', @_);
	}

#-----------------------------------------------------------------------------
# set text spans that are attributed using a particular style

sub	setSpan
	{
	my $self	= shift;
	my $last	= pop;
	my $tag		= 'text:span';
	if ($last =~ /:/)
		{
		$tag = $last;
		}
	else
		{
		push @_, $last;
		}
	my $path	= shift;
	my $pos		= ref $path ? undef : shift;

	my $element	= undef;
	my $span	= undef;
	if (ref $path)
		{
		if ($path->isElementNode)
			{ $element = $path; }
		else
			{ return undef; }
		}
	else
		{
		my $context	= shift;
		unless (ref $context)
			{
			$element = $self->getElement($path, $pos)
					or return undef;
			unshift @_, $context;
			}
		else
			{
			$element = $self->getElement
						($path, $pos, $context)
					or return undef;
			}
		}
	my $expression = shift; return undef unless defined $expression;
	my $value = shift or return undef;
	my %attrs = (@_);
	if ($tag eq 'text:span')
		{
		$attrs{'text:style-name'}	= $value;
		}
	elsif ($tag eq 'text:a')
		{
		$attrs{'xlink:href'}		= $value;
		my $prefix = $attrs{'-prefix'} || 'text';
		delete $attrs{'-prefix'};
		foreach my $k (keys %attrs)
			{
			unless ($k =~ /:/)
				{
				$attrs{"$prefix:$k"} = $attrs{$k};
				delete $attrs{$k};
				}
			}
		}

	return $element->mark("($expression)", $tag, { %attrs });
	}

#-----------------------------------------------------------------------------

sub	textField
	{
	my $self	= shift;
	my $name	= shift;
	my %opt		=
		(
		'-prefix'	=> 'text',
		@_
		);
	return $self->create_field($name, %opt);
	}

#-----------------------------------------------------------------------------

sub	setTextField
	{
	my $self	= shift;
	my $path	= shift;
	my $pos		= ref $path ? undef : shift;

	my $element	= undef;
	my $span	= undef;
	if (ref $path)
		{
		if ($path->isElementNode)
			{ $element = $path; }
		else
			{ return undef; }
		}
	else
		{
		my $context	= shift;
		unless (ref $context)
			{
			$element = $self->getElement($path, $pos)
					or return undef;
			unshift @_, $context;
			}
		else
			{
			$element = $self->getElement
						($path, $pos, $context)
					or return undef;
			}
		}

	my $expression = shift; return undef unless defined $expression;
	my $field = shift or return undef;
	my $tag = $field =~ /:/ ? $field : "text:$field";
	my %attrs = (@_);
	my $prefix = $attrs{'-prefix'} || 'text'; delete $attrs{'-prefix'};
	foreach my $k (keys %attrs)
		{
		unless ($k =~ /:/)
			{
			$attrs{"$prefix:$k"} = $attrs{$k}; delete $attrs{$k};
			}
		}

	return $element->mark("($expression)", $tag, { %attrs });
	}

#-----------------------------------------------------------------------------

sub	extendText
	{
	my $self	= shift;
	my $path	= shift;
	my $pos		= (ref $path) ? undef : shift;
	my $element = $self->getElement($path, $pos) or return undef;
	my $text	= shift;
	return undef	unless defined $text;
	my $style	= shift;

	if (ref $text)
		{
		my $tagname = $text->getName;
		if ($tagname =~ /^text:(p|h)$/)
			{
			$text = $self->getFlatText($text);
			}
		}

	if ($style)
		{
		$text = $self->createElement('text:span', $text)
					unless ref $text;
		$self->textStyle($text, $style);
		}
	return $self->SUPER::extendText($element, $text, @_);
	}

#-----------------------------------------------------------------------------

sub	setHyperlink
	{
	my $self	= shift;
	return $self->setSpan(@_, 'text:a');
	}

#-----------------------------------------------------------------------------

sub	selectHyperlinkElements
	{
	my $self	= shift;
	my $url		= shift;
	return $self->selectElementsByAttribute
		('//text:a', 'xlink:href', $url, @_);
	}

#-----------------------------------------------------------------------------

sub	selectHyperlinkElement
	{
	my $self	= shift;
	my $url		= shift;
	return $self->selectElementByAttribute
		('//text:a', 'xlink:href', $url, @_);
	}

#-----------------------------------------------------------------------------

sub	hyperlinkURL
	{
	my $self	= shift;
	my $hl		= shift	or return undef;
	unless (ref $hl)
		{
		$hl = $self->selectHyperlinkElement($hl);
		return undef unless $hl;
		}
	my $url		= shift;
	if ($url)
		{
		$self->setAttribute($hl, 'xlink:href', $url);
		}
	return $self->getAttribute($hl, 'xlink:href');
	}

#-----------------------------------------------------------------------------

sub	setAnnotation
	{
	my $self	= shift;
	my $path	= shift;
	my $pos		= ref $path ? undef : shift;
	my $element	= $self->getElement($path, $pos);
	my %opt		=
		(
		'offset'	=> 0,
		'text'		=> "",
		'style'		=> 'Standard',
		@_
		);

	my $creator = $opt{'creator'} || $opt{'author'} || $ENV{'USER'};
	my $date = (defined $opt{'date'}) ?
		$opt{'date'}	:
		OpenOffice::OODoc::XPath::odfLocaltime();
	my $annotation	= $element->insertNewNode
		('office:annotation', 'within', $opt{'offset'});
	$self->appendElement
		($annotation, 'dc:creator', text => $creator);
	$self->appendElement
		($annotation, 'dc:date', text => $date);
	$self->appendParagraph
		(
		attachment	=> $annotation,
		text		=> $opt{'text'},
		style		=> $opt{'style'}
		);

	return $annotation;
	}

#-----------------------------------------------------------------------------

sub	removeSpan
	{
	my $self	= shift;
	my $path	= shift;
	my $pos		= ref $path ? undef : shift;
	my $tagname	= shift	|| 'text:span';

	my $element	= ref $path ?
				$path	:
				$self->getElement($path, @_);
	return undef	unless $element;

	my $text	= "";
	my @nodes	= $element->getChildNodes;
	my $n		= undef;
	my $last_text_node = undef;
	foreach $n (@nodes)
		{
		if	($n->isTextNode)
			{
			$last_text_node	= $n;
			}
		elsif	($n->isElementNode && $n->hasTag($tagname))
			{
			my $t = $n->string_value;
			if ($last_text_node)
				{
				$last_text_node->append_pcdata($t);
				}
			else
				{
				$last_text_node =
				    OpenOffice::OODoc::XPath::new_text_node($t);
				$element->insertBefore($last_text_node, $n);
				}
			$n->delete;
			}
		}

	return $element;
	}

#-----------------------------------------------------------------------------

sub	removeHyperlink
	{
	my $self	= shift;
	return $self->removeSpan(@_, 'text:a');
	}

#-----------------------------------------------------------------------------
# get all the bibliographic entries

sub	getBibliographyMarks
	{
	my $self	= shift;
	my $id		= shift;

	unless ($id)
		{
		return $self->getDescendants('text:bibliography-mark');
		}
	else
		{
		return $self->selectElementsByAttribute
			(
			'//text:bibliography-mark', 'text:identifier',
			$id, @_
			);
		}
	}

#-----------------------------------------------------------------------------
# get/set the content of a bibliography entry

sub	bibliographyEntryContent
	{
	my $self	= shift;
	my $id		= shift;
	my $e		= undef;
	my %desc	= @_;
	unless (ref $id)
		{
		my $i = $self->inputTextConversion($id);
		$e = $self->getNodeByXPath
		      (
		      "//text:bibliography-mark[\@text:identifier=\"$i\"]",
		      $desc{'context'}
		      );
		}
	else
		{
		$e = $id;
		}
	return undef unless $e;

	my $k = undef;
	foreach $k (keys %desc)
		{
		next if $k =~ /:/;
		my $v = $desc{$k};
		delete $desc{$k};
		$k = 'text:' . $k;
		$desc{$k} = $v;
		}
	$self->setAttributes($e, %desc);
	%desc = $self->getAttributes($e);
	foreach $k (keys %desc)
		{
		my $new_key = $k;
		$new_key =~ s/^text://;
		my $v = $desc{$k}; delete $desc{$k}; $desc{$new_key} = $v;
		}
	return %desc;
	}

#-----------------------------------------------------------------------------
# inserts a new bibliography entry within a text element

sub	setBibliographyMark
	{
	my $self	= shift;
	my $path	= shift;
	my $pos		= ref $path ? undef : shift;
	my $element	= $self->getElement($path, $pos);
	my $offset	= shift;
	my %opt		= @_;
# 	my $bib	= $self->createElement('text:bibliography-mark');
	my $bib	= OpenOffice::OODoc::Element->new('text:bibliography-mark');
	$bib->paste_within($element, $offset);
	$self->bibliographyEntryContent($bib, @_);
	return $bib;
	}

#-----------------------------------------------------------------------------
# get a bookmark

sub	getBookmark
	{
	my $self	= shift;
	my $name	= $self->inputTextConversion(shift);

	return	(
		$self->getNodeByXPath
			("//text:bookmark[\@text:name=\"$name\"]")
			||
		$self->getNodeByXPath
			("//text:bookmark-start[\@text:name=\"$name\"]")
		);
	}

#-----------------------------------------------------------------------------
# retrieve the element where is a given bookmark

sub	selectElementByBookmark
	{
	my $self	= shift;

	my $bookmark	= $self->getBookmark(@_);
	return $bookmark ? $bookmark->parent : undef;
	}

#-----------------------------------------------------------------------------
# attach a bookmark to a given element

sub	setBookmark
	{
	my $self	= shift;
	my $path	= shift;
	my $element     = ref $path ? $path : $self->getElement($path, shift);
	return undef unless $element;
	my $name	= shift;
	my $offset	= shift || 0;
	unless ($name)
		{
		warn	"[" . __PACKAGE__ . "::setBookmark] "	.
			"Missing bookmark name\n";
		return undef;
		}
	my $bookmark	= OpenOffice::OODoc::XPath::new_element
						('text:bookmark', @_);
	$self->setAttribute($bookmark, 'text:name', $name);
	return $bookmark->paste_within($element, $offset);
	}

#-----------------------------------------------------------------------------
# delete a bookmark

sub	deleteBookmark
	{
	my $self	= shift;

	$self->removeElement($self->getBookmark(@_));
	}

#-----------------------------------------------------------------------------
# get the footnote bodies in the document

sub	getFootnoteList
	{
	my $self	= shift;

	my $xpath = $self->{'opendocument'}	?
	    '//text:note[@text:note-class="footnote"]/text:note-body' :
	    '//text:footnote-body';
	return $self->getElementList($xpath, @_);
	}

#-----------------------------------------------------------------------------
# get the footnote citations in the document

sub	getFootnoteCitationList
	{
	my $self	= shift;

	my $xpath = $self->{'opendocument'}	?
	    '//text:note[@text:note-class="footnote"]/text:note-citation' :
	    '//text:footnote-citation';
	return $self->getElementList($xpath, @_);
	}

#-----------------------------------------------------------------------------
# get the endnote bodies in the document

sub	getEndnoteList
	{
	my $self	= shift;

	my $xpath = $self->{'opendocument'}	?
	    '//text:note[@text:note-class="endnote"]/text:note-body' :
	    '//text:endnote-body';
	return $self->getElementList($xpath, @_);
	}

#-----------------------------------------------------------------------------
# get the endnote citations in the document

sub	getEndnoteCitationList
	{
	my $self	= shift;

	my $xpath = $self->{'opendocument'}	?
	    '//text:note[@text:note-class="endnote"]/text:note-citation' :
	    '//text:endnote-citation';
	return $self->getElementList($xpath, @_);
	}

#-----------------------------------------------------------------------------
# get the note citations in the document (ODF only)

sub	getNoteCitationList
	{
	my $self	= shift;
	return $self->getDescendants('text:note-citation', @_);
	}

#-----------------------------------------------------------------------------

sub	getNoteElementList
	{
	my $self	= shift;
	my $class	= shift;

	unless ($class)
		{
		if ($self->{'opendocument'})
			{
			return $self->getElementList('//text:note');
			}
		else
			{
			return	(
				$self->getElementList('//text:footnote'),
				$self->getElementList('//text:endnote')
				);
			}
		}
	elsif (($class eq 'footnote') or ($class eq 'endnote'))
		{
		if ($self->{'opendocument'})
			{
			return $self->getElementList
			    ("//text:note\[\@text:note-class=\"$class\"\]");
			}
		else
			{
			return $self->getElementList("//text:$class");
			}
		}
	else
		{
		warn	"[" . __PACKAGE__ . "::getNoteElementList] " .
			"Unknown note class $class\n";
		return undef;
		}
	}

#-----------------------------------------------------------------------------
# retrieve a note element using its identifier (ODF only)

sub	getNoteElement
	{
	my $self	= shift;
	my $p1		= shift;
	if (ref $p1)
		{
		return $p1->isNote ? $p1 : undef;
		}
	else
		{
		unshift @_, $p1;
		}
	my %opt		= @_;

	my $xpath	= undef;
	my $id		= $opt{id};
	my $class	= $opt{class};
	my $citation	= $opt{citation};

	if ($id)
		{
		unless ($self->{'opendocument'})
			{
			return	$self->getElement
				    ("//text:$class\[\@text:id=\"$id\"\]")
				    if $class;
			return 	$self->getElement
				    ("//text:footnote\[\@text:id=\"$id\"\]")
					||
				$self->getElement
				    ("//text:endnote\[\@text:id=\"$id\"\]");
			}
		else
			{
			my $xpath = $class ?
			    "//text:note\[\@text:note-class=\"$class\"" .
			    " and \@text:id=\"$id\"\]"			:
			    "//text:note\[\@text:id=\"$id\"\]";
			return $self->getElement($xpath);
			}
		}
	elsif ($class && defined $citation)
		{
		my @list = $self->getNoteElementList($class);
		my $tagname = $self->{'opendocument'} ?
			"text:note-citation" : "text:$class-citation";
		foreach my $elt (@list)
			{
			next unless $elt;
			my $text = $self->getFlatText
					($elt->first_child($tagname));
			return $elt if $text eq $citation;
			}
		return undef;
		}
	else
		{
		warn	"[" . __PACKAGE__ . "::getNoteElement] " .
			"Requires (Id) OR (class AND citation)\n";
		return undef;
		}
	}

#-----------------------------------------------------------------------------

sub	getNoteClass
	{
	my $self	= shift;
	my $element	= shift	or return undef;
	unless (ref $element)
		{
		unshift @_, $element;
		$element = $self->getNoteElement(@_) or return undef;
		}
	return $element->getNoteClass;
	}

#-----------------------------------------------------------------------------
# get the list of tables in the document

sub	getTableList
	{
	my $self	= shift;
	return $self->getElementList('//table:table', @_);
	}

#-----------------------------------------------------------------------------
# get a heading element selected by position number and level

sub	getHeading
	{
	my $self	= shift;
	my $pos		= shift;
	my %opt		= (@_);
	my $heading	= undef;

	if (ref $pos)
		{
		return undef unless $pos->isHeading;
		if ($opt{'level'})
			{
			my $level = $pos->att($self->{'level_attr'});
			return undef unless
				($level && ($level == $opt{'level'}));
			}
		return $pos;
		}

	unless ($opt{'level'})
		{
		$heading = $self->getElement
				('//text:h', $pos, $opt{'context'});
		}
	else
		{
		my $path	=	'//text:h[@'		.
					$self->{'level_attr'}	.
					'="' . $opt{'level'} . '"]';
		$heading = $self->getElement
			($path, $pos, $opt{'context'});
		}
	return undef unless $heading;
	}

#-----------------------------------------------------------------------------
# get the text of a heading element

sub	getHeadingContent
	{
	my $self	= shift;
	return $self->getText('//text:h', @_);
	}

#-----------------------------------------------------------------------------
# get the level attribute (if defined) of an element
# the level must be defined for heading elements

sub	getLevel
	{
	my $self	= shift;
	my $path	= shift;
	my $pos		= (ref $path) ? undef : shift;

	my $element	= $self->getElement($path, $pos, @_);
	return $element->getAttribute($self->{'level_attr'}) || "";
	}

#-----------------------------------------------------------------------------

sub	setLevel
	{
	my $self	= shift;
	my $path	= shift;
	my $pos		= (ref $path) ? undef : shift;
	my $level	= shift;

	my $element	= $self->getElement($path, $pos, @_) or return undef;
	return $element->setAttribute($self->{'level_attr'} => $level);
	}

#-----------------------------------------------------------------------------

sub	makeHeading
	{
	my $self	= shift;
	my %opt		= @_;
	my $element	= $opt{'element'};
	if ($element)
		{
		$element->set_name('text:h');
		}
	else
		{
		$element = $self->createElement('text:h');
		}
	if ($opt{'level'})
		{
		$element->set_att($self->{'level_attr'}, $opt{'level'});
		}
	my $style = $opt{'style'} ? $opt{'style'} : $self->{'heading_style'};
	$self->setAttribute($element, 'text:style-name', $style);
	if (defined $opt{'text'})
		{
		$self->setText($element, $opt{'text'});
		}
	return $element;
	}

#-----------------------------------------------------------------------------

sub	getSection
	{
	my $self	= shift;
	my $name	= shift;
	return undef unless defined $name;

	if (ref $name)
		{
		return ($name->isSection) ? $name : undef;
		}
	my $context	= shift;
	if (($name =~ /^\d*$/) || ($name =~ /^[\d+-]\d+$/))
		{
		return $self->getElement('//text:section', $name, $context);
		}

	my $n = $self->inputTextConversion($name);
	return $self->getNodeByXPath
			(
			"//text:section[\@text:name=\"$n\"]"
			);
	}

#-----------------------------------------------------------------------------

sub	getSectionList
	{
	my $self	= shift;
	return $self->getDescendants('text:section', @_);
	}

#-----------------------------------------------------------------------------

sub	sectionStyle
	{
	my $self	= shift;
	my $section	= $self->getSection(shift) or return undef;
	my $new_style	= shift;
	return $new_style ?
		$self->setAttribute($section, 'text:style-name', $new_style) :
		$self->getAttribute($section, 'text:style-name');
	}

#-----------------------------------------------------------------------------

sub	renameSection
	{
	my $self	= shift;
	my $section	= $self->getSection(shift) or return undef;
	my $newname	= shift or return undef;

	if ($self->getSection($newname))
		{
		warn	"[" . __PACKAGE__ . "::renameSection] " .
			"Section name $newname already in use\n";
		return undef;
		}
	return $self->setAttribute($section, 'text:name' => $newname);
	}

#-----------------------------------------------------------------------------

sub	sectionName
	{
	my $self	= shift;
	my $section	= $self->getSection(shift) or return undef;
	my $newname	= shift;
	return $newname ?
		$self->renameSection($section, $newname)	:
		$self->getAttribute($section, 'text:name');
	}

#-----------------------------------------------------------------------------

sub	appendSection
	{
	my $self	= shift;
	my $name	= shift;
	my %opt		=
			(
			'attachment'	=> $self->{'body'},
			'style'		=> $name,
			'protected'	=> 'false',
			@_
			);

	if ($self->getSection($name, $self->{'xpath'}))
		{
		warn	"[" . __PACKAGE__ . "::appendSection] "	.
			"Section $name exists\n";
		return	undef;
		}

	my $link	= undef;
	if ($opt{"link"})
		{
		$link	= $opt{'link'}; delete $opt{'link'}
		}

	my $section = $self->appendElement
			(
			$opt{'attachment'}, 'text:section',
			attribute =>
			    {
			    'text:name'			=> $name,
			    'text:style-name'		=> $opt{'style'}
			    },
			%opt
			)
			or return undef;

	$self->insertSubdocument
		($section, $link, $opt{'filter'}) if $link;
	$section->set_att('text:protected', $opt{'protected'})
			if $opt{'protected'};
	$section->set_att('text:protection-key', $opt{'key'})
			if $opt{'key'};

	return $section;
	}

#-----------------------------------------------------------------------------

sub	lockSection
	{
	my $self	= shift;
	my $section	= $self->getSection(shift)	or return undef;
	$section->set_att('text:protected', 'true');
	my $key		= shift;
	$section->set_att('text:protection-key', $key) if $key;
	}

sub	unlockSection
	{
	my $self	= shift;
	my $section	= $self->getSection(shift)	or return undef;
	$section->del_att('text:protected');
	my $key		= $section->att('text:protection-key');
	$section->del_att('text:protection-key');
	return $key;
	}

sub	unlockSections
	{
	my $self	= shift;
	foreach my $section ($self->getSectionList(@_))
		{
		$self->unlockSection($section);
		}
	}

sub	sectionProtectionKey
	{
	my $self	= shift;
	my $section	= $self->getSection(shift)	or return undef;
	return $section->att('text:protection-key');
	}

#-----------------------------------------------------------------------------

sub	insertSection
	{
	my $self	= shift;
	my $path	= shift;
	my $pos		= ref $path ? undef : shift;
	my $name	= shift;
	my %opt		=
			(
			'style'		=> $name,
			'protected'	=> 'false',
			@_
			);
	my $posnode	= $self->getElement($path, $pos, $opt{'context'})
				or return undef;

	if ($self->getSection($name, $self->{'xpath'}))
		{
		warn	"[" . __PACKAGE__ . "::insertSection] "	.
			"Section $name exists\n";
		return	undef;
		}

	my $link	= undef;
	if ($opt{"link"})
		{
		$link	= $opt{'link'}; delete $opt{'link'}
		}

	my $section = $self->insertElement
			(
			$posnode, 'text:section',
			attribute =>
			    {
			    'text:name'			=> $name,
			    'text:style-name'		=> $opt{'style'}
			    },
			%opt
			)
			or return undef;

	$self->insertSubdocument
		($section, $link, $opt{'filter'}) if $link;
	$section->set_att('text:protected', $opt{'protected'})
			if $opt{'protected'};
	$section->set_att('text:protection-key', $opt{'key'})
			if $opt{'key'};

	return $section;
	}

#-----------------------------------------------------------------------------
# link a section to a subdocument

our	$section_source_tag	= "text:section-source";

sub	insertSubdocument
	{
	my $self	= shift;
	my $section_id	= shift;
	my $url		= shift;
	my %attr	= ();

	my $section	= $self->getSection($section_id);
	unless ($section)
		{
		warn	"[" . __PACKAGE__ . "::insertSubdocument] "	.
			"Non existing target section\n";
		return undef;
		}
	my $doclink	=
		$section->first_child($section_source_tag)
				||
		$self->appendElement($section, $section_source_tag);

	if ($attr{'filter'})
		{
		$attr{'text:filter-name'} = $attr{'filter'};
		delete $attr{'filter'};
		}
	$self->setAttributes($doclink, "xlink:href" => $url, %attr);

	return $doclink;
	}

#-----------------------------------------------------------------------------
# get the content depending on a given heading element

sub	getChapterContent
	{
	my $self	= shift;
	my $h		= shift || 0;
	my $heading	= ref $h ? $h : $self->getHeading($h, @_);
	return undef unless $heading;
	my @list	= ();
	my $level	= $self->getLevel($heading) or return @list;

	my $next_element	= $heading->next_sibling;
	while ($next_element)
		{
		my $l = $self->getLevel($next_element);
		last if ($l && $l <= $level);
		push @list, $next_element;
		$next_element = $next_element->next_sibling;
		}

	return @list;
	}

#-----------------------------------------------------------------------------

sub	moveElementsToSection
	{
	my $self	= shift;
	my $section	= $self->getSection(shift) or return undef;
	$section->pickUpChildren(@_);
	return $section;
	}

#-----------------------------------------------------------------------------
# get a paragraph element selected by number

sub	getParagraph
	{
	my $self	= shift;
	return $self->getElement('//text:p', @_);
	}

#-----------------------------------------------------------------------------
# same as getParagraph() but only among the 1st level paragraphs
# and only in text documents

sub	getTopParagraph
	{
	my $self	= shift;
	my $path = $self->{'opendocument'} ?
		'//office:body/office:text/text:p'	:
		'//office:body/text:p';
	return $self->getElement($path, @_);
	}

#-----------------------------------------------------------------------------
# select paragraphs by stylename

sub	selectParagraphsByStyle
	{
	my $self	= shift;
	return $self->selectElementsByAttribute
		('//text:p', 'text:style-name', @_);
	}

#-----------------------------------------------------------------------------
# select a single paragraph by stylename

sub	selectParagraphByStyle
	{
	my $self	= shift;
	return $self->selectElementByAttribute
		('//text:p', 'text:style-name', @_);
	}

#-----------------------------------------------------------------------------
# get text content of a paragraph

sub	getParagraphText
	{
	my $self	= shift;
	return $self->getText('//text:p', @_);
	}

#-----------------------------------------------------------------------------
# select a draw page by name

sub	selectDrawPageByName
	{
	my $self	= shift;
	my $text	= $self->inputTextConversion(shift);
	return $self->selectNodeByXPath
			("//draw:page\[\@draw:name=\"$text\"\]", @_);
	}
#-----------------------------------------------------------------------------
# get a draw page by position or name

sub	getDrawPage
	{
	my $self	= shift;
	my $p		= shift;
	return undef unless defined $p;
	if (ref $p)	{ return ($p->isDrawPage) ? $p : undef; }
	if ($p =~ /^[\-0-9]*$/)
		{
		return $self->getElement('//draw:page', $p, @_);
		}
	else
		{
		return $self->selectDrawPageByName($p, @_);
		}
	}

#-----------------------------------------------------------------------------

sub	getDrawPages
	{
	my $self	= shift;
	return $self->getDescendants('draw:page', @_);
	}

#-----------------------------------------------------------------------------
# create a draw page (to be inserted later)

sub	createDrawPage
	{
	my $self        = shift;
	my $class	= $self->contentClass;
	unless ($class eq 'presentation' || $class eq 'drawing')
		{
		warn	"[" . __PACKAGE__ . "::createDrawPage] "	.
			"Unsupported operation for this document\n";
		return undef;
		}
        my %opt         = @_;
        my $body        = $self->getBody;

        my $p = $self->createElement('draw:page');
        $self->setAttribute($p, 'draw:name' => $opt{'name'})
                        if $opt{'name'};
        $self->setAttribute($p, 'draw:id' => $opt{'id'})
                        if $opt{'id'};
        $self->setAttribute($p, 'draw:style-name' => $opt{'style'})
                        if $opt{'style'};
        $self->setAttribute($p, 'draw:master-page-name' => $opt{'master'})
                        if $opt{'master'};
        return $p;
	}

#-----------------------------------------------------------------------------
# append a new draw page to the document

sub	appendDrawPage
	{
	my $self        = shift;
        my $page	= $self->createDrawPage(@_) or return undef;
        my $body        = $self->getBody;
        $self->appendElement($body, $page);
        return $page;
 	}

#-----------------------------------------------------------------------------
# insert a new draw page before or after an existing one

sub	insertDrawPage
	{
	my $self	= shift;
	my $pos		= shift	or return undef;
	my $pos_page	= $self->getDrawPage($pos);
	unless ($pos_page)
		{
		warn	"[" . __PACKAGE__ . "::insertDrawPage] "	.
			"Unknown position\n";
		return undef;
		}
	my %opt = @_;
	my $page = $self->createDrawPage(%opt) or return undef;
	$self->insertElement($pos_page, $page, position => $opt{'position'});

	return $page;
	}

#-----------------------------------------------------------------------------

sub	drawPageAttribute
	{
	my $self	= shift;
	my $att		= shift;
	my $pos		= shift;
	my $page	= $self->getDrawPage($pos)	or return undef;
	my $value	= shift;

	return $value ?
		$self->setAttribute($page, $att, $value)	:
		$self->getAttribute($page, $att);
	}

#-----------------------------------------------------------------------------

sub	drawPageName
	{
	my $self	= shift;
	return $self->drawPageAttribute('draw:name', @_);
	}

#-----------------------------------------------------------------------------

sub	drawPageStyle
	{
	my $self	= shift;
	return $self->drawPageAttribute('draw:style-name', @_);
	}

#-----------------------------------------------------------------------------

sub	drawPageId
	{
	my $self	= shift;
	return $self->drawPageAttribute('draw:id', @_);
	}

#-----------------------------------------------------------------------------

sub	drawMasterPage
	{
	my $self	= shift;
	return $self->drawPageAttribute('draw:master-page-name', @_);
	}

#-----------------------------------------------------------------------------

sub	createTextBoxElement
	{
	my $self	= shift;
	my %opt		= @_;
	my $frame	= undef;
	my $text_box	= undef;
	if ($self->{'opendocument'})
		{
		$frame = $self->createFrame(tag => 'draw:frame', %opt);
		$text_box = $self->appendElement($frame, 'draw:text-box');
		}
	else
		{
		$text_box = $self->createFrame(tag => 'draw:text-box', %opt);
		$frame = $text_box;
		}
	if ($opt{'content'})
		{
		if (ref $opt{'content'})
			{
			$opt{'content'}->paste_last_child($text_box);
			}
		else
			{
			$self->appendParagraph
				(
				attachment	=> $text_box,
				text		=> $opt{'content'}
				);
			}
		}
	return wantarray ? ($frame, $text_box) : $text_box;
	}

#-----------------------------------------------------------------------------

sub	getTextBoxElement
	{
	my $self	= shift;
	my $tb		= shift;
	return undef unless defined $tb;

	if (ref $tb)
		{
		my $name = $tb->getName;
		if ($name eq 'draw:frame')
			{
			return $tb->first_child('draw:text-box') ?
					$tb : undef;
			}
		elsif ($name eq 'draw:text-box')
			{
			return $tb unless $self->{'opendocument'};
			my $frame = $tb->parent;
			return $frame->isFrame ? $frame : undef;
			}
		else
			{
			return undef;
			}
		}
	else
		{
		if ($tb =~ /^[\-0-9]*$/)
			{
			my $e = $self->getElement('//draw:text-box', $tb, @_);
			return $self->{'opendocument'} ?
				$e->parent() : $e;
			}
		else
			{
			return $self->selectTextBoxElementByName($tb, @_);
			}
		}
	}

#-----------------------------------------------------------------------------

sub	setTextBoxContent
	{
	my $self	= shift;
	my $frame = $self->getTextBoxElement(shift) or return undef;

	if ($frame->isFrame)
		{
		$frame = $frame->first_child('draw:text-box')
			or return undef;
		}

	$frame->cut_children;
	my $content	= shift;
	if (ref $content)
		{
		$content->paste_last_child($frame);
		return $content;
		}
	else
		{
		return $self->appendParagraph
			(
			attachment	=> $frame,
			text		=> $content
			);
		}
	}

#-----------------------------------------------------------------------------
# text box attributes accessors

sub	textBoxCoordinates
	{
	my $self	= shift;
	my $tb		= $self->getTextBoxElement(shift) or return undef;
	my $coord	= shift;
	return (defined $coord) ?
		$self->setObjectCoordinates($tb, $coord)	:
		$self->getObjectCoordinates($tb);
	}

sub	textBoxSize
	{
	my $self	= shift;
	my $tb		= $self->getTextBoxElement(shift) or return undef;
	my $size	= shift;
	return (defined $size) ?
		$self->setObjectSize($tb, $size)	:
		$self->getObjectSize($tb);
	}

sub	textBoxDescription
	{
	my $self	= shift;
	my $tb		= $self->getTextBoxElement(shift) or return undef;
	my $description	= shift;
	return (defined $description) ?
		$self->setObjectDescription($tb, $description)	:
		$self->getObjectDescription($tb);
	}

sub	textBoxName
	{
	my $self	= shift;
	my $tb		= $self->getTextBoxElement(shift) or return undef;
	return $self->objectName($tb, shift);
	}

#-----------------------------------------------------------------------------

sub	selectTextBoxElementByName
	{
	my $self	= shift;
	my $tag = $self->{'opendocument'} ? 'draw:frame' : 'draw:text-box';
	my $frame = $self->getFrameElement(shift, $tag);
	if ($self->{'opendocument'})
		{
		return undef unless ($frame->first_child('draw:text-box'));
		}
	return $frame;
	}

#-----------------------------------------------------------------------------

sub	getTextElementist
	{
	my $self	= shift;
	my $context	= shift;
	my @tblist = $self->getDescendants('draw:text-box', $context);
	return @tblist unless $self->{'opendocumpent'};
	my @frlist = ();
	foreach my $tb (@tblist)
		{
		push @frlist, $tb->parent;
		}
	return @frlist;
	}

#-----------------------------------------------------------------------------
# get list element

sub	getItemList
	{
	my $self	= shift;
	my $pos		= shift;
	if (ref $pos)
		{
		return $pos->isItemList ? $pos : undef;
		}
	return $self->getElement('//text:list', $pos, @_);
	}

#-----------------------------------------------------------------------------
# return the text content of an item list (in array or string)

sub	getItemListText
	{
	my $self	= shift;
	my $list	= $self->getItemList(@_) or return undef;
	my @items	= $list->children('text:list-item');
	if (wantarray)
		{
		my @result = ();
		foreach my $item (@items)
			{
			push @result, $self->getItemText($item);
			}
		return @result;
		}
	else
		{
		my $tagname	= $list->getName;
		my $line_break	=
			$self->{'line_separator'} || '';
		my $item_begin	=
			$self->{'delimiters'}{'text:p'}{'begin'} || '';
		my $item_end	=
			$self->{'delimiters'}{'text:p'}{'end'} || '';
		my $result	=
			$self->{'delimiters'}{$tagname}{'begin'} || '';
		my $end_list	=
			$self->{'delimiters'}{$tagname}{'end'} || '';
		my $count = 0;
		foreach my $item (@items)
			{
			$result .= $line_break if $count > 0;
			$result .= $item_begin;
			$result .= ($self->getItemText($item) || "");
			$result .= $item_end;
			$count++;
			}
		$result .= $end_list;
		return $result;
		}
	}

#-----------------------------------------------------------------------------
# get ordered list root element

sub	getOrderedList
	{
	my $self	= shift;
	my $pos		= shift;
	if (ref $pos)
		{
		return $pos->isOrderedList ? $pos : undef;
		}
	return $self->getElement('//text:ordered-list', $pos, @_);
	}

#-----------------------------------------------------------------------------
# get unordered list root element

sub	getUnorderedList
	{
	my $self	= shift;
	my $pos		= shift;
	if (ref $pos)
		{
		return $pos->isUnorderedList ? $pos : undef;
		}
	return $self->getElement('//text:unordered-list', $pos, @_);
	}

#-----------------------------------------------------------------------------
# get item elements list

sub	getItemElementList
	{
	my $self	= shift;
	my $list	= shift;
	return $list->children('text:list-item');
	}

#-----------------------------------------------------------------------------

sub	getListItem
	{
	my $self	= shift;
	my $list	= $self->getItemList(shift) or return undef;
	return $list->child(shift, 'text:list-item');
	}

#-----------------------------------------------------------------------------
# get item element text

sub	getItemText
	{
	my $self	= shift;
	my $item	= shift;

	return	undef	unless $item;
	my $para = $item->selectChildElement('text:(p|h)');
	return $para ? $self->getText($para) : undef;
	}

#-----------------------------------------------------------------------------
# set item element text

sub	setItemText
	{
	my $self	= shift;
	my $item	= shift;
	return	undef	unless $item;
	my $text	= shift;
	return undef unless (defined $text);

	my $para =	$item->selectChildElement('text:(p|h)')
				||
			$self->appendElement($item, 'text:p');
	return	$self->setText($para, $text);
	}

#-----------------------------------------------------------------------------
# get item element style

sub	getItemStyle
	{
	my $self	= shift;
	my $item	= shift;
	return	undef	unless $item;

	my $para	= $item->selectChildElement('text:(p|h)');
	return	$self->textStyle($para);
	}

#-----------------------------------------------------------------------------
# set item element style

sub	setItemStyle
	{
	my $self	= shift;
	my $item	= shift;
	return	undef	unless $item;
	my $style	= shift;

	my $para	= $item->selectChildElement('text:(p|h)');
	return	$self->textStyle($para, $style);
	}

#-----------------------------------------------------------------------------
# append a new item in a list

sub	appendListItem
	{
	my $self	= shift;
	my $list	= shift;
	return	undef	unless $list;
	my %opt		=
			(
			type	=> 'text:p',
			@_
			);

	my $type	= $opt{'type'};

	my $item	= $self->appendElement($list, 'text:list-item');
	return $item unless $type;

	my $text	= $opt{'text'};
	my $style	= $opt{'style'};
	$style	= $opt{'attribute'}{'text:style-name'}	unless $style;

	unless ($style)
		{
		my $first_item	= $list->selectChildElement('text:list-item');
		if ($first_item)
			{
			my $p	= $first_item->selectChildElement
					('text:(p|h)');
			$style	= $self->textStyle($p)	if ($p);
			}
		}

	if	($type eq 'paragraph')	{ $type = 'text:p'; }
	elsif	($type eq 'heading')	{ $type = 'text:h'; }

	my $para	= $self->appendElement
					(
					$item, $type,
					text => $text
					);
	$style	= $self->{'paragraph_style'}	unless $style;
	$opt{'attribute'}{'text:style-name'} = $style;
	$self->setAttributes($para, %{$opt{'attribute'}});

	return $item;
	}

sub	appendItem
	{
	my $self	= shift;
	return $self->appendListItem(@_);
	}

#-----------------------------------------------------------------------------
# append a new item list

sub	appendItemList
	{
	my $self	= shift;
	my %opt		= @_;
	my $name	= 'text:unordered-list';
	$opt{'attribute'}{'text:style-name'} = $opt{'style'} if $opt{'style'};
	$opt{'attribute'}{'text:style-name'} = $self->{'paragraph_style'}
		unless $opt{'attribute'}{'text:style-name'};
	$opt{'attribute'}{'text:continue-numbering'} =
		$opt{'continue-numbering'} if $opt{'continue-numbering'};

	if ($self->{'opendocument'})
		{
		$name	= 'text:list';
		}
	else
		{
		if (defined $opt{'type'} && ($opt{'type'} eq 'ordered'))
			{ $name = 'text:ordered-list' ; }
		}

	my $attachment = $opt{'attachment'} || $self->{'body'};
	return $self->appendElement($attachment, $name, %opt);
	}

#-----------------------------------------------------------------------------
# insert a new item list

sub	insertItemList
	{
	my $self	= shift;
	my $path	= shift;
	my $posnode	= (ref $path)	?
				$path	:
				$self->getElement($path, shift);
	my %opt		= @_;
	my $name	= 'text:unordered-list';
	$opt{'attribute'}{'text:style-name'} = $opt{'style'} if $opt{'style'};
	$opt{'attribute'}{'text:style-name'} = $self->{'paragraph_style'}
		unless $opt{'attribute'}{'text:style-name'};
	$opt{'attribute'}{'text:continue-numbering'} =
		$opt{'continue-numbering'} if $opt{'continue-numbering'};

	if ($self->{'opendocument'})
		{
		$name	= 'text:list';
		}
	else
		{
		if (defined $opt{'type'} && ($opt{'type'} eq 'ordered'))
			{ $name = 'text:ordered-list' ; }
		}

	return $self->insertElement($posnode, $name, %opt);
	}

#-----------------------------------------------------------------------------
# row expansion utility for _expand_table

sub	_expand_row
	{
	my $self	= shift;
	my $row		= shift;
	unless ($row)
		{
		warn	"[" . __PACKAGE__ . "::_expand_row] "	.
			"Unknown table row\n";
		return undef;
		}
	my $width	= shift;

	my @cells	= $row->selectChildElements
					('table:(covered-|)table-cell');

	my $cell	= undef;
	my $last_cell	= undef;
	my $rep		= 0;
	my $cellnum	= 0;
	while (@cells)
		{
		last	if (defined $width and ($cellnum >= $width));
		$cell = shift @cells;
		$last_cell = $cell;
		$rep  =	$cell	?
				$cell->getAttribute($COL_REPEAT_ATTRIBUTE) :
				0;
		if ($rep)
			{
			$cell->removeAttribute($COL_REPEAT_ATTRIBUTE);
			while ($rep > 1)
				{
				last if
				    (defined $width and ($cellnum >= $width));
				$last_cell = $last_cell->replicateNode;
				$rep--; $cellnum++;
				}
			}
		$cellnum++ if $cell;
		}

	$last_cell->setAttribute($COL_REPEAT_ATTRIBUTE, $rep)
			if ($rep && ($rep > 1));

	return $cellnum;
	}

#-----------------------------------------------------------------------------
# column expansion utility for _expand_table

sub	_expand_columns
	{
	my $self	= shift;
	my $table	= shift;
	return undef unless ($table && ref $table);
	my $width	= shift;

	my @cols	= $table->children('table:table-column');

	my $col		= undef;
	my $last_col	= undef;
	my $rep		= 0;
	my $colnum	= 0;
	while (@cols)
		{
		last if (defined $width and ($colnum >= $width));
		$col	= shift @cols; $last_col = $col;
		$rep =	$col	?
				$col->getAttribute($COL_REPEAT_ATTRIBUTE) :
				0;
		if ($rep)
			{
			$col->removeAttribute($COL_REPEAT_ATTRIBUTE);
			while ($rep > 1)
				{
				last if
				    (defined $width and ($colnum >= $width));
				$last_col = $last_col->replicateNode;
				$rep--; $colnum++;
				}
			}
		$colnum++ if $col;
		}

	$last_col->setAttribute($COL_REPEAT_ATTRIBUTE, $rep)
			if ($rep && ($rep > 1));
	return $colnum;
	}

#-----------------------------------------------------------------------------
# expands repeated table elements in order to address them in spreadsheets
# in the same way as in text documents

sub	_expand_table
	{
	my $self	= shift;
	my $table	= shift;
	my $length	= shift	|| $self->{'max_rows'};
	my $width	= shift || $self->{'max_cols'};
	return undef unless ($table && ref $table);
	if ($length && ($length eq 'full'))
		{
		$length = undef; $width = undef;
		}

	my $new_width = $self->_expand_columns($table, $width);

	my @rows	= ();
	my $header = $table->first_child('table:table-header-rows');
	@rows = $header->children('table:table-row') if $header;
	push @rows, $table->children('table:table-row');

	my $row		= undef;
	my $last_row	= undef;
	my $rep		= 0;
	my $rownum	= 0;
	while (@rows)
		{
		last	if (defined $length and ($rownum >= $length));
		$row	= shift @rows; $last_row = $row;
		my $last_width = $self->_expand_row($row, $width);
		$new_width = $last_width if $last_width > $new_width;
		$rep =	$row	?
				$row->getAttribute($ROW_REPEAT_ATTRIBUTE) :
				0;
		if ($rep)
			{
			$row->removeAttribute($ROW_REPEAT_ATTRIBUTE);
			while ($rep > 1)
				{
				last if
				    (defined $length and ($rownum >= $length));
				$last_row = $last_row->replicateNode;
				$rep--; $rownum++;
				}
			}
		$rownum++ if $row;
		}

	$last_row->setAttribute($ROW_REPEAT_ATTRIBUTE, $rep)
			if ($rep && ($rep > 1));

	return wantarray ? ($rownum, $new_width) : $table;
	}

#-----------------------------------------------------------------------------
# get a table size in ($lines, $columns) form

sub	getTableSize
	{
	my $self	= shift;
	my $table	= $self->getTable(@_)	or return undef;
	my $height	= 0;
	my $width	= 0;

	my @rows	= ();
	my $header = $table->first_child('table:table-header-rows');
	@rows = $header->children('table:table-row') if $header;
	push @rows, $table->children('table:table-row');
	foreach my $row (@rows)
		{
		my $rep = $row->getAttribute($ROW_REPEAT_ATTRIBUTE) || 1;
		$height += $rep;
		my @cells = $row->selectChildElements
					('table:(covered-|)table-cell');
		my $row_width = 0;
		foreach my $cell (@cells)
			{
			my $rep = $cell->getAttribute($COL_REPEAT_ATTRIBUTE);
			$row_width += $rep ? $rep : 1;
			}
		$width = $row_width if $row_width > $width;
		}
	return ($height, $width);
	}

#-----------------------------------------------------------------------------
# increases the size of an existing table
# improved by Barry Slaymaker [rt.cpan.org #41975]

sub	expandTable
	{
	my $self	= shift;
	my $table	= shift;
	my $length	= shift || 0;
	my $width	= shift || 0;
	my $context	= shift;

	my ($old_length, $old_width) = $self->getTableSize($table);
	$table = $self->normalizeSheet($table, 'full');
	unless ($table)
		{
		warn	"[" . __PACKAGE__ . "::expandTable] " .
			"Unknown or badly formed table\n";
		return undef;
		}
	my $last_col	= $self->getTableColumn($table, -1);
	my $last_row	= $self->getRow($table, -1);
	my $i		= 0;
	my $j		= 0;

	# expand column declarations
	for ($i = $old_width ; $i < $width ; $i++)
		{
		$last_col = $last_col->replicateNode;
		}

	# expand existing rows
	for ($i = 0 ; $i < $old_length ; $i++)
		{
		my $row		= $self->getTableRow($table,  $i);
		my $last_cell	= $self->getTableCell($row, -1);
		for ($j = $old_width ; $j < $width ; $j++)
			{
			$last_cell = $last_cell->replicateNode;
			}
		}

	# append new rows
	for ($i = $old_length; $i < $length; $i++)
		{
		$last_row = $last_row->replicateNode;
		}
	return wantarray ? $self->getTableSize($table) : $table;
	}

#-----------------------------------------------------------------------------
# get a table column descriptor element

sub	getTableColumn
	{
	my $self	= shift;
	my $p1		= shift;
	return $p1	if (ref $p1 && $p1->isTableColumn);
	my $col		= shift || 0;
	my $table	= $self->getTable($p1, @_)	or return undef;

	return $table->child($col, 'table:table-column');
	}

#-----------------------------------------------------------------------------
# get/set a column style

sub	columnStyle
	{
	my $self	= shift;
	my $p1		= shift;
	my $column	= undef;
	if (ref $p1 && $p1->isTableColumn)
		{
		$column	= $p1;
		}
	else
		{
		$column = $self->getTableColumn($p1, shift) or return undef;
		}
	my $newstyle	= shift;

	return	defined $newstyle ?
		$self->setAttribute($column, 'table:style-name' => $newstyle)
			:
		$self->getAttribute($column, 'table:style-name');
	}

#-----------------------------------------------------------------------------
# get/set a row style

sub	rowStyle
	{
	my $self	= shift;
	my $p1		= shift;
	my $row		= undef;
	if (ref $p1 && $p1->isTableRow)
		{
		$row	= $p1;
		}
	else
		{
		$row = $self->getTableRow($p1, shift) or return undef;
		}
	my $newstyle	= shift;

	return	defined $newstyle ?
		$self->setAttribute($row, 'table:style-name' => $newstyle)
			:
		$self->getAttribute($row, 'table:style-name');
	}

#-----------------------------------------------------------------------------
# get a row element from table id and row num,
# or the row cells if wantarray

sub	getTableRow
	{
	my $self	= shift;
	my $p1		= shift;
	return $p1	if (ref $p1 && $p1->isTableRow);
	my $line	= shift || 0;
	my $table	= $self->getTable($p1, @_)	or return undef;

	return $table->child($line, 'table:table-row');
	}

#-----------------------------------------------------------------------------
# get a table header container

sub	getTableHeader
	{
	my $self	= shift;
	my $table	= $self->getTable(@_) or return undef;
	return $table->first_child('table:table-header-rows');
	}

#-----------------------------------------------------------------------------
# get a header row in a table

sub	getTableHeaderRow
	{
	my $self	= shift;
	my $p1		= shift;
	if (ref $p1)
		{
		if ($p1->isTableRow)
		    {
		    if ($p1->parent->hasTag('table:table-header-rows'))
		    	{ return $p1;	}
		    else
		    	{ return undef;	}
		    }
		}
	my $line	= shift || 0;
	my $table	= $self->getTable($p1, @_)
		or return undef;
	my $header	= $table->first_child('table:table-header-rows')
		or return undef;
	return $header->child($line, 'table:table-row');
	}

#-----------------------------------------------------------------------------
# insert a table header container

sub	copyRowToHeader
	{
	my $self	= shift;
	my $row		= $self->getTableRow(@_) or return undef;
	my $table	= $row->parent;
	my $header =	$table->first_child('table:table-header-rows');
	unless ($header)
		{
		my $first_row = $self->getTableRow($table, 0);
		unless ($first_row)
			{
			warn	"[" . __PACKAGE__ . "::createTableHeader] " .
				"Not allowed with an empty table\n";
			return undef;
			}
		$header = $self->createElement('table:table-header-rows');
		$header->paste_before($first_row);
		}
	my $header_row = $row->copy;
	$header_row->paste_last_child($header);
	return $header_row;
	}

#-----------------------------------------------------------------------------
# get all the rows in a table

sub	getTableRows
	{
	my $self	= shift;
	my $table	= $self->getTable(@_)	or return undef;

	return $table->children('table:table-row');
	}

#-----------------------------------------------------------------------------
# spreadsheet coordinates conversion utility

sub	_coord_conversion
	{
	my $arg	= shift or return ($arg, @_);
	my $coord = uc $arg;
	return ($arg, @_) unless $coord =~ /[A-Z]/;

	$coord	=~ s/\s*//g;
	$coord	=~ /(^[A-Z]*)(\d*)/;
	my $c	= $1;
	my $r	= $2;
	return ($arg, @_) unless ($c && $r);

	my $rownum	= $r - 1;
	my @csplit	= split '', $c;
	my $colnum	= 0;
	foreach my $p (@csplit)
		{
		$colnum *= 26;
		$colnum	+= ((ord($p) - ord('A')) + 1);
		}
	$colnum--;

	return ($rownum, $colnum, @_);
	}

#-----------------------------------------------------------------------------
# get cell element by 3D coordinates ($tablenum, $line, $column)
# or by ($tablename/$tableref, $line, $column)

sub	getTableCell
	{
	my $self		= shift;
	my $p1			= shift;
	return undef	unless defined $p1;
	my $table		= undef;
	my $row			= undef;
	my $cell		= undef;

	if	(! ref $p1 || ($p1->isTable))
		{
		@_ = OpenOffice::OODoc::Text::_coord_conversion(@_);
		my $r	= shift || 0;
		my $c	= shift || 0;
		if (ref $p1)
			{
			$table = $p1;
			}
		else
			{
			my $context = shift;
			unless (ref $context)
				{
				unshift @_, $context; $context = undef;
				}
			$table	= $self->getTable($p1, $context)
				or return undef;
			}
		$row	= $table->child($r, 'table:table-row')
				or return undef;
		$cell = (
			$row->selectChildElements
				('table:(covered-|)table-cell')
			)[$c];
		}
	elsif	($p1->isTableCell)
		{
		$cell	= $p1;
		}
	else	# assume $p1 is a table row
		{
		$cell = $p1->selectChildElement
				(
				'table:(covered-|)table-cell',
				shift
				);
		}

	return undef unless ($cell && ! $cell->isCovered);
	return wantarray ? ($cell, @_) : $cell;
	}

#-----------------------------------------------------------------------------
# adapted from a suggestion by dhoworth

sub getCellPosition
	{
	my $self	= shift;
	my $cell	= $self->getTableCell(@_);
	unless ($cell && $cell->isTableCell)
		{
		warn	"[" . __PACKAGE__ . "::cellPosition] "	.
			"Non-cell argument\n";
		return undef;
		}
	my $cp		= $cell->pos() - 1;
	my $row		= $cell->parent;
	my $rp		= $row->pos('table:table-row') - 1;
	my $table	= $row->parent;
	my $tp		= $table->pos('table:table') - 1;
	return wantarray ? ($tp, $rp, $cp) : $tp;
	}

#-----------------------------------------------------------------------------
# get all the cells in a row

sub	getRowCells
	{
	my $self	= shift;
	my $row		= $self->getTableRow(@_)	or return undef;

	return $row->children('table:table-cell');
	}

#-----------------------------------------------------------------------------

sub	getCellParagraph
	{
	my $self	= shift;
	my $cell	= $self->getTableCell(@_)	or return undef;
	return $cell->first_child('text:p');
	}

#-----------------------------------------------------------------------------

sub	getCellParagraphs
	{
	my $self	= shift;
	my $cell	= $self->getTableCell(@_)	or return undef;
	return $cell->children('text:p');
	}

#-----------------------------------------------------------------------------
# get table cell value

sub	getCellValue
	{
	my $self	= shift;
	my $cell	= $self->getTableCell(@_) or return undef;

	my $prefix = $self->{'opendocument'} ? 'office' : 'table';
	my $cell_type	= $self->cellType($cell);
	if ((! $cell_type) || ($cell_type eq 'string'))		# text value
		{
		return $self->getText($cell);
		}
	else
		{
		my $attribute = $self->cellValueAttributeName($cell);
		return $cell->att($attribute);
		}
	}

#-----------------------------------------------------------------------------
# get/set a cell value type

sub	cellValueType
	{
	my $self	= shift;
	@_ = $self->getTableCell(@_);
	my $cell	= shift		or return undef;

	return $self->cellType($cell, @_);
	}

#-----------------------------------------------------------------------------
# get/set a cell currency

sub	fieldCurrency
	{
	my $self	= shift;
	@_ = $self->getTableCell(@_);
	my $cell	= shift		or return undef;

	my $newcurrency	= shift;
	my $prefix	= $self->{'opendocument'} ? 'office' : 'table';
	unless ($newcurrency)
		{
		return $cell->att($prefix . ':currency');
		}
	else
		{
		$cell->set_att($prefix . ':value-type', 'currency');
		return $cell->set_att($prefix . ':currency', $newcurrency);
		}
	}

#-----------------------------------------------------------------------------
# get/set accessor for the formula of a table cell

sub	cellFormula
	{
	my $self	= shift;
	@_ = $self->getTableCell(@_);
	my $cell	= shift		or return undef;

	my $formula = shift;
	if (defined $formula)
		{
		if ($formula gt ' ')
			{
			$self->setAttribute($cell, 'table:formula', $formula);
			}
		else
			{
			$self->removeAttribute($cell, 'table:formula');
			}
		}
	return $self->getAttribute($cell, 'table:formula');
	}

#-----------------------------------------------------------------------------
# set value of an existing cell

sub	updateCell
	{
	my $self	= shift;
	@_ = $self->getTableCell(@_);
	my $cell	= shift		or return undef;

	my $value	= shift;
	my $text	= shift;

	$text		= $value	unless defined $text;
	my $cell_type	= $self->cellType($cell);
	unless ($cell_type)
		{
		$cell_type	= 'string';
		$self->cellType($cell, $cell_type);
		}

	my $p = $cell->first_child('text:p');
	unless ($p)
		{
		$p = $self->createParagraph($text);
		$p->paste_last_child($cell);
		}
	else
		{
		$self->SUPER::setText($p, $text);
		}

	unless ($cell_type eq 'string')
		{
		my $attribute = $self->cellValueAttributeName($cell);
		$cell->setAttribute($attribute, $value);
		}
	return $cell;
	}

#-----------------------------------------------------------------------------
# get/set a cell value

sub	cellValue
	{
	my $self	= shift;
	@_ = $self->getTableCell(@_);
	my $cell	= shift		or return undef;
	my $newvalue	= shift;
	if (defined $newvalue)
		{
		$self->updateCell($cell, $newvalue, @_);
		}
	return $self->getCellValue($cell);
	}

#-----------------------------------------------------------------------------
# get/set a cell style

sub	cellStyle
	{
	my $self	= shift;
	@_ = $self->getTableCell(@_);
	my $cell	= shift		or return undef;

	my $newstyle	= shift;

	return defined $newstyle ?
		$self->setAttribute($cell, 'table:style-name' => $newstyle) :
		$self->getAttribute($cell, 'table:style-name');
	}

#-----------------------------------------------------------------------------
# get/set cell spanning (from a contribution by Don_Reid[at]Agilent.com)

sub	removeCellSpan
	{
	my $self	= shift;
	my $cell	= $self->getTableCell(@_) or return undef;
	my $hspan = $cell->getAttribute('table:number-columns-spanned') || 1;
	$cell->removeAttribute('table:number-columns-spanned');
	my $vspan = $cell->getAttribute('table:number-rows-spanned') || 1;
	$cell->removeAttribute('table:number-rows-spanned');
	my $row = $cell->parent('table:table-row');
	my $table = $row->parent('table:table');
	my $vpos = $row->getLocalPosition;
	my $hpos = $cell->getLocalPosition(qr'table:(covered-|)table-cell');
	my $vend = $vpos + $vspan - 1;
	my $hend = $hpos + $hspan - 1;
	my $cell_paragraph = $cell->first_child('text:p');
	ROW: for (my $i = $vpos ; $i <= $vend ; $i++)
		{
		my $cr = $self->getRow($table, $i) or last ROW;
		CELL: for (my $j = $hpos ; $j <= $hend ; $j++)
			{
			my $covered = $cr->selectChildElement
				(qr 'table:(covered-|)table-cell', $j)
				or last CELL;
			next CELL if $covered == $cell;
			$covered->set_name('table:table-cell');
			$covered->set_atts($cell->atts);
			$covered->removeAttribute('table:value');
			if ($cell_paragraph)
				{
				my $p = $cell_paragraph->copy;
				$p->set_text("");
				$p->paste_first_child($covered);
				}
			}
		}
	}

sub	cellSpan
	{
	my $self	= shift;
	@_ = $self->getTableCell(@_);
	my $cell	= shift		or return undef;

	my $rnum	= undef;
	my $cnum	= undef;
	my $table	= undef;

	my $old_hspan	= $cell->att('table:number-columns-spanned')	|| 1;
	my $old_vspan	= $cell->att('table:number-rows-spanned')	|| 1;
	my $hspan	= shift;
	my $vspan	= shift;
	unless ($hspan || $vspan)
		{
		return wantarray ? ($old_hspan, $old_vspan) : $old_hspan;
		}
	$hspan	= $old_hspan unless $hspan;
	$vspan	= $old_vspan unless $vspan;

	$self->removeCellSpan($cell);
	my $row = $cell->parent('table:table-row');
	$table = $row->parent('table:table') unless $table;
	my $vpos = $row->getLocalPosition;
	my $hpos = $cell->getLocalPosition(qr'table:(covered-|)table-cell');
	my $hend = $hpos + $hspan - 1;
	my $vend = $vpos + $vspan - 1;
	$cell->setAttribute('table:number-columns-spanned', $hspan);
	$cell->setAttribute('table:number-rows-spanned', $vspan);

	ROW: for (my $i = $vpos ; $i <= $vend ; $i++)
		{
		my $cr = $self->getRow($table, $i) or last ROW;
		CELL: for (my $j = $hpos ; $j <= $hend ; $j++)
			{
			my $covered = $self->getCell($cr, $j)
				or last CELL;
			next CELL if $covered == $cell;

			my @paras = $covered->children('text:p');
			while (@paras)
				{
				my $p = shift @paras;
				$p->paste_last_child($cell) if
					(defined $p->text && $p->text ge ' ');
				}
			$self->removeCellSpan($covered);
			$covered->set_name('table:covered-table-cell');
			}
		}
	return wantarray ? ($hspan, $vspan) : $hspan;
	}

#-----------------------------------------------------------------------------
# get the content of a table element in a 2D array

sub	_get_row_content
	{
	my $self	= shift;
	my $row		= shift;

	my @row_content	= ();
	foreach my $cell ($row->children('table:table-cell'))
		{
		push @row_content, $self->getText($cell);
		}
	return @row_content;
	}

sub	getTableText
	{
	my $self	= shift;
	my $table	= $self->getTable(shift);

	return undef	unless $table;

	my @table_content = ();
	my $headers	= $table->getFirstChild('table:table-header-rows');
	if ($headers)
		{
		push @table_content, [ $self->_get_row_content($_) ]
			for ($headers->children('table:table-row'));
		}
	push @table_content, [ $self->_get_row_content($_) ]
		for ($table->children('table:table-row'));

	if (wantarray)
		{
		return @table_content;
		}
	else
		{
		my $delimiter	= $self->{'field_separator'} || '';
		my $line_break	= $self->{'line_separator'}  || '';
		my @list	= ();
		foreach my $row (@table_content)
			{
			push @list, join($delimiter, @{$row});
			}
		return join $line_break, @list;
		}
	}

#-----------------------------------------------------------------------------
# get table element selected by number

sub	getTable
	{
	my $self	= shift;
	my $table	= shift;
	my $length	= shift;
	my $width	= shift;
	my $context	= shift;

	if (ref $length)
		{
		$context	= $length;
		$length		= undef;
		$width		= undef;
		}
	elsif (ref $width)
		{
		$context	= $width;
		$width		= undef;
		$length		= undef;
		}

	return undef	unless defined $table;

	my $t	= undef;
	if (ref $table)
		{
		if ($table->isTable)
			{
			$t = $table;
			}
		else
			{
			warn	"[" . __PACKAGE__ . "::getTable] "	.
				"Non table object\n";
			return undef;
			}
		}
	else	# retrieve table by number or name
		{
		if (($table =~ /^\d*$/) || ($table =~ /^[\d+-]\d+$/))
			{
			$t = $self->getElement
				('//table:table', $table, $context);
			}
		unless ($t)
			{
			my $n = $self->inputTextConversion($table);
			$t = $self->getNodeByXPath
				(
				"//table:table[\@table:name=\"$n\"]"
				);
			}
		}
	return undef	unless $t;
	if	(
		$length		||
			(
			$self->{'expand_tables'}		&&
			($self->{'expand_tables'} eq 'on')
			)
		)
		{
		$length = 'full' if ($length && ($length eq 'normalize'));
		return $self->_expand_table($t, $length, $width);
		}
	return wantarray ? $self->getTableSize($t) : $t;
	}

#-----------------------------------------------------------------------------

sub	getTableByName
	{
	my $self	= shift;
	my $name 	= $self->inputTextConversion(shift);
	my $table = $self->getNodeByXPath
		("//table:table[\@table:name=\"$n\"]");
	return $self->getTable($table, @_);
	}

#-----------------------------------------------------------------------------
# user-controlled spreadsheet expansion

sub	normalizeSheet
	{
	my $self	= shift;
	my $table	= shift;
	my $length	= shift;
	my $width	= shift;
	my $context	= shift;
	unless (ref $table)
		{
		if ($table =~ /^\d*$/)
			{
			$table = $self->getElement
				('//table:table', $table, $context);
			}
		else
			{
			my $n = $self->inputTextConversion($table);
			$table = $self->getNodeByXPath
				(
				"//table:table[\@table:name=\"$n\"]",
				$context
				);
			}
		}

	unless ((ref $table) && $table->isTable)
		{
		warn	"[" . __PACKAGE__ . "::normalizeSheet] "	.
			"Missing sheet\n";
		return undef;
		}
	return $self->_expand_table($table, $length, $width, @_);
	}

sub	normalizeSheets
	{
	my $self	= shift;
	my $length	= shift;
	my $width	= shift;
	my @sheets	= $self->getTableList;
	my $count	= 0;
	foreach my $sheet (@sheets)
		{
		$self->normalizeSheet($sheet, $length, $width, @_);
		$count++;
		}
	return $count;
	}

#-----------------------------------------------------------------------------
# activate/deactivate and parametrize automatic spreadsheet expansion

sub	autoSheetNormalizationOn
	{
	my $self	= shift;
	my $length	= shift || $self->{'max_rows'};
	my $width	= shift || $self->{'max_cols'};

	$self->{'expand_tables'}	= 'on';
	$self->{'max_rows'}		= $length;
	$self->{'max_cols'}		= $width;

	return 'on';
	}

sub	autoSheetNormalizationOff
	{
	my $self	= shift;
	my $length	= shift || $self->{'max_rows'};
	my $width	= shift || $self->{'max_cols'};

	$self->{'expand_tables'}	= 'no';
	$self->{'max_rows'}		= $length;
	$self->{'max_cols'}		= $width;

	return 'no';
	}

#-----------------------------------------------------------------------------
# common code for insertTable and appendTable

sub	_build_table
	{
	my $self	= shift;
	my $table	= shift;
	my $rows	= shift || $self->{'max_rows'} || 1;
	my $cols	= shift || $self->{'max_cols'} || 1;
	my %opt		=
			(
			'cell-type'	=> 'string',
			'text-style'	=> 'Table Contents',
			@_
			);

	$rows = $self->{'max_rows'} unless $rows;
	$cols = $self->{'max_cols'} unless $cols;

	my $col_proto	= $self->createElement('table:table-column');
	$self->setAttribute
		($col_proto, 'table:style-name', $opt{'column-style'})
			if $opt{'column-style'};
	$col_proto->paste_first_child($table);
	$col_proto->replicateNode($cols - 1, 'after');

	my $row_proto	= $self->createElement('table:table-row');
	my $cell_proto	= $self->createElement('table:table-cell');
	$self->cellValueType($cell_proto, $opt{'cell-type'});
	$self->cellStyle($cell_proto, $opt{'cell-style'});

	if ($opt{'paragraphs'})
		{
		my $para_proto	= $self->createElement('text:p');
		$self->setAttribute
			($para_proto, 'text:style-name', $opt{'text-style'})
				if $opt{'text-style'};
		$para_proto->paste_last_child($cell_proto);
		}

	$cell_proto->paste_first_child($row_proto);
	$cell_proto->replicateNode($cols - 1, 'after');

	$row_proto->paste_last_child($table);
	$row_proto->replicateNode($rows - 1, 'after');

	return $table;
	}

#-----------------------------------------------------------------------------
# create a new table and append it to the end of the document body (default),
# or attach it as a new child of a given element

sub	appendTable
	{
	my $self	= shift;
	my $name	= shift;
	my $rows	= shift || $self->{'max_rows'} || 1;
	my $cols	= shift || $self->{'max_cols'} || 1;
	my %opt		=
			(
			'attachment'	=> $self->{'body'},
			'table-style'	=> $name,
			@_
			);

	if ($self->getTable($name, $self->{'xpath'}))
		{
		warn	"[" . __PACKAGE__ . "::appendTable] "	.
			"Table $name exists\n";
		return	undef;
		}

	my $table = $self->appendElement
				(
				$opt{'attachment'}, 'table:table',
				attribute =>
					{
					'table:name'		=>
						$name,
					'table:style-name'	=>
						$opt{'table-style'}
					}
				)
			or return undef;

	return $self->_build_table($table, $rows, $cols, %opt);
	}

#-----------------------------------------------------------------------------

sub	insertTable
	{
	my $self	= shift;
	my $path	= shift;
	my $pos		= ref $path ? undef : shift;
	my $name	= shift;
	my $rows	= shift || $self->{'max_rows'} || 1;
	my $cols	= shift || $self->{'max_cols'} || 1;
	my %opt		=
			(
			'table-style'	=> $name,
			@_
			);
	my $posnode	= $self->getElement($path, $pos, $opt{'context'})
				or return undef;

	if ($self->getTable($name, $self->{'xpath'}))
		{
		warn	"[" . __PACKAGE__ . "::insertTable] "	.
			"Table $name exists\n";
		return	undef;
		}

	my $table = $self->insertElement
				(
				$posnode, 'table:table',
				attribute =>
					{
					'table:name'		=>
						$name,
					'table:style-name'	=>
						$opt{'table-style'}
					},
				%opt
				)
			or return undef;

	return $self->_build_table($table, $rows, $cols, %opt);
	}

#-----------------------------------------------------------------------------

sub	renameTable
	{
	my $self	= shift;
	my $table	= $self->getTable(shift) or return undef;
	my $newname	= shift;

	if ($self->getTable($newname, $self->{'xpath'}))
		{
		warn	"[" . __PACKAGE__ . "::renameTable] " .
			"Table name $newname already in use\n";
		return undef;
		}
	return $self->setAttribute($table, 'table:name' => $newname);
	}

#-----------------------------------------------------------------------------

sub	tableName
	{
	my $self	= shift;
	my $table	= $self->getTable(shift) or return undef;
	my $newname	= shift;
	if (ref $newname)
		{
		unshift @_, $newname; $newname = undef;
		}
	$self->renameTable($table, $newname, @_) if $newname;
	return $self->getAttribute($table, 'table:name', @_);
	}

#-----------------------------------------------------------------------------

sub	tableStyle
	{
	my $self	= shift;
	my $table	= $self->getTable(shift) or return undef;
	my $newstyle	= shift;
	if (ref $newstyle)
		{
		unshift @_, $newstyle; $newstyle = undef;
		}

	return defined $newstyle ?
		$self->setAttribute
			($table, 'table:style-name' => $newstyle, @_) :
		$self->getAttribute
			($table, 'table:style-name', @_);
	}

#-----------------------------------------------------------------------------
# replicates a column in a normalized table

sub	insertTableColumn
	{
	my $self	= shift;
	my $table	= shift;
	my $col_num	= shift;
	my %options	=
		(
		position	=> 'before',
		@_
		);
	$table	= $self->getTable($table, $options{'context'})
				or return undef;
	my ($height, $width) = $self->getTableSize($table);
	unless ($col_num < $width)
		{
		warn	"[" . __PACKAGE__ . "::replicateTableColumn] "	.
			"Column number out of range\n";
		return undef;
		}
	$self->_expand_columns($table, $width);
	my $column	= $table->child($col_num, 'table:table-column');
	my $new_cell	= undef;
	if ($column)
		{
		my $new_column = $column->copy;
		$new_column->paste($options{position}, $column);
		}
	my @rows = ();
	my $header = $table->first_child('table:table-header-rows');
	@rows = $header->children('table:table-row') if $header;
	push @rows, $self->getTableRows($table);
	foreach my $row (@rows)
		{
		my $cell = $row->selectChildElement
		  		('table:(covered-|)table-cell', $col_num)
		  	or next;
		$new_cell = $cell->copy;
		$new_cell->paste($options{'position'}, $cell);
		}
	return $column || $new_cell;
	}

#-----------------------------------------------------------------------------
# delete a column in a table

sub	deleteTableColumn
	{
	my $self	= shift;
	my $p1		= shift;
	my $col_num	= shift;
	my $table	= undef;
	if (ref $p1 && $p1->isTableColumn)
		{
		$table = $p1->parent;
		$col_num = $p1->getLocalPosition;
		}
	else
		{
		$table = $p1;
		}
	$table = $self->getTable($table);
	unless ($table)
		{
		warn	"[" . __PACKAGE__ . "::deleteTableColumn] " .
			"Unknown table\n";
		return undef;
		}
	my ($height, $width) = $self->getTableSize($table);
	unless (defined $col_num)
		{
		warn	"[" . __PACKAGE__ . "::deleteTableColumn] "	.
			"Missing column position\n";
		return undef;
		}
	$self->_expand_columns($table, $width);
	my $column = $table->child($col_num, 'table:table-column');
	$column->delete if $column;
	my @rows = ();
	my $header = $table->first_child('table:table-header-rows');
	@rows = $header->children('table:table-row') if $header;
	push @rows, $self->getTableRows($table);
	foreach my $row (@rows)
		{
		my $cell = $row->selectChildElement
		  		('table:(covered-|)table-cell', $col_num)
		 	or next;
		$cell->delete;
		}
	return 1;
	}

#-----------------------------------------------------------------------------
# replicates a row in a table

sub	replicateTableRow
	{
	my $self	= shift;
	my $p1		= shift;
	my $table	= undef;
	my $row		= undef;
	my $line	= undef;

	if (ref $p1 && $p1->isTableRow)
		{
		$row	= $p1;
		}
	else
		{
		$line	= shift;
		}
	my %options	=
		(
		position	=> 'after',
		@_
		);
	if (defined $line)
		{
		$row	= $self->getTableRow($p1, $line, $options{'context'})
			or return undef;
		}

	return $self->replicateElement($row, $row, %options);
	}

#-----------------------------------------------------------------------------
# replicate a row and insert the clone before (default) or after the prototype

sub	insertTableRow
	{
	my $self	= shift;
	my $p1		= shift;
	my $row		= undef;
	my $line	= undef;
	if (ref $p1)
		{
		if  	($p1->isTableRow)
			{ $row = $p1; }
		else
			{
			$line = shift;
			$row = $self->getTableRow($p1, $line);
			}
		}
	else
		{
		$row = $self->getTableRow($p1, shift);
		}
	return undef	unless $row;

	my %options	=
			(
			position	=> 'before',
			@_
			);
	return $self->replicateTableRow($row, %options);
	}

#-----------------------------------------------------------------------------
# append a new row (replicating the last existing one) to a table

sub	appendTableRow
	{
	my $self	= shift;
	my $table	= shift;
	return $self->replicateTableRow($table, -1, position => 'after', @_);
	}

#-----------------------------------------------------------------------------
# delete a given table row

sub	deleteTableRow
	{
	my $self	= shift;
	my $row		= $self->getTableRow(@_) or return undef;
	return $self->removeElement($row);
	}

#-----------------------------------------------------------------------------
# update the user field references according to the internal value

sub	updateUserFieldReferences
	{
	my $self	= shift;
	my $fd		= shift or return undef;
	my $field_decl	= undef;
	my $name	= undef;
	if (ref $fd)
		{
		$name = $self->getAttribute($fd, 'text:name');
		$field_decl = $fd;
		}
	else
		{
		$field_decl= $self->getUserFieldElement($fd);
		$name = $fd;
		}
	unless ($field_decl && $name)
		{
		warn	"[" . __PACKAGE__ . "::updateUserFieldReferences] " .
			"Unknown or bad user field\n";
		return undef;
		}
	my @fields = $self->selectNodesByXPath
		("//text:user-field-get[\@text:name=\"$name\"]");
	my $content = $self->userFieldValue($field_decl) || "";
	my $count = 0;
	foreach my $field (@fields)
		{
		$self->setText($field, $content);
		$count++;
		}
	return $count;
	}

#-----------------------------------------------------------------------------
# get user field element

sub	getUserField
	{
	my $self	= shift;
	my $name	= shift;
	unless ($name)
		{
		warn "[" . __PACKAGE__ . "::getUserField] Missing name\n";
		return undef;
		}
	if (ref $name)
		{
		my $n = $name->getName;
		return ($n eq 'text:user-field-decl') ? $name : undef;
		}
	$name = $self->inputTextConversion($name);
	return $self->getNodeByXPath
			("//text:user-field-decl[\@text:name=\"$name\"]");
	}

#-----------------------------------------------------------------------------
# get/set user field value

sub	userFieldValue
	{
	my $self	= shift;
	my $field	= $self->getUserFieldElement(shift)
				or return undef;
	my $value	= shift;

	my $value_att	= $self->fieldValueAttributeName($field);

	if (defined $value)
		{
		if ($value)
			{
			$self->setAttribute($field, $value_att, $value);
			}
		else
			{
			$field->set_att($value_att => $value);
			}
		}
	return $self->getAttribute($field, $value_att);
	}

#-----------------------------------------------------------------------------
# get a variable element (contributed by Andrew Layton)

sub	getVariableElement
	{
	my $self	= shift;
	my $name	= shift;

	unless ($name) {
		warn	"[" . __PACKAGE__ . "::getVariableElement] " .
			"Missing name\n";
		return undef;
		}

	if (ref $name) {
		my $n = $name->getName;
		return ($n eq 'text:variable-set') ? $name : undef;
	}

	return
	$name = $self->inputTextConversion($name);
	$self->getNodeByXPath("//text:variable-set[\@text:name=\"$name\"]");
	}

#-----------------------------------------------------------------------------
# get/set the content of a variable element (contributed by Andrew Layton)

sub	variableValue
	{
	my $self	= shift;
	my $variable	= $self->getVariableElement(shift) or return undef;
	my $value	= shift;

	my $value_att	= $self->fieldValueAttributeName($variable);

	if (defined $value)
		{
		$self->setAttribute($variable, $value_att, $value);
		$self->setText($variable, $value);
		}

	$value = $self->getAttribute($variable, $value_att);
	return defined $value ? $value : $self->getText($variable);
	}

#-----------------------------------------------------------------------------
# append an element to the document body

sub	appendBodyElement
	{
	my $self	= shift;

	return $self->appendElement($self->{'body'}, @_);
	}

#-----------------------------------------------------------------------------
# create a new paragraph

sub	createParagraph
	{
	my $self	= shift;
	my $text	= shift;
	my $style	= shift || "Standard";

	my $p = OpenOffice::OODoc::XPath::new_element('text:p');
	if (defined $text)
		{
		$self->SUPER::setText($p, $text);
		}
	$self->setAttribute($p, 'text:style-name' => $style);
	return $p;
	}

#-----------------------------------------------------------------------------
# inserts a flat text string within a given text element

sub	insertString
	{
	my $self	= shift;
	my $path	= shift;
	my $pos		= ref $path ? undef : shift;
	my $element	= $self->getElement($path, $pos) or return undef;
	my $text	= shift;
	my $offset	= shift;
	return $element->insertTextChild($text, $offset);
	}

#-----------------------------------------------------------------------------
# add a new or existing text at the end of the document

sub	appendText
	{
	my $self	= shift;
	my $name	= shift;
	my %opt		= @_;

	my $attachment	= $opt{'attachment'} || $self->{'body'};
	$opt{'attribute'}{'text:style-name'} = $opt{'style'}
			if $opt{'style'};
	unless ((ref $name) || $opt{'attribute'}{'text:style-name'})
		{
		$opt{'attribute'}{'text:style-name'} =
					$self->{'paragraph_style'};
		}

	delete $opt{'attachment'};
	delete $opt{'style'};
	return $self->appendElement($attachment, $name, %opt);
	}

#-----------------------------------------------------------------------------
# insert a new or existing text element before or after an given element

sub	insertText
	{
	my $self	= shift;
	my $path	= shift;
	my $pos		= (ref $path) ? undef : shift;
	my $name	= shift;
	my %opt		= @_ ;

	$opt{'attribute'}{'text:style-name'} = $opt{'style'} if $opt{'style'};

	return (ref $path)	?
		$self->insertElement($path, $name, %opt)		:
		$self->insertElement($path, $pos, $name, %opt);
	}

#-----------------------------------------------------------------------------
# create and add a new paragraph at the end of the document

sub	appendParagraph
	{
	my $self	= shift;
	my %opt		=
			(
			style		=> $self->{'paragraph_style'},
			@_
			);

	my $paragraph = $self->createParagraph($opt{'text'}, $opt{'style'});

	my $attachment	= $opt{'attachment'} || $self->{'body'};
	$paragraph->paste_last_child($attachment);

	return $paragraph;
	}

#-----------------------------------------------------------------------------
# add a new heading at the end of the document

sub	appendHeading
	{
	my $self	= shift;
	my %opt		=
			(
			style	=> $self->{'heading_style'},
			level	=> '1',
			@_
			);

	$opt{'attribute'}{$self->{'level_attr'}}	= $opt{'level'};

	return $self->appendText('text:h',%opt);
	}

#-----------------------------------------------------------------------------
# insert a new paragraph at a given position

sub	insertParagraph
	{
	my $self	= shift;
	my $path	= shift;
	my $pos		= (ref $path) ? undef : shift;
	my %opt		=
			(
			style	=> $self->{'paragraph_style'},
			@_
			);

	return (ref $path)	?
		$self->insertText($path, 'text:p', %opt)		:
		$self->insertText($path, $pos, 'text:p', %opt);
	}

#-----------------------------------------------------------------------------
# insert a new heading at a given position

sub	insertHeading
	{
	my $self	= shift;
	my $path	= shift;
	my $pos		= (ref $path) ? undef : shift;
	my %opt		=
			(
			style	=> $self->{'heading_style'},
			level	=> '1',
			@_
			);

	$opt{'attribute'}{$self->{'level_attr'}}	= $opt{'level'};

	return (ref $path) ?
		$self->insertText($path, 'text:h', %opt)		:
		$self->insertText($path, $pos, 'text:h', %opt);
	}

#-----------------------------------------------------------------------------
# remove the paragraph element at a given position

sub	removeParagraph
	{
	my $self	= shift;
	my $pos		= shift;
	return $self->removeElement($pos)	if (ref $pos);
	return $self->removeElement('//text:p', $pos);
	}

#-----------------------------------------------------------------------------
# remove the heading element at a given position

sub	removeHeading
	{
	my $self	= shift;
	my $element = $self->getHeading(@_);
	return $self->removeElement($element);
	}

#-----------------------------------------------------------------------------

sub	textStyle
	{
	my $self	= shift;
	my $path	= shift;
	my $pos		= (ref $path) ? undef : shift;
	my $element	= $self->getElement($path, $pos) or return undef;
	my $newstyle	= shift;

	if (ref $newstyle)
		{
		$newstyle = $self->getAttribute($newstyle, 'style:name');
		unless ($newstyle)
			{
			warn	"[" . __PACKAGE__ . "::textStyle] "	.
				"Bad text style\n";
			return undef;
			}
		}

	if ($element->isListItem)
		{
		return defined $newstyle ?
			$self->setItemStyle($element)	:
			$self->getItemStyle($element);
		}
	else
		{
		return defined $newstyle ?
			$self->setAttribute
				($element, 'text:style-name' => $newstyle) :
			$self->getAttribute($element, 'text:style-name');
		}
	}

#-----------------------------------------------------------------------------
package	OpenOffice::OODoc::Element;
#-----------------------------------------------------------------------------
# text element type detection (add-in for OpenOffice::OODoc::Element)

sub	isOrderedList
	{
	my $element	= shift;
	return $element->hasTag('text:ordered-list');
	}

sub	isUnorderedList
	{
	my $element	= shift;
	return $element->hasTag('text:unordered-list');
	}

sub	isItemList
	{
	my $element	= shift;
	my $name	= $element->getName;
	return ($name =~ /^text:.*list$/) ? 1 : undef;
	}

sub	isListItem
	{
	my $element	= shift;
	return $element->hasTag('text:list-item');
	}

sub	isParagraph
	{
	my $element	= shift;
	return $element->hasTag('text:p');
	}

sub	isHeader	# DEPRECATED
	{
	my $element	= shift;
	return $element->hasTag('text:h');
	}

sub	isHeading
	{
	my $element	= shift;
	return $element->hasTag('text:h');
	}

sub	headerLevel	# DEPRECATED
	{
	my $element	= shift;
	return $element->getAttribute($self->{'level_attr'});
	}

sub	headingLevel
	{
	my $element	= shift;
	return $element->getAttribute($self->{'level_attr'});
	}

sub	isTable
	{
	my $element	= shift;
	return $element->hasTag('table:table');
	}

sub	isTableRow
	{
	my $element	= shift;
	return $element->hasTag('table:table-row');
	}

sub	isTableColumn
	{
	my $element	= shift;
	return $element->hasTag('table:table-column');
	}

sub	isTableCell
	{
	my $element	= shift;
	return $element->hasTag('table:table-cell');
	}

sub	isCovered
	{
	my $element	= shift;
	my $name	= $element->getName;
	return ($name && ($name =~ /covered/)) ? 1 : undef;
	}

sub	isSpan
	{
	my $element	= shift;
	return $element->hasTag('text:span');
	}

sub	isHyperlink
	{
	my $element	= shift;
	return $element->hasTag('text:a');
	}

sub	checkNoteClass
	{
	my ($element, $class)	= @_;
	my $name	= $element->getName;
	return 1 if $name eq "text:$class";
	return undef unless $name eq 'text:note';
	my $elt_class = $element->att('text:note-class');
	return ($elt_class && ($elt_class eq $class));
	}

sub	getNoteClass
	{
	my $element	= shift;
	return undef unless $element->isNote;
	my $class = $element->att('text:note-class');
	return $class if $class;
	my $tagname = $element->getName;
	$tagname =~ /^text:(endnote|footnote)$/;
	return $1;
	}

sub	isEndnote
	{
	my $element	= shift;
	return $element->checkNoteClass('endnote');
	}

sub	isFootnote
	{
	my $element	= shift;
	return $element->checkNoteClass('footnote');
	}

sub	checkNoteBodyClass
	{
	my ($element, $class) = @_;
	my $name	= $element->getName;
	return	($name eq "text:$class-body")	?
		1 : $element->parent->checkNoteClass($class);
	}

sub	checkNoteCitationClass
	{
	my ($element, $class) = @_;
	my $name = $element->getName;
	return	($name eq "text:$class-citation")	?
		1 : $element->parent->checkNoteClass($class);
	}

sub	isFootnoteCitation
	{
	my $element	= shift;
	return $element->checkNoteCitationClass('footnote');
	}

sub	isEndnoteCitation
	{
	my $element	= shift;
	return $element->checkNoteCitationClass('endnote');
	}

sub	isEndnoteBody
	{
	my $element	= shift;
	return $element->checkNoteBodyClass('endnote');
	}

sub	isFootnoteBody
	{
	my $element	= shift;
	return $element->checkNoteBodyClass('footnote');
	}

sub	isNoteBody
	{
	my $element	= shift;
	my $tag		= $element->name;
	return $tag =~ /^text:(|foot|end)note-body$/;
	}

sub	isNoteCitation
	{
	my $element	= shift;
	my $tag		= $element->name;
	return $tag =~ /^text:(|foot|end)note-citation$/;
	}

sub	isNote
	{
	my $element	= shift;
	my $tag		= $element->name;
	return $tag =~ /^text:(|foot|end)note$/;
	}

sub	isSequenceDeclarations
	{
	my $element	= shift;
	return $element->hasTag('text:sequence-decls');
	}

sub	isBibliographyMark
	{
	my $element	= shift;
	return $element->hasTag('text:bibliography-mark');
	}

sub	isDrawPage
	{
	my $element	= shift;
	return $element->hasTag('draw:page');
	}

sub	isSection
	{
	my $element	= shift;
	return $element->hasTag('text:section');
	}

sub	isTextBox
	{
	my $element	= shift;
	my $name	= $element->getName	or return undef;
	if ($name eq 'draw:frame')
		{
		my $child = $element->first_child('draw:text-box');
		return $child ? 1 : undef;
		}
	else
		{
		return ($name eq 'draw:text-box') ? 1 : undef;
		}
	}

sub	textId
	{
	my $element	= shift;
	my $id		= shift;
	my $id_attr	= 'text:id';
	if (defined $id)
		{
		$element->set_att($id_attr => $id);
		}
	return $element->att($id_attr);
	}

#-----------------------------------------------------------------------------
1;
