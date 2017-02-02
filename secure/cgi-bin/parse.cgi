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
print "<pre>";

# Setup our DB connection
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

# Grabs the data that was POST'd under the name 'data'.
my $input = param('data');
my $playercount = 0;
my $lootcount = 0;
my $raid_id;

@lines = split(/\n/, $input);

# Deal with the data line-by-line
foreach $line (@lines) {
	$type = substr($line, 0, 1);
	$data = substr($line, 1);
	$data =~ s/\r//g;
	if ($type eq '#') { # Raid info
		($date, $scheduled, $attendees) = split(/\//, $data);

		# Debug output
		print "**Raid info**\tDate: $date\tScheduled: $scheduled\tAttendees: $attendees\n";
		
		#$dbh->do("INSERT INTO RAID_CALENDAR(DATE, SCHEDULED, ATTENDANCE_COUNT) VALUES('2008-12-28', $scheduled, $attendees);") or die $dbh->errstr;
		my $statement =
			$dbh->prepare("INSERT INTO RAID_CALENDAR (DATE, SCHEDULED, ATTENDANCE_COUNT) " .
					"VALUES (?, ?, ?);");
		$statement->bind_param(1, $date);
		$statement->bind_param(2, $scheduled);
		$statement->bind_param(3, $attendees);
		$statement->execute() or die $dbh->errstr;

		my $statement =
			$dbh->prepare("SELECT RAID_ID FROM RAID_CALENDAR " .
					"WHERE DATE=? " .
					"AND SCHEDULED=? " .
					"AND ATTENDANCE_COUNT=?;");
		$statement->bind_param(1, $date);
		$statement->bind_param(2, $scheduled);
		$statement->bind_param(3, $attendees);
		$statement->execute() or die $dbh->errstr;
		$row=$statement->fetchrow_hashref;
		$raid_id = "$row->{RAID_ID}";

		
		print "RAID_ID = $raid_id\n";

		
	} elsif ($type eq '@') { # Attendance info
		($player, $class, $attendance, $rank) = split(/;/, $data);

		# Debug output
		print "**Attendance Info**\tPlayer: $player\tClass: $class\tAttendance: $attendance\tRank: $rank\n";

		if ($rank eq 'Unguilded') {
			my $statement =
				$dbh->prepare("INSERT INTO `CHARACTER`(`NAME`, `CLASS`) " .
						"VALUES(?, ?);");
			$statement->bind_param(1, $player);
			$statement->bind_param(2, $class);
			$statement->execute() or print "$player already exists.\n";
		}
		else
		{
			my $statement =
				$dbh->prepare("INSERT INTO `CHARACTER`(`NAME`, `CLASS`, `DATE_JOINED`) " .
						"VALUES(?, ?, ?);");
			$statement->bind_param(1, $player);
			$statement->bind_param(2, $class);
			$statement->bind_param(3, $date);
			$statement->execute() or print "$player already exists.\n";
		}


		my $statement =
			$dbh->prepare("SELECT CHAR_ID, RANK FROM `CHARACTER` " .
					"WHERE `NAME`=?;");
		$statement->bind_param(1, $player);
		$statement->execute() or die $dbh->errstr;
		$row=$statement->fetchrow_hashref;
		$char_id = "$row->{CHAR_ID}";
		$old_rank = "$row->{RANK}";

		if (($old_rank eq 'P.U.G.') && ($rank ne 'P.U.G.')) {
			my $statement =
				$dbh->prepare("UPDATE `CHARACTER` " .
						"SET `RANK`=?, `DATE_JOINED`=? " .
						"WHERE CHAR_ID=?;");
			$statement->bind_param(1, $rank);
			$statement->bind_param(2, $date);
			$statement->bind_param(3, $char_id);
			$statement->execute or die $dbh->errstr;
		} else {
			my $statement =
				$dbh->prepare("UPDATE `CHARACTER` " .
						"SET `RANK`=? " .
						"WHERE CHAR_ID=?;");
			$statement->bind_param(1, $rank);
			$statement->bind_param(2, $char_id);
			$statement->execute or die $dbh->errstr;
		}

		print "CHAR_ID = $char_id\n";
		
		my $statement =
			$dbh->prepare("INSERT INTO `RAID_ATTENDANCE`(`CHAR_ID`, `RAID_ID`, `ATTENDANCE`) " .
					"VALUES(?, ?, ?);");
		$statement->bind_param(1, $char_id);
		$statement->bind_param(2, $raid_id);
		$statement->bind_param(3, $attendance);
		$statement->execute() or print "$player already has attendance for this raid.\n";
		$playercount = $playercount+1;


	} elsif ($type eq '$') { # Loot info
		($player, $item_name, $item_id, $date, $spec, $zone, $subzone, $rarity, $iLevel, $iType, $iSubType, $iEquipLoc) = split(/;/, $data);

		# Debug output
		print "**Item info**\tPlayer: $player\titem: $item_name\titem_id: $item_id\trarity: $rarity\tzone: $zone\tdate: $date\n";

		my $statement =
			$dbh->prepare("SELECT CHAR_ID FROM `CHARACTER` " .
					"WHERE `NAME`=?;");
		$statement->bind_param(1, $player);
		$statement->execute() or die $dbh->errstr;
		$row=$statement->fetchrow_hashref;
		$char_id = "$row->{CHAR_ID}";

		$temp_id = "";
		$temp_rarity = "";
		my $statement =
#			$dbh->prepare("SELECT `ITEM_ID`, `RARITY` FROM `ITEM` " .
#					"WHERE (`ITEM_ID`=? " .
#					"OR ITEM_NAME = ? ) " .
#					"AND ITEM_ID <> 0 " .
#					"ORDER BY ITEM_ID DESC;");
			$dbh->prepare("SELECT `ITEM_ID`, `RARITY` FROM `ITEM` " .
					"WHERE `ITEM_ID`=?;");
		$statement->bind_param(1, $item_id);
		$statement->execute() or die $dbh->errstr;
		$row=$statement->fetchrow_hashref;
		$temp_rarity = "$row->{RARITY}";
		$temp_id = "$row->{ITEM_ID}";

		if ($temp_id eq $item_id) {
			print "$item_name already exists in the database.\n";
		} else {
			my $statement = 
				$dbh->prepare("INSERT INTO `ITEM`(`ITEM_ID`, `ITEM_NAME`) " .
						"VALUES(?, ?);");
			$statement->bind_param(1, $item_id);
			$statement->bind_param(2, $item_name);
			$statement->execute or print "$item_name already exists in the database.  Error, this shouldn't happen.\n";
		}
		
		#if ($temp_rarity eq $rarity) {
		#	print "$item_name already set to $temp_rarity. Skipping update.\n";
		#} else {
		#	if ($rarity ne "") {
				print "Updating $item_name rarity to $rarity.\n";
				my $statement = 
					$dbh->prepare("UPDATE `ITEM` " .
							"SET RARITY = ? , " .
							"ITEM_LEVEL = ? , " .
							"ITEM_TYPE = ? , " .
							"ITEM_SUBTYPE = ? , " .
							"ITEM_EQUIPLOC = ? " .
							"WHERE item_id = ?");
				$statement->bind_param(1, $rarity);
				$statement->bind_param(2, $iLevel);
				$statement->bind_param(3, $iType);
				$statement->bind_param(4, $iSubType);
				$statement->bind_param(5, $iEquipLoc);
				$statement->bind_param(6, $item_id);
				$statement->execute or print "$item_name - $item_id error. Failure updating rarity to $rarity.\n";
		#	} else {
		#		print "WARNING: No rarity given for $item_name - $item_id.\n";
		#	}
		#}

		my $statement =
			$dbh->prepare("INSERT INTO `ITEMS_LOOTED`(`CHAR_ID`, `ITEM_ID`, `RAID_ID`, `TIMESTAMP`, `SPEC`, `ZONE`, `SUBZONE`, `CURRENT_ITEM_NAME`) " .
					"VALUES(?, ?, ?, ?, ?, ?, ?, ?);");
		$statement->bind_param(1, $char_id);
		$statement->bind_param(2, $item_id);
		$statement->bind_param(3, $raid_id);
		$statement->bind_param(4, $date);
		$statement->bind_param(5, $spec);
		$statement->bind_param(6, $zone);
		$statement->bind_param(7, $subzone);
		$statement->bind_param(8, $item_name);
		$statement->execute() or die $dbh->errstr;

		$lootcount = $lootcount+1;
	}
}
my $statement =
#       $dbh->prepare("select chr1.CHAR_ID, removed.DATE " .
#		      "from `CHARACTER` chr1 " .
#		      "LEFT JOIN ( " .
#		      "select raidmax.CHAR_ID, rc.DATE " .
#		      "from (select ra.CHAR_ID, max(ra.RAID_ID) raid_id " .
#		      "from RAID_ATTENDANCE ra " .
#		      "group by ra.CHAR_ID) raidmax, `CHARACTER` chr, RAID_CALENDAR rc " .3
#		      "where raidmax.raid_id <> (select max(RAID_ID) from RAID_CALENDAR) " .
#		      "and chr.CHAR_ID = raidmax.CHAR_ID " .
#		      "and raidmax.RAID_ID = rc.RAID_ID " .
#		      ") removed ON removed.CHAR_ID = chr1.CHAR_ID " .
#		      "where chr1.rank <> 'P.U.G.';");
$dbh->prepare("select chr1.CHAR_ID, removed.DATE " .
	"from `CHARACTER` chr1 " .
	"LEFT JOIN ( " .
	"select raidmax.CHAR_ID, rc.DATE " .
	"from (select ra.CHAR_ID, MAX(rc1.DATE) raid_date " .
	"from RAID_ATTENDANCE ra, RAID_CALENDAR rc1 " .
	"where ra.RAID_ID = rc1.RAID_ID " .
	"group by ra.CHAR_ID) raidmax, `CHARACTER` chr, RAID_CALENDAR rc " .
	"where raidmax.raid_date <> (select max(DATE) from RAID_CALENDAR) " .
	"and chr.CHAR_ID = raidmax.CHAR_ID " .
	"and raidmax.RAID_DATE = rc.DATE " .
	") removed ON removed.CHAR_ID = chr1.CHAR_ID " .
	"where chr1.rank <> 'P.U.G.';");



$statement->execute() or die $dbh->errstr;
while (my $row = $statement->fetchrow_hashref()) {
	print "Updating $row->{CHAR_ID} setting removed_date to $row->{DATE}.\n";
	my $insert_statement =
		$dbh->prepare("UPDATE `CHARACTER` " .
			      "SET DATE_REMOVED = ? " .
			      "WHERE CHAR_ID=?;");
	$insert_statement->bind_param(1, $row->{DATE});
	$insert_statement->bind_param(2, $row->{CHAR_ID});
	$insert_statement->execute or die $dbh->errstr;
}
print "Parse Complete.\n";

auditquery("SUCCESS","**Raid info** Raid_id: $raid_id, Date: $date Scheduled: $scheduled Attendees: $attendees, Items loaded: $lootcount, Players parsed: $playercount");
		
$dbh->disconnect();
print "</pre>";
print "<meta HTTP-EQUIV=\"REFRESH\" content=\"0; url=http://www.legiontracker.com/hermit/raiddetail.shtml?data=$raid_id\">";
