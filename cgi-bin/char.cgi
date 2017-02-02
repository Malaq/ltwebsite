#!/usr/bin/perlml

# The libraries we're using
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use DBI;

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


my $mainchar = '';

my $piechart = '';

sub URLEncode {
my $theURL = $_[0];
$theURL =~ s/([\W])/"%" . uc(sprintf("%2.2x",ord($1)))/eg;
return $theURL;
}

# Database handle
my $dbh2 = DBI->connect("dbi:mysql:database=$database;host=$hostname;port=$dbport", $username, $password) or print $DBI::errstr;

sub dayRange {
	#Code added to display date range
	my $tempdate = shift;
	
	my $sql_datediff = 
		$dbh2->prepare("SELECT DATEDIFF(LOCALTIME(), DATE( ? ) ) ;");
	$sql_datediff->bind_param(1, $tempdate);
	$sql_datediff->execute() or die $dbh2->errstr;

	my $row2 = $sql_datediff->fetchrow_arrayref();
	if ( $row2->[0] <= "7" )
	{
		#$range = "7";
		$sql_datediff->finish();
		return "7";
	}
	elsif ( $row2->[0] <= "21" )
	{
		#$range = "30";
		$sql_datediff->finish();
		return "21";
	}
	elsif ( $row2->[0] <= "30" )
	{
		#$range = "30";
		$sql_datediff->finish();
		return "30";
	}
	elsif ( $row2->[0] <= "60" )
	{
		#$range = "60";
		$sql_datediff->finish();
		return "60";
	}
	else
	{
		#$range = "61+";
		$sql_datediff->finish();
		return "61+";
	}
	$sql_datediff->finish();
	return "";
}

sub sumTable {
	my $temprange = shift;
	my $temp_char = shift;

	#create table here
#my $sql_text = 
my $sum_attn_stmt = "";
my $sum_loot_stmt = "";

if ( $temprange ne "0" )
{
$sum_loot_stmt =
	$dbh2->prepare(
	"select " .
	"IFNULL(sum(if(spec='Main', 1, 0)),0) Main_Spec,  " .
	"IFNULL(sum(if(spec='Alt', 1, 0)),0) Alt_Spec,  " .
	"IFNULL(sum(if(spec='Off', 1, 0)),0) Off_Spec " .
	"from ITEMS_LOOTED il, RAID_CALENDAR rc, `CHARACTER` chr " .
	"where chr.char_id = il.char_id " .
	"and rc.raid_id = il.raid_id " .
	"and rc.date >= DATE(DATE_SUB(LOCALTIME(),INTERVAL ? DAY )) " .
	"and rc.scheduled = 1 " .
	"and chr.name = ? ;");		
$sum_attn_stmt =
	$dbh2->prepare(
	"select floor((sum(length(REPLACE(ra.ATTENDANCE,'0','')))*100)/(sum(length(ra.ATTENDANCE)))) ATTENDANCE, " .
	"concat(concat(sum(length(REPLACE(ra.ATTENDANCE, '0', ''))),'/'),sum(length(ra.ATTENDANCE))) val, " .
	"floor((sum(length(REPLACE(REPLACE(ra.ATTENDANCE,'0',''),'1','')))*100)/(sum(length(ra.ATTENDANCE)))) SITTING " .
	"from RAID_ATTENDANCE ra, RAID_CALENDAR rc, `CHARACTER` chr " .
	"where ra.raid_id = rc.raid_id " .
	"and chr.char_id = ra.char_id " .
	"and rc.date >= DATE(DATE_SUB(LOCALTIME(),INTERVAL ? DAY )) " .
	"and ra.ATTENDANCE Regexp '[[:digit:]]+' <> 0 " .
	"and rc.scheduled = 1 " .
	"and chr.name = ? ;");
}
else
{
$sum_loot_stmt =
	$dbh2->prepare(
	"select " .
	"IFNULL(sum(if(spec='Main', 1, 0)),0) Main_Spec,  " .
	"IFNULL(sum(if(spec='Alt', 1, 0)),0) Alt_Spec,  " .
	"IFNULL(sum(if(spec='Off', 1, 0)),0) Off_Spec " .
	"from ITEMS_LOOTED il, RAID_CALENDAR rc, `CHARACTER` chr " .
	"where chr.char_id = il.char_id " .
	"and rc.raid_id = il.raid_id " .
	"and rc.scheduled = 1 " .
	"and chr.name = ? ;");		
$sum_attn_stmt =
	$dbh2->prepare(
	"select floor((sum(length(REPLACE(ra.ATTENDANCE,'0','')))*100)/(sum(length(ra.ATTENDANCE)))) ATTENDANCE, " .
	"concat(concat(sum(length(REPLACE(ra.ATTENDANCE, '0', ''))),'/'),sum(length(ra.ATTENDANCE))) val, " .
	"floor((sum(length(REPLACE(REPLACE(ra.ATTENDANCE,'0',''),'1','')))*100)/(sum(length(ra.ATTENDANCE)))) SITTING " .
	"from RAID_ATTENDANCE ra, RAID_CALENDAR rc, `CHARACTER` chr " .
	"where ra.raid_id = rc.raid_id " .
	"and chr.char_id = ra.char_id " .
	"and rc.scheduled = 1 " .
	"and ra.ATTENDANCE Regexp '[[:digit:]]+' <> 0 " .
	"and chr.name = ? ;");
}

if ( $temprange ne "0" )
{
$sum_loot_stmt->bind_param(1, $temprange);
$sum_loot_stmt->bind_param(2, $temp_char);
$sum_attn_stmt->bind_param(1, $temprange);
$sum_attn_stmt->bind_param(2, $temp_char);
}
else
{
$sum_loot_stmt->bind_param(1, $temp_char);
$sum_attn_stmt->bind_param(1, $temp_char);
}

$sum_loot_stmt->execute() or die $dbh2->errstr;
my $rowl = $sum_loot_stmt->fetchrow_hashref();
$sum_attn_stmt->execute() or die $dbh2->errstr;
my $rowa = $sum_attn_stmt->fetchrow_hashref();

print "<TD>";
if ( $temprange ne "0" )
{
print "<B>$temprange Day</B>";
}
else
{
print "<B>Lifetime</B>";
}
print "</TD>";
print "<TD>";
print "$rowa->{ATTENDANCE}%"; #Attendance
print "</TD>";
print "<TD>";
print "$rowa->{val}"; #Attendance
print "</TD>";
print "<TD>";
print "$rowl->{Main_Spec}"; #Main spec
print "</TD>";
print "<TD>";
print "$rowl->{Alt_Spec}"; #Alt spec
print "</TD>";
print "<TD>";
print "$rowl->{Off_Spec}"; #Off spec
print "</TD>";
$raiding=$rowa->{ATTENDANCE} - $rowa->{SITTING};
$sitting=$rowa->{SITTING};
$offline=100 - $rowa->{ATTENDANCE};
$piechart = "http://chart.apis.google.com/chart?cht=p3&chf=bg,s,000000&chco=00FF00,FFFF00,FF0000&chtt=$temprange+Day+Chart&chd=t:$raiding,$sitting,$offline&chs=280x100&chl=Raiding+($raiding%)|Sitting+($sitting%)|Offline+($offline%)";
$sum_loot_stmt->finish();
$sum_attn_stmt->finish();
}

