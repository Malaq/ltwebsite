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
	my $item_name = shift;
	if ($item_id eq "0")
	{
		return "F";
	}

	my $SQL = 
		$dbh->prepare("SELECT ITEM_ID, ITEM_NAME " .
				"FROM ITEM " .
				"WHERE ITEM_ID = ? ;");

	$SQL->bind_param(1, $item_id);
	$SQL->execute() or die $dbh->errstr;
	
	my $row = $SQL->fetchrow_hashref();
	if ($row->{ITEM_ID} eq $item_id)
	{
		return ("T",$row->{ITEM_NAME});
	}
	return ("F",$item_name);
}

my $stage_row_id = param('STAGE_ROW_ID');
my $stage_set_id = param('STAGE_SET_ID');
my $item_id = param('ITEM_ID');
my $item_name = param('ITEM_NAME');
my $valid = "";

	$valid,$item_name = validItem($item_id, $item_name);

	my $SQL = 
	$dbh->prepare("UPDATE BIS_ITEMS_STAGING BIS  " .
		"SET BIS.ITEM_ID = ?, " .
		"BIS.ITEM_NAME_OVERRIDE = ? " . 
		"WHERE BIS.STAGING_ID = ? ;");
		
	$SQL->bind_param(1,$item_id);
	$SQL->bind_param(2,$item_name);
	$SQL->bind_param(3,$stage_row_id);
	$SQL->execute() or die $dbh->errstr;

	auditquery("SUCCESS","Updated staging table, rowid: $stage_row_id, item_id $item_id, item_name $item_name");

print "<head><meta HTTP-EQUIV=\"REFRESH\" content=\"0; url=../editbislists.shtml?CREATE_LIST=STAGE&STAGE_SET_ID=$stage_set_id\"></head>";

#auditquery("SUCCESS","**Raid info** Raid_id: $raid_id, Date: $date Scheduled: $scheduled Attendees: $attendees, Items loaded: $lootcount, Players parsed: $playercount");
		
$dbh->disconnect();
print "</pre>";
