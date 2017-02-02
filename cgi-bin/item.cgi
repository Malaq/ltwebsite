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

my $item_name = param('data');

#print "<font size=\"6\" face=\"Monotype Corsiva\"><B>$char_name</B></font>";

#print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\" \"http://www.w3.org/TR/html4/strict.dtd\">\n";
#print "<HTML>\n";

# Overview
print "<script src=\"http://www.wowhead.com/widgets/power.js\"></script>\n";
print "<fieldset>";
print "<legend>Item Details:</legend>";
my $sql_text = 
my $summary_statement =
	$dbh->prepare("SELECT it1.ITEM_NAME, it1.ITEM_ID, il.TIMESTAMP, chr.NAME, firstl.COUNT, it1.RARITY, it1.ITEM_LEVEL, it1.ITEM_TYPE, it1.ITEM_SUBTYPE, it1.ITEM_EQUIPLOC, IFNULL(it1.REWARD_ILEVEL,'n/a') REWARD_ILEVEL " .
			"FROM `CHARACTER` chr, ITEMS_LOOTED il, ITEM it1, ( " .
			"SELECT il.ITEM_ID, MIN( il.TIMESTAMP ) TIMESTAMP, count(*) COUNT " .
			"FROM ITEMS_LOOTED il, ITEM it " .
			"WHERE il.ITEM_ID = it.ITEM_ID " .
			"AND it.ITEM_NAME like ? " .
			"GROUP BY il.ITEM_ID " .
			")firstl " .
			"WHERE firstl.ITEM_ID = il.ITEM_ID " .
			"AND firstl.TIMESTAMP = il.TIMESTAMP " .
			"AND chr.CHAR_ID = il.CHAR_ID " .
			"AND il.ITEM_ID = it1.ITEM_ID " .
			"ORDER BY TIMESTAMP;");
$summary_statement->bind_param(1, '%'.$item_name.'%');
$summary_statement->execute() or die $dbh->errstr;
my $row = $summary_statement->fetchrow_hashref();

if ( $row->{ITEM_ID} ne "" ) {
	print "<B>Name:</B><a href=\"http://www.wowhead.com/?item=$row->{ITEM_ID}\" TARGET=\"_blank\">$row->{ITEM_NAME}</a><BR>";
	print "<B>Rarity:</B> $row->{RARITY}<BR>";
        print "<B>Item Level:</B> $row->{ITEM_LEVEL}<BR>";
        print "<B>Reward I-level:</B> $row->{REWARD_ILEVEL}<BR>";
	print "<B>Item Type:</B> $row->{ITEM_TYPE}<BR>";
        print "<B>Item Subtype:</B> $row->{ITEM_SUBTYPE}<BR>";
        print "<B>EquipLoc:</B> $row->{ITEM_EQUIPLOC}<BR>";
	print "<B>Times Looted:</B> $row->{COUNT}</B><BR>";
	print "<B>First Time Looted:</B> $row->{TIMESTAMP} <BR>";
	print "<B>Who First Looted:</B> $row->{NAME} <BR>";
		my $sql2_text = 
		my $dust_statement =
			$dbh->prepare("SELECT total_looted.ITEM_ID, FLOOR((IFNULL(total_dusted.all_dusted,0)*100)/IFNULL(total_looted.all_looted,0)) percent_dust " .
					"FROM ITEM it " .
					"LEFT JOIN " .
					"(select ITEM_ID, count(*) all_looted from ITEMS_LOOTED where ITEM_ID = $row->{ITEM_ID} group by ITEM_ID) total_looted " .
					"ON total_looted.ITEM_ID = it.ITEM_ID " .
					"LEFT JOIN " .
					"(select ITEM_ID, count(*) all_dusted from ITEMS_LOOTED where ITEM_ID = $row->{ITEM_ID} AND SPEC = 'DE\\'d' group by ITEM_ID) total_dusted " .
					"ON total_dusted.ITEM_ID = it.ITEM_ID " .
					"WHERE it.ITEM_ID = $row->{ITEM_ID};");
		#$dust_statement->bind_param(1, '%'.$item_name.'%');
		$dust_statement->execute() or die $dbh->errstr;
		my $row2 = $dust_statement->fetchrow_hashref();
	print "<B>Percent Dusted:</B> $row2->{percent_dust}% <BR>";
		$dust_statement->finish();
} else {
	print "<B>Item $item_name is not found.</B>";
}
print "</fieldset>";

$summary_statement->finish();

# Loot table
print "<fieldset>";
print "<legend>Loot History (limit of 500 rows):</legend>";
my $sql_text = 
my $loot_statement =
	$dbh->prepare("SELECT chr.NAME, it.ITEM_NAME, it.ITEM_ID, IFNULL(it.REWARD_ILEVEL,it.ITEM_LEVEL) AS ITEM_LEVEL, il.SPEC, il.TIMESTAMP, il.ZONE, il.SUBZONE " .
			"FROM `CHARACTER` chr, ITEMS_LOOTED il, RAID_CALENDAR rc, ITEM it " .
			"WHERE chr.CHAR_ID = il.CHAR_ID " .
			"AND il.RAID_ID = rc.RAID_ID " .
			"AND it.ITEM_ID = il.ITEM_ID " .
			"AND it.ITEM_NAME like ? " .
			"ORDER BY it.ITEM_NAME, il.TIMESTAMP DESC " .
			"limit 500;");
# 1373 is the limit this can handle.  It breaks at 1374. Research why later.
$loot_statement->bind_param(1, '%'.$item_name.'%');
$loot_statement->execute() or die $dbh->errstr;
print "<script src=\"sorttable.js\"></script>\n";
print "<script src=\"http://www.wowhead.com/widgets/power.js\"></script>\n";
print "<table cellspacing=\"1\" cellpadding=\"2\" class=\"sortable normal\" id=\"lootDetail\">";
print "<THEAD>";
print "<TR>";
print "<TH><U><B>Name</B></U></TH>";
print "<TH><U><B>Item Name</B></U></TH>";
print "<TH><U><B>Spec</B></U></TH>";
print "<TH><U><B>I-Level</B></U></TH>";
print "<TH><U><B>Date</B></U></TH>";
print "<TH><U><B>Zone</B></U></TH>";
print "<TH><U><B>SubZone</B></U></TH>";
print "</TR>";
print "</THEAD>\n";
print "<TBODY>";
while (my $row = $loot_statement->fetchrow_hashref()) {
	print "<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\" onclick=\"location.href='char.shtml?data=$row->{NAME}'\">";
	print "<TD><B><A HREF=\"char.shtml?data=$row->{NAME}\">$row->{NAME}</A></B></TD><TD><a href=\"http://www.wowhead.com/?item=$row->{ITEM_ID}\" TARGET=\"_blank\">$row->{ITEM_NAME}</a></TD>";
	print "<TD>$row->{SPEC}</TD><TD>$row->{ITEM_LEVEL}</TD><TD>$row->{TIMESTAMP}</TD><TD>$row->{ZONE}</TD><TD>$row->{SUBZONE}</TD>";
	print "</TR>\n";
	print "\n";
}
print "</TBODY>";
print "</TABLE>";
#print "<script type=\"text/javascript\">";
#print "var t = new ScrollableTable(document.getElementById('lootDetail'), 500);";
#print "</script>";
print "</fieldset>";
#print "</HTML>";
$loot_statement->finish();
$dbh->disconnect();
