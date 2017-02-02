#!/usr/bin/perlml

# The libraries we're using
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use DBI;

sub attendanceColor {
	my $attendance = shift;
	my $attendance_type = '';
	if ($attendance > 27) {
		$attendance_type = 'high_attendance';
	} elsif ($attendance > 22) {
		$attendance_type = 'medium_attendance';
	} else {
		$attendance_type = 'low_attendance';
	}
	print "<TD class='$attendance_type'>$attendance</TD>";
}

sub saturationColor {
	my $saturation = shift;
	my $satnum = substr($saturation, 0, - 1);
	my $attendance_type = '';
	if ($satnum < 25) {
		$attendance_type = 'high_attendance';
	} elsif ($satnum < 50) {
		$attendance_type = 'medium_attendance';
	} else {
		$attendance_type = 'low_attendance';
	}
	print "<TD class='$attendance_type'>$saturation</TD>";
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


# Database handle
my $dbh = DBI->connect("dbi:mysql:database=$database;host=$hostname;port=$dbport", $username, $password) or print $DBI::errstr;

my $char_name = param('data');

print "<font size=\"6\" face=\"Monotype Corsiva\"><B>$char_name</B></font>";

	print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\" \"http://www.w3.org/TR/html4/strict.dtd\">\n";
	print "<HTML>\n";

# Raid table
my $list_statement =
	$dbh->prepare("SELECT rc.RAID_ID, rc.DATE, date_format(rc.DATE, '%a') DAYOFWEEK, rc.ATTENDANCE_COUNT, IFNULL(total_members.numb,'n/a') MEMBERS, IFNULL(total_loot.numb,0) DROPS, " .
	"concat(IFNULL(floor((de.numb*100)/total_loot.numb),0),'%') SATURATION, rc.SCHEDULED, zones.ZONES " .
	"FROM `RAID_CALENDAR` rc " .
	"LEFT JOIN " .
	"     (SELECT raid_id, count(item_id) numb  " .
	" FROM ITEMS_LOOTED  " .
	" WHERE spec in ('DE\\'d', 'Off')  " .
	" GROUP BY raid_id) de " .
	"ON de.raid_id = rc.raid_id " .
	"LEFT JOIN  " .
	" (SELECT raid_id, count(item_id) numb  " .
	" FROM ITEMS_LOOTED  " .
	" WHERE spec <> 'Unassigned'  " .
	" GROUP BY raid_id) total_loot  " .
	"ON total_loot.raid_id = rc.raid_id  " .
	"LEFT JOIN  " .
	"(SELECT raid_id, count(*) numb  " .
	"  FROM RAID_ATTENDANCE  " .
	"  WHERE ATTENDANCE Regexp '[[:digit:]]+' <> 0  " .
	"  GROUP BY raid_id) total_members  " .
	"ON total_members.raid_id = rc.raid_id  " .
	"LEFT JOIN " .
	"(SELECT RAID_ID, ID, ZONES " .
	"	FROM (SELECT A.RAID_ID, A.ID, GROUP_CONCAT(A.ZONE) ZONES " .
	"				FROM (SELECT IL.RAID_ID, " .
	"							MIN(CASE WHEN (IL.SPEC IN ('Main', 'Alt', 'Off')) " .
	"								THEN 1 " .
	"							ELSE 2 " .
	"							END) ID, IL.ZONE ZONE  " .
	"							FROM ITEMS_LOOTED IL  " .
	"							WHERE IL.RAID_ID IS NOT NULL " .
	"							GROUP BY IL.RAID_ID, IL.ZONE " .
	"							ORDER BY IL.RAID_ID DESC) A " .
	"				GROUP BY A.RAID_ID, A.ID " .
	"				ORDER BY A.RAID_ID, A.ID) B " .
	"	GROUP BY RAID_ID) zones " .
	"ON zones.raid_id = rc.raid_id " .
	"GROUP BY raid_id  " .
	"ORDER BY rc.DATE desc;");


$list_statement->execute() or die $dbh->errstr;
print "<fieldset>";
print "<legend>Scheduled Raids</legend>";
print "<script src=\"sorttable.js\"></script>\n";
print "<TABLE class=\"sortable normal\" ALIGN=LEFT>";
print "<THEAD>\n";
print "<TR>";
print "<TH WIDTH=100><U><B>Raid Date</B></U></TH>";
print "<TH WIDTH=75><U><B>Weekday</B></U></TH>";
print "<TH WIDTH=100><U><B>Raiders Available</B></U></TH>";
print "<TH WIDTH=75><U><B>Raiders</B></U></TH>";
print "<TH WIDTH=100><U><B>Epics Dropped</B></U></TH>";
print "<TH WIDTH=100><U><B>Loot Saturation</B></U></TH>";
print "<TH><U><B>Zones Raided</B></U></TH>";
print "</TR>\n";
print "</THEAD>";
while (my $row = $list_statement->fetchrow_hashref()) {
	my $raidid = $row->{RAID_ID};
	if ($row->{SCHEDULED} eq "1")
	{
		print "<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\" onclick=\"location.href='raiddetail.shtml?data=$raidid'\">";
	}
	else
	{
		print "<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='alert'\" class=\"alert\" onclick=\"location.href='raiddetail.shtml?data=$raidid'\">";
	}
	print "<TD>";
	print "<A HREF=\"raiddetail.shtml?data=$raidid\">";
	print "$row->{DATE}";
	print "</A>";
	print "</TD>";
	print "<TD>";
	print "$row->{DAYOFWEEK}";
	print "</TD>";
	attendanceColor($row->{ATTENDANCE_COUNT});
	print "<TD>";
	print "$row->{MEMBERS}";
	print "</TD>";
	print "<TD>";
	print "$row->{DROPS}";
	print "</TD>";
	saturationColor($row->{SATURATION});
	print "<TD>";
	print "$row->{ZONES}";
	print "</TD>";
	print "</TR>\n";
	print "\n";
}
print "</fieldset>";
print "</TABLE>";
print "</HTML>";
$list_statement->finish();
$dbh->disconnect();
