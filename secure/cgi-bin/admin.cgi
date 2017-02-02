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

#Process to build token tables.
my $token_table = "";
sub token_table {
	my $type = shift;
	my $token_statement = "";

	if ($type eq "broken") {
	$token_statement = 
		$dbh->prepare("SELECT A.ITEM_ID, A.ITEM_NAME, A.RARITY, A.ITEM_LEVEL, A.ITEM_TYPE, A.ITEM_SUBTYPE, A.ITEM_EQUIPLOC, A.REWARD_ILEVEL, A.IS_TOKEN " .
				"FROM ( " .
				"	SELECT ITEM_ID, ITEM_NAME, RARITY, ITEM_LEVEL, ITEM_TYPE, ITEM_SUBTYPE, ITEM_EQUIPLOC, REWARD_ILEVEL, IFNULL(IS_TOKEN,'Unselected') IS_TOKEN  " .
				"	FROM ITEM  " .
				"	WHERE ITEM_TYPE = 'Miscellaneous'  " .
				"	AND ITEM_SUBTYPE = 'Junk'  " .
				"	AND RARITY = 'Epic'  " .
				"	UNION " .
				"	SELECT ITEM_ID, ITEM_NAME, RARITY, ITEM_LEVEL, ITEM_TYPE, ITEM_SUBTYPE, ITEM_EQUIPLOC, REWARD_ILEVEL, IFNULL(IS_TOKEN,'UNSELECTED') IS_TOKEN  " .
				"	FROM ITEM " .
				"	WHERE ITEM_NAME LIKE '%Vanquisher' " .
				"	OR ITEM_NAME LIKE '%Conqueror' " .
				"	OR ITEM_NAME LIKE '%Protector' ) A " .
				"WHERE IFNULL(A.REWARD_ILEVEL,0) = 0 " .
				"AND A.IS_TOKEN <> 'False' " .
				"ORDER BY A.ITEM_ID DESC;");	
	} elsif ($type eq "all") {
	$token_statement = 
		$dbh->prepare("SELECT ITEM_ID, ITEM_NAME, RARITY, ITEM_LEVEL, ITEM_TYPE, ITEM_SUBTYPE, ITEM_EQUIPLOC, REWARD_ILEVEL, IFNULL(IS_TOKEN,'Unselected') IS_TOKEN  " .
				"FROM ITEM  " .
				"WHERE ITEM_TYPE = 'Miscellaneous'  " .
				"AND ITEM_SUBTYPE = 'Junk'  " .
				"AND RARITY = 'Epic'  " .
				"UNION " .
				"SELECT ITEM_ID, ITEM_NAME, RARITY, ITEM_LEVEL, ITEM_TYPE, ITEM_SUBTYPE, ITEM_EQUIPLOC, REWARD_ILEVEL, IFNULL(IS_TOKEN,'UNSELECTED') IS_TOKEN  " .
				"FROM ITEM " .
				"WHERE ITEM_NAME LIKE '%Vanquisher' " .
				"OR ITEM_NAME LIKE '%Conqueror' " .
				"OR ITEM_NAME LIKE '%Protector' " .
				"ORDER BY ITEM_ID DESC;");
	} else {
		die "bad token query request, this should never happen";
	}

$token_statement->execute() or die $dbh->errstr;

$token_table = "";
#$token_table = "$token_table<script src=\"../../sorttable.js\"></script>\n";
$token_table = "$token_table<script src=\"http://www.wowhead.com/widgets/power.js\"></script>\n";
$token_table = "$token_table<TABLE class=\"sortable normal\" id=\"token_table\">";
$token_table = "$token_table<THEAD>";
$token_table = "$token_table<TR>";
$token_table = "$token_table<TH WIDTH=200><U><B>Item Name</B></U></TH>";
$token_table = "$token_table<TH><U><B>Rarity</B></U></TH>";
$token_table = "$token_table<TH><U><B>I-Level</B></U></TH>";
$token_table = "$token_table<TH><U><B>Type</B></U></TH>";
$token_table = "$token_table<TH><U><B>Sub-Type</B></U></TH>";
$token_table = "$token_table<TH><U><B>Equip-Loc</B></U></TH>";
$token_table = "$token_table<TH><U><B>Reward Ilevel</B></U></TH>";
$token_table = "$token_table<TH><U><B>Is Token?</B></U></TH>";
$token_table = "$token_table<TH><U><B>Commit</B></U></TH>";
$token_table = "$token_table</TR>\n";
$token_table = "$token_table</THEAD>";
while (my $row = $token_statement->fetchrow_hashref()) {
	my $url = URLEncode($row->{ITEM_NAME});
	$token_table = "$token_table<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\">";
	$token_table = "$token_table<form action=\"cgi-bin/rewardilevel.cgi\"><input type=\"hidden\" name=\"ITEM_ID\" value=\"$row->{ITEM_ID}\"/>";
	$token_table = "$token_table<TD><A HREF=\"http://www.wowhead.com/?item=$row->{ITEM_ID}\" TARGET=\"_blank\">$row->{ITEM_NAME}</A></TD>";
	$token_table = "$token_table<TD>$row->{RARITY}</TD>";
	$token_table = "$token_table<TD>$row->{ITEM_LEVEL}</TD>";
	$token_table = "$token_table<TD>$row->{ITEM_TYPE}</TD>";
	$token_table = "$token_table<TD>$row->{ITEM_SUBTYPE}</TD>";
	$token_table = "$token_table<TD>$row->{ITEM_EQUIPLOC}</TD>";
	$token_table = "$token_table<TD><input type=\"text\" name=\"REWARD_ILEVEL\" style=\"font-size:10px;font-family:Arial\" value=\"$row->{REWARD_ILEVEL}\" /></TD>";
	$token_table = "$token_table<TD>";
	$token_table = "$token_table<select name=\"IS_TOKEN\" style=\"font-size:10px;font-family:Arial\">";
	$token_table = "$token_table<option value=\"$row->{IS_TOKEN}\">$row->{IS_TOKEN}</option>";
	$token_table = "$token_table<option value=\"True\">True</option>";
	$token_table = "$token_table<option value=\"False\">False</option>";
	$token_table = "$token_table<option value=\"\">null</option>";
	$token_table = "$token_table</select>";
	$token_table = "$token_table</TD>";
	$token_table = "$token_table<TD><input type=\"submit\" value=\"Save\" /></TD>";
	$token_table = "$token_table</form></TR>\n";
	$token_table = "$token_table\n"
}
$token_table = "$token_table</TABLE>";
}

