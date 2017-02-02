#!/usr/bin/perlml

# The libraries we're using
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use DBI;

my $script = $ENV{'SCRIPT_NAME'};
#Who is running the script
my $audituser = "null";
$audituser = $ENV{'REMOTE_USER'};

# Tells the browser that we're outputting HTML
print "Content-type: text/html\n\n";

# For debug output
#print "<pre>";
#my $rowcolor = '#A69C8B';
my $rowcolor = '#463C2B';
#my $rowcolor = 'silver';

sub round {
    my($number) = shift;
    return int($number + .5);
}

sub URLEncode {
my $theURL = $_[0];
$theURL =~ s/([\W])/"%" . uc(sprintf("%2.2x",ord($1)))/eg;
return $theURL;
}

#Class Coloring
sub classColor {
	my $tempclass = shift;
	my $classclr = 'black';
	my $imagename = '';
	my $key = '0';
	#my $classbg = 'black';
	#my $classbg = '#867C6B';
	#my $classbg = 'silver';
	if ($tempclass eq 'Druid') {
		$classclr='#FF7D0A';
		$imagename = 'druid.gif';
		$key = '9';
	} elsif ($tempclass eq 'Hunter') {
		$classclr='#ABD473';
		$imagename = 'hunter.gif';
		$key = '8';
	} elsif ($tempclass eq 'Mage') {
		$classclr='#69CCF0';
		$imagename = 'mage.gif';
		$key = '7';
	} elsif ($tempclass eq 'Paladin') {
		$classclr='#F58CBA';
		$imagename = 'paladin.gif';
		$key = '6';
	} elsif ($tempclass eq 'Priest') {
		$classclr='#FFFFFF';
		$imagename = 'priest.gif';
		$key = '5';
	} elsif ($tempclass eq 'Rogue') {
		$classclr='#FFF569';
		$imagename = 'rogue.gif';
		$key = '4';
	} elsif ($tempclass eq 'Shaman') {
		$classclr='#2459FF';
		$imagename = 'shaman.gif';
		$key = '3';
	} elsif ($tempclass eq 'Warlock') {
		$classclr='#9482C9';
		$imagename = 'warlock.gif';
		$key = '2';
	} elsif ($tempclass eq 'Warrior') {
		$classclr='#C79C6E';
		$imagename = 'warrior.gif';
		$key = '1';
	} elsif ($tempclass eq 'Death Knight') {
		$classclr='#C41F3B';
		$imagename = 'deathknight.gif';
		$key = '10';
	}
	#print "<TD BGCOLOR=$rowcolor>";
	print "<TD sorttable_customkey=\"$key\">";
	print "<B>";
	#print "<font color=$classclr>$tempclass</font>";
	print "<img src=\"images/$imagename\" align=\"center\" title=\"$tempclass\">";
	print "</B>";
	print "</TD>";
}

#Attendance Coloring
sub attendanceColor {
	my $attendance = shift;
	my $attendance_type = '';
	if ($attendance > 84) {
		$attendance_type = 'high_attendance';
	} elsif ($attendance > 59) {
		$attendance_type = 'medium_attendance';
	} else {
		$attendance_type = 'low_attendance';
	}
	print "<TD class='$attendance_type' align=\"right\">$attendance%</TD>";
}

#Sitting Coloring
sub sittingColor {
	my $attendance = shift;
#	my $attendance_type = '';
#	if ($attendance > 84) {
#		$attendance_type = 'high_attendance';
#	} elsif ($attendance > 59) {
#		$attendance_type = 'medium_attendance';
#	} else {
#		$attendance_type = 'low_attendance';
#	}
	#print "<TD class='$attendance_type' align=\"right\">$attendance%</TD>";
	print "<TD class='sitting_neutral' align=\"right\">$attendance%</TD>";
}

#Loot Coloring
sub lootColor {
	my $temploot = shift;
	my $loot_type = '';
	my $bold1 = '';
	my $bold2 = '';
	if ($temploot > 0) {
		$loot_type='loot';
	} else {
		$loot_type='no_loot';
	}
	print "<TD class='$loot_type'>$temploot</TD>";
}

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

#Sub to insert audit information.
sub auditquery {
	my $audittype = shift;
	my $details = shift;

	my $audit_statement = 
		$dbh->prepare("INSERT INTO LT_AUDIT(AUDIT_TYPE, USERNAME, SCRIPT, DETAILS) ".
				"VALUES(?,?,?,?);");

	$audit_statement->bind_param(1, $audittype);	
	$audit_statement->bind_param(2, $audituser);
	$audit_statement->bind_param(3, $script);
	$audit_statement->bind_param(4, $details);

	$audit_statement->execute() or die $dbh->errstr;
}

sub zone_table {

	my $zone_query =
		$dbh->prepare("SELECT ZO.ZONE_ID, ZO.ZONE_NAME, EX.EXPANSION_NAME " .
		"FROM ZONES ZO, EXPANSION EX " .
		"WHERE ZO.EXPANSION_ID = EX.EXPANSION_ID " .
		"ORDER BY ZO.EXPANSION_ID DESC;");
	
	$zone_query->execute() or die $dbh->errstr;
	
	$zone_table = "";
	$zone_table = "$zone_table<TABLE class=\"sortable normal\" id=\"token_table\">";
	#TABLE HEADER
	$zone_table = "$zone_table<THEAD>";
	$zone_table = "$zone_table<TR>";
	$zone_table = "$zone_table<TH><U><B>Zone Name</B></U></TH>";
	$zone_table = "$zone_table<TH><U><B>Expansion Name</B></U></TH>";
	$zone_table = "$zone_table</TR>";
	$zone_table = "$zone_table</THEAD>";
	#END HEADER
	#
	#ROWS

	while (my $row = $zone_query->fetchrow_hashref()) {
		$zone_table = "$zone_table<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\" onclick=\"location.href='bosses.shtml?ZONE_ID=$row->{ZONE_ID}'\">";
		$zone_table = "$zone_table<TD>$row->{ZONE_NAME}</TD>";
		$zone_table = "$zone_table<TD>$row->{EXPANSION_NAME}</TD>";
		$zone_table = "$zone_table</TR>";
	}
	#END ROWS
	#
	$zone_table = "$zone_table</TABLE>";

	return $zone_table;
}


################
# Main page
################
#my $tier_id = param('TIER_ID');
#my $class_id = param('CLASS_ID');
#my $spec_id = param('SPEC_ID');
#my $bis_list_id = param('BIS_LIST_ID');
#my $confirm_new_tier = param('CONFIRM_NEW_TIER');

print "<fieldset>";
print "<legend>Zone List:</A></legend>";
print zone_table();
print "</fieldset>";

$dbh->disconnect();
#print "</pre>";
