#!/usr/bin/perlml

# The libraries we're using
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use DBI;

sub URLEncode {
my $theURL = $_[0];
$theURL =~ s/([\W])/"%" . uc(sprintf("%2.2x",ord($1)))/eg;
return $theURL;
}

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


my $sched = "Error";

# Database handle
my $dbh = DBI->connect("dbi:mysql:database=$database;host=$hostname;port=$dbport", $username, $password) or print $DBI::errstr;

my $raid_id = param('data');

print "<font size=\"6\" face=\"Monotype Corsiva\"><B>$char_name</B></font>";

#print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\" \"http://www.w3.org/TR/html4/strict.dtd\">\n";
	#print "<HTML>\n";

# Raid Summary
my $raid_query =
	$dbh->prepare(
		"select rc.raid_id, " .
		"rc.DATE, " .
		"rc.SCHEDULED, " .
		"rc.ATTENDANCE_COUNT, " .
		"SEC_TO_TIME((length(max(ra.ATTENDANCE))-1)*600) tic " .
		"from RAID_CALENDAR rc, RAID_ATTENDANCE ra " .
		"where rc.raid_id = ra.raid_id " .
		"and ATTENDANCE Regexp '[[:digit:]]+' <> 0 " .
		"and rc.raid_id = ? " .
		"group by rc.raid_id;");

$raid_query->bind_param(1, $raid_id);
$raid_query->execute() or die $dbh->errstr;
my $row = $raid_query->fetchrow_hashref();
print "<div id=\'rdraidsummary\'>";
print "<fieldset style=\"width: 200px;\">";
print "<legend>Raid Summary:</legend>";
#print "Raid ID: <B>$raid_id</B><br>";
print "Date: <B>$row->{DATE}</B><br>";
if ($row->{SCHEDULED} == "1") {
	$sched = "True";
} else {
	$sched = "False";
}
print "Scheduled: <B>$sched</B><br>";
print "Raiders Available: <B>$row->{ATTENDANCE_COUNT}</B><br>";
print "Raid Duration: <B>$row->{tic}</B><br>";
print "</fieldset>";
print "</div>";
$raid_query->finish();

#print "Epics Dropped: <B>$row->{TOTAL_LOOT}</B><br>";
my $raid_query =
	$dbh->prepare(
		"select rc.raid_id, " .
		"IFNULL(sum(if(spec<>'Unassigned', 1, 0)),0) ALN, " .
		"IFNULL(sum(if(spec='Main', 1, 0)),0) MLN, " .
		"IFNULL(sum(if(spec='Alt', 1, 0)),0) TLN, " .
		"IFNULL(sum(if(spec='Off', 1, 0)),0) OLN, " .
		"IFNULL(sum(if(spec='DE''d', 1, 0)),0) DLN " .
		"from RAID_CALENDAR rc, ITEMS_LOOTED il " .
		"where rc.raid_id = il.raid_id " .
		"and rc.raid_id = ? " .
		"group by rc.raid_id;");

$raid_query->bind_param(1, $raid_id);
$raid_query->execute() or die $dbh->errstr;
my $row = $raid_query->fetchrow_hashref();

print "<div id=\'rdepicsdropped\'>";
print "<fieldset style=\"width: 200px;\">";
print "<legend>Epics Dropped: <B>$row->{ALN}</B></legend>";
print "Main Spec: <B>$row->{MLN}</B><br>";
print "Alt Spec: <B>$row->{TLN}</B><br>";
print "Off Spec: <B>$row->{OLN}</B><br>";
print "Disenchanted: <B>$row->{DLN}</B><br>";
print "</fieldset>";
print "</div>";
#print "<br>";

$raid_query->finish();

my $next_prev_query = 
#$dbh->prepare("select next_raid.raid_id as next_raid, next_raid.date as next_raid_date, prev_raid.raid_id as prev_raid, prev_raid.date as prev_raid_date " .
#	"from " .
$dbh->prepare("select (select raid_id " .
	" from RAID_CALENDAR rc " .
	" where date > (select date from RAID_CALENDAR rc1 where raid_id = ? ) " .
	" and scheduled = 1 " .
	" order by DATE asc " .
	" limit 1) next_raid, " .
	"(select raid_id " .
	" from RAID_CALENDAR rc " .
	" where date < (select date from RAID_CALENDAR rc1 where raid_id = ? ) " .
	" and scheduled = 1 " .
	" order by DATE desc " .
	" limit 1) prev_raid;"); 

