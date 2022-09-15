use strict;
use warnings;
use File::Find;
use File::Basename;
use DateTime;

package backup;

my @src = ();
my @src_files = ();
my $delta_days_thresh = 100;

sub push_to_src() {
    my $item = shift;
    push(@src, $item);
}

sub copy_src_to_arg() {
    my $dst_base = shift;
    my %dir_tbl = (Pictures => "picture",
                   Videos   => "movie");

    &do_mount($dst_base);

    foreach (@src) {
        my $src_dir = $_;
        File::Find::find(\&chk_copy_file, $src_dir);
    }

    foreach (@src_files) {
        my $src_file = $_;
        if (! -f $src_file) { die("Error:$src_file $!"); }
        $src_file = add_dq($src_file);

        my $dev_null;
        my $dir_name1;
        my $dir_name2;
        my $file_name = File::Basename::basename $_;

        s/\/${file_name}$//;
        ($dir_name2, $dir_name1) = File::Basename::fileparse $_;

        s/\/${dir_name2}$//;
        ($dir_name1, $dev_null) = File::Basename::fileparse $_;

        $file_name =~ m/^(\d\d\d\d)-/;
        my $year = sprintf("%04d", $1);

        my $dst_file;
        if ($dir_tbl{$dir_name1} eq "movie" && $dir_name2 eq "Home") {
            $dst_file = "$dst_base/$dir_tbl{$dir_name1}/$dir_name2/$file_name";
        }
        else {
            $dst_file = "$dst_base/$dir_tbl{$dir_name1}/$dir_name2/$dir_name2($year)/$file_name";
        }
        if (-f $dst_file) { print "$dst_file is exists, so file copy is skipped.\n"; next; }
        $dst_file = add_dq($dst_file);

        print "src_file=$src_file, dst_file=$dst_file\n";
        system "cp $src_file $dst_file";
    }

    &do_umount($dst_base);
}

sub chk_copy_file() {
    if (/^\d\d\d\d-/) {
        push(@src_files, $File::Find::name);
    }
}

sub arch_src_to_arg() {
    my $dst_dir = shift;
    my $pass = shift;
    $delta_days_thresh = shift;

    &do_mount($dst_dir);

    my $src_items;
    foreach (@src) { $src_items .= '"' . $_ . '" '; }

    my $dt = DateTime->today;
    my $date = $dt->ymd;
    $date =~ s/^\d\d//;
    $date =~ s/-//g;
    my $dst_file = $dst_dir . '/bak_' . $date . '.rar';
    $dst_file = &add_dq($dst_file);

    File::Find::find(\&chk_del, $dst_dir);

    print "dst_file=$dst_file, src_items=$src_items\n";
    system "rar a -v1000000k -p$pass $dst_file $src_items";

    &do_umount($dst_dir);
}

sub chk_del() {
    if (/^bak_(\d\d)(\d\d)(\d\d).*\.rar$/) {
        my $dt1 = DateTime->new(year => int("20" . $1), month => int($2), day => int($3));
        my $dt2 = DateTime->today;
        my $delta = $dt2->delta_days($dt1);
        my $delta_days = int($delta->delta_days);
        if (($delta_days > $delta_days_thresh) || ($delta_days == 0)) {
            my $rm_file = $File::Find::name; 
            $rm_file = &add_dq($rm_file);
            print "rm_file=$rm_file, delta_days=$delta_days\n";
            system "rm $rm_file";
        }
    }
}

sub add_dq() {
    my $ret = shift;
    $ret = '"' . $ret . '"';
    return $ret;
}

sub do_mount() {
    my $dir = shift;
    my $result = chk_mntc_dir($dir);
    if ($result) {
        print "sudo mount $result\n";
        system "sudo mount $result";
    }
}

sub do_umount() {
    my $dir = shift;
    my $result = chk_mntc_dir($dir);
    if ($result) {
        print "sudo umount $result\n";
        system "sudo umount $result";
    }
}

sub chk_mntc_dir() {
    my $dir = shift;
    $dir =~ m/^(\/mnt\/\w+)/;
    my $match = $1;
    if ($match) {
        if ($match ne '/mnt/c') { return $match; }
        else                    { return undef; }
    }
    else { return undef; }
}

1;
