#-----------------------------------------------------------------------------
# 02read.t	OpenOffice::OODoc Installation test		2009-01-16
#-----------------------------------------------------------------------------

use Test;
BEGIN	{ plan tests => 12 }

use OpenOffice::OODoc	2.108;
ok($OpenOffice::OODoc::VERSION >= 2.108);

#-----------------------------------------------------------------------------

my $testfile    =       $OpenOffice::OODoc::File::DEFAULT_OFFICE_FORMAT == 2 ?
                "odftest.odt" : "ootest.sxw";
my $generator	=	"OpenOffice::OODoc " . $OpenOffice::OODoc::VERSION .
			" installation test";
my $image_name	= "Logo";

# Opening the $testfile file
my $archive = odfContainer($testfile);
unless ($archive)
	{
	ok(0); # Unable to get the $testfile file
	exit;
	}
ok(1); # Test file open

# Opening the document content
my $doc = odfConnector(container => $archive);
unless ($doc)
	{
	ok(0); # Unable to get a regular document content
	}
else
	{
	ok(1); # Content parsed
	}

# Opening the metadata
my $meta = odfMeta(container => $archive);
unless ($meta)
	{
	ok(0); # Unable to get regular metadata
	exit unless $doc; # Give up if neither content nor metadata
	}
else
	{
	ok(1); # Metadata parsed
	}

my $manifest = odfManifest(container => $archive);
unless ($manifest)
	{
	ok(0); # Unable to get the manifest
	}
else
	{
	ok(1); # Manifest parsed
	}

# Checking the mime type
my $mimetype = $manifest->getMainType || "";
if ($OpenOffice::OODoc::File::DEFAULT_OFFICE_FORMAT == 2)
	{
	ok($mimetype eq "application/vnd.oasis.opendocument.text");
	}
else
	{
	ok($mimetype eq "application/vnd.sun.xml.writer");
	}

# Checking the image element
ok($doc->getImageElement($image_name));

# Selecting a paragraph by style
ok($doc->selectParagraphByStyle("Colour"));

# Getting the table
my $table = $doc->getTable("Environment");
unless ($table)
	{
	ok(0);		# unable to get the table
	}
else
	{
	ok(1);		# table found
	}
my ($h, $w) = $doc->getTableSize($table);

# Checking the table size; must be 6x2
ok(($h == 6) && ($w == 2)); 

# Checking cell value
my $cv = $doc->cellValue($table, "B5");
ok($cv eq $OpenOffice::OODoc::VERSION);

# Checking the installation signature in the metadata
ok($meta->generator() eq $generator);

$manifest->dispose;
$doc->dispose;
$meta->dispose;

exit 0;