$next_prev_query->bind_param(1, $raid_id);
$next_prev_query->bind_param(2, $raid_id);
$next_prev_query->execute() or die $dbh->errstr;
my $row = $next_prev_query->fetchrow_hashref();

my $next_raid = $row->{next_raid};
my $prev_raid = $row->{prev_raid};
#my $next_raid_date = $row->{next_raid_date};
#my $prev_raid_date = $row->{prev_raid_date};

if ($prev_raid == "")
{
	#print "<a href=\"raid.shtml?data=$prev_raid\">";
	print "<img src=\"images/stop.png\" alt=\"No previous raids\" />";
	#print "</a>";
}
else
{
	print "<a href=\"raiddetail.shtml?data=$prev_raid\">";
	print "<img src=\"images/prevraid.png\" />";
	print "</a>";
}
if ($next_raid == "")
{
	#print "<a href=\"raid.shtml?data=$prev_raid\">";
	print "<img src=\"images/stop.png\" alt=\"No next raids\" />";
	#print "</a>";
}
else
{
	print "<a href=\"raiddetail.shtml?data=$next_raid\">";
	print "<img src=\"images/nextraid.png\" />";
	print "</a>";
}
#Attendees
#print "<BR CLEAR=all>";
print "<div id=\'rddetails\'>";
print "<fieldset>";
print "<legend>Attendance Details:</legend>";
#print "<B><font size=5>Attendees</font></B><br>";
my $attendance_stmt =
	$dbh->prepare("SELECT chr.NAME, chr.CLASS, ra.ATTENDANCE, " .
			"concat( floor( length(replace(ATTENDANCE,'0',''))*100 / length(ATTENDANCE)) ,'%') PERCENT " .
			"FROM `CHARACTER` chr, `RAID_ATTENDANCE` ra " .
			"WHERE ra.CHAR_ID = chr.CHAR_ID " .
			"AND ra.RAID_ID = ? " .
			#"and chr.rank not in ('Alt','Officer Alt') " .
			"and chr.active = 'Y' " .
			"and ra.ATTENDANCE Regexp '[[:digit:]]+' <> 0 " .
			#"AND ra.CHAR_ID in (select ra1.CHAR_ID from RAID_ATTENDANCE ra1 where ra1.RAID_ID = ? AND INSTR(ra1.ATTENDANCE, '1') > 0 " .
			#"UNION select ra2.CHAR_ID from RAID_ATTENDANCE ra2 where ra2.RAID_ID = ? AND INSTR(ra2.ATTENDANCE, '0') > 0) " .
			"ORDER BY chr.NAME;");

$attendance_stmt->bind_param(1, $raid_id);
$attendance_stmt->bind_param(2, $raid_id);
$attendance_stmt->bind_param(3, $raid_id);
$attendance_stmt->execute() or die $dbh->errstr;
print "<script src=\"sorttable.js\"></script>\n";
print "<TABLE class=\"sortable normal\" ALIGN=LEFT>";
print "<THEAD>";
print "<TR>";
print "<TH><U><B>Name</B></U></TH>";
print "<TH><U><B>Class</B></U></TH>";
print "<TH><U><B>Pct</B></U></TH>";
print "<TH><U><B>Attendance</B>(10 min increments)</U></TH>";
print "</TR>";
print "</THEAD>\n";
print "<TBODY>";
while (my $row = $attendance_stmt->fetchrow_hashref()) {
	my $attn = $row->{ATTENDANCE};
	$attn =~ s|0|~|g;
	#$attn =~ s|1|<div style='width:10px;height:10px;background-color:green;display:inline-block'></div>|g;
	#$attn =~ s|~|<div style='width:10px;height:10px;background-color:red;display:inline-block'></div>|g;
	#$attn =~ s|1|<td style='background-color:green;'></td>|g;
	#$attn =~ s|~|<td style='background-color:red;'></td>|g;
	$attn =~ s|1|<img src=\"images/greenbox.JPG\" TITLE=\"Online - In Raid\">|g;
	$attn =~ s|2|<img src=\"images/yellowbox.JPG\" TITLE=\"Online - Sitting\">|g;
	$attn =~ s|~|<img src=\"images/redbox.JPG\" TITLE=\"Offline\">|g;
	print "<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\" onclick=\"location.href='char.shtml?data=$row->{NAME}'\">";
	print "<td><A HREF=\"char.shtml?data=$row->{NAME}\"><B>$row->{NAME}</B></A></td>";
	print "<td>$row->{CLASS}</td>";
	print "<td>$row->{PERCENT}</td>";
	print "<td>$attn</td> ";
	print "</tr>";
	}
