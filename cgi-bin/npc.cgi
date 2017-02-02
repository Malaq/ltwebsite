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

sub npc_table {
	$npc_id = shift;
	my $zone_query =
		$dbh->prepare("SELECT IT.ITEM_ID, " .
	"       IT.ITEM_NAME, " .
	"       NPC.NPC_NAME, " .
	"       IT.ITEM_LEVEL, " .
	"       BIS.BIS_FOR " .
	"FROM NPC, " .
	"     ITEM_SOURCES ITS, " .
	"     ITEM IT " .
	"     LEFT JOIN (select A.ITEM_ID, SUBSTRING_INDEX(GROUP_CONCAT(CONCAT(' <a href=\"bis_lists.shtml?BIS_LIST_ID=',A.BIS_LIST_ID,'\">[',A.NAME,']</A>')), ',', 15) AS BIS_FOR " .
	"                from ( " .
	"                  select NPC.NPC_NAME, IT.ITEM_NAME, IT.ITEM_LEVEL, IT.ITEM_ID, CHR.NAME, BL.BIS_LIST_ID " .
	"                  from NPC, ITEM_SOURCES ITS, BIS_ITEMS BI, BIS_LISTS BL, CLASSES CL, CLASS_SPEC CS, BIS_TIERS BT, ITEM IT, `CHARACTER` CHR " .
	"                  where NPC.NPC_ID = ITS.NPC_ID " .
	"                  and ITS.ITEM_ID = BI.ITEM_ID " .
	"                  and BI.BIS_LIST_ID = BL.BIS_LIST_ID " .
	"                  and BL.CLASS_ID = CL.CLASS_ID " .
	"                  and BL.SPEC_ID = CS.SPEC_ID " .
	"                  and BL.TIER_ID = BT.TIER_ID " .
	"                  and BI.ITEM_ID = IT.ITEM_ID " .
	"                  and CS.SPEC_ID = CHR.PRIMARY_SPEC " .
	" 		   and NOT EXISTS (select 'x' from ITEMS_LOOTED IL where IL.ITEM_ID = IT.ITEM_ID and IL.CHAR_ID = CHR.CHAR_ID) " .
	"                  and NPC.NPC_ID = ? " .
	"                  and BL.ACTIVE_FLAG = 'T' " .
	"                  and BI.ITEM_ID <> 0 " .
	"		   and CHR.RANK not in ('Friend','Alt','Officer Alt','P.U.G.','PvPer', '') " .
	"		   and CHR.DATE_REMOVED IS NULL " .
       "		   AND CHR.ACTIVE = 'Y' " .
	"                  UNION " .
	"                  select NPC.NPC_NAME, " .
	"                        IT.ITEM_NAME, " .
	"                        IT.ITEM_LEVEL, " .
	"                        IT.ITEM_ID, " .
	"                        CHR.NAME, " .
	"                        BL.BIS_LIST_ID " .
	"                  from NPC, ITEM_SOURCES ITS, BIS_ITEMS BI, BIS_LISTS BL, CLASSES CL, CLASS_SPEC CS, BIS_TIERS BT, ITEM IT, CURRENCY_FOR CF, `CHARACTER` CHR " .
	"                  where NPC.NPC_ID = ITS.NPC_ID " .
	"                  and ITS.ITEM_ID = CF.SOURCE_ITEM_ID " .
	"                  and CF.REWARD_ITEM_ID = BI.ITEM_ID " .
	"                  and BI.BIS_LIST_ID = BL.BIS_LIST_ID " .
	"                  and BL.CLASS_ID = CL.CLASS_ID " .
	"                  and BL.SPEC_ID = CS.SPEC_ID " .
	"                  and BL.TIER_ID = BT.TIER_ID " .
	"                  and CF.SOURCE_ITEM_ID = IT.ITEM_ID " .
	"                  and CS.SPEC_ID = CHR.PRIMARY_SPEC " .
	" 		   and NOT EXISTS (select 'x' from ITEMS_LOOTED IL where IL.ITEM_ID = IT.ITEM_ID and IL.CHAR_ID = CHR.CHAR_ID) " .
	"                  and NPC.NPC_ID = ? " .
	"                  and BL.ACTIVE_FLAG = 'T' " .
	"                  and BI.ITEM_ID <> 0 " .
	"		   and CHR.RANK not in ('Friend','Alt','Officer Alt','P.U.G.','PvPer', '') " .
	"		   and CHR.DATE_REMOVED IS NULL " .
        "		   AND CHR.ACTIVE = 'Y' " .
	"                  order by ITEM_LEVEL, ITEM_NAME " .
	"		   ) as A " .

	"                GROUP BY NPC_NAME, ITEM_NAME, ITEM_LEVEL) AS BIS " .
	"     ON IT.ITEM_ID = BIS.ITEM_ID " .
	"WHERE NPC.NPC_ID = ITS.NPC_ID " .
	"  AND ITS.ITEM_ID = IT.ITEM_ID " .
	"  and NPC.NPC_ID = ? " .
	"ORDER BY IT.ITEM_LEVEL, IT.ITEM_NAME;");

#New Query, still has kinks
#	"select CHR.NAME, CHR.RANK, A.TIER_NAME, A.ITEM_NAME " .
#	"FROM `CHARACTER` CHR " .
#	"LEFT JOIN (select BMV.NAME, BMV.CHAR_ID, BMV.RANK, BMV.TIER_NAME, GROUP_CONCAT(IFNULL(BMV.CURR_ITEM_NAME,BMV.ITEM_NAME)) as ITEM_NAME " .
#	"          from BIS_MASTER_V BMV " .
#	"          where BMV.HAS_IT IS NULL " .
#	"          and (BMV.NPC_ID = ? " .
#	"          OR BMV.CURR_NPC_ID = ? ) " .
#	"          group by BMV.TIER_NAME, BMV.NAME " .
#	"          order by BMV.TIER_NAME, BMV.NAME, BMV.ITEM_NAME) AS A " .
#	"on CHR.CHAR_ID = A.CHAR_ID " .
#	"where CHR.rank not in (SELECT RANK FROM NON_RAIDER_RANK) " .
#	"and CHR.ACTIVE = 'Y' " .
#	"and CHR.DATE_REMOVED IS NULL " .
#	"order by A.TIER_NAME, CHR.NAME;");

	

	$zone_query->bind_param(1, $npc_id);	
	$zone_query->bind_param(2, $npc_id);	
	$zone_query->bind_param(3, $npc_id);	
	$zone_query->execute() or die $dbh->errstr;
	
	$zone_table = "";
	$zone_table = "$zone_table<TABLE class=\"sortable normal\" id=\"token_table\">";
	#TABLE HEADER
	$zone_table = "$zone_table<THEAD>";
	$zone_table = "$zone_table<TR>";
	$zone_table = "$zone_table<TH><U><B>Item Name</B></U></TH>";
	$zone_table = "$zone_table<TH><U><B>Item Level</B></U></TH>";
#	$zone_table = "$zone_table<TH><U><B>Tier Name</B></U></TH>";
#	$zone_table = "$zone_table<TH><U><B>Items Needed</B></U></TH>";
	$zone_table = "$zone_table<TH><U><B>NPC Name</B></U></TH>";
	$zone_table = "$zone_table<TH><U><B>BIS For... (Limited to 15 people)</B></U></TH>";
	$zone_table = "$zone_table</TR>";
	$zone_table = "$zone_table</THEAD>";
	#END HEADER
	#
	#ROWS

	while (my $row = $zone_query->fetchrow_hashref()) {
		#$zone_table = "$zone_table<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\" onclick=\"location.href='item.shtml?data=$row->{ITEM_NAME}'\">";
		$zone_table = "$zone_table<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\">";
		$zone_table = "$zone_table<TD><a href=\"http://www.wowhead.com/?item=$row->{ITEM_ID}\" TARGET=\"_blank\">[$row->{ITEM_NAME}]</a></TD>";
		$zone_table = "$zone_table<TD>$row->{ITEM_LEVEL}</TD>";
		$zone_table = "$zone_table<TD>$row->{NPC_NAME}</TD>";
		$zone_table = "$zone_table<TD>$row->{BIS_FOR}</TD>";
#		$zone_table = "$zone_table<TD>$row->{NAME}</TD>";
#		$zone_table = "$zone_table<TD>$row->{RANK}</TD>";
#		$zone_table = "$zone_table<TD>$row->{TIER_NAME}</TD>";
#		$zone_table = "$zone_table<TD>$row->{ITEM_NAME}</TD>";
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
my $npc_id = param('NPC_ID');
#my $class_id = param('CLASS_ID');
#my $spec_id = param('SPEC_ID');
#my $bis_list_id = param('BIS_LIST_ID');
#my $confirm_new_tier = param('CONFIRM_NEW_TIER');
print "<script src=\"http://www.wowhead.com/widgets/power.js\"></script>\n";
print "<fieldset>";
print "<legend>Loot Table:</A></legend>";
print npc_table($npc_id);
print "</fieldset>";

$dbh->disconnect();
#print "</pre>";