# Tells the browser that we're outputting HTML
print "Content-type: text/html\n\n";



# Database handle
my $dbh = DBI->connect("dbi:mysql:database=$database;host=$hostname;port=$dbport", $username, $password) or print $DBI::errstr;

my $char_name = param('data');

#print "<font size=\"6\" face=\"Monotype Corsiva\"><B>$char_name</B></font>";

#print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\" \"http://www.w3.org/TR/html4/strict.dtd\">\n";
#print "<HTML>\n";

# Overview
print "<fieldset>";
print "<legend>Character Details:</legend>";
my $sql_text = 
my $summary_statement =
	$dbh->prepare("SELECT char_id, " .
			"name, class, rank, date_joined, date_removed, active, " .
			"IFNULL((select CLASS_SPEC.SPEC_NAME from CLASS_SPEC where CLASS_SPEC.SPEC_ID = `CHARACTER`.PRIMARY_SPEC),'UNASSIGNED!') as PRIMARY_SPEC, " .
			"IFNULL((select CLASS_SPEC.SPEC_NAME from CLASS_SPEC where CLASS_SPEC.SPEC_ID = `CHARACTER`.SECONDARY_SPEC),'UNASSIGNED!') as SECONDARY_SPEC " .
			"from `CHARACTER` " .
			"where name = ? ;");
