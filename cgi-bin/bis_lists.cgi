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
			$tier_table = "$tier_table<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\" onclick=\"location.href='bis_lists.shtml?TIER_ID=$row->{TIER_ID}'\">";
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
	$class_table = "$class_table</TR>";
	$class_table = "$class_table</THEAD>";
	while (my $row = $SQL->fetchrow_hashref()) {
		if ($row->{LISTS} eq 0)
		{
			$class_table = "$class_table<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='alert'\" class=\"alert\" onclick=\"location.href='bis_lists.shtml?TIER_ID=$v_tier&CLASS_ID=$row->{CLASS_ID}&SPEC_ID=$row->{SPEC_ID}'\" >";
		}
		else
		{
			$class_table = "$class_table<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\" onclick=\"location.href='bis_lists.shtml?TIER_ID=$v_tier&CLASS_ID=$row->{CLASS_ID}&SPEC_ID=$row->{SPEC_ID}'\" >";
		}
		$class_table = "$class_table<TD sorttable_customkey=\"$row->{CLASS_ID}\"><img src=\"images/$row->{ICON_FILENAME}\" align=\"center\" title=\"$row->{CLASS_NAME}\"></TD>";
		$class_table = "$class_table<TD>$row->{CLASS_NAME}</TD>";
		$class_table = "$class_table<TD>$row->{SPEC_NAME}</TD>";
		$class_table = "$class_table<TD sorttable_customkey=\"$row->{SPEC_ROLE}$row->{CLASS_ID}\">$row->{SPEC_ROLE}</TD>";
		$class_table = "$class_table<TD align=\"CENTER\"><a href=\"bis_lists.shtml?TIER_ID=$v_tier&CLASS_ID=$row->{CLASS_ID}&SPEC_ID=$row->{SPEC_ID}\">$row->{LISTS}</A></TD>";
		$class_table = "$class_table</TR>";
	}
	$class_table = "$class_table</TABLE>";

	return $class_table;
}

sub displayLists {
	my $tier_id = shift;
	my $class_id = shift;
	my $spec_id = shift;

	my $SQL = 
	$dbh->prepare("SELECT BL.BIS_LIST_ID,  " .
			"       BL.DESCRIPTION, " .
			"       BL.CLASS_ID, " .
			"	 CL.CLASS_NAME, " .
			"	 BL.SPEC_ID, " .
			"	 CS.SPEC_NAME, " .
			"	 BL.TIER_ID, " .
			"	 BT.TIER_DESC " .
			"FROM BIS_LISTS BL, " .
			"     CLASSES CL, " .
			"		 CLASS_SPEC CS, " .
			"		 BIS_TIERS BT " .
			"WHERE BL.CLASS_ID = CL.CLASS_ID " .
			"AND BL.SPEC_ID = CS.SPEC_ID " .
			"AND BL.TIER_ID = BT.TIER_ID " .
			"AND BL.ACTIVE_FLAG = 'T' " .
			"AND BL.TIER_ID = ? " .
			"AND BL.CLASS_ID = ? " .
			"AND BL.SPEC_ID = ? ;");	
	$SQL->bind_param(1, $tier_id);
	$SQL->bind_param(2, $class_id);
	$SQL->bind_param(3, $spec_id);
	$SQL->execute() or die $dbh->errstr;

	$table = "$table<TABLE class=\"sortable normal\" id=\"class_table\">";
	#TABLE HEADER
	$table = "$table<THEAD>";
	$table = "$table<TR>";
	$table = "$table<TH><U><B>Class</B></U></TH>";
	$table = "$table<TH><U><B>Spec</B></U></TH>";
	$table = "$table<TH><U><B>Description</B></U></TH>";
	$table = "$table</TR>";
	$table = "$table</THEAD>";
	while (my $row = $SQL->fetchrow_hashref()) {
		$table = "$table<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\" onclick=\"location.href='bis_lists.shtml?BIS_LIST_ID=$row->{BIS_LIST_ID}'\">";
		$table = "$table<TD>$row->{CLASS_NAME}</TD>";
		$table = "$table<TD>$row->{SPEC_NAME}</TD>";
		$table = "$table<TD>$row->{DESCRIPTION}</TD>";
		$table = "$table</TR>";
	}
	$table = "$table</TABLE>";

	return $table;
}


