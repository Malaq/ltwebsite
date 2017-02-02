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

sub insert_tier {
	my $v_name = shift;
	my $v_desc = shift;
	my $v_low = shift;
	my $v_high = shift;

	my $SQL = 
		$dbh->prepare("insert into BIS_TIERS(TIER_NAME, TIER_DESC, TIER_ILEVEL_LOW, TIER_ILEVEL_HIGH) " .
				"VALUES (?,?,?,?);");

	$SQL->bind_param(1, $v_name);
	$SQL->bind_param(2, $v_desc);
	$SQL->bind_param(3, $v_low);
	$SQL->bind_param(4, $v_high);

	$SQL->execute() or die $dbh->errstr;
}

sub tier_table {
	my $type = shift;
	my $tier_query = "";

	if ($type eq "ACTIVE") {
		$tier_query =
			$dbh->prepare("SELECT TIER_ID, TIER_NAME, TIER_DESC, TIER_ILEVEL_LOW, TIER_ILEVEL_HIGH " .
					"FROM BIS_TIERS " .
					"WHERE ACTIVE_FLAG = 'T';");
	
		$tier_query->execute() or die $dbh->errstr;
	}
	
	$tier_table = "";
	$tier_table = "$tier_table<TABLE class=\"sortable normal\" id=\"token_table\">";
	#TABLE HEADER
	$tier_table = "$tier_table<THEAD>";
	$tier_table = "$tier_table<TR>";
	$tier_table = "$tier_table<TH><U><B>Tier Name</B></U></TH>";
	$tier_table = "$tier_table<TH><U><B>Tier Description</B></U></TH>";
	if ($type eq "ACTIVE") {
		$tier_table = "$tier_table<TH><U><B>Tier I-Level Range</B></U></TH>";
	} 
	elsif ($type eq "CREATE")
	{
		$tier_table = "$tier_table<TH><U><B>I-Level Low</B></U></TH>";
		$tier_table = "$tier_table<TH><U><B>I-Level High</B></U></TH>";
		$tier_table = "$tier_table<TH><U><B>Commit</B></U></TH>";
	}
	$tier_table = "$tier_table</TR>";
	$tier_table = "$tier_table</THEAD>";
	#END HEADER
	#
	#ROWS
	if ($type eq "ACTIVE") {
		while (my $row = $tier_query->fetchrow_hashref()) {
			$tier_table = "$tier_table<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\" onclick=\"location.href='bis.shtml?TIER_ID=$row->{TIER_ID}'\">";
			$tier_table = "$tier_table<TD>$row->{TIER_NAME}</TD>";
			$tier_table = "$tier_table<TD>$row->{TIER_DESC}</TD>";
			$tier_table = "$tier_table<TD>$row->{TIER_ILEVEL_LOW}-$row->{TIER_ILEVEL_HIGH}</TD>";
			$tier_table = "$tier_table</TR>";
		}
	}
	elsif ($type eq "CREATE")
	{
		#target=\"_blank\"
		$tier_table = "$tier_table<form name=\"newtier\" action=\"bis.shtml\" ONSUBMIT=\"return checkRequired(this)\" >";
		$tier_table = "$tier_table<TD><input type=\"text\" name=\"TIER_NAME\" required /></TD>";
		$tier_table = "$tier_table<TD><input type=\"text\" name=\"TIER_DESC\" required /></TD>";
		$tier_table = "$tier_table<TD><input type=\"text\" name=\"ILEVEL_LOW\" required /></TD>";
		$tier_table = "$tier_table<TD><input type=\"text\" name=\"ILEVEL_HIGH\" required /></TD>";
		$tier_table = "$tier_table<TD><input type=\"submit\" value=\"Create\" /></TD>";
		$tier_table = "$tier_table</form>";
		$tier_table = "$tier_table</TR>";
	}
	$tier_table = "$tier_table</TR>";
	#END ROWS
	#
	$tier_table = "$tier_table</TABLE>";

	return $tier_table;
}