$summary_statement->bind_param(1, $char_name);
$summary_statement->execute() or die $dbh->errstr;
my $row = $summary_statement->fetchrow_hashref();
my $utf8name = $row->{name};
utf8::encode($utf8name); 
$utf8name = URLEncode($utf8name);
print "<table>";
print "<TR>";
print "<TD rowspan=\"6\">";
print "<B>Name:</B> <A HREF=\"http://us.battle.net/wow/en/character/medivh/$utf8name/simple\" TITLE=\"CHAR_ID=$row->{char_id}\" TARGET=\"_blank\">$row->{name}</A><BR>";
print "<B>Class:</B> $row->{class} <BR>";
print "<B>Rank:</B> $row->{rank} <BR>";
print "<B>Active:</B> $row->{active} <BR>";
my $rank = $row->{rank};
print "<B>Date Joined:</B> $row->{date_joined} <BR>";
if ( $row->{date_removed} ne "" )
{
print "<B>Date Removed (estimated):</B> $row->{date_removed} <BR>";
}
print "<BR>";
print "<B>Main Spec:</B> $row->{PRIMARY_SPEC} <BR>";
print "<B>Alt Spec:</B> $row->{SECONDARY_SPEC} <BR>";
$summary_statement->finish();
print "</TD>";
print "<TD>";
if (( $rank eq "Alt" ) || ( $rank eq "Officer Alt" ))
{
	print "<B>Main:</B>";
	print "</TD>";
	print "<TD>";
	#blank
	print "</TD>";
	print "<TD>";
	print "Attendance";
	print "</TD>";
	print "<TD>";
	print "Values";
	print "</TD>";
	print "<TD>";
	print "MS";
	print "</TD>";
	print "<TD>";
	print "AS";
	print "</TD>";
	print "<TD>";
	print "OS";
	print "</TD>";
	print "</TR>";
	print "<TR>";
	print "<TD rowspan=\"5\">";
	#Mains
	my $sql_text = 
	my $main_statement =
		$dbh->prepare("SELECT ra.attendance MAIN " .
				"FROM `CHARACTER` chr, RAID_ATTENDANCE ra " .
				"WHERE chr.char_id = ra.char_id " .
				"AND chr.NAME = ? " .
				"and ra.raid_id = (select distinct max(raid_id) from RAID_ATTENDANCE ra, `CHARACTER` chr where ra.char_id = chr.char_id and chr.NAME = ? );");
	$main_statement->bind_param(1, $char_name);
	$main_statement->bind_param(2, $char_name);
	$main_statement->execute() or die $dbh->errstr;
	my $row = $main_statement->fetchrow_hashref();
	$mainchar = $row->{MAIN};
	print "<A HREF=\"char.shtml?data=$mainchar\" STYLE=\"text-decoration:none\" class='member_name'>";
	print "$mainchar";
	print "</A>";
	print "<br>";
	
	$main_statement->finish();

}
else
{
	print "<B>Alts:</B>";
	print "</TD>";
	print "<TD>";
	#blank
	print "</TD>";
	print "<TD>";
	print "Attendance";
	print "</TD>";
	print "<TD>";
	print "Values";
	print "</TD>";
	print "<TD>";
	print "MS";
	print "</TD>";
	print "<TD>";
	print "AS";
	print "</TD>";
	print "<TD>";
	print "OS";
	print "</TD>";
	print "</TR>";
	print "<TR>";
	print "<TD rowspan=\"5\">";
	
	#Alts
	my $sql_text = 
	my $alt_statement =
		$dbh->prepare("SELECT DISTINCT chr.NAME " .
				"FROM RAID_ATTENDANCE ra, `CHARACTER` chr " .
				"WHERE ra.char_id = chr.char_id " .
				"AND ra.attendance = ? " .
				"and ra.raid_id = (select distinct max(raid_id) from RAID_ATTENDANCE ra, `CHARACTER` chr where ra.char_id = chr.char_id and chr.NAME = ? );");
	$alt_statement->bind_param(1, $char_name);
	$alt_statement->bind_param(2, $char_name);
	$alt_statement->execute() or die $dbh->errstr;
	while (my $row = $alt_statement->fetchrow_hashref()) {
		my $altname = $row->{NAME};
		print "<A HREF=\"char.shtml?data=$altname\" STYLE=\"text-decoration:none\" class='member_name'>";
		print "$altname";
		print "</A>";
		print "<br>";
	}
	$alt_statement->finish();
}
my $tempchar = "";
if ( $mainchar ne "" )
{
$tempchar = $mainchar;
}
else
{
$tempchar = $char_name;
}
print "</TD>";
sumTable("7",$tempchar);
print "</TR>";
print "</TD>";
sumTable("21",$tempchar);
print "</TR>";
print "<TR>";
sumTable("30",$tempchar);
$phpiechart=$piechart;
print "</TR>";
print "<TR>";
sumTable("60",$tempchar);
print "</TR>";
print "<TR>";
sumTable("0",$tempchar);
print "</TR>";

