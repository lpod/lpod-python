#-----------------------------------------------------------------------------
#
#	$Id : OODoc.pm 2.108 2009-01-30 JMG$
#
#	Created and maintained by Jean-Marie Gouarne
#	Copyright 2008 by Genicorp, S.A. (www.genicorp.com)
#
#-----------------------------------------------------------------------------

use OpenOffice::OODoc::File		2.118;
use OpenOffice::OODoc::Meta		2.012;
use OpenOffice::OODoc::Document		2.023;
use OpenOffice::OODoc::Manifest		2.005;

#-----------------------------------------------------------------------------

package	OpenOffice::OODoc;
use 5.008_000;
our $VERSION				= 2.108;

require Exporter;
our @ISA    = qw(Exporter);
our @EXPORT = qw
	(
	ooXPath ooText ooMeta ooManifest ooImage ooStyles
	odfXPath odfText odfMeta odfManifest odfImage odfStyles
	odfConnector odfDocument ooDocument odfPackage odfContainer ooFile
	odfLocalEncoding localEncoding ooLocalEncoding
	odfEncodeText odfDecodeText ooEncodeText ooDecodeText
	ooLocaltime ooTimelocal odfLocaltime odfTimelocal
	odfTemplatePath ooTemplatePath
	odfWorkingDirectory workingDirectory ooWorkingDirectory
	odfReadConfig readConfig ooReadConfig
	);

#-----------------------------------------------------------------------------
# config loader

sub	odfReadConfig
	{
	my $filename = shift;
	unless ($filename)
		{
		$filename = $INSTALLATION_PATH . '/config.xml'
			if $INSTALLATION_PATH;
		}
	unless ($filename)
		{
		warn	"[" . __PACKAGE__ . "::odfReadConfig] "	.
			"Missing configuration file\n";
		return undef;
		}
	my $config = XML::Twig->new->safe_parsefile($filename);
	unless ($config)
		{
		warn	"[" . __PACKAGE__ . "::odfReadConfig] "	.
			"Syntax error in configuration file $filename\n";
		return undef;
		}
	my $root = $config->get_xpath('//OpenOffice-OODoc', 0);
	unless ($root && $root->isElementNode)
		{
		return undef;
		}
	foreach my $node ($root->getChildNodes)
		{
		next unless $node->isElementNode;
		my $name = $node->getName; $name =~ s/-/::/g;
		my $varname = 'OpenOffice::OODoc::' . $name;
		$$varname = $node->string_value;
		$$varname = odfDecodeText($$varname);
		}
	OpenOffice::OODoc::Styles::ooLoadColorMap();
	return 1;
	}

#-----------------------------------------------------------------------------

sub	odfFile
	{
	return OpenOffice::OODoc::File->new(@_);
	}

sub	odfXPath
	{
	return OpenOffice::OODoc::XPath->new(@_);
	}

sub	odfText
	{
	return OpenOffice::OODoc::Text->new(@_);
	}

sub	odfMeta
	{
	return OpenOffice::OODoc::Meta->new(@_);
	}

sub	odfManifest
	{
	return OpenOffice::OODoc::Manifest->new(@_);
	}

sub	odfImage
	{
	return OpenOffice::OODoc::Image->new(@_);
	}

sub	odfDocument
	{
	return OpenOffice::OODoc::Document->new(@_);
	}

sub	odfStyles
	{
	return OpenOffice::OODoc::Styles->new(@_);
	}
	
#-----------------------------------------------------------------------------
# accessor for local character set control

sub	odfLocalEncoding
	{
	my $newcharset = shift;
	if ($newcharset)
	    	{
	    	if (Encode::find_encoding($newcharset))
		    {
		    $OpenOffice::OODoc::XPath::LOCAL_CHARSET = $newcharset;
		    }
		else
		    {
		    warn	"[" . __PACKAGE__ . "::odfLocalEncoding] " .
				"Unsupported encoding\n";
		    }
		}
	return $OpenOffice::OODoc::XPath::LOCAL_CHARSET;
	}

#-----------------------------------------------------------------------------
# accessor for default XML templates for document creation

sub	odfTemplatePath
	{
	return OpenOffice::OODoc::File::templatePath(@_);
	}

#-----------------------------------------------------------------------------
# accessor for default working directory control

sub	odfWorkingDirectory
	{
	my $path = shift;

	$OpenOffice::OODoc::File::WORKING_DIRECTORY = $path
		if defined $path;
	OpenOffice::OODoc::File::checkWorkingDirectory
		(
		$OpenOffice::OODoc::File::WORKING_DIRECTORY
		);

	return $OpenOffice::OODoc::File::WORKING_DIRECTORY;
	}
	
#-----------------------------------------------------------------------------
# shortcuts for low-level local/utf8 code conversion 

sub	odfEncodeText
	{
	return OpenOffice::OODoc::XPath::encode_text(@_);
	}

sub	odfDecodeText
	{
	return OpenOffice::OODoc::XPath::decode_text(@_);
	}

#-----------------------------------------------------------------------------
# initialization

BEGIN
	{
	*ooDocument		= *odfDocument;
	*odfConnector		= *odfDocument;
	*odfContainer		= *odfFile;
	*odfPackage		= *odfFile;
	*ooFile			= *odfFile;
	*ooXPath		= *odfXPath;
	*ooText			= *odfText;
	*ooStyles		= *odfStyles;
	*ooImage		= *odfImage;
	*ooMeta			= *odfMeta;
	*ooManifest		= *odfManifest;
	*localEncoding		= *odfLocalEncoding;
	*workingDirectory	= *odfWorkingDirectory;
	*readConfig		= *odfReadConfig;
	*ooLocalEncoding	= *odfLocalEncoding;
	*ooWorkingDirectory	= *odfWorkingDirectory;
	*ooReadConfig		= *odfReadConfig;
	*ooEncodeText		= *odfEncodeText;
	*ooDecodeText		= *odfDecodeText;
	*ooTemplatePath		= *odfTemplatePath;
	*odfLocaltime		= *OpenOffice::OODoc::XPath::odfLocaltime;
	*odfTimelocal		= *OpenOffice::OODoc::XPath::odfTimelocal;
	*ooLocaltime		= *odfLocaltime;
	*ooTimelocal		= *odfTimelocal;
	
	my $module_path = $INC{"OpenOffice/OODoc.pm"};
	$module_path =~ s/\.pm$//;
	$OpenOffice::OODoc::INSTALLATION_PATH = $module_path;
	odfReadConfig() if ( -e "$INSTALLATION_PATH/config.xml" );
	}

#-----------------------------------------------------------------------------
1;
