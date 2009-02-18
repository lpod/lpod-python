#-----------------------------------------------------------------------------
#
#	$Id : Document.pm 2.024 2008-10-23 JMG$
#
#	Created and maintained by Jean-Marie Gouarne
#	Copyright 2008 by Genicorp, S.A. (www.genicorp.com)
#
#-----------------------------------------------------------------------------

use OpenOffice::OODoc::Text	2.234;
use OpenOffice::OODoc::Image	2.018;
use OpenOffice::OODoc::Styles	2.025;

package OpenOffice::OODoc::Document;
our @ISA	= qw	(
			OpenOffice::OODoc::Text
			OpenOffice::OODoc::Image
			OpenOffice::OODoc::Styles
			);
our $VERSION	= 2.024;

#-----------------------------------------------------------------------------
# constructor

sub	new
	{
	my $caller	= shift;
	my $class	= ref ($caller) || $caller;
	my %options	=
			(
			part	=> 'content',
			@_
			);
	my $object	= $class->SUPER::new(%options);
	return	$object	?
		bless $object, $class	:
		undef;
	}

#-----------------------------------------------------------------------------
# create and append a new image style

sub	createImageStyle
	{
	my $self	= shift;
	my $stylename	= shift;
	my %opt		=
			(
			%OpenOffice::OODoc::Image::DEFAULT_IMAGE_STYLE,
			@_
			);
	$opt{'family'} = $self->{'opendocument'} ? 'graphic' : 'graphics';
	return $self->createStyle($stylename, %opt);
	}

#-----------------------------------------------------------------------------
# create and append a new text style
# default attributes come from the 'Standard' style of the document

sub	createTextStyle
	{
	my $self	= shift;
	my $stylename	= shift;
	my $proto	= $self->getStyleElement('Standard');
	my %default_options	=
			$proto	?
				$self->getStyleAttributes($proto)	:
				%OpenOffice::OODoc::Text::DEFAULT_TEXT_STYLE;
	
	my %opt		=
			(
			%default_options,
			@_
			);
	
	return $self->createStyle($stylename, %opt);
	}

#-----------------------------------------------------------------------------
# set a page break before a paragraph

sub	setPageBreak
	{
	my $self	= shift;
	my $p1		= shift;
	my $pos		= ref $p1 ? undef : shift;
	my %opt		= (position => 'before', @_);
	my $element	= $self->getElement($p1, $pos) or return undef;
	my $stylename	= $self->getStyle($element);
	unless ($stylename)
		{
		warn	"[" . __PACKAGE__ . "::setPageBreak] "	.
			"Element has no style\n";
		return	undef;
		}
	my $style	= undef;
	if ($opt{'style'})
		{
		$style = $self->createStyle
					(
					$opt{'style'},
					family		=> 'paragraph',
					parent		=> $stylename,
					category	=> 'auto',
					properties	=>
						{
						'style:page-number' => '0'
						}
					);
		unless ($style)
			{
			warn	"[" . __PACKAGE__ . "::setPageBreak] "	.
				"Style $stylename creation failure\n";
			return	undef;
			}
		$self->textStyle($element, $opt{'style'});
		}
	else
		{
		$style = $self->getStyleElement($stylename);
		unless ($style)
			{
			warn	"[" . __PACKAGE__ . "::setPageBreak] "	.
				"Element style not found\n";
			return	undef;
			}
		}
	if ($opt{'page'})
		{
		my $name = undef;
		if (ref $opt{'page'})
			{
			unless ($opt{'page'}->isMasterPage)
				{
				warn "[" . __PACKAGE__ . "::setPageBreak] " .
				     "Style element is not master page\n";
				return undef;
				}
			$name = $self->getAttribute
					($opt{'page'}, 'style:name');
			}
		else
			{
			$name = $opt{'page'};
			}
		$self->setAttribute($style, 'style:master-page-name', $name);
		}
	else
		{
		$self->styleProperties
				(
				$style,
				('fo:break-' . $opt{'position'}) => 'page'
				);
		}
	return $element;
	}

#-----------------------------------------------------------------------------
# removes a page break from a paragraph

sub	removePageBreak
	{
	my $self	= shift;
	my $element	= $self->getElement(@_) or return undef;
	my $stylename	= $self->getStyle($element);
	my $style	= $self->getStyleElement($self->getStyle($element));
	unless ($style)
		{
		warn	"[" . __PACKAGE__ . "::removePageBreak] "	.
			"Element style not found in the active document\n";
		return	undef;
		}
	$self->setAttribute($style, 'style:master-page-name' => undef);
	my $prop	= $self->getStyleNode($style, 'properties');
	$self->setAttribute($prop, 'fo:break-before' => undef) if $prop;

	return $element;
	}

#-----------------------------------------------------------------------------
# get/set the style of a text or image element

sub	style
	{
	my $self	= shift;
	my $path	= shift;
	unless ($path)
		{
		warn	"[" . __PACKAGE__ . "::style] Missing object\n";
		return undef;
		}
	my $element	= undef;
	if (ref $path)
		{
		$element	= $path;
		}
	else
		{
		$element	= ($path =~ /^\//)	?
			$self->getElement($path, shift)	:
			$self->getImageElement($path);
		}
	return undef	unless $element;

	my $value	= shift;
	my $namespace	= $element->getPrefix;
	unless ($namespace)
		{
		warn	"[" . __PACKAGE__ . "::style] Unknown class\n";
		return undef;
		}
		
	my $attribute	= $namespace . ":" . 'style-name';
	return	defined $value	?
		$self->setAttribute($element, $attribute => $value)	:
		$self->getAttribute($element, $attribute);
	}

#-----------------------------------------------------------------------------
# get the style name of any content element

sub	getStyle
	{
	my $self	= shift;
	my $path	= shift;
	my $element	= ref $path	?
				$path	:
				$self->getElement($path, shift)
			or return undef;	
	my $fullname	= $element->getName || "";
	my ($namespace, $name)	= split /:/, $fullname;
	my $style_attribute	= undef;
	if ($name eq 'master-page')
		{
		$style_attribute = $namespace . 'page-master-name';
		}
	else
		{
		$style_attribute = $namespace . ':style-name';
		}
	return $self->getAttribute($element, $style_attribute);
	}

#-----------------------------------------------------------------------------
1;