print "</TBODY>";
print "</TABLE>";
print "</fieldset>";
#print "</div>";
#print "</HTML>";
$attendance_stmt->finish();

# Loot table
#print "<B><font size=5>Loot</font></B><br>";
#print "<div id=\'rdlootdetails\'>";
print "<fieldset>";
print "<legend>Loot Details:</legend>";
my $loot_statement =
	$dbh->prepare("SELECT chr.NAME, it.ITEM_ID, if(il.ITEM_ID = 0, CURRENT_ITEM_NAME, it.ITEM_NAME) as ITEM_NAME, IFNULL(REWARD_ILEVEL,ITEM_LEVEL) ITEM_LEVEL, DATE_FORMAT(il.TIMESTAMP, '<font size=\"2\">%m/%d/%Y (%r)</font>') TIMESTAMP, il.SPEC, il.ZONE, il.SUBZONE " .
			"FROM `CHARACTER` chr, ITEMS_LOOTED il, RAID_CALENDAR rc, ITEM it " .
			"WHERE il.RAID_ID = rc.RAID_ID " .
			"AND il.CHAR_ID = chr.CHAR_ID " .
			"AND it.ITEM_ID = il.ITEM_ID " .
			"AND il.SPEC <> 'Unassigned' " .
			"AND rc.RAID_ID = ?" .
			"ORDER BY timestamp DESC;");

$loot_statement->bind_param(1, $raid_id);
$loot_statement->execute() or die $dbh->errstr;
print "<script src=\"sorttable.js\"></script>\n";
print "<script src=\"http://www.wowhead.com/widgets/power.js\"></script>\n";
print "<TABLE class=\"sortable normal\" ALIGN=LEFT>";
print "<THEAD>";
print "<TR>";
print "<TH><U><B>Name</B></U></TH>";
print "<TH><U><B>Item Name</B></U></TH>";
print "<TH><U><B>I-Level</B></U></TH>";
print "<TH><U><B>Date</B></U></TH>";
print "<TH><U><B>Spec</B></U></TH>";
print "<TH><U><B>Zone</B></U></TH>";
print "<TH><U><B>SubZone</B></U></TH>";
print "</TR>";
print "</THEAD>\n";
print "<TBODY>";
while (my $row = $loot_statement->fetchrow_hashref()) {
	my $url = URLEncode($row->{ITEM_NAME});
	print "<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\" onclick=\"location.href='item.shtml?data=$url'\">";
        print "<td><A HREF=\"char.shtml?data=$row->{NAME}\"><B>$row->{NAME}</B></A></td>";
	print "<TD><a href=\"http://www.wowhead.com/?item=$row->{ITEM_ID}\">$row->{ITEM_NAME}</a></TD><TD>$row->{ITEM_LEVEL}</TD><TD>$row->{TIMESTAMP}</TD>";
	print "<TD>$row->{SPEC}</TD><TD>$row->{ZONE}</TD><TD>$row->{SUBZONE}</TD>";
	print "</TR>\n";
	print "\n";
}
print "</TBODY>";
print "</TABLE>";
print "</fieldset>";
print "</div>";
$loot_statement->finish();

$dbh->disconnect();