#Process to build guild settings table.
my $settings_table = "";
sub settings_table {
	my $type = shift;
	my $settings_statement = "";

	$settings_statement = 
		$dbh->prepare("SELECT CONFIG_ID, SCRIPT, LOOKUP_NAME, LOOKUP_VALUE, LOOKUP_VALUE_2 " .
				"FROM LT_CONFIG_LOOKUPS;");

$settings_statement->execute() or die $dbh->errstr;

$settings_table = "";
#$token_table = "$token_table<script src=\"../../sorttable.js\"></script>\n";
$settings_table = "$settings_table<script src=\"http://www.wowhead.com/widgets/power.js\"></script>\n";
$settings_table = "$settings_table<TABLE class=\"sortable normal\" id=\"settings_table\">";
$settings_table = "$settings_table<THEAD>";
$settings_table = "$settings_table<TR>";
$settings_table = "$settings_table<TH><U><B>Script</B></U></TH>";
$settings_table = "$settings_table<TH><U><B>Setting</B></U></TH>";
$settings_table = "$settings_table<TH><U><B>Value 1</B></U></TH>";
$settings_table = "$settings_table<TH><U><B>Value 2</B></U></TH>";
$settings_table = "$settings_table<TH><U><B>Commit</B></U></TH>";
$settings_table = "$settings_table</TR>\n";
$settings_table = "$settings_table</THEAD>";
while (my $row = $settings_statement->fetchrow_hashref()) {
	$settings_table = "$settings_table<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\">";
	$settings_table = "$settings_table<form action=\"cgi-bin/guildsetting.cgi\"><input type=\"hidden\" name=\"CONFIG_ID\" value=\"$row->{CONFIG_ID}\"/>";
	$settings_table = "$settings_table<TD>$row->{SCRIPT}</TD>";
	$settings_table = "$settings_table<TD>$row->{LOOKUP_NAME}</TD>";
	$settings_table = "$settings_table<TD><input type=\"text\" name=\"VALUE1\" style=\"font-size:10px;font-family:Arial\" value=\"$row->{LOOKUP_VALUE}\" /></TD>";
	$settings_table = "$settings_table<TD><input type=\"text\" name=\"VALUE2\" style=\"font-size:10px;font-family:Arial\" value=\"$row->{LOOKUP_VALUE_2}\" /></TD>";
	$settings_table = "$settings_table<TD><input type=\"submit\" value=\"Save\" /></TD>";
	$settings_table = "$settings_table</form></TR>\n";
	$settings_table = "$settings_table\n"
}
$settings_table = "$settings_table</TABLE>";
}

