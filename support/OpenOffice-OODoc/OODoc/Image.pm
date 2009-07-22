#-----------------------------------------------------------------------------
#
#	$Id : Image.pm 2.019 2009-02-18 JMG$
#
#	Created and maintained by Jean-Marie Gouarne
#	Copyright 2009 by Genicorp, S.A. (www.genicorp.com)
#
#-----------------------------------------------------------------------------

package	OpenOffice::OODoc::Image;
use	5.008_000;
use	OpenOffice::OODoc::XPath	2.229;
use	File::Basename;
our	@ISA		= qw ( OpenOffice::OODoc::XPath );
our	$VERSION	= 2.019;

#-----------------------------------------------------------------------------
# default attributes for image style

our	%DEFAULT_IMAGE_STYLE =
	(
	references	=>
		{
		'style:family'			=> 'graphics',
		'style:parent-style-name'	=> 'Graphics'
		},
	properties	=>
		{
		'fo:clip'			=> 'rect(0cm 0cm 0cm 0cm)',
		'style:vertical-rel'		=> 'paragraph',
		'style:horizontal-rel'		=> 'paragraph',
		'style:vertical-pos'		=> 'from-top',
		'style:horizontal-pos'		=> 'from-left',
		'draw:color-mode'		=> 'standard',
		'draw:luminance'		=> '0%',
		'draw:red'			=> '0%',
		'draw:green'			=> '0%',
		'draw:blue'			=> '0%',
		'draw:gamma'			=> '1',
		'draw:color-inversion'		=> 'false'
		}
	);

#-----------------------------------------------------------------------------
# constructor : calling OO XPath constructor

sub	new
	{
	my $caller	= shift;
	my $class	= ref ($caller) || $caller;
	my %options	=
		(
		@_
		);
	my $object = $class->SUPER::new(%options);
	return $object ?
		bless $object, $class	:
		undef;
	}

#-----------------------------------------------------------------------------
# create & insert a new image element

sub	createImageElement
	{
	my $self	= shift;
	my $name	= shift;
	my %opt		= @_;

	my $content_class = $self->contentClass;
	my $container	= $self->{'image_container'};
	my $attachment	= undef;
	my $firstnode	= undef;
	my $element	= undef;
	my $description	= undef;
	my $size	= undef;
	my $position	= undef;
	my $import	= undef;
	my $path	= undef;

	if	(
			($content_class eq 'presentation')
				or
			($content_class eq 'drawing')
		)
		{
		my $target = $opt{'page'} || '';
		my $page = ref $target ?
				$target		:
				$self->getNodeByXPath
				    ("//draw:page[\@draw:name=\"$target\"]");

		delete $opt{'page'};
		$path = $page;
		}
	else
		{
		$path	= $opt{'attachment'};
		}
	delete $opt{'attachment'};
	unless ($path)
		{
		$attachment	=
			($self->{'body'})
			||
			($self->getElement('//style:header', 0))
			||
			($self->getElement('//style:footer', 0));
		if ($attachment && defined $opt{'page'})
			{
			$firstnode = $self->selectChildElementByName
					($attachment, 'text:(p|h)');
			}
		}
	else
		{
		$attachment = ref $path ? $path : $self->getElement($path, 0);
		}
	unless ($attachment)
		{
		warn	"[" . __PACKAGE__ .
			"::createImageElement] No valid attachment\n";
		return undef;
		}

				# parameters translation
	$opt{'draw:name'} = $name;
	if ($opt{'description'})
		{
		$description = $opt{'description'};
		delete $opt{'description'};
		}
	if ($opt{'style'})
		{
		$opt{'draw:style-name'} = $opt{'style'};
		delete $opt{'style'};
		}
	if ($opt{'size'})
		{
		$size = $opt{'size'};
		delete $opt{'size'};
		}
	if ($opt{'position'})
		{
		$position = $opt{'position'};
		$opt{'text:anchor-type'} = 'paragraph';
		delete $opt{'position'};
		}
	if ($opt{'link'})
		{
		$opt{'xlink:href'} = $opt{'link'};
		delete $opt{'link'};
		}
	if ($opt{'import'})
		{
		$import	= $opt{'import'};
		delete $opt{'import'};
		}
	
	if ($opt{'page'})	# create appropriate parameters if anchor=page
		{		# and insert before the 1st text element
		$opt{'text:anchor-type'}	= 'page';
		$opt{'text:anchor-page-number'}	= $opt{'page'};
		$opt{'draw:z-index'}		= "1";
		$element	= $firstnode ?	# is there a text element ?
			$self->insertElement	# yes, insert before it
				(
				$firstnode,
				$container,
				position => 'before'
				)
				:		# no, append to parent element
			$self->appendElement
				(
				$attachment,
				$container
				);
		delete $opt{'page'};
		}
	else
		{
		if	($path)	# append to the given attachment if any
			{
			$element = $self->appendElement
						($attachment, $container);
			}
		else		# else append to a new paragraph at the end
			{
			my $p = $self->appendElement($attachment, 'text:p');
			$element = $self->appendElement($p, $container);
			}
		}

	if ($self->{'opendocument'})
		{
		my $img = $self->appendElement($element, 'draw:image');
		foreach my $a (keys %opt)
			{
			if ($a =~ /^xlink:/)
				{
				$self->setAttribute($img, $a, $opt{$a});
				delete $opt{$a};
				}
			}
		}

	$self->setAttributes($element, %opt);
	$self->setImageDescription($element, $description)
		if (defined $description);
	$self->setImageSize($element, $size)
		if (defined $size);
	$self->setImagePosition($element, $position)
		if (defined $position);
	$self->importImage($element, $import)
		if (defined $import);
	return $element;
	}

