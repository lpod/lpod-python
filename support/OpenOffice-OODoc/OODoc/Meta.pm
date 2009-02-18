#-----------------------------------------------------------------------------
#
#	$Id : Meta.pm 2.012 2008-10-23 JMG$
#
#	Created and maintained by Jean-Marie Gouarne
#	Copyright 2008 by Genicorp, S.A. (www.genicorp.com)
#
#-----------------------------------------------------------------------------

package	OpenOffice::OODoc::Meta;
use	5.008_000;
our	$VERSION	= 2.012;
use	OpenOffice::OODoc::XPath	2.227;
our	@ISA		= qw ( OpenOffice::OODoc::XPath );

#-----------------------------------------------------------------------------

BEGIN
	{
	*author			= *creator;
	*version		= *editing_cycles;
	}

#-----------------------------------------------------------------------------
# constructor : calling OOXPath constructor with 'meta' as member choice

sub	new
	{
	my $caller	= shift;
	my $class	= ref ($caller) || $caller;
	my %options	=
		(
		part		=> 'meta',
		body_path	=> '//office:meta',
		@_
		);

	my $object = $class->SUPER::new(%options);
	if ($object)
		{
		bless $object, $class;
		$object->{'body'}	= $object->getBody();
		return $object;
		}
	else
		{
		return undef;
		}
	}

#-----------------------------------------------------------------------------
# overrides setText() because meta elements contain flat text only

sub	setText
	{
	my $self	= shift;
	return $self->setFlatText(@_);
	}

#-----------------------------------------------------------------------------
# generic read/write accessor for text elements