print "</TABLE>";
print "<img src=\"$phpiechart\" alt=\"30 Day Chart\" />";
print "</fieldset>";
#End Alts

if ( $rank ne "Friend" )
{
# Attendance
print "<fieldset>";
if (( $rank eq "Alt") || ( $rank eq "Officer Alt" ))
{
	print "<legend>Attendance Details (<B>$mainchar</B>):</legend>";
}
else
{
	print "<legend>Attendance Details:</legend>";
}
print <<STRINGDELIM;
	<div id="oID_1" style="overflow: scroll; height: 360px">
	<table cellspacing="1" cellpadding="2" class="sortable normal" id="attnDetail">
	<thead>
	<tr>
		<th>Date</th>
		<TH>Range</TH>
		<TH>Day</TH>
		<th>Attendance (10 min increments)</th>
		<th>Value</th>
		<th>Percent</th>
	</tr>
	</thead>	
STRINGDELIM

my $sql_text = <<STRINGDELIM;
SELECT rc.RAID_ID, 
rc.DATE, 
date_format(rc.DATE,'%a') WEEKDAY, 
ra.ATTENDANCE, 
if(ra.ATTENDANCE Regexp '[[:digit:]]+'<>0, concat(concat(length(REPLACE(ra.ATTENDANCE, '0', '')),'/'),length(ra.ATTENDANCE)), 'n/a') val, 
if(ra.ATTENDANCE Regexp '[[:digit:]]+'<>0, concat(FLOOR(IFNULL(length(REPLACE(ra.ATTENDANCE, '0', ''))*100/length(ra.ATTENDANCE),'0')),'%'), 'n/a') PERCENT,
rc.scheduled SCHEDULED
from `CHARACTER` chr, RAID_ATTENDANCE ra, RAID_CALENDAR rc
where ra.RAID_ID = rc.RAID_ID
and chr.CHAR_ID = ra.CHAR_ID
and chr.NAME = ?
order by rc.DATE desc;
STRINGDELIM
#and rc.scheduled = 1

my $attn_statement = $dbh->prepare( $sql_text );
if (( $rank eq "Alt") || ( $rank eq "Officer Alt" ))
{
$attn_statement->bind_param(1, $mainchar);
}
else
{
$attn_statement->bind_param(1, $char_name);
}
$attn_statement->execute() or die $dbh->errstr;

print "<TBODY>";
while (my $row = $attn_statement->fetchrow_hashref()) {
	#Added Range
	my $range = dayRange($row->{DATE});
	
	my $attn = $row->{ATTENDANCE};
	$attn =~ s|0|~|g;
	$attn =~ s|1|<img src=\"images/greenbox.JPG\" TITLE=\"Online - In Raid\">|g;
	$attn =~ s|2|<img src=\"images/yellowbox.JPG\" TITLE=\"Online - Sitting\">|g;
	$attn =~ s|~|<img src=\"images/redbox.JPG\" TITLE=\"Offline\">|g;
	if ($row->{SCHEDULED} eq "1")
	{	
		print "<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\" onclick=\"location.href='raiddetail.shtml?data=$row->{RAID_ID}'\">";
	}
	else
	{
		print "<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='alert'\" class=\"alert\" onclick=\"location.href='raiddetail.shtml?data=$row->{RAID_ID}'\">";
	}
	print "<td><A HREF=\"raiddetail.shtml?data=$row->{RAID_ID}\" TITLE=\"RAID_ID=$row->{RAID_ID}\">$row->{DATE}</A></td>";
	print "		<td>$range</td>";
	print "		<TD>$row->{WEEKDAY}</TD>";
	print "		<td>$attn</td>";
	print "		<td>$row->{val}</td>";
	print "		<td>$row->{PERCENT}</td>";
	print "	</tr>";

}
print <<STRINGDELIM;
</TBODY>
</table>
STRINGDELIM
#print "<script type=\"text/javascript\">";
#print "var t = new ScrollableTable(document.getElementById('attnDetail'),360,800);";
#print "var t = new ScrollableTable(document.getElementById('attnDetail'),360);";
#print "</script>";
print "</div>";
print "</fieldset>";

$attn_statement->finish();
}