sub	insertImageElement
	{
	my $self	= shift;
	return $self->createImageElement(@_);
	}

#-----------------------------------------------------------------------------
# image list

sub	getImageElementList
	{
	my $self	= shift;
	return $self->getElementList($self->{'image_xpath'}, @_);
	}

#-----------------------------------------------------------------------------
# select an individual image element by name

sub	selectImageElementByName
	{
	my $self	= shift;
	my $text	= shift;

	unless ($self->{'opendocument'})
		{
		return $self->selectNodeByXPath
			("//draw:image\[\@draw:name=\"$text\"\]", @_);
		}
	else
		{
		my $frame = $self->selectFrameElementByName($text);
		my $child = $frame->first_child('draw:image');
		return $child ? $frame : undef;
		}
	}

#-----------------------------------------------------------------------------
# select a list of image elements by name

sub	selectImageElementsByName
	{
	my $self	= shift;
	return $self->selectElementsByAttribute
				($self->{'image_xpath'}, 'draw:name', @_);
	}

#-----------------------------------------------------------------------------
# select a list of image elements by description

sub	selectImageElementsByDescription
	{
	my $self	= shift;
	my $filter	= shift;
	my @result	= ();
	foreach my $i ($self->getImageElementList)
		{
		my $desc = $self->getXPathValue($i, 'svg:desc');
		push @result, $i if ($desc =~ /$filter/);
		}
	return @result;
	}

#-----------------------------------------------------------------------------
# select the 1st image element matching a given description

sub	selectImageElementByDescription
	{
	my $self	= shift;
	my $filter	= shift;
	my @result	= ();
	foreach my $i ($self->getImageElementList)
		{
		my $desc = $self->getXPathValue($i, 'svg:desc');
		return $i if ($desc =~ /$filter/);
		}
	return undef;
	}

#-----------------------------------------------------------------------------
# gets image element (name or ref, with type checking)

