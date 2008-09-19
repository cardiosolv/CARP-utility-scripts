#!/usr/bin/perl -w
use strict;

my $filename;
my @infile;
my $define_flag;
my @header;
my @footer;


foreach $filename (@ARGV) {
    open(FILE, $filename) or die "Can't open file $filename: $!\n";
    @infile = <FILE>;
    close(FILE);

    if (! ($infile[0] =~ /HEADER GUARD/)) {
	$define_flag = $filename;
	$define_flag =~ tr/a-z/A-Z/; 
	$define_flag =~ s!^.*/!!;
	$define_flag =~ tr/./_/;
	$define_flag = "__" . $define_flag;
	$define_flag .= "__";
	
	open(OUTFILE, ">$filename") or die "Can't open file $filename for writing: $!\n";
	print OUTFILE <<_EOF
//// HEADER GUARD ///////////////////////////
// If automatically generated, keep above
// comment as first line in file.
#ifndef $define_flag
#define $define_flag
//// HEADER GUARD ///////////////////////////
_EOF
;
	print OUTFILE join("\n", @infile) . "\n";
	print OUTFILE <<_EOF
//// HEADER GUARD ///////////////////////////
#endif
//// HEADER GUARD ///////////////////////////
_EOF
;
	close(OUTFILE);
    }
}