sub	accessor
	{
	my ($self, $path, $value)	= @_;

	my $element	= $self->getElement($path, 0);
	unless ($element)
		{
		return undef	unless defined $value;
		my $name	= $path;
		$name	=~ s/\/*//g;
		$element = $self->appendElement
				($self->{'body'}, $name, text => $value);
		return $value;
		}

	return 	(defined $value)			?
		$self->setText($element, $value)	:
		$self->getText($element);
	}

#-----------------------------------------------------------------------------
# get/set the 'generator' field (i.e. the signature of the office software)

sub	generator
	{
	my $self	= shift;
	return $self->accessor('//meta:generator', @_);
	}

#-----------------------------------------------------------------------------
# get/set the 'title' field

sub	title
	{
	my $self	= shift;
	return $self->accessor('//dc:title', @_);
	}

#-----------------------------------------------------------------------------
# get/set the 'description' field

sub	description
	{
	my $self	= shift;
	return $self->accessor('//dc:description', @_);
	}

#-----------------------------------------------------------------------------
# get/set the 'subject' field

sub	subject
	{
	my $self	= shift;
	return $self->accessor('//dc:subject', @_);
	}

#-----------------------------------------------------------------------------
# get/set the 'creation-date' field
# in OpenOffice.org (normally ISO-8601) date format

sub	creation_date
	{
	my $self	= shift;
	return $self->accessor('//meta:creation-date', @_);
	}

#-----------------------------------------------------------------------------
# get/set the 'creator' field (i.e. author)

sub	creator
	{
	my $self	= shift;
	return $self->accessor('//dc:creator', @_);
	}

#-----------------------------------------------------------------------------
# get/set the 'initial-creator' field (i.e. author)

sub	initial_creator
	{
	my $self	= shift;
	return $self->accessor('//meta:initial-creator', @_);
	}

#-----------------------------------------------------------------------------
# get/set the 'date' (i.e. the date of last update) field
# in OpenOffice.org (normally ISO-8601) date format

sub	date
	{
	my $self	= shift;
	return $self->accessor('//dc:date', @_);
	}

#-----------------------------------------------------------------------------
# get/set the 'language' code (ex : 'fr-FR') of the document

sub	language
	{
	my $self	= shift;
	return $self->accessor('//dc:language', @_);
	}

#-----------------------------------------------------------------------------
# get/set the 'editing-cycles' field (i.e. the number of editing sessions)

sub	editing_cycles
	{
	my $self	= shift;
	return $self->accessor('//meta:editing-cycles', @_);
	}

#-----------------------------------------------------------------------------
# get/set the 'editing-duration' field (i.e. the total elapsed time for all
# the editing sessions) in OpenOffice.org (ISO-8601) format

sub	editing_duration
	{
	my $self	= shift;
	return $self->accessor('//meta:editing-duration', @_);
	}

#-----------------------------------------------------------------------------
# get/set the 'keywords' list
# optional arguments are a list of one or more keywords ;
# each argument is appended to the keywords list only if not present in
# the old list ;
# result is an array of strings or a single string (with ',' as keyword
# separator) ; optional newly added keywords are included in the result set

sub	_od_keywords		# Open Document version
	{
	my $self	= shift;
	my @new_kws	= @_;

	my @list	= $self->getTextList('//meta:keyword');
	my $body	= $self->{'body'};
	NEW_KWS: foreach my $new_kw (@new_kws)
		{
		foreach my $old_kw (@list)
			{
			next NEW_KWS if ($old_kw eq $new_kw);
			}
		
		$self->appendElement
				(
				$body,
				'meta:keyword',
				text	=> $new_kw
				);
		push @list, $new_kw;
		}
	return wantarray ? @list : join ", ", @list;
	}

sub	_oo_keywords		# OpenOffice.org version
	{
	my $self	= shift;
	my @new_words	= @_;

	$self->_oo_addKeyword($_)	for @new_words;
	
	my $base	= $self->getElement('//meta:keywords', 0);
	return undef	unless $base;

	my @list	= ();

	foreach my $element
		($self->selectChildElementsByName($base, 'meta:keyword'))
		{ push @list, $self->getText($element); }

	return wantarray ? @list : join ", ", @list;
	}

sub	keywords
	{
	my $self	= shift;
	return ($self->{'opendocument'}) ?
		$self->_od_keywords(@_)	: $self->_oo_keywords(@_);
	}
	
#-----------------------------------------------------------------------------
# append a new keyword (if unknown) in the keywords list

sub	_od_addKeyword		# Open Document version
	{
	my $self	= shift;
	my $new_kw	= shift or return undef;

	my @list	= $self->getTextList('//meta:keyword');
	foreach my $old_kw (@list)
		{
		return undef if ($new_kw eq $old_kw);
		}

	$self->appendElement
			(
			$self->{'body'},
			'meta:keyword',
			text => $new_kw
			);
	return $new_kw;
	}

sub	_oo_addKeyword		# OpenOffice.org version
	{
	my $self	= shift;
	my $new_word	= shift;

	my $kw_base	= $self->getElement('//meta:keywords', 0);
	if ($kw_base)
	    {
	    foreach my $element
		($self->selectChildElementsByName($kw_base, 'meta:keyword'))
		{
		my $old_word	= $self->getText($element);
		return undef	if ($old_word eq $new_word);
		}
	    }
	else
	    {
	    $kw_base	=
		$self->appendElement('//office:meta', 0, 'meta:keywords');
	    }

	$self->appendElement($kw_base, 'meta:keyword', text => $new_word);
	return $new_word;
	}

sub	addKeyword
	{
	my $self	= shift;
	return $self->{'opendocument'} ?
		$self->_od_addKeyword(@_) : $self->_oo_addKeyword(@_);
	}

#-----------------------------------------------------------------------------
# remove a given keyword (if known) from the keyword list

sub	_od_removeKeyword	# Open Document version
	{
	my $self	= shift;
	my $kw		= shift;

	my @list	= $self->getElementList('//meta:keyword');
	my $count	= 0;
	foreach my $element (@list)
		{
		my $old_kw = $self->getText($element);
		if ($old_kw eq $kw)
			{
			$self->removeElement($element);
			$count++;
			}
		}
	return $count;
	}

sub	_oo_removeKeyword	# OpenOffice.org version
	{
	my $self	= shift;
	my $word	= shift;

	my $kw_base	= $self->getElement('//meta:keywords', 0);
	return undef	unless $kw_base;
	my $count	= 0;	
	foreach my $element
		($self->selectChildElementsByName($kw_base, 'meta:keyword'))
		{
		my $old_word	= $self->getText($element);
		if ($old_word eq $word)
			{
			$kw_base->removeChild($element);
			$count++;
			}
		}
	return $count;
	}

sub	removeKeyword
	{
	my $self	= shift;
	return $self->{'opendocument'} ?
		$self->_od_removeKeyword(@_) : $self->_oo_removeKeyword(@_);
	}

#-----------------------------------------------------------------------------
# remove the keyword list

sub	_od_removeKeywords	# Open Document version
	{
	my $self	= shift;

	my @list	= $self->getElementList('//meta:keyword');
	my $count	= 0;
	foreach my $element (@list)
		{
		$count++;
		$self->removeElement($element);
		}
	return $count;
	}

sub	removeKeywords
	{
	my $self	= shift;
	return ($self->{'opendocument'}) ?
		$self->_od_removeKeywords(@_)	:
		$self->removeElement('//meta:keywords', 0);
	}

#-----------------------------------------------------------------------------
# get/set the list of the user defined fields of the meta-data
# without argument, returns a hash where keys are the field names
# and values are the field values
# to set/update the user-defined fields, arguments should be passed
# as a hash with the same structure

sub	user_defined
	{
	my $self	= shift;
	my %new_fields	= @_;

	my @elements	= $self->getElementList('//meta:user-defined');

	if (%new_fields)
		{
		my $count	= 0;
		foreach my $key (sort keys %new_fields)
			{
			my $element	= $elements[$count];
			last	unless $element;
			$self->setAttribute($element, 'meta:name', $key);
			$self->setText($element, $new_fields{$key});
			$count++;
			last if $count > 3;
			}
		}
	
	my %fields	= ();
	foreach my $element (@elements)
		{
		my $name	= $self->getAttribute($element, 'meta:name');
		my $content	= $self->getText($element);
		$fields{$name}	= $content;
		}

	return %fields;
	}

#-----------------------------------------------------------------------------

sub	statistic
	{
	my $self	= shift;
	my %new_fields	= @_;

	my $element	= $self->getElement('//meta:document-statistic', 0);

	unless (%new_fields)
		{ return $self->getAttributes($element);		}
	else
		{ return $self->setAttributes($element, %new_fields);	}
	
	}

#-----------------------------------------------------------------------------
1;
