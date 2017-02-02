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

sub validItem {
	my $item_id = shift;
	if ($item_id eq "0")
	{
		return "F";
	}

	my $SQL = 
		$dbh->prepare("SELECT ITEM_ID " .
				"FROM ITEM " .
				"WHERE ITEM_ID = ? ;");

	$SQL->bind_param(1, $item_id);
	$SQL->execute() or die $dbh->errstr;
	
	my $row = $SQL->fetchrow_hashref();
	if ($row->{ITEM_ID} eq $item_id)
	{
		return "T";
	}
	return "F";
}

sub applyStagedData {
	my $stage_set_id = shift;
	#select count and details of set
	my $SQL = 
	$dbh->prepare("SELECT LIST_DESCRIPTION, TIER_ID, CLASS_ID, SPEC_ID, BIS_LIST_ID, COUNT(*) ROWS " .
			"FROM BIS_ITEMS_STAGING " .
			"WHERE STAGE_SET_ID = ? " .
			"GROUP BY LIST_DESCRIPTION, TIER_ID, CLASS_ID, SPEC_ID;");
	$SQL->bind_param(1,$stage_set_id);
	$SQL->execute() or die $dbh->errstr;
	my $row = $SQL->fetchrow_hashref();
	my $list_desc = $row->{LIST_DESCRIPTION};
	my $bis_list_id = $row->{BIS_LIST_ID};
	my $tier_id = $row->{TIER_ID};
	my $class_id = $row->{CLASS_ID};
	my $spec_id = $row->{SPEC_ID};
	my $rows = $row->{ROWS};

	if ($bis_list_id eq "")
	{
		my $SQL = 
		$dbh->prepare("INSERT INTO BIS_LISTS(CLASS_ID, SPEC_ID, TIER_ID, GUILD_ID, DESCRIPTION, UPDATED_BY) " .
				"VALUES (?, ?, ?, ?, ?, ?);");
		$SQL->bind_param(1,$class_id);
		$SQL->bind_param(2,$spec_id);
		$SQL->bind_param(3,$tier_id);
		$SQL->bind_param(4,0);
		$SQL->bind_param(5,$list_desc);
		$SQL->bind_param(6,$audituser);
		$SQL->execute() or die $dbh->errstr;
	
		my $SQL =
		$dbh->prepare("SELECT MAX(BIS_LIST_ID) AS BIS_LIST_ID " .
				"FROM BIS_LISTS;");
		$SQL->execute() or die $dbh->errstr;	
		$row = $SQL->fetchrow_hashref();
		my $bis_list_id = $row->{BIS_LIST_ID};
	
		my $SQL = 
		$dbh->prepare("INSERT INTO BIS_ITEMS(BIS_LIST_ID, " .
			"			ITEM_ID, " .
			"			ITEM_NAME_OVERRIDE, " .
			"			SLOT_ID, " .
			"			START_DATE, " .
			"			UPDATED_BY) " .
			"SELECT ?, " .
			"	 ITEM_ID, " .
			"	 ITEM_NAME_OVERRIDE, " .
			"	 SLOT_ID, " .
			"	 SYSDATE(), " .
			"	 ? " .
			"FROM BIS_ITEMS_STAGING AS BIS " .
			"WHERE STAGE_SET_ID = ? ;");
		$SQL->bind_param(1,$bis_list_id);
		$SQL->bind_param(2,$audituser);
		$SQL->bind_param(3,$stage_set_id);
		$SQL->execute() or die $dbh->errstr;
	}
	else
	{
		my $SQL = 
		$dbh->prepare("UPDATE BIS_ITEMS BI " .
				"SET ITEM_ID = (SELECT ITEM_ID FROM BIS_ITEMS_STAGING BIS WHERE BIS.SLOT_ID = BI.SLOT_ID AND STAGE_SET_ID = ?), " .
				"    ITEM_NAME_OVERRIDE = (SELECT ITEM_NAME_OVERRIDE FROM BIS_ITEMS_STAGING BIS WHERE BIS.SLOT_ID = BI.SLOT_ID AND STAGE_SET_ID = ?) " .
				"WHERE BI.BIS_LIST_ID = ? ;");
		$SQL->bind_param(1,$stage_set_id);
		$SQL->bind_param(2,$stage_set_id);
		$SQL->bind_param(3,$bis_list_id);
		$SQL->execute() or die $dbh->errstr;
	}

	#purge from staging table
	my $SQL = 
	$dbh->prepare("DELETE " .
			"FROM BIS_ITEMS_STAGING " .
			"WHERE STAGE_SET_ID = ? ");
	$SQL->bind_param(1,$stage_set_id);
	$SQL->execute() or die $dbh->errstr;

	#return count and details
	return ($rows, $bis_list_id, $list_desc, $tier_id, $class_id, $spec_id);
}

my $stage_set_id = param('STAGE_SET_ID');
my $rows = "";
my $bis_list_id = "";
my $list_desc = "";
my $tier_id = "";
my $class_id = "";
my $spec_id = "";

my ($rows, $bis_list_id, $list_desc, $tier_id, $class_id, $spec_id) = applyStagedData($stage_set_id);

auditquery("SUCCESS","Saved bis list: $bis_list_id($rows), name: $list_desc, tierid: $tier_id, classid: $class_id, specid: $spec_id");
#print "Saved bis list: $bis_list_id($rows), name: $list_desc, tierid: $tier_id, classid: $class_id, specid: $spec_id";
print "<head><meta HTTP-EQUIV=\"REFRESH\" content=\"0; url=../bis.shtml?TIER_ID=$tier_id\" ></head>";

#auditquery("SUCCESS","**Raid info** Raid_id: $raid_id, Date: $date Scheduled: $scheduled Attendees: $attendees, Items loaded: $lootcount, Players parsed: $playercount");
		
$dbh->disconnect();
print "</pre>";