sub class_table {

	my $v_tier = shift;

	my $SQL = 
		$dbh->prepare("SELECT CL.CLASS_NAME,  " .
		"			 CL.CLASS_ID, " .
		"			 CS.SPEC_NAME,  " .
		"			 CS.SPEC_ID, " .
		"			 CS.SPEC_ROLE,  " .
		"			 CL.ICON_FILENAME,  " .
		"			 (SELECT COUNT(*) FROM BIS_LISTS BL WHERE BL.CLASS_ID = CL.CLASS_ID AND BL.SPEC_ID = CS.SPEC_ID AND BL.ACTIVE_FLAG = 'T' AND BL.TIER_ID = ?) LISTS " .
		"FROM CLASSES CL,  " .
		"     CLASS_SPEC CS " .
		"WHERE CL.CLASS_ID = CS.CLASS_ID;");
	$SQL->bind_param(1,$v_tier);

	$SQL->execute() or die $dbh->errstr;

	$class_table = "$class_table<TABLE class=\"sortable normal\" id=\"class_table\">";
	#TABLE HEADER
	$class_table = "$class_table<THEAD>";
	$class_table = "$class_table<TR>";
	$class_table = "$class_table<TH><U><B>Icon</B></U></TH>";
	$class_table = "$class_table<TH><U><B>Class Name</B></U></TH>";
	$class_table = "$class_table<TH><U><B>Spec Name</B></U></TH>";
	$class_table = "$class_table<TH><U><B>Spec Role</B></U></TH>";
	$class_table = "$class_table<TH><U><B>BIS Lists Existing</B></U></TH>";
	$class_table = "$class_table<TH><U><B>Create</B></U></TH>";
	$class_table = "$class_table</TR>";
	$class_table = "$class_table</THEAD>";
	while (my $row = $SQL->fetchrow_hashref()) {
		$class_table = "$class_table<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\" onclick=\"location.href='editbislists.shtml?TIER_ID=$v_tier&CLASS_ID=$row->{CLASS_ID}&SPEC_ID=$row->{SPEC_ID}'\" >";
		$class_table = "$class_table<TD sorttable_customkey=\"$row->{CLASS_ID}\"><img src=\"../images/$row->{ICON_FILENAME}\" align=\"center\" title=\"$row->{CLASS_NAME}\"></TD>";
		$class_table = "$class_table<TD>$row->{CLASS_NAME}</TD>";
		$class_table = "$class_table<TD>$row->{SPEC_NAME}</TD>";
		$class_table = "$class_table<TD sorttable_customkey=\"$row->{SPEC_ROLE}$row->{CLASS_ID}\">$row->{SPEC_ROLE}</TD>";
		$class_table = "$class_table<TD align=\"CENTER\"><a href=\"editbislists.shtml?TIER_ID=$v_tier&CLASS_ID=$row->{CLASS_ID}&SPEC_ID=$row->{SPEC_ID}\">$row->{LISTS}</A></TD>";
		$class_table = "$class_table<TD><a href=\"editbislists.shtml?CREATE_LIST=T&TIER_ID=$v_tier&CLASS_ID=$row->{CLASS_ID}&SPEC_ID=$row->{SPEC_ID}\"><input type=\"button\" name=\"Create\" value=\"Create\" style=\"height: 20px; width: 60px\" /></a></TD>";
		$class_table = "$class_table</TR>";
	}
	$class_table = "$class_table</TABLE>";

	return $class_table;
}

sub tier_title
{
	my $tierid = shift;

	$SQL = 
	$dbh->prepare("SELECT TIER_NAME, TIER_DESC, TIER_ILEVEL_LOW, TIER_ILEVEL_HIGH, ACTIVE_FLAG " .
			"FROM BIS_TIERS " .
			"WHERE TIER_ID = ?;");

	$SQL->bind_param(1,$tierid);

	$SQL->execute() or die $dbh->errstr;
	my $row = $SQL->fetchrow_hashref();
	print "<B>Tier Name:</B> $row->{TIER_NAME}<BR>";
	print "<B>Tier Desc:</B> $row->{TIER_DESC}<BR>";
	print "<B>Item Level Range:</B> $row->{TIER_ILEVEL_LOW} - $row->{TIER_ILEVEL_HIGH}<BR><BR>";

}

################
# Main page
################
my $tier_name = param('TIER_NAME');
my $tier_desc = param('TIER_DESC');
my $ilevel_low = param('ILEVEL_LOW');
my $ilevel_high = param('ILEVEL_HIGH');
#populated if going to the class screen
my $tier_id = param('TIER_ID');
my $confirm_new_tier = param('CONFIRM_NEW_TIER');

