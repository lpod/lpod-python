#-----------------------------------------------------------------------------
#
#	$Id : Manifest.pm 2.005 2008-09-16 JMG$
#
#	Created and maintained by Jean-Marie Gouarne
#	Copyright 2008 by Genicorp, S.A. (www.genicorp.com)
#
#-----------------------------------------------------------------------------

package	OpenOffice::OODoc::Manifest;
use	5.008_000;
our	$VERSION	= 2.005;

use	OpenOffice::OODoc::XPath	2.226;
our	@ISA		= qw ( OpenOffice::OODoc::XPath );

#-----------------------------------------------------------------------------
# constructor : calling odfXPath constructor with 'manifest' as member choice

sub	new
	{
	my $caller	= shift;
	my $class	= ref ($caller) || $caller;
	my %options	=
		(
		part		=> 'META-INF/manifest.xml',
		element		=> 'manifest:manifest',
		body_path	=> '/manifest:manifest',
		@_
		);

	my $object = $class->SUPER::new(%options);
	return	$object ?
		bless $object, $class	:
		undef;
	}

#-----------------------------------------------------------------------------
# override the basic getBody() method; here the body is the root

sub	getBody
	{
	my $self	= shift;
	return $self->getRootElement;
	}

#-----------------------------------------------------------------------------
# retrieving an entry by content

sub	getEntry
	{
	my ($self, $entry)	= @_;
	my @list = $self->getElementList('//manifest:file-entry');
	foreach my $element (@list)
		{
		my $member = $self->getAttribute
					($element, 'manifest:full-path');
		next unless $member;
		return $element if ($member eq $entry);
		}
	return undef;
	}

#-----------------------------------------------------------------------------
# get the entry describing the OpenOffice.org mime type of the document

sub	getMainEntry
	{
	my $self = shift;
	return $self->getEntry('/');
	}

#-----------------------------------------------------------------------------
# set the entry describing the OpenOffice.org mime type of the document

sub	setMainEntry
	{
	my $self	= shift;
	return $element = $self->setEntry("/", @_);
	}

#-----------------------------------------------------------------------------
# get the media type of a given entry

sub	getType
	{
	my ($self, $entry) = @_;
	my $element = $self->getEntry($entry);
	return $element ?
		$self->getAttribute($element, 'manifest:media-type')	:
		undef;
	}

#-----------------------------------------------------------------------------
# get the media type of the main entry

sub	getMainType
	{
	my $self = shift;
	return $self->getType("/");
	}

#-----------------------------------------------------------------------------
# remove an entry

sub	removeEntry
	{
	my ($self, $entry) = @_;
	
	my $element = $self->getEntry($entry);
	return $element ?
		$self->removeElement($element)	:
		undef;
	}
	
#-----------------------------------------------------------------------------
# create a new entry

sub	setEntry
	{
	my $self	= shift;
	my $entry	= shift;
	my $type	= shift || '';

	my $element = $self->getEntry($entry);
	unless ($element)
		{
		$element = $self->appendElement
			(
			$self->getBody(),
			'manifest:file-entry'
			);
		$self->setAttribute($element, 'manifest:media-type', $type);
		$self->setAttribute($element, 'manifest:full-path', $entry);
		}
	else
		{
		$self->setAttribute($element, 'manifest:media-type', $type);
		}
	return $element;
	}
	
#-----------------------------------------------------------------------------
1;
