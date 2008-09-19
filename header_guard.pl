#!/usr/bin/perl -w
use strict;

use FindBin qw($RealBin);
use lib "$RealBin/perl_inc";
use rcb_functions;

my $filename;
my @infile;
my $define_flag;
my @header;
my @footer;


foreach $filename (@ARGV) {
    @infile = file_to_list($filename);
    

    if (! ($infile[0] =~ /HEADER GUARD/)) {
	$define_flag = $filename;
	$define_flag =~ tr/a-z/A-Z/; 
	$define_flag =~ s!^.*/!!;
	$define_flag =~ tr/./_/;
	$define_flag = "__" . $define_flag;
	$define_flag .= "__";
	
	@header = (   "//// HEADER GUARD ///////////////////////////"
		   ,  "// If automatically generated, keep above"
                   ,  "// comment as first line in file."
		   ,  "#ifndef $define_flag"
		   ,  "#define $define_flag"
		   ,  "//// HEADER GUARD ///////////////////////////"
		   );

	@footer = (   "//// HEADER GUARD ///////////////////////////"
		   ,  "#endif"
                   ,  "//// HEADER GUARD ///////////////////////////"
		   );

	unshift @infile, @header;
	push @infile, @footer;

	open(OUTFILE, "> $filename");
	print OUTFILE make_list_a_file(@infile);
	print OUTFILE "\n";
	close OUTFILE;
    }
}
