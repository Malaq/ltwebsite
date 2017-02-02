#!/usr/bin/perlml

# The libraries we're using
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use DBI;

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
	##print "<TD BGCOLOR=$rowcolor>";
	#print "<TD sorttable_customkey=\"$key\">";
	#print "<B>";
	##print "<font color=$classclr>$tempclass</font>";
	#print "<img src=\"images/$imagename\" align=\"center\" title=\"$tempclass\">";
	#print "</B>";
	#print "</TD>";
	my $returnval = "<TD sorttable_customkey=\"$key\">";
	my $returnval = "$returnval<B>";
	my $returnval = "$returnval<img src=\"../images/$imagename\" align=\"center\" title=\"$tempclass\">";
	my $returnval = "$returnval</B>";
	my $returnval = "$returnval</TD>";
	return $returnval;
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

open(INF,"../../db.txt");
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

sub spec_list {
}
#Input Char Name
#Output Dropdown select element
sub primarySpecDropDown {
	my $char_id = shift;
	my $spec_query = "";
	my $return_form = "";

my $SQL1 = "select chr.CHAR_ID, cs.SPEC_ID, cs.CLASS_ID, cs.SPEC_NAME, cs.SPEC_ROLE, CASE WHEN cs.SPEC_ID = chr.PRIMARY_SPEC THEN 1 ELSE 0 END ORDERING " .
	"from `CHARACTER` chr, CLASS_SPEC cs, CLASSES cl " .
	"where chr.CLASS = cl.CLASS_NAME " .
	"  and cl.CLASS_ID = cs.CLASS_ID " .
	"  and chr.CHAR_ID = ? " .
	"union " .
	"select chr1.CHAR_ID, " .
	"       0 as SPEC_ID, " .
	"       0 AS CLASS_ID, " .
	"       IFNULL(CAST(PRIMARY_SPEC AS CHAR),'--UNASSIGNED--') AS SPEC_NAME, " .
	"       '' AS SPEC_ROLE, " .
	"       IFNULL(PRIMARY_SPEC,1) AS ORDERING " .
	"from `CHARACTER` chr1 " .
	"where chr1.CHAR_ID = ? " .
	"and chr1.PRIMARY_SPEC IS NULL " . 
	"ORDER BY ORDERING DESC, SPEC_NAME ASC;";

	$spec_query =
		$dbh->prepare($SQL1);

	$spec_query->bind_param(1,$char_id);
	$spec_query->bind_param(2,$char_id);
	$spec_query->execute() or die $dbh->errstr;

	$return_form = "${return_form}<SELECT style=\"font-size:10px;font-family:Arial\" name=\"PRIMARY_SPEC\" onchange=\"this.form.submit()\">";
	while (my $row1 = $spec_query->fetchrow_hashref()) {
		$return_form = "${return_form}<option value=\"$row1->{SPEC_ID}\">$row1->{SPEC_NAME}</option>";
	}
	$return_form = "${return_form}</SELECT>";

	return $return_form;
}

sub secondarySpecDropDown {
	my $char_id = shift;
	my $spec_query = "";
	my $return_form = "";

my $SQL1 = "select chr.CHAR_ID, cs.SPEC_ID, cs.CLASS_ID, cs.SPEC_NAME, cs.SPEC_ROLE, CASE WHEN cs.SPEC_ID = chr.SECONDARY_SPEC THEN 1 ELSE 0 END ORDERING " .
	"from `CHARACTER` chr, CLASS_SPEC cs, CLASSES cl " .
	"where chr.CLASS = cl.CLASS_NAME " .
	"  and cl.CLASS_ID = cs.CLASS_ID " .
	"  and chr.CHAR_ID = ? " .
	"union " .
	"select chr1.CHAR_ID, " .
	"       0 as SPEC_ID, " .
	"       0 AS CLASS_ID, " .
	"       IFNULL(CAST(SECONDARY_SPEC AS CHAR),'--UNASSIGNED--') AS SPEC_NAME, " .
	"       '' AS SPEC_ROLE, " .
	"       IFNULL(SECONDARY_SPEC,1) AS ORDERING " .
	"from `CHARACTER` chr1 " .
	"where chr1.CHAR_ID = ? " .
	"and chr1.SECONDARY_SPEC IS NULL " . 
	"ORDER BY ORDERING DESC, SPEC_NAME ASC;";

	$spec_query =
		$dbh->prepare($SQL1);

	$spec_query->bind_param(1,$char_id);
	$spec_query->bind_param(2,$char_id);
	$spec_query->execute() or die $dbh->errstr;

	$return_form = "${return_form}<SELECT style=\"font-size:10px;font-family:Arial\" name=\"SECONDARY_SPEC\" onchange=\"this.form.submit()\">";
	while (my $row1 = $spec_query->fetchrow_hashref()) {
		$return_form = "${return_form}<option value=\"$row1->{SPEC_ID}\">$row1->{SPEC_NAME}</option>";
	}
	$return_form = "${return_form}</SELECT>";

	return $return_form;
}

