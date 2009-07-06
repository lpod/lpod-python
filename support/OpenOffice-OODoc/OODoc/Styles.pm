#-----------------------------------------------------------------------------
#
# $Id : Styles.pm 2.025 2008-09-16 JMG$
#
# Created and maintained by Jean-Marie Gouarne
# Copyright 2008 by Genicorp, S.A. (www.genicorp.com)
#
#-----------------------------------------------------------------------------

package OpenOffice::OODoc::Styles;
use 5.008_000;
our $VERSION = 2.025;

use OpenOffice::OODoc::XPath 2.226;
use File::Basename;
require Exporter;
our @ISA = qw ( Exporter OpenOffice::OODoc::XPath );
our @EXPORT = qw
  (
  odfLoadColorMap ooLoadColorMap
  oo2rgb rgb2oo rgbColor odfColor
  );

#-----------------------------------------------------------------------------

our $COLORMAP  = undef;
our %COLORMAP  =
 (
 'red'   => '255,0,0',
 'green'   => '0,255,0',
 'blue'   => '0,0,255',
 'white'   => '255,255,255',
 'black'   => '0,0,0',
 'brown'   => '165,42,42',
 'cyan'   => '0,255,255',
 'grey'   => '190,190,190',
 'magenta'  => '255,0,255',
 'orange'  => '255,165,0',
 'pink'   => '255,192,203',
 'violet'  => '238,130,238',
 'yellow'  => '255,255,0'
 );

#-----------------------------------------------------------------------------

BEGIN {
 *odfLoadColorMap  = *ooLoadColorMap;
 *rgbColor   = *oo2rgb;
 *odfColor   = *rgb2oo;
 *getPageMasterElement  = *getPageLayoutElement;
 *getPageMasterAttributes = *getPageLayoutAttributes;
 *createPageMaster  = *createPageLayout;
 *updatePageMaster  = *updatePageLayout;
 *pageMasterStyle  = *pageLayout;
 }
 
#-----------------------------------------------------------------------------
# loading a color map from an external file
# the file format must be "%d %d %d %s"
 
sub ooLoadColorMap
 {
 my $filename = shift || $COLORMAP or return undef;
 unless ( -e $filename && -r $filename )
  {
  warn "[" . __PACKAGE__ . "::ooLoadColorMap] " .
   "Color map file non existent or unreadable\n";
  return undef;
  }
 my $r = open COLORS, "<", $filename;
 unless ($r)
  {
  warn "[" . __PACKAGE__ . "::ooLoadColorMap] " .
   "Error opening $filename\n";
  return undef;
  }
 while (my $line = <COLORS>)
  {
  $line =~ s/^\s*//; $line =~ s/\s*$//;
  next unless $line =~ /^[0-9]/;
  $line =~ /(\d*)\s*(\d*)\s*(\d*)\s*(.*)/;
  my $name = $4;
  $COLORMAP{$name} = "$1,$2,$3" if $name;
  }
 close COLORS;
 return 1;
 }

#-----------------------------------------------------------------------------
# converting an hexadecimal OOo color code to decimal RGB

sub oo2rgb
 {
 my $hexcolor = shift; return undef unless $hexcolor;
 return undef unless $hexcolor =~ /^#[0-9A-Fa-f]{6}$/;
 $hexcolor =~ /#(..)(..)(..)/;
 my ($red, $green, $blue) = ($1, $2, $3);
 my @rgb = (hex($red), hex($green), hex($blue));
 if (wantarray)
  {
  return @rgb;
  }
 else
  {
  my $color = join(",", @rgb);
  foreach my $k (keys %COLORMAP)
   {
   return $k if ($COLORMAP{$k} eq $color);
   }
  return $color;
  }
 }

#-----------------------------------------------------------------------------
# converting a decimal RGB expression to an hexadecimal OOo color 