print "<fieldset>";
print "<legend><A HREF=\"bis.shtml\">Tier List:</A></legend>";
if ($tier_id ne "")
{
	tier_title($tier_id);
	print "<B>Choose a class/spec combination:</B><BR>";
	print "**Click a row to edit, or the create button to start a new BIS list.";
	print "<BR>";
	print class_table($tier_id);
	print "<BR>";
	print "Warning, this process can take a long time... <FORM><INPUT TYPE=\"BUTTON\" VALUE=\"Reload from Wowhead\" ONCLICK=\"window.location='cgi-bin/wh_data_extract.cgi?BIS_TIER=$tier_id' \"></FORM>";
}
elsif (($tier_name ne "") and ($tier_desc ne "") and ($ilevel_low ne "") and ($ilevel_low ne "") and ($confirm_new_tier eq "TRUE")) 
{
	auditquery("SUCCESS","Create_Tier: $tier_name, Tier_Desc: $tier_desc, Low_Ilevel: $ilevel_low, High_Ilevel: $ilevel_high");
	insert_tier($tier_name, $tier_desc, $ilevel_low, $ilevel_high);

	print "<B>Tier Created.</B>";
	print "<BR>";
	print "<TABLE class=\"sortable normal\" id=\"token_table\">";
	print "<THEAD>";
	print "<TR>";
	print "<TH><U><B>Key</B></U></TH>";
	print "<TH><U><B>Value</B></U></TH>";
	print "</TR>";
	print "</THEAD>";
	print "<TR>";
	print "<TD>Tier Name: </TD>";
	print "<TD>$tier_name</TD>";
	print "</TR>";
	print "<TR>";
	print "<TD>Tier Description: </TD>";
	print "<TD>$tier_desc</TD>";
	print "</TR>";
	print "<TR>";
	print "<TD>Low Item Level: </TD>";
	print "<TD>$ilevel_low</TD>";
	print "</TR>";
	print "<TR>";
	print "<TD>High Item Level: </TD>";
	print "<TD>$ilevel_high</TD>";
	print "</TR>";
	print "</TABLE>";
	print "<a href=\"bis.shtml\"><input type=\"button\" name=\"return\" value=\"Return to tier list.\" /></a>";
}
elsif (($tier_name ne "") and ($tier_desc ne "") and ($ilevel_low ne "") and ($ilevel_low ne ""))
{
	print "<B>Confirm New Tier:</B>";
	print "<BR>";
	print "<FORM NAME=\"confirm_new_tier\" action=\"bis.shtml\" >";
	print "<input type=\"hidden\" name=\"CONFIRM_NEW_TIER\" value=\"TRUE\" />";
	print "<input type=\"hidden\" name=\"TIER_NAME\" value=\"$tier_name\" />";
	print "<input type=\"hidden\" name=\"TIER_DESC\" value=\"$tier_desc\" />";
	print "<input type=\"hidden\" name=\"ILEVEL_LOW\" value=\"$ilevel_low\" />";
	print "<input type=\"hidden\" name=\"ILEVEL_HIGH\" value=\"$ilevel_high\" />";
	print "<TABLE class=\"sortable normal\" id=\"token_table\">";
	print "<THEAD>";
	print "<TR>";
	print "<TH><U><B>Key</B></U></TH>";
	print "<TH><U><B>Value</B></U></TH>";
	print "</TR>";
	print "</THEAD>";
	print "<TR>";
	print "<TD>Tier Name: </TD>";
	print "<TD>$tier_name</TD>";
	print "</TR>";
	print "<TR>";
	print "<TD>Tier Description: </TD>";
	print "<TD>$tier_desc</TD>";
	print "</TR>";
	print "<TR>";
	print "<TD>Low Item Level: </TD>";
	print "<TD>$ilevel_low</TD>";
	print "</TR>";
	print "<TR>";
	print "<TD>High Item Level: </TD>";
	print "<TD>$ilevel_high</TD>";
	print "</TR>";
	print "</TABLE>";
	print "<input type=\"submit\" value=\"Confirm\" />";
	print "<a href=\"bis.shtml\"><input type=\"button\" name=\"Cancel\" value=\"Cancel\" /></a>";
	print "</FORM>";
}
else
{
	print "<B>Choose an existing tier:</B>";
	print "<BR>";
	print tier_table("ACTIVE");
	print "</BR>";
	print "<B>Or,  create a new tier: </B>";
	print tier_table("CREATE");
}
print "</fieldset>";

$dbh->disconnect();
#print "</pre>";
