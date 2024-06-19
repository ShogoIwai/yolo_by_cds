#!/usr/bin/perl -w

use strict;
use warnings;
use Getopt::Long qw(:config posix_default no_ignore_case bundling);
use Cwd;
use File::Find;
use File::Copy;
use Fcntl ':mode';

my %opts = ();
&parseOptions();

my $m_fmatch = '';
my $m_pre = '';
my $m_post = '';

sub parseOptions {
    GetOptions(\%opts, 'help',
                       'replace=s',
                       'file=s',
                       'pre=s',
                       'post=s',
    );
    if ($opts{help}) { &help(); exit; }
    &main();
}

sub help {
    print << "ENDLINE";
Usage  : ${0} [Options]
Option :
    --help   : print this usage
    --replace: specify replace execute path
    --file   : specify replace file regular expression 
    --pre    : specify pre regular expression 
    --post   : specify post regular expression 
ENDLINE
}

sub main() {
    if ($opts{replace}) {
        $m_fmatch = $opts{file}; $m_pre = $opts{pre}; $m_post = $opts{post};
        File::Find::find(\&replace, Cwd::realpath($opts{replace}));
    }
}

sub replace() {
    my $file_path = $File::Find::name;
    my $temp_file = "$file_path.tmp";
    my $match = 0;
    if ($file_path =~ /$m_fmatch/) {
        open (INFILE, "<$file_path") or die "$file_path: $!";
        open (OUTFILE, ">$temp_file") or die "$temp_file: $!";
        while (<INFILE>) {
            if (/$m_pre/) { $match = 1; }
            s/$m_pre/$m_post/g;
            print OUTFILE $_;
        }
        close (OUTFILE);
        close (INFILE);
        if ($match) {
            overwriteFile($file_path, $temp_file);
        }
        else {
            unlink($temp_file);
        }
    }
}

sub overwriteFile() {
    my $file_path = shift;
    my $temp_file = shift;

    my $mode = (stat($file_path))[2] & 07777;
    chmod $mode, $temp_file or die "Cannot chmod $temp_file: $!";

    File::Copy::move($temp_file, $file_path) or die "Cannot move $temp_file to $file_path: $!";
}