# Loot table
print "<fieldset>";
print "<legend>Loot Details (<B>$char_name</B>):</legend>";
my $loot_statement =
	$dbh->prepare("SELECT chr.NAME, " .
	"       it.ITEM_ID, " .
	"       if(il.ITEM_ID = 0, il.CURRENT_ITEM_NAME, it.ITEM_NAME) as ITEM_NAME, " .
	"       il.TIMESTAMP, " .
	"       il.SPEC, " .
	"       il.ZONE, " .
	"       il.SUBZONE, " .
	"       rc.SCHEDULED, " .
	"       IFNULL(REWARD_ILEVEL,ITEM_LEVEL) ITEM_LEVEL,  " .
	"       case " .
	"	when (SELECT COUNT(BI.ITEM_ID) " .
	"             FROM BIS_LISTS BL, BIS_ITEMS BI  " .
	"             LEFT JOIN (SELECT CF.SOURCE_ITEM_ID, CF.REWARD_ITEM_ID " .
	"                        FROM CURRENCY_FOR CF) AS REWARD " .
	"             ON REWARD.REWARD_ITEM_ID = BI.ITEM_ID " .
	"             WHERE BI.BIS_LIST_ID = BL.BIS_LIST_ID " .
	"             AND BL.SPEC_ID = chr.PRIMARY_SPEC " .
	"             AND (BI.ITEM_ID = it.ITEM_ID OR REWARD.SOURCE_ITEM_ID = it.ITEM_ID)) > 0 " .
	"	then 'T' " .
	"	else '' " .
	"	end BIS " .
	"FROM `CHARACTER` chr, ITEMS_LOOTED il, RAID_CALENDAR rc, ITEM it " .
	"WHERE il.RAID_ID = rc.RAID_ID " .
	"AND il.CHAR_ID = chr.CHAR_ID " .
	"AND it.ITEM_ID = il.ITEM_ID " .
			#"AND rc.DATE > DATE( DATE_SUB( LOCALTIME( ) , INTERVAL 60 " .
			#"DAY ) ) " .
	"AND il.SPEC <> 'Unassigned' " .
	"AND il.SPEC not like 'DE%' " .
	"AND chr.NAME = ? " .
	"ORDER BY timestamp DESC;");


$loot_statement->bind_param(1, $char_name);
$loot_statement->bind_param(2, $char_name);
$loot_statement->execute() or die $dbh->errstr;
print "<div id=\"oID_2\" style=\"overflow: scroll; height: 360px\">";
print "<script src=\"sorttable.js\"></script>\n";
print "<script src=\"http://www.wowhead.com/widgets/power.js\"></script>\n";
print "<table cellspacing=\"1\" cellpadding=\"2\" class=\"sortable normal\" id=\"lootDetail\">";
print "<THEAD>";
print "<TR>";
print "<TH><U><B>Name</B></U></TH>";
print "<TH><U><B>Item Name</B></U></TH>";
print "<TH><U><B>Item Level</B></U></TH>";
print "<TH><U><B>BIS</B></U></TH>";
print "<TH><U><B>Date</B></U></TH>";
print "<TH><U><B>Range</B></U></TH>";
print "<TH><U><B>Spec</B></U></TH>";
print "<TH><U><B>Zone</B></U></TH>";
print "<TH><U><B>SubZone</B></U></TH>";
print "</TR>";
print "</THEAD>\n";
print "<TBODY>";
while (my $row = $loot_statement->fetchrow_hashref()) {
	my $url = URLEncode($row->{ITEM_NAME}); 
	my $range = dayRange($row->{TIMESTAMP});
	if ($row->{SCHEDULED} eq "1")
	{
		print "<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\" onclick=\"location.href='item.shtml?data=$url'\">";
	}
	else
	{
		print "<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='alert'\" class=\"alert\" onclick=\"location.href='item.shtml?data=$url'\">";
	}
	print "<TD>$row->{NAME}</TD>";
	print "<TD><a href=\"http://www.wowhead.com/?item=$row->{ITEM_ID}\">$row->{ITEM_NAME}</a></TD>";
	print "<TD>$row->{ITEM_LEVEL}</TD>";
	print "<TD>$row->{BIS}</TD>";
	print "<TD>$row->{TIMESTAMP}</TD>";
	print "<TD>$range</TD>";
	print "<TD>$row->{SPEC}</TD>";
	print "<TD>$row->{ZONE}</TD>";
	print "<TD>$row->{SUBZONE}</TD>";
	print "</TR>\n";
	print "\n";
}
print "</TBODY>";
print "</TABLE>";
#print "<script type=\"text/javascript\">";
#print "var t = new ScrollableTable(document.getElementById('lootDetail'), 500);";
#print "</script>";
print "</div>";
print "</fieldset>";
#print "</HTML>";
$loot_statement->finish();
$dbh2->disconnect();
$dbh->disconnect();
