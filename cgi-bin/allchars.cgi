#!/usr/bin/perlml

# The libraries we're using
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use DBI;

# Tells the browser that we're outputting HTML
print "Content-type: text/html\n\n";

# Setup our DB connection
my $database = "";
my $username = "";
my $password = "";
my $hostname = "";
my $dbport = "";

open(INF,"../db.txt");
my @login = <INF>;
close(INF);

my $database = @login[0];
$database =~ s/\n//g;
my $username = @login[1];
$username =~ s/\n//g;
my $password = @login[2];
$password =~ s/\n//g;
my $hostname = @login[3];
$hostname =~ s/\n//g;
my $dbport = @login[4];
$dbport =~ s/\n//g;


# Database handle
my $dbh = DBI->connect("dbi:mysql:database=$database;host=$hostname;port=$dbport", $username, $password) or print $DBI::errstr;

my $char_name = param('data');

print "<font size=\"6\" face=\"Monotype Corsiva\"><B>$char_name</B></font>";

	print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\" \"http://www.w3.org/TR/html4/strict.dtd\">\n";
	print "<HTML>\n";

# Loot table
my $list_statement =
	$dbh->prepare("SELECT NAME, CLASS, RANK, DATE_JOINED, DATE_REMOVED " .
			"FROM `CHARACTER` " .
			"ORDER BY NAME;");

$list_statement->execute() or die $dbh->errstr;
print "<fieldset>";
print "<legend>All Guilded Characters</legend>";
print "<script src=\"sorttable.js\"></script>\n";
print "<TABLE class=\"sortable normal\" ALIGN=LEFT><TR>";
print "<TH WIDTH=155><U><B>Name</B></U></TH>";
print "<TH WIDTH=100><U><B>Class</B></U></TH>";
print "<TH WIDTH=100><U><B>Rank</B></U></TH>";
print "<TH WIDTH=100><U><B>Date Joined</B></U></TH>";
print "<TH WIDTH=100><U><B>Date Removed</B></U></TH>";
print "</TR>\n";
while (my $row = $list_statement->fetchrow_hashref()) {
	if ( $row->{DATE_REMOVED} eq "" ) {
		#print "<TR>";
		print "<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\" onclick=\"location.href='char.shtml?data=$row->{NAME}'\">";
	} else {
		print "<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='alert'\" class=\"alert\" onclick=\"location.href='char.shtml?data=$row->{NAME}'\">";
	}
	print "<TD><A HREF=\"char.shtml?data=$row->{NAME}\">$row->{NAME}</A></TD><TD>$row->{CLASS}</TD><TD>$row->{RANK}</TD>";
	print "<TD>$row->{DATE_JOINED}</TD>";
	print "<TD>$row->{DATE_REMOVED}</TD>";
	print "</TR>\n";
	print "\n";
}
print "</TABLE>";
print "</fieldset>";
print "</HTML>";
$list_statement->finish();
$dbh->disconnect();