my $char_spec_table = "";
sub char_spec_table {
	my $spec_statement = "";

	$SQL =  "select CHAR_ID, NAME, CLASS, RANK, DATE_JOINED, DATE_REMOVED, ACTIVE, PRIMARY_SPEC, SECONDARY_SPEC, " .
		"IFNULL((select SPEC_NAME from CLASS_SPEC where CLASS_SPEC.SPEC_ID = PRIMARY_SPEC),'-- UNASSIGNED --') AS PRIMARY_SPEC_NAME, " .
		"IFNULL((select SPEC_ROLE from CLASS_SPEC where CLASS_SPEC.SPEC_ID = PRIMARY_SPEC),'-- UNASSIGNED --') AS PRIMARY_SPEC_ROLE, " .
		"IFNULL((select SPEC_NAME from CLASS_SPEC where CLASS_SPEC.SPEC_ID = SECONDARY_SPEC),'-- UNASSIGNED --') AS SECONDARY_SPEC_NAME, " .
		"IFNULL((select SPEC_ROLE from CLASS_SPEC where CLASS_SPEC.SPEC_ID = SECONDARY_SPEC),'-- UNASSIGNED --') AS SECONDARY_SPEC_ROLE " .
		"from `CHARACTER` " .
		"where rank not in ('P.U.G.','Alt','Friend','Officer Alt','PvPer') " .
		"and DATE_REMOVED is null " .
		"and ACTIVE = 'Y' " .
		"ORDER BY NAME; ";

	$spec_statement =
		$dbh->prepare($SQL);

	$spec_statement->execute() or die $dbh->errstr;

	$char_spec_table = "";
	$char_spec_table = "$char_spec_table<TABLE class=\"sortable normal\" id=\"char_spec_table\">";
	$char_spec_table = "$char_spec_table<THEAD>";
	$char_spec_table = "$char_spec_table<TR>";
	$char_spec_table = "$char_spec_table<TH>Name</TH>";
	$char_spec_table = "$char_spec_table<TH>Class</TH>";
	$char_spec_table = "$char_spec_table<TH>Rank</TH>";
	$char_spec_table = "$char_spec_table<TH>Date Joined</TH>";
	$char_spec_table = "$char_spec_table<TH>Main Spec</TH>";
	$char_spec_table = "$char_spec_table<TH>Alt Spec</TH>";
	$char_spec_table = "$char_spec_table<TH>Primary Role</TH>";
	$char_spec_table = "$char_spec_table<TH>Alt Role</TH>";
	$char_spec_table = "$char_spec_table</TR>";
	$char_spec_table = "$char_spec_table</THEAD>";	
	while (my $row = $spec_statement->fetchrow_hashref()) {
		$char_spec_table = "$char_spec_table<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\">";
		$char_spec_table = "$char_spec_table<TD>$row->{NAME}</TD>";
		my $class_label = classColor($row->{CLASS});
		$char_spec_table = "${char_spec_table}$class_label";
		$char_spec_table = "$char_spec_table<TD>$row->{RANK}</TD>";
		$char_spec_table = "$char_spec_table<TD>$row->{DATE_JOINED}</TD>";
		$char_spec_table = "$char_spec_table<FORM NAME=\"specForm\" action=\"cgi-bin/updateCharSpec.cgi\">";
		$char_spec_table = "$char_spec_table<input type=\"hidden\" name=\"CHAR_NAME\" value=\"$row->{NAME}\">";
		$char_spec_table = "$char_spec_table<input type=\"hidden\" name=\"CHAR_ID\" value=\"$row->{CHAR_ID}\">";
		my $dropdown = primarySpecDropDown($row->{CHAR_ID});
		$char_spec_table = "$char_spec_table<TD>$dropdown</TD>";
		my $altDropDown = secondarySpecDropDown($row->{CHAR_ID});
		$char_spec_table = "$char_spec_table<TD>$altDropDown</TD>";
		$char_spec_table = "$char_spec_table<TD>$row->{PRIMARY_SPEC_ROLE}</TD>";
		$char_spec_table = "$char_spec_table<TD>$row->{SECONDARY_SPEC_ROLE}</TD>";
		$char_spec_table = "$char_spec_table</FORM>";
		$char_spec_table = "$char_spec_table</TR>";
	}
	$char_spec_table = "$char_spec_table</TABLE>";
}

print "<fieldset>";
print "<legend><A HREF=\"bis.shtml\">Character Specs:</A></legend>";
char_spec_table();
print "	    <p>$char_spec_table</p>";
print "</fieldset>";

$dbh->disconnect();
#print "</pre>";