my $logging_table = "";
sub logging_table {
	my $type = shift;
	my $logging_statement = '';

	$logging_statement = 
		$dbh->prepare("select AUDIT_TYPE, USERNAME, SCRIPT, TIMESTAMP, DETAILS " .
				"from LT_AUDIT " .
				"order by AUDIT_ID DESC " .
				"limit 40;");

$logging_statement->execute() or die $dbh->errstr;

$logging_table = "";
#$token_table = "$token_table<script src=\"../../sorttable.js\"></script>\n";
$logging_table = "$logging_table<script src=\"http://www.wowhead.com/widgets/power.js\"></script>\n";
$logging_table = "$logging_table<TABLE class=\"sortable normal\" id=\"logging_table\">";
$logging_table = "$logging_table<THEAD>";
$logging_table = "$logging_table<TR>";
$logging_table = "$logging_table<TH><U><B>Audit Type</B></U></TH>";
$logging_table = "$logging_table<TH><U><B>Username</B></U></TH>";
$logging_table = "$logging_table<TH><U><B>Script</B></U></TH>";
$logging_table = "$logging_table<TH><U><B>Timestamp</B></U></TH>";
$logging_table = "$logging_table<TH><U><B>Details</B></U></TH>";
$logging_table = "$logging_table</TR>\n";
$logging_table = "$logging_table</THEAD>";
while (my $row = $logging_statement->fetchrow_hashref()) {
	$logging_table = "$logging_table<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\">";
	$logging_table = "$logging_table<TD>$row->{AUDIT_TYPE}</TD>";
	$logging_table = "$logging_table<TD>$row->{USERNAME}</TD>";
	$logging_table = "$logging_table<TD>$row->{SCRIPT}</TD>";
	$logging_table = "$logging_table<TD>$row->{TIMESTAMP}</TD>";
	$logging_table = "$logging_table<TD>$row->{DETAILS}</TD>";
	$logging_table = "$logging_table</TR>\n";
	$logging_table = "$logging_table\n"
}
$logging_table = "$logging_table</TABLE>";
}



#Tabs for display.
#print "USER: $ENV{'REMOTE_USER'}";
#print "<script src=\"../sorttable.js\"></script>\n";
print "<div class=\"tabber\">";
print "   <div class=\"tabbertab\">";
print "	  <h2>Import Log</h2>";
print "	  <p class=\"normal\">";
print "        <B>Paste exported legiontracker log here and click submit.</B>";
print "			<form method=\"POST\" action=\"cgi-bin/parse.cgi\">";
print "				<textarea cols=100 rows=10 name=\"data\" style=\"font-size:11px;font-family:Arial\" id=\"data\"></textarea>";
print "				<input type=\"submit\" value=\"Submit\"></input>";
print "			</form>";
print "   </p>";
print "   </div>";
print "  <div class=\"tabbertab\">";
print "	  <h2>Tokens</h2>";
print "	  <p>The tables below displays items that potentially need to have a reward item level set. <BR/>";
print "   This is usually for items with a quest reward like tier tokens. <BR/>";
print "   The reward item level is used to better represent what item level the player received.<BR/>";
print "   If you feel an item is on this list that shouldn't be, simply select \"FALSE\" in the dropdown menu and click save.<BR/>";
print "   </p>";
#Subtabs for tokens
print "   <div class=\"tabber\" id=\"tab1-1\">";
print "      <div class=\"tabbertab\">";
print "        <h3>Broken Tokens</h3>";
token_table("broken");
print "        <P>$token_table</p>";
print "      </div>";
print "      <div class=\"tabbertab\">";
print "        <h3>All Potential Reward Items</h3>";
token_table("all");
print "        <P>$token_table</p>";
print "      </div>";
print "    </div>";
print "   </div>";
#print "     <div class=\"tabbertab\">";
#print "	    <h2>Character Specs</h2>";
#char_spec_table();
#print "	    <p>$char_spec_table</p>";
#print "     </div>";
#
#Guild settings
print "     <div class=\"tabbertab\">";
print "	    <h2>Guild Settings</h2>";
settings_table();
print "	    <p>$settings_table</p>";
print "     </div>";
#Logging Table
print "     <div class=\"tabbertab\">";
print "	    <h2>Audit Log</h2>";
logging_table();
print "	    <p>Last 40 lines: <BR/>$logging_table</p>";
print "     </div>";
print "</div>";

$dbh->disconnect();
#print "</pre>";