sub	getImageElement
	{
	my $self	= shift;
	my $image	= shift;
	return undef	unless $image;
	my $element	= undef;
	if (ref $image)
		{
		$element = $image;
		}
	else
		{
		$element = ($image =~ /^\//) ?
			$self->getElement($image, @_)	:
			$self->selectImageElementByName($image, @_);
		}
	return undef unless $element;
	my $name = $element->name;
	return ($name eq $self->{'image_container'}) ? $element : undef;
	}

#-----------------------------------------------------------------------------
# basic image attribute accessor

sub	imageAttribute
	{
	my $self	= shift;
	my $image	= shift;
	my $attribute	= shift;
	my $value	= shift;
	my $element	= $self->getImageElement($image);
	if ($self->{'opendocument'} && ($attribute =~ /^xlink:/))
		{
		$element = $element->first_child('draw:image');
		}
	return undef	unless $element;
	return	(defined $value)	?
		$self->setAttribute($element, $attribute => $value)	:
		$self->getAttribute($element, $attribute);
	}

#-----------------------------------------------------------------------------
# selects image element by image URL

sub	selectImageElementByLink
	{
	my $self	= shift;
	my $link	= shift;
	
	my $node = $self->selectNodeByXPath
			("//draw:image\[\@xlink:href=\"$link\"\]", @_);
	return $self->{'opendocument'} ? $node->parent : $node;
	}

#-----------------------------------------------------------------------------
# select image element list by image URL

sub	selectImageElementsByLink
	{
	my $self	= shift;

	if ($self->{'opendocument'})
		{
		my @list1 = $self->selectElementsByAttribute
			('//draw:image', 'xlink:href', @_);
		my @list2 = ();
		foreach my $frame (@list1)
			{
			push @list2, $frame if $frame;
			}
		return @list2;
		}
	else
		{
		return $self->selectElementsByAttribute
			($self->{'image_xpath'}, 'xlink:href', @_);
		}
	}

#-----------------------------------------------------------------------------
# get/set image URL

sub	imageLink
	{
	my $self	= shift;
	return $self->imageAttribute(shift, 'xlink:href', @_);
	}

#-----------------------------------------------------------------------------
# return the internal filepath in canonical form ('Pictures/xxxx')

sub	getInternalImagePath
	{
	my $self	= shift;
	my $image	= shift;
	my $link	= $self->imageLink($image);
	my $tmpl	= $self->{'image_fpath'};
	if ($link && ($link =~ /^$tmpl/))
		{
		$link =~ s/^#//;
		return $link;
		}
	else
		{
		return undef;
		}
	}

#-----------------------------------------------------------------------------
# return image coordinates

sub	getImagePosition
	{
	my $self	= shift;
	my $image	= shift;
	my $element	= $self->getImageElement($image);
	return $self->getObjectCoordinates($element, @_);
	}

#-----------------------------------------------------------------------------
# update image coordinates

sub	setImagePosition
	{
	my $self	= shift;
	my $image	= shift;
	my $element	= $self->getImageElement($image);
	return $self->setObjectCoordinates($element, @_);
	}

#-----------------------------------------------------------------------------
# get/set image coordinates

sub	imagePosition
	{
	my $self	= shift;
	my $image	= shift;
	my $x		= shift;
	my $y		= shift;

	return	(defined $x)	?
		$self->setImagePosition($image, $x, $y, @_) :
		$self->getImagePosition($image);
	}

#-----------------------------------------------------------------------------
# get image size

sub	getImageSize
	{
	my $self	= shift;
	my $image	= shift;
	my $element	= $self->getImageElement($image);
	return $self->getObjectSize($element, @_);
	}

#-----------------------------------------------------------------------------
# update image size

sub	setImageSize
	{
	my $self	= shift;
	my $image	= shift;
	my $element	= $self->getImageElement($image);
	return $self->setObjectSize($element, @_);
	}

#-----------------------------------------------------------------------------
# get/set image size

sub	imageSize
	{
	my $self	= shift;
	my $image	= shift;
	my $w		= shift;
	my $h		= shift;

	return	(defined $w)	?
		$self->setImageSize($image, $w, $h, @_) :
		$self->getImageSize($image);
	}

#-----------------------------------------------------------------------------
# get/set image name

sub	imageName
	{
	my $self	= shift;
	return $self->imageAttribute(shift, 'draw:name', @_);
	}

#-----------------------------------------------------------------------------
# get/set image stylename

sub	imageStyle
	{
	my $self	= shift;
	return $self->imageAttribute(shift, 'draw:style-name', @_);
	}

#-----------------------------------------------------------------------------
# get image description

sub	getImageDescription
	{
	my $self	= shift;
	my $image	= shift;
	my $element	= $self->getImageElement($image);
	return $self->getObjectDescription($element);
	}

#-----------------------------------------------------------------------------
# set/update image description

sub	setImageDescription
	{
	my $self	= shift;
	my $image	= shift;
	my $element	= $self->getImageElement($image);
	return $self->setObjectDescription($element, @_);
	}

#-----------------------------------------------------------------------------
# delete image description

sub	removeImageDescription
	{
	my $self	= shift;
	$self->setImageDescription(shift);
	}

#-----------------------------------------------------------------------------
# get/set accessor for image description

sub	imageDescription
	{
	my $self	= shift;
	my $image	= shift;
	my $desc	= shift;
	return	(defined $desc)	?
		$self->setImageDescription($image, $desc, @_) :
		$self->getImageDescription($image, @_);
	}

#-----------------------------------------------------------------------------
# export a selected image file from ODF container

sub	exportImage
	{
	my $self	= shift;
	my $element	= $self->getImageElement(shift);
	return undef	unless $element;
	my $path	= $self->imageLink($element)	or return undef;
	my $tmpl	= $self->{'image_fpath'};
	unless ($path =~ /^$tmpl/)
		{
		warn	"[" . __PACKAGE__ . "::exportImage] "		.
			"Image content $path is an external link. "	.
			"Can't be exported\n";
		return	undef;
		}
	my $target	= shift;
	unless ($target)
		{
		my $name = $self->imageName($element);
		if ($name)
			{
			$path =~ /(\..*$)/;
			$target = $name . ($1 || '');
			}
		else
			{
			$target = $path;
			}
		}
	return $self->raw_export($path, $target, @_);
	}

#-----------------------------------------------------------------------------
# export all the internal image files, or a subset of them selected by name
# return the list of exported files

sub	exportImages
	{
	my $self	= shift;
	my %opt		= @_;
	my $filter	= $opt{'filter'} || $opt{'name'} || $opt{'selection'};
	my $basename	= $opt{'path'} || $opt{'target'};
	my $suffix	= $opt{'suffix'} || $opt{'extension'};
	my $number	= defined $opt{'start_count'} ?
					$opt{'start_count'} : 1;
	my @list	= ();
	my $count	= 0;

	my @to_export	= $filter ?
				$self->selectImageElementsByName($filter)
				:
				$self->getImageElementList();

	my $tmpl	= $self->{'image_fpath'};

	IMAGE_LOOP: foreach my $image (@to_export)
		{
		my $link	= $self->imageLink($image);
		next IMAGE_LOOP unless ($link && ($link =~ /^$tmpl/));
		my $filename	= undef;
		my $extension	= undef;
		my $target	= undef;
		if (defined $suffix)
			{
			$extension = $suffix;
			}
		else
			{
			$link =~ /(\..*$)/;
			$extension = $1 || '';
			}
		if (defined $basename)
			{
			$target = $basename . $number . $extension;
			}
		else
			{
			my $name = $self->imageName($image) || "Image$number";
			$target = $name . $extension;
			}
		$filename = $self->exportImage($image, $target);
		push @list, $filename	if $filename;
		$count++; $number++;
		}
	return wantarray ? @list : $count;
	}

#-----------------------------------------------------------------------------
# import image file

sub	importImage
	{
	my $self	= shift;
	my $element	= $self->getImageElement(shift);
	return undef	unless $element;
	my $filename	= shift;
	my $tmpl	= $self->{'image_fpath'};
	unless ($filename)
		{
		my $source = $self->imageLink($element);
		unless ($source)
			{
			warn	"[" . __PACKAGE__ . "::importImage] "	.
				"Missing source path\n";
			return undef;
			}
		$source =~ s/%(..)/{ chr(hex($1)) }/eg;
		$source =~ s/^\.\.[\\\/]/\.\//;
		$filename = $source;
		}
	my ($base, $path, $suffix) =
		File::Basename::fileparse($filename, '\..*');	
	my $link	= shift;
	if ($link)
		{
		$link = $tmpl . $link unless $link =~ /^$tmpl/;
		$self->imageLink($element, $link);
		}
	else
		{
		$link	= $self->imageLink($element);
		unless ($link && $link =~ /^$tmpl/)
			{
			$link = $tmpl . $base . $suffix;
			$self->imageLink($element, $link);
			}
		}
	$self->raw_import($link, $filename);	
	return $link;
	}

#-----------------------------------------------------------------------------
package	OpenOffice::OODoc::Element;
#-----------------------------------------------------------------------------

sub	isImage
	{
	my $element	= shift;
	my $name	= $element->getName	or return undef;
	if ($name eq 'draw:frame')
		{
		my $child = $element->first_child('draw:image');
		return $child ? 1 : undef;
		}
	else
		{
		return ($name eq 'draw:image') ? 1 : undef;
		}
	}

#-----------------------------------------------------------------------------
1;