sub bis_list {
	my $bis_list_id = shift;
	my $table = "";

	if ($bis_list_id ne "") 
	{
		$SQL = 
		$dbh->prepare("SELECT BL.DESCRIPTION, " .
				"	     CL.CLASS_NAME, " .
				"       CS.SPEC_NAME, " .
				"       BT.TIER_NAME, " .
				"	     BT.TIER_DESC, " .
				"       BT.TIER_ILEVEL_LOW, " .
				"       BT.TIER_ILEVEL_HIGH " .
				"FROM BIS_LISTS BL, " .
				"     BIS_TIERS BT, " .
				"     CLASSES CL, " .
				"     CLASS_SPEC CS " .
				"WHERE BL.TIER_ID = BT.TIER_ID " .
				"AND BL.CLASS_ID = CL.CLASS_ID " .
				"AND BL.SPEC_ID = CS.SPEC_ID " .
				"AND BL.BIS_LIST_ID = ? ;");


		$SQL->bind_param(1,$bis_list_id);
		$SQL->execute() or die $dbh->errstr;
		my $row = $SQL->fetchrow_hashref();
	
		$table = "${table}<BR><B>$row->{SPEC_NAME} $row->{CLASS_NAME}</B><BR>$row->{TIER_NAME} - $row->{TIER_DESC}<BR>Item level range: <B>$row->{TIER_ILEVEL_LOW} - $row->{TIER_ILEVEL_HIGH}</B><BR><BR>";
		#$table = "$table<form name=\"details\" method=\"post\" action=\"cgi-bin/bisSave.cgi\" ONSUBMIT=\"return checkRequired(this)\" >";
		$table = "$table";
		$table = "${table}<B>BIS List Name:</B> \"$row->{DESCRIPTION}\"";
#		$SQL = 
#		$dbh->prepare("select BL.BIS_LIST_ID, BS.SLOT_SEQUENCE, IFNULL(IT.ITEM_NAME,BI.ITEM_NAME_OVERRIDE) ITEM_NAME, BS.SLOT_NAME, IT.ITEM_EQUIPLOC, BI.ITEM_ID, BL.DESCRIPTION " .
#			"from BIS_LISTS BL, " .
#			"     BIS_SLOTS BS, " .
#			"     BIS_ITEMS BI " .
#			"     LEFT JOIN ITEM AS IT " .
#			"     ON BI.ITEM_ID = IT.ITEM_ID " .
#			"WHERE BL.BIS_LIST_ID = BI.BIS_LIST_ID " .
#			"AND BI.SLOT_ID = BS.SLOT_ID " .
#			"AND BS.DISPLAY = 'T' " .
#			"AND BI.ITEM_ID <> 0 " .
#			"AND BL.BIS_LIST_ID = ? " .
#			"ORDER BY BL.BIS_LIST_ID, BS.SLOT_SEQUENCE;");

		$SQL = 
		$dbh->prepare("select BL.BIS_LIST_ID, BS.SLOT_SEQUENCE, IFNULL(IT.ITEM_NAME,BI.ITEM_NAME_OVERRIDE) ITEM_NAME, BS.SLOT_NAME, IT.ITEM_EQUIPLOC, BI.ITEM_ID, BL.DESCRIPTION, SUBSTRING(GROUP_CONCAT(SRC.NPC_NAME),1,100) AS SOURCES " .
		"from BIS_LISTS BL, " .
		"     BIS_SLOTS BS, " .
		"     BIS_ITEMS BI " .
		"     LEFT JOIN ITEM AS IT " .
		"     ON BI.ITEM_ID = IT.ITEM_ID " .
		"     LEFT JOIN (SELECT ITS.ITEM_ID, NPC.NPC_NAME " .
		"                FROM ITEM_SOURCES ITS, NPC " .
		"                WHERE ITS.NPC_ID = NPC.NPC_ID " .
		#" 		 and ITS.SOURCE_TYPE <> 'SOLD' " .
		"                UNION " .
		"                SELECT cf.REWARD_ITEM_ID, npc2.NPC_NAME " .
		#"                SELECT cf.SOURCE_ITEM_ID, npc2.NPC_NAME " .
		"                FROM CURRENCY_FOR cf, ITEM_SOURCES its2, NPC npc2 " .
		"                where cf.SOURCE_ITEM_ID = its2.ITEM_ID " .
		#"                where cf.REWARD_ITEM_ID = its2.ITEM_ID " .
		"                  and its2.NPC_ID = npc2.NPC_ID) AS SRC " .
		"      ON BI.ITEM_ID = SRC.ITEM_ID " .
		"WHERE BL.BIS_LIST_ID = BI.BIS_LIST_ID " .
		"AND BI.SLOT_ID = BS.SLOT_ID " .
		"AND BS.DISPLAY = 'T' " .
		#"AND BI.ITEM_ID <> 0 " .
		"AND BL.BIS_LIST_ID = ? " .
		"group by BL.BIS_LIST_ID, BS.SLOT_SEQUENCE, ITEM_NAME, BS.SLOT_NAME, IT.ITEM_EQUIPLOC, BI.ITEM_ID, BL.DESCRIPTION " .
		"ORDER BY BL.BIS_LIST_ID, BS.SLOT_SEQUENCE;");

			

		$SQL->bind_param(1,$bis_list_id);

		$SQL->execute() or die $dbh->errstr;

		$table = "$table<BR><BR>";
		$table = "$table<script src=\"http://www.wowhead.com/widgets/power.js\"></script>\n";
		$table = "$table<TABLE class=\"sortable normal\" id=\"bis_table\">";
		#TABLE HEADER
		$table = "$table<THEAD>";
		$table = "$table<TR>";
		$table = "$table<TH><U><B>Slot</B></U></TH>";
		$table = "$table<TH><U><B>Item Link</B></U></TH>";
		$table = "$table<TH><U><B>Sources (limited to 100 characters)</B></U></TH>";
		$table = "$table</TR>";
		$table = "$table</THEAD>";
		while (my $row = $SQL->fetchrow_hashref()) {
			if ($row->{ITEM_ID} ne 0)
			{
				$table = "$table<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\" >";
				$table = "$table<input type=\"hidden\" name=\"STAGE_ROW_ID\" value=\"$row->{STAGING_ID}\" />";
				$table = "$table<input type=\"hidden\" name=\"STAGE_SET_ID\" value=\"$row->{STAGE_SET_ID}\" />";
				$table = "$table<TD sorttable_customkey=\"$row->{SLOT_SEQUENCE}\">$row->{SLOT_NAME}</TD>";
				$table = "$table<TD><a href=\"http://www.wowhead.com/?item=$row->{ITEM_ID}\">[$row->{ITEM_NAME}]</a></TD>";
				$table = "$table<TD>[$row->{SOURCES}]</TD>";
				$table = "$table</TR>";
			}
			else
			{
				$table = "$table<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\" >";
				$table = "$table<input type=\"hidden\" name=\"STAGE_ROW_ID\" value=\"$row->{STAGING_ID}\" />";
				$table = "$table<input type=\"hidden\" name=\"STAGE_SET_ID\" value=\"$row->{STAGE_SET_ID}\" />";
				$table = "$table<TD sorttable_customkey=\"$row->{SLOT_SEQUENCE}\">$row->{SLOT_NAME}</TD>";
				$table = "$table<TD></TD>";
				$table = "$table<TD></TD>";
				$table = "$table</TR>";			
			}
		}
		$table = "$table<TFOOT><TR><TD>";
		$table = "$table<form name=\"details\" action=\"cgi-bin/bisSave.cgi\">";
		$table = "$table<input type=\"hidden\" name=\"STAGE_SET_ID\" value=\"$stage_set_id\" />";
		$table = "$table</form></TD></TR></TFOOT>";
		$table = "$table</TABLE>";
		$table = "$table</FORM>";
	}

	return $table;
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
#populated if going to the class screen
my $tier_id = param('TIER_ID');
my $class_id = param('CLASS_ID');
my $spec_id = param('SPEC_ID');
my $bis_list_id = param('BIS_LIST_ID');
my $confirm_new_tier = param('CONFIRM_NEW_TIER');

print "<fieldset>";
print "<legend><A HREF=\"bis_lists.shtml\">Tier List:</A></legend>";
if ($bis_list_id ne "")
{
	#print "<B>Please view your BIS list below:</B>";
	#print "<BR>";
	print bis_list($bis_list_id)
}
elsif (($class_id ne "") && ($tier_id ne "") && ($spec_id ne ""))
{
	tier_title($tier_id);
	print "<B>Please choose your BIS list below:</B><BR>";
	print "<BR>";
	print displayLists($tier_id, $class_id, $spec_id);
}
elsif ($tier_id ne "")
{
	tier_title($tier_id);
	print "<B>Choose a class/spec combination:</B><BR>";
	print "**If you do not see any lists for your class/spec, contact your role leader to update it.";
	print "<BR>";
	print class_table($tier_id);
}
else
{
	print "<B>Choose an existing tier:</B>";
	print "<BR>";
	print tier_table("ACTIVE");
}
print "</fieldset>";

$dbh->disconnect();
#print "</pre>";
