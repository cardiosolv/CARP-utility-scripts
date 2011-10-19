#!/usr/bin/env perl

use strict;

unless(@ARGV == 2){
    die "Usage: itris_to_etris.pl <i2e file> <model_i.tris file>";
}

my $i2e_file = $ARGV[0];
my $tris_file = $ARGV[1];

open(I2E, "<$i2e_file") || die "Failed to open supplied i2e file $i2e_file: $!\n";
chomp(my @i2edata = <I2E>);
close(I2E);

open(TRIS, "<$tris_file") || die "Failed to open supplied tris file $tris_file: $!\n";
chomp(my @tris = <TRIS>);
close(TRIS);

# Read mapping into hash
my %i2emap;

foreach my $line (@i2edata){
    my @tmp = split(/\s+/, $line);
    if(@tmp != 2){
        die "Failed to read 2 entries from i2e file $i2e_file - Line was: $line\n";
    }

    $i2emap{$tmp[0]} = $tmp[1];
}

# Reprint .tris file to stdout using remapped point numbers
print shift(@tris) . "\n";
foreach my $line (@tris){
    my @tmp = split(/\s+/, $line);
    if(@tmp != 4){
        die "Failed to read 4 entries from tris file $tris_file - Line was: $line\n";
    }

    for(my $i=0; $i < 3; $i++){
        print $i2emap{$tmp[$i]}.' ';
    }
    
    # region ID (?)
    print $tmp[3]."\n";
}