sub rgb2oo
 {
 my $colour = shift;
 my ($red, $green, $blue);
 if ($colour =~ /,/)
  {
  $colour =~ s/ //g;
  ($red, $green, $blue) = split(",", $colour);
  }
 elsif ($colour =~ /^[a-zA-Z]/)
  {
  if (defined $COLORMAP{$colour})
   {
   ($red, $green, $blue) = split(",", $COLORMAP{$colour});
   }
  else
   {
   return undef;
   }
  }
 elsif ($colour =~ /^#/)
  {
  my $rgb  = oo2rgb($colour);
  return undef unless $rgb;
  my $hexrgb = rgb2oo($rgb);
  return undef unless $hexrgb;
  return (lc $hexrgb eq lc $colour) ? $colour : undef;
  }
 else
  {
  $red = $colour; ($green, $blue) = @_;
  }
 return sprintf("#%02x%02x%02x", $red, $green, $blue);
 }
 
#-----------------------------------------------------------------------------
package OpenOffice::OODoc::Element;
#-----------------------------------------------------------------------------
 
sub isStyle
 {
 my $element = shift;
 my $fullname = $element->getName;
 my ($prefix, $name) = split ':', $fullname;
 return
   (
  $prefix
   &&
   (($prefix eq 'style') || ($prefix eq 'number'))
   &&
   $name
   &&
   ($name ne 'properties')
  )
   ? 1 : undef;
 }

sub isOutlineStyle
 {
 my $element = shift;
 return $element->hasTag('text:outline-level-style');
 }

sub isMasterPage
 {
 my $element = shift;
 return (
  $element->isElementNode
   &&
  $element->getName eq 'style:master-page'
  )
  ? 1 : undef;
  
 }
 
#-----------------------------------------------------------------------------
package OpenOffice::OODoc::Styles;
#-----------------------------------------------------------------------------
# constructor

sub new
 {
 my $caller = shift;
 my $class = ref($caller) || $caller;
 my %options =
  (
  part   => 'styles', # XML member
  @_
  );
 my $object = $class->SUPER::new(%options);
 return $object ?
  bless $object, $class :
  undef;
 }

#-----------------------------------------------------------------------------
# get the tag name of the "properties" style sub-element

sub _properties_tagname
 {
 my $self = shift;
 my $element = shift;
 my $part = shift;

 my $prefix = $element->getPrefix;
 if ($prefix eq 'number')
  {
  return 'number:number';
  }
 elsif ($self->{'opendocument'})
  {
  unless ($part)
   {
   $part = $element->att('style:family');
   }
  return $part ?
   $prefix . ':' . $part . '-properties' :
   $element->name() . '-properties';
  }
 else
  {
  return 'style:properties';
  }
 }

#-----------------------------------------------------------------------------
# get the path of an individual style property node

sub _get_property_path
 {
 my $self = shift;
 my $element = shift;
 my $nodename = shift;
 my $part = shift;

 if (($nodename eq 'header') || ($nodename eq 'footer'))
  {
  return 'style:' . $nodename . '-style/style:properties';
  }
 my $path = $self->_properties_tagname($element, $part);
 $path .= ('/' . $nodename) if $nodename;
 return $path;
 }

#-----------------------------------------------------------------------------
# get a particular node in a main style element

sub getStyleNode
 {
 my $self = shift;
 my $element = shift;
 my $nodename = shift;
 my $xpath = $self->_get_property_path($element, $nodename);
 return $self->getNodeByXPath($element, $xpath);
 }

#-----------------------------------------------------------------------------
# create the path for a particular node in a main style element

sub setStyleNode
 {
 my $self = shift;
 my $element = shift;
 my $nodename = shift;
 my $xpath = $self->_get_property_path($element, $nodename);
 return $self->makeXPath($element, $xpath); 
 }

#-----------------------------------------------------------------------------
# get named styles root element

sub getNamedStyleRoot
 {
 my $self = shift;
 return $self->getElement($self->{'named_style_path'}, 0);
 }

#-----------------------------------------------------------------------------
# get automatic styles root element

sub getAutoStyleRoot
 {
 my $self = shift;
 return $self->getElement($self->{'auto_style_path'}, 0);
 }

#-----------------------------------------------------------------------------
# get master styles root element

sub getMasterStyleRoot
 {
 my $self = shift;
 return $self->getElement($self->{'master_style_path'}, 0);
 }

#-----------------------------------------------------------------------------
# get the root of font declarations

sub getFontDeclarationBody
 {
 my $self = shift;
 
 my $path = $self->{'opendocument'} ?
  '//office:font-face-decls' : '//office:font-decls';
 return $self->getElement($path, 0);
 }

#-----------------------------------------------------------------------------
# get a font declaration element

sub getFontDeclaration
 {
 my $self = shift;
 my $font = shift  or return undef;
 my $tag  = $self->{'opendocument'} ?
   "style:font-face" : "style:font-decl";
 if (ref $font)
  {
  my $n = $font->name;
  if ($n && ($n eq $tag))
   {
   return $font;
   }
  else
   {
   warn "[" . __PACKAGE__ . "::getFontDeclaration] " .
    "Invalid font declaration element\n";
   return undef;
   }
  }
 else
  {
  my $context = $self->getFontDeclarationBody;
  my $path = "//$tag\[\@style:name=\"$font\"]";
  return $self->getNodeByXPath($context, $path);
  }
 }

#-----------------------------------------------------------------------------

sub getFontDeclarations
 {
 my $self = shift;
 my $context = $self->getFontDeclarationBody;
 my $path = $self->{'opendocument'} ?
    '//style:font-face' : 'style:font-decl';
 return $self->getNodesByXPath($context, $path);
 }

#-----------------------------------------------------------------------------

sub getFontName
 {
 my $self = shift;
 my $fd  = $self->getFontDeclaration(@_)
  or return undef;
 return $self->getAttribute($fd, 'style:name');
 }

#-----------------------------------------------------------------------------
# imports a copy of an existing font declaration

sub importFontDeclaration
 {
 my $self = shift;
 my $p1  = shift  or return undef;
 
 my $font_element = undef;
 
 if (ref $p1)
  {
  my $e = undef;
  if ($p1->isa('OpenOffice::OODoc::Styles'))
   {  # copy from another document
   my $font_name = shift;
   $e = $p1->getFontDeclaration($font_name);
   }
  else
   {  # replicate from the same document
   $e = $self->getFontDeclaration($p1);
   }
  $font_element = $e->copy if $e;
  }
 else
  {   # from anything (we hope XML)
  $font_element =
   OpenOffice::OODoc::XPath::new_element($p1);
  }
     # check the element type
 $font_element = $self->getFontDeclaration($font_element);
 $font_element->paste_last_child($self->getFontDeclarationBody);
 
 return $font_element;
 }

#-----------------------------------------------------------------------------
# select a list of style elements matching a given attribute, value pair
# $path may be 'auto' or 'named' to search only in automatic or named styles
# without args, returns the full style list

sub selectStyleElementsByAttribute
 {
 my $self = shift;
 my $attribute = shift;
 my $value = shift;
 my %opt  =
   (
   namespace => 'style',
   type  => 'style',
   @_
   );
 my $path = $opt{'category'};

 return $self->getStyleList unless ($attribute && $value);

 unless ($path)
  {
  return ($self->selectElementsByAttribute
    (
    $self->{'named_style_path'} .
     "/$opt{'namespace'}:$opt{'type'}",
    $attribute, $value
    )
    ,
   $self->selectElementsByAttribute
    (
    $self->{'auto_style_path'}  .
     "/$opt{'namespace'}:$opt{'type'}",
    $attribute, $value
    )
   );
  }
 else
  {
  $path = lc $path;
  if ($path =~ /^named/)
   {
   $path = $self->{'named_style_path'};
   }
  elsif ($path =~ /^auto/)
   {
   $path = $self->{'auto_style_path'};
   }
  else
   {
   return undef;
   }
  return $self->selectElementsByAttribute
    (
    "$path/$opt{'namespace'}:$opt{'type'}",
    $attribute, $value
    );
  }
 }

#-----------------------------------------------------------------------------
# select a style element by name
# $path may be 'auto' or 'named' to search only in automatic or named styles

sub selectStyleElementByAttribute
 {
 my $self = shift;
 my $attribute = shift;
 my $value = shift;
 my %opt  =
   (
   namespace => 'style',
   type  => 'style',
   @_
   );

 unless ($attribute)
  {
  warn "[" . __PACKAGE__ .
   "::selectStyleElementByAttribute] Missing attribute\n";
  return undef;
  }

 my $path = $opt{'category'};
 unless ($path)
  {
  return $self->selectElementByAttribute
    (
    $self->{'named_style_path'} . '/style:style',
    $attribute, $value
    )
    ||
   $self->selectElementByAttribute
    (
    $self->{'auto_style_path'} . '/style:style',
    $attribute, $value
    );
  }
 else
  {
  $path = lc $path;
  if ($path =~ /^named/)
   {
   $path = $self->{'named_style_path'};
   }
  elsif ($path =~ /^auto/)
   {
   $path = $self->{'auto_style_path'};
   }
  else
   {
   return undef;
   }
  return $self->selectElementByAttribute
    (
    "$path/$opt{'namespace'}:$opt{'type'}",
    $attribute, $value
    )
  }
 }

#-----------------------------------------------------------------------------

sub selectStyleElementByName
 {
 my $self = shift;
 return $self->selectStyleElementByAttribute('style:name', @_);
 }

#-----------------------------------------------------------------------------

sub selectStyleElementByFamily
 {
 my $self = shift;
 return $self->selectStyleElementByAttribute('style:family', @_);
 }

#-----------------------------------------------------------------------------

sub selectStyleElementsByName
 {
 my $self = shift;
 return $self->selectStyleElementsByAttribute('style:name', @_);
 }

#-----------------------------------------------------------------------------

sub selectStyleElementsByFamily
 {
 my $self = shift;
 return $self->selectStyleElementsByAttribute('style:family', @_);
 }

#-----------------------------------------------------------------------------
# get style element by exact internal name or display name 

sub getStyleElement
 {
 my $self = shift;
 my $style = shift;
 return undef unless $style;
 return $style->isStyle ? $style : undef if ref $style;
 $style  = $self->inputTextConversion($style);
 my %opt  = (retry => 1, @_);
 if ($opt{'retry'})
  {
  delete $opt{'retry'}
      unless
   (($opt{'retry'} eq 1) || ($opt{'retry'} eq 'true'));
  }

 my $root = undef;
 my $type = $opt{'type'}  || 'style';
 my $namespace = $opt{'namespace'} || 'style';

 if ($opt{'category'})
  {
  my $path = '//office:' ;
  if ($opt{'category'} =~ /^auto/)
    { $path .= 'automatic-styles'; }
  elsif ($opt{'category'} =~ /^named/)
    { $path .= 'styles';  }
  else
    { $path = $opt{'category'};  }
  $root = $self->getElement($path, 0);
  unless ($root)
   {
   warn "[" . __PACKAGE__ . "::getStyleElement] " .
    "Unknown search space\n";
   return undef;
   }
  }
 my $attr  = $self->{'retrieve_by'} || 'name';
 my $xpath = "//$namespace" . ':' .
    "$type\[\@style:$attr\=\"$style\"\]";
 my $e = $self->getNodeByXPath($xpath, $root);
 return $e if ((defined $e) || !$opt{'retry'});
 if ($attr eq 'name')
  {
  $attr = 'display-name';
  }
 elsif ($attr eq 'display-name')
  {
  $attr = 'name';
  }
 else
  {
  return undef;
  }
 $xpath = "//$namespace" . ':' .
   "$type\[\@style:$attr\=\"$style\"\]";
 return $self->getNodeByXPath($xpath, $root);
 }

#-----------------------------------------------------------------------------

sub getOutlineStyleElement
 {
 my $self = shift;
 my $level = shift  or return undef;
 
 if (ref $level)
  {
  return $level->isOutlineStyle ? $level : undef;
  }
 
 my $xpath = "//text:outline-level-style\[\@text:level\=\"$level\"\]";
 return $self->getNodeByXPath($xpath);
 }

#-----------------------------------------------------------------------------
 
sub updateOutlineStyle
 {
 my $self = shift;
 my $style = $self->getOutlineStyleElement(shift)
    or return undef;
 my %attr = @_;
 foreach my $k (keys %attr)
  {
  unless ($k =~ /:/)
   {
   my $v = $attr{$k}; delete $attr{$k};
   $k = 'style:' . $k;
   $attr{$k} = $v;
   }
  }
 return $self->setAttributes($style, %attr);
 }

#-----------------------------------------------------------------------------
# get the name of the parent style, if any

sub getParentStyle
 {
 my $self = shift;
 my $style = $self->getStyleElement(@_);
 unless ($style)
  {
  warn "[" . __PACKAGE__ .
   "::getParentStyle] Unknown style\n";
  return undef;
  }
 return $self->getAttribute($style, 'style:parent-style-name');
 }

#-----------------------------------------------------------------------------
# get the name of the primary ancestor
# (returns the style name if it doesn't have any ancestor)

sub getAncestorStyle
 {
 my $self = shift;
 my $style = $self->getStyleElement(@_);
 unless ($style)
  {
  warn "[" . __PACKAGE__ .
   "::getAncestorStyle] Unknown style\n";
  return undef;
  }
 my $name = $self->styleName($style);
 my $parent_name = $self->getParentStyle($style);

 while ($parent_name)
  {
  $name   = $parent_name;
  $style  = $self->getStyleElement($name);
  $parent_name = $style ?
     $self->getParentStyle($style) :
     undef;
  }

 return $name;
 }

#-----------------------------------------------------------------------------

sub styleName
 {
 my $self = shift;
 my $p1  = shift;
 my $style = undef;
 my $newname = undef;
 if (ref $p1)
  {
  $style = $self->getStyleElement($p1) or return undef;
  $newname = shift;
  }
 else
  {
  my %opt = @_;
  $style = $self->getStyleElement($p1, %opt) or return undef;
  $newname = $opt{'newname'};
  }
 $self->setAttribute($style, 'style:name', $newname) if $newname;
 return $self->getAttribute($style, 'style:name');
 }

#-----------------------------------------------------------------------------

sub getAutoStyleList
 {
 my $self = shift;
 my %opt  =
  (
  namespace => 'style',
  type  => 'style',
  @_
  );
 my $path = $self->{'auto_style_path'} . '/' .
   $opt{'namespace'} . ':' . $opt{'type'};
 return $self->getElementList($path);
 }

#-----------------------------------------------------------------------------

sub getNamedStyleList
 {
 my $self = shift;
 my %opt  =
  (
  namespace => 'style',
  type  => 'style',
  @_
  );
 my $path = $self->{'named_style_path'} . '/' .
   $opt{'namespace'} . ':' . $opt{'type'};
 return $self->getElementList($path);
 }

#-----------------------------------------------------------------------------

sub getMasterStyleList
 {
 my $self = shift;
 my %opt  =
  (
  namespace => 'style',
  type  => 'master-page',
  @_
  );
 my $path = $self->{'master_style_path'} . '/' .
   $opt{'namespace'} . ':' . $opt{'type'};
 return $self->getElementList($path);
 }

#-----------------------------------------------------------------------------

sub getStyleList
 {
 my $self = shift;
 return ($self->getNamedStyleList(@_), $self->getAutoStyleList(@_));
 }

#-----------------------------------------------------------------------------

sub styleProperties
 {
 my $self = shift;
 my $style = shift;
 my %opt  = @_;
 my $namespace = $opt{'namespace'};
 my $type = $opt{'type'};
 my $path = $opt{'path'};
 my $part_name = $opt{'-area'} || $opt{'area'};
 my $element = $self->getStyleElement
     (
     $style,
     namespace => $namespace,
     type  => $type,
     category => $path
     );
 return undef unless $element;
 delete $opt{'namespace'};
 delete $opt{'type'};
 delete $opt{'path'};
 delete $opt{'-area'};
 delete $opt{'area'};

 my $change = undef;
 my $e_prefix = $element->getPrefix;
 my $tag_name = undef;

 unless ($part_name)
  {
  if ($e_prefix eq 'number')
   {
   $tag_name = 'number:number';
   }
  elsif ($self->{'opendocument'})
   {
   my $family = $element->att('style:family');
   $tag_name = $family ?
    $e_prefix . ':' . $family . '-properties' :
    $element->name() . '-properties';
   }
  else
   {
   $tag_name = 'style:properties';
   }
  }
 else
  {
  $tag_name = $self->{'opendocument'} ?
   $e_prefix . ':' . $part_name . '-properties' :
   'style:properties';
  }
 
 my $properties = $self->getChildElementByName($element, $tag_name);
 my %attr = ();
 foreach my $k (keys %opt)
  {
  my $a = $k =~ /:/ ? $k : $e_prefix . ':' . $k;
  $attr{$a} = $opt{$k}; $change = 1;
  }
 if ($change)
  {
  $properties = $self->appendElement($element, $tag_name)
    unless $properties;
  $self->setAttributes($properties, %attr); 
  }
 return $properties ? $self->getAttributes($properties) : undef;
 }

#-----------------------------------------------------------------------------

sub getStyleAttributes
 {
 my $self = shift;
 my $name = shift;
 my %style = ();
 my $element = $self->getStyleElement($name, @_);
 unless ($element)
  {
  warn "[" . __PACKAGE__ .
   "::getStyleAttributes] Unknown style\n";
  return %style;
  }
 %{$style{'properties'}} = $self->styleProperties($element)
     if $self->styleProperties($element);
 %{$style{'references'}} = $self->getAttributes($element);
 return %style;
 }

#-----------------------------------------------------------------------------

sub getDefaultStyleElement
 {
 my $self = shift;
 my $style = shift;
 if (ref $style)
  {
  return ($style->getName eq 'style:default-style') ?
   $style : undef;
  }
 else
  {
  return $self->getNodeByXPath
    ("//style:default-style\[\@style:family=\"$style\"\]", @_);
  }
 }

#-----------------------------------------------------------------------------

sub getDefaultStyleAttributes
 {
 my $self = shift;
 my $style = $self->getDefaultStyleElement(@_);
 unless ($style)
  {
  warn "[" . __PACKAGE__ . "::getDefaultStyleAttributes] " .
   "No available default style in the context\n";
  return undef;
  }
 return $self->getStyleAttributes($style, @_);
 }

#-----------------------------------------------------------------------------
# create a new style with given $name and %options
# by default, the style is regarded as an 'named style' if $self is
# 'styles.xml'but if $opt{path} or $opt{category} is 'auto', then
# the style is inserted as an automatic style
# if $self is a 'content.xml' object, the style is automatic

sub createStyle
 {
 my $self = shift;
 my $name = shift;

 unless ($name)
  {
  warn "[" . __PACKAGE__ . "::createStyle] " .
   "Missing style name\n";
  return undef;
  }
 my %opt = (check => 'true', @_);
 
 my $check = lc $opt{'check'} eq 'true'; delete $opt{'check'};
 my $replace = lc $opt{'replace'} eq 'true'; delete $opt{'replace'};  
 if ($check || $replace)
  {
  my $old = $self->getStyleElement($name, %opt);
  if (defined $old)
   {
   unless ($replace)
       {
       warn "[" . __PACKAGE__ . "::createStyle] " .
     "Style $name exists\n";
    return undef;
       }
   else
       {
       $self->removeElement($old);
       }
   }
  }

 my $element = undef;
 my $path = undef;
 my $type = $opt{'type'} || 'style';
 
 my $namespace = $opt{'namespace'} || 'style';
 
 if ($self->getElement('//office:document-content', 0))
  {
  $path = $self->{'auto_style_path'};
  }
 elsif ($self->getElement('//office:document-styles', 0))
  {
  $path =
   ($opt{'path'}  && $opt{'path'} =~ /auto/)
    ||
   ($opt{'category'} && $opt{'category'} =~ /auto/)
    ?
   $self->{'auto_style_path'} :
   $self->{'named_style_path'};
  }
 else
  {
  warn "[" . __PACKAGE__ . "::createStyle] " .
   "Style creation is not allowed in the area\n";
  return undef;
  }

 if ($opt{'prototype'} || $opt{'source'})
  {
  my $p = $opt{'prototype'} || $name;
  delete $opt{'prototype'};
  my $source = $opt{'source'} || $self;
  delete $opt{'source'};
  my $proto = $source->getStyleElement($p, %opt);
  unless ($proto)
   {
   warn "[" . __PACKAGE__ . "::createStyle] " .
    "Unknown prototype style\n";
   return undef;
   }
  $element = $proto->copy;
  }
 else
  {
  $element = $self->createElement($namespace . ':' . $type);
  }
 my $attachment = $self->getElement($path, 0);
 $element->paste_last_child($attachment);
 if  ($type eq 'default-style')
  { $opt{'family'}   = $name; }
 elsif ($type eq 'number-style')
  {
  $opt{'references'}{'style:name'} = $name;
  $opt{'family'}   = 'data-style';
  }
 else
  { $opt{'references'}{'style:name'} = $name; }
  
 delete $opt{'type'};
 delete $opt{'namespace'};
 delete $opt{'path'};
 delete $opt{'category'}; 
 
 $self->updateStyle($element, %opt);
 return $element;
 }

#-----------------------------------------------------------------------------
# set style attributes

sub updateStyle
 {
 my $self = shift;
 my $style = shift;
 my %opt  = @_;
 my $namespace = $opt{'namespace'};
 my $type = $opt{'type'};
 my $path = $opt{'path'} || $opt{'category'};
 my $element = $self->getStyleElement
     (
     $style,
     namespace => $namespace,
     type  => $type,
     category => $path
     );

 unless ($element)
  {
  warn "[" . __PACKAGE__ . "::updateStyle] " .
   "Unknown style\n";
  return undef;
  }

 if ($opt{'prototype'})
  {
  my $sv_name = $self->getAttribute($element, 'style:name');
  my %proto = $self->getStyleAttributes($opt{'prototype'});
  while (my ($key, $value) = each %proto)
   {
   if (ref $value)
    {
    while (my ($k, $v) = each %{$value})
     {
     $opt{$key}{$k} = $v
      unless $opt{$key}{$k};
     }
    }
   else
    {
    $opt{$key} = $value unless $opt{$key};
    }
   }
  delete $opt{'prototype'};
  $opt{'references'}{'style:name'} = $sv_name if $sv_name;
  }
 $opt{'references'}{'style:family'} = $opt{'family'}
    if $opt{'family'};
 $opt{'references'}{'style:class'} = $opt{'class'}
    if $opt{'class'};
 $opt{'references'}{'style:display-name'} = $opt{'display-name'}
    if $opt{'display-name'};
 if ($opt{'next'})
  {
  $opt{'references'}{'style:next-style-name'} =
   ref $opt{'next'} ?
    $self->styleName($opt{'next'}) :
    $opt{'next'};
  }
 if ($opt{'parent'})
  {
  $opt{'references'}{'style:parent-style-name'} =
   ref $opt{'parent'} ?
    $self->styleName($opt{'parent'}) :
    $opt{'parent'};
  }
 $self->setAttributes($element, %{$opt{'references'}});
 $self->styleProperties($element, %{$opt{'properties'}})
    if ($opt{'properties'});

 return $self->getStyleAttributes($element);
 }

#-----------------------------------------------------------------------------
# get a page layout descriptor (pagemaster) element.
# the argument $page could be already a page layout;
# if $page appears to be a master page (or master page name), the method
# tries to get the linked page layout.

sub getPageLayoutElement
 {
 my $self = shift;
 my $page = shift;
 my $name = undef;
 my $pagemaster = undef;

 my $l = $self->{'opendocument'} ?  'layout' : 'master';
 my $layout_tag_name = 'style:page-' . $l;
 my $layout_key  = $layout_tag_name . '-name';
 my $layout_path  = '//' . $layout_tag_name;

 if (ref $page)
  { # it is an element
  $name = $page->getName || "";
   # is it pagemaster element ?
  if ($name eq $layout_tag_name)
   { # OK, return it
   return $page;
   }
   # is it a master page element ?
  elsif ($name eq 'style:master-page')
   { # yes, get the page master name
   $page = $self->getAttribute($page, $layout_key)
    or return undef;
   }
  }
  # here we have a name
 $pagemaster = $self->selectElementByAttribute
   ($layout_path, 'style:name', $page);
 return $pagemaster if $pagemaster;
  # it's not a page master name,
  # so we try it as a master page name
 my $masterpage = $self->selectElementByAttribute
   ('//style:master-page', 'style:name', $page)
   or return undef;
  # great! we got the master page, so get the page master name
 $name = $self->getAttribute($masterpage, $layout_key);
  # and cross the fingers
 return $self->selectElementByAttribute
   ($layout_path, 'style:name', $name);
 }

#-----------------------------------------------------------------------------

sub getPageLayoutAttributes
 {
 my $self = shift;
 my %attributes = ();
 my $pagemaster = $self->getPageLayoutElement(shift);
 unless ($pagemaster)
  {
  warn "[" . __PACKAGE__ . "::getPageLayoutAttributes] " .
   "Unknown page master\n";
  return %attributes;
  }
 
 my $node = undef;
 %{$attributes{'references'}} = $self->getAttributes($pagemaster);
 %{$attributes{'properties'}} = $self->styleProperties($pagemaster);
 $node = $self->getStyleNode($pagemaster, 'background-image');
 %{$attributes{'background-image'}} = $node ?
  $self->getAttributes($node) : ();
 $node = $self->getStyleNode($pagemaster, 'footnote-sep');
 %{$attributes{'footnote-sep'}} = $node ?
  $self->getAttributes($node) : ();
 $node = $self->getStyleNode($pagemaster, 'header');
 %{$attributes{'header'}} = $node ?
  $self->getAttributes($node) : ();
 $node = $self->getStyleNode($pagemaster, 'footer');
 %{$attributes{'footer'}} = $node ?
  $self->getAttributes($node) : ();
 
 return %attributes;
 }

#-----------------------------------------------------------------------------

sub createPageLayout
 {
 my $self = shift;
 my $name = shift;
 my $layout_name = $self->{'opendocument'} ?
   'page-layout' : 'page-master';
 my %opt  =
   (
   category => 'auto',
   namespace => 'style',
   type  => $layout_name,
   @_
   );
 my $pagemaster = undef;

 if ($opt{'prototype'})
  {
  my $proto = $self->getStyleElement
    ($opt{'prototype'}, type => $layout_name);
  unless ($proto)
   {
   warn "[" . __PACKAGE__ . "::createPageMaster] " .
    "Improper prototype style\n";
   return undef;
   }
  my $attachment = $self->getAutoStyleRoot;
  $pagemaster = $self->replicateElement($proto, $attachment);
  $self->setAttribute($pagemaster, 'style:name', $name);
  delete $opt{'prototype'};
  }
 else
  {
  $pagemaster = $self->createStyle($name, %opt) or return undef;
  }
 
 delete $opt{'namespace'};
 delete $opt{'type'};
 delete $opt{'category'};

 $self->updatePageMaster($pagemaster, %opt);
 return $pagemaster;
 }

#-----------------------------------------------------------------------------

sub updatePageLayout
 {
 my $self = shift;
 my $pagemaster = $self->getPageLayoutElement(shift) or return undef;
 my %opt  = @_;
 if ($opt{'prototype'})
  {
  my $sv_name = $self->getAttribute($pagemaster, 'style:name');
  my %proto = $self->getPageLayoutAttributes($opt{'prototype'});
  while (my ($key, $value) = each %proto)
   {
   if (ref $value)
    {
    while (my ($k, $v) = each %{$value})
     {
     $opt{$key}{$k} = $v
      unless $opt{$key}{$k};
     }
    }
   else
    {
    $opt{$key} = $value unless $opt{$key};
    }
   }
  delete $opt{'prototype'};
  $opt{'references'}{'style:name'} = $sv_name if $sv_name;
  }
 $self->setAttributes($pagemaster, %{$opt{'references'}});
 delete $opt{'references'};
 $self->styleProperties($pagemaster, %{$opt{'properties'}});
 delete $opt{'properties'};
 my %p  = ();
 $p{'background-image'} =
  $self->setStyleNode($pagemaster, 'background-image');
 $p{'footnote-sep'} =
  $self->setStyleNode($pagemaster, 'footnote-sep');
 $p{'header'}  =
  $self->setStyleNode($pagemaster, 'header');
 $p{'footer'}  =
  $self->setStyleNode($pagemaster, 'footer');

 foreach my $k (keys %opt)
  {
  my $node = $p{$k} or next;
  my %parm = %{$opt{$k}}; my %attr = ();
  foreach my $name (keys %parm)
   {
   if ($name eq 'link')
    {
    $attr{'xlink:href'} = $parm{'link'};
    }
   elsif (! ($name =~ /:/))
    {
    $attr{"style:$name"} = $parm{$name};
    }
   else
    {
    $attr{$name} = $parm{$name};
    }
   }
  $self->setAttributes($node, %attr);
  }

 return $self->getPageLayoutAttributes($pagemaster);
 }

#-----------------------------------------------------------------------------
# switch page orientation (portrait -> landscape or landscape -> portrait)

sub switchPageOrientation
 {
 my $self = shift;
 my $page = $self->getPageLayoutElement(shift);
 my %op  = $self->styleProperties($page);
 my %np  = ();
 $np{'fo:page-width'} = $op{'fo:page-height'};
 $np{'fo:page-height'} = $op{'fo:page-width'};
 my $o  = $op{'style:print-orientation'};
 if ($o)
  {
  if ($o eq 'portrait')
   {
   $np{'style:print-orientation'} = 'landscape';
   }
  elsif ($o eq 'landscape')
   {
   $np{'style:print-orientation'} = 'portrait';
   }
  }
 return $self->styleProperties($page, %np);
 }

#-----------------------------------------------------------------------------
# get the page content for a given page style

sub getMasterPageElement
 {
 my $self = shift;
 my $name = shift;
 if (ref $name)
  {
  return $name->getName eq 'style:master-page' ?
   $name : undef;
  }
 else
  {
  return $self->selectElementByAttribute
    ('//style:master-page', 'style:name', $name);
  }
 }

#-----------------------------------------------------------------------------
# get/set the page master name of a given master page

sub pageLayout
 {
 my $self = shift;
 my $masterpage = $self->getMasterPageElement(shift) or return undef;
 my $pagemaster = shift;
 my $ln  = $self->{'opendocument'} ?  'layout' : 'master';
 my $layout_key = 'style:page-' . $ln . '-name';
 unless ($pagemaster)
  {
  return $self->getAttribute($masterpage, $layout_key);
  }
 else
  {
  my $pm_name = ref $pagemaster ?
   $pm_name = $self->getAttribute
     ($pagemaster, 'style:name') :
   $pagemaster;
  $self->setAttribute($masterpage, $layout_key => $pm_name);
  return $pm_name;
  }
 }

#-----------------------------------------------------------------------------
# get the background image node in a given page master

sub getBackgroundImageElement
 {
 my $self = shift;
 my $page = shift;
 my $pagemaster = $self->getPageLayoutElement($page);
 unless ($pagemaster)
  {
  my $masterpage = $self->getMasterPageElement($page)
   or return undef;
  my $name = $self->pageLayout($masterpage);
  $pagemaster = $self->getPageLayoutElement($name)
   or return undef;
  }
 return $self->getStyleNode($pagemaster, 'background-image');
 }

#-----------------------------------------------------------------------------
# get/set a background image link

sub backgroundImageLink
 {
 my $self = shift;
 my $page = shift;
 my $pagemaster = $self->getPageLayoutElement($page);
 unless ($pagemaster)
  {
  my $masterpage = $self->getMasterPageElement($page)
   or return undef;
  my $name = $self->pageLayout($masterpage);
  $pagemaster = $self->getPageLayoutElement($name)
   or return undef;
  }
 my $newlink = shift;
 my $node = $self->getStyleNode($pagemaster, 'background-image');
 unless (defined $newlink)
  {
  return $node ?
   $self->getAttribute($node, 'xlink:href') :
   undef;
  }
 else
  {
  my $xpath = $self->_get_property_path
    ($element, 'background-image')  .
    '[@xlink:href="' . $newlink . '"]';
  
  return $self->makeXPath($pagemaster, $xpath);
  }
 }

#-----------------------------------------------------------------------------

sub getBackgroundImageAttributes
 {
 my $self = shift;
 my $node = $self->getBackgroundImageElement(@_)
    or return undef;
 return $self->getAttributes($node);
 }

#-----------------------------------------------------------------------------
# create or update a backgound image element associated to a given pagemaster

sub setBackgroundImage
 {
 my $self = shift;
 my $page = shift;
 my $pagemaster = $self->getPageLayoutElement($page);
 unless ($pagemaster)
  {
  my $masterpage = $self->getMasterPageElement($page)
   or return undef;
  my $name = $self->pageLayout($masterpage);
  $pagemaster = $self->getPageLayoutElement($name)
   or return undef;
  }
 my %opt  =
   (
   'style:position' => 'center center',
   'style:repeat'  => 'no-repeat',
   'xlink:type'  => 'simple',
   'xlink:actuate'  => 'onLoad',
   @_
   );
 
 my $node = $self->makeXPath
    (
    $pagemaster,
    $self->_get_property_path
     ($pagemaster, 'background-image')
    )
    or return undef;
 if ($opt{'link'})
  {
  $opt{'xlink:href'} = $opt{'link'};
  delete $opt{'link'};
  }
 if ($opt{'import'})
  {
  $self->importBackgroundImage($pagemaster, $opt{'import'});
  delete $opt{'import'};
  }
 $self->setAttributes($node, %opt);
 return $node;
 }

#-----------------------------------------------------------------------------

sub exportBackgroundImage
 {
 my $self = shift;
 my $source = $self->backgroundImageLink(shift)
    or return undef;
 $self->raw_export($source, @_);
 }

#-----------------------------------------------------------------------------

sub importBackgroundImage
 {
 my $self = shift;
 my $page = shift;
 my $pagemaster = $self->getPageLayoutElement($page);
 unless ($pagemaster)
  {
  my $masterpage = $self->getMasterPageElement($page)
   or return undef;
  my $name = $self->pageLayout($masterpage);
  $pagemaster = $self->getPageLayoutElement($name)
   or return undef;
  }
 my $filename = shift;
 unless ($filename)
  {
  warn "[" . __PACKAGE__ . "::importBackgroundImage] " .
   "No source file name\n";
  return undef;
  }
 my ($base, $path, $suffix) =
  File::Basename::fileparse($filename, '\..*');

 my $link = shift;
 my $fpath = $self->{'image_fpath'};
 if ($link)
  {
  $link = $fpath . $link unless $link =~ /^$fpath/;
  $self->backgroundImageLink($pagemaster, $link);
  }
 else
  {
  $link = $self->backgroundImageLink($pagemaster);
  unless ($link && $link =~ /^$fpath/)
   {
   $link = $fpath . $base . $suffix;
   $self->backgroundImageLink($pagemaster, $link);
   }
  }
 $self->raw_import($link, $filename); 
 return $link;
 }

#-----------------------------------------------------------------------------

sub createMasterPage
 {
 my $self = shift;
 my $name = shift;
 my $element = $self->getMasterPageElement($name);
 if ($element)
  {
  warn "[" . __PACKAGE__ . "::createMasterPage] " .
   "Master page $name exists\n";
  return undef;
  }
 my %opt  = @_;
 my $root = $self->getElement('//office:master-styles', 0);
 unless ($root)
  {
  warn "[" . __PACKAGE__ . "::createMasterPage] " .
   "No master styles space in the document\n";
  return undef;
  }

 $opt{'style:name'} = $name;
 my $page_layout = $opt{'layout'}  ||
    $opt{'page-layout'} ||
    $opt{'page-master'};
 if ($page_layout)
  {
  my $ln = $self->{'opendocument'} ? 'layout' : 'master';
  my $layout_key = 'style:page-' . $ln . '-name';
  $opt{$layout_key} = $page_layout;
  delete $opt{'layout'};
  delete $opt{'page-layout'};
  delete $opt{'page-master'};
  }
 if ($opt{'next'})
  {
  $opt{'style:next-style-name'} = $opt{'next'};
  delete $opt{'next'};
  }
 return $self->appendElement
    (
    $root,
    'style:master-page',
    attribute => { %opt }
    );
 }

#-----------------------------------------------------------------------------

sub masterPageExtension
 {
 my $self = shift;
 my $masterpage = $self->getMasterPageElement(shift) or return undef;
 my $position = shift or return undef;
 my $element = shift;
 my $tag  = 'style:' . $position;
 unless ($element)
  {
  return $self->getNodeByXPath($masterpage, "//$tag");
  }
 else
  {
  my $node = $self->makeXPath($masterpage, "/$tag");
  return $self->appendElement($node, $element, @_);
  }
 }

#-----------------------------------------------------------------------------

sub masterPageHeader
 {
 my $self = shift;
 return $self->masterPageExtension(shift, 'header', @_);
 }

sub masterPageFooter
 {
 my $self = shift;
 return $self->masterPageExtension(shift, 'footer', @_);
 }

sub masterPageHeaderLeft
 {
 my $self = shift;
 return $self->masterPageExtension(shift, 'header-left', @_);
 }

sub masterPageFooterLeft
 {
 my $self = shift;
 return $self->masterPageExtension(shift, 'footer-left', @_);
 }

#-----------------------------------------------------------------------------

sub getHeaderParagraph
 {
 my $self = shift;
 my $root = $self->masterPageHeader(shift) or return undef;
 my $n  = shift;
 return $self->getElement('text:p', $n, $root);
 }

#-----------------------------------------------------------------------------

sub getFooterParagraph
 {
 my $self = shift;
 my $root = $self->masterPageFooter(shift) or return undef;
 my $n  = shift;
 return $self->getElement('text:p', $n, $root);
 }

#-----------------------------------------------------------------------------

sub updateDefaultStyle
 {
 my $self = shift;
 my $style = $self->getDefaultStyleElement(shift);
 unless ($style)
  {
  warn "[" . __PACKAGE__ . "::updateDefaultStyle] " .
   "Unavailable default style in the context\n";
  return undef;
  }
 return $self->updateStyle($style, @_);
 }

#-----------------------------------------------------------------------------
# remove a given style element (with element type checking)

sub removeStyle
 {
 my $self = shift;
 my $element = $self->getStyleElement(@_);
 if ($element && $element->isStyle)
  {
  return $self->removeElement($element);
  }
 else
  {
  warn "[" . __PACKAGE__ . "::removeStyle] " .
   "Unknown style or non-style element\n";
  return undef;
  }
 }

#-----------------------------------------------------------------------------
1;
