#!/usr/bin/perlml

# The libraries we're using
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use DBI;
use LWP::Simple;
use HTML::SimpleParse;
use URI::Escape;

my $script = $ENV{'SCRIPT_NAME'};
#Who is running the script
my $audituser = "null";
$audituser = $ENV{'REMOTE_USER'};

# Tells the browser that we're outputting HTML
print "Content-type: text/html\n\n";

# For debug output
print "<pre>";
print "<html>";
print "PLEASE WAIT...<BR>";
print "Parsing wowhead for item information...<BR>";

sub URLEncode {
my $theURL = $_[0];
$theURL =~ s/([\W])/"%" . uc(sprintf("%2.2x",ord($1)))/eg;
return $theURL;
}

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

sub stageItem {
	my $stage_set_id = shift;
	my $tier_id = shift;
	my $class_id = shift;
	my $spec_id = shift;
	my $slot_id = shift;
	my $item_id = shift;
	my $valid = shift;
	my $list_name = shift;

	my $SQL =
	$dbh->prepare("INSERT INTO BIS_ITEMS_STAGING (STAGE_SET_ID, " .
			" 			SLOT_ID, " .
			" 			ITEM_ID, " .
			" 			TIER_ID, " .
			"			CLASS_ID, " .
			"			SPEC_ID, " .
			"			LIST_DESCRIPTION, " .
			" 			VALID, " .
			"			UPDATED_BY) " .
			"VALUES (?,?,?,?,?,?,?,?,?);");
		
	$SQL->bind_param(1,$stage_set_id);
	$SQL->bind_param(2,$slot_id);
	$SQL->bind_param(3,$item_id);
	$SQL->bind_param(4,$tier_id);
	$SQL->bind_param(5,$class_id);
	$SQL->bind_param(6,$spec_id);
	$SQL->bind_param(7,$list_name);
	$SQL->bind_param(8,$valid);
	$SQL->bind_param(9,$audituser);

	$SQL->execute() or die $dbh->errstr;

	my $SQL = 
	$dbh->prepare("UPDATE BIS_ITEMS_STAGING BIS  " .
		"SET BIS.ITEM_SUBTYPE = (SELECT IT.ITEM_SUBTYPE FROM ITEM IT WHERE IT.ITEM_ID = BIS.ITEM_ID), " .
		"BIS.ITEM_EQUIPLOC = (SELECT IT.ITEM_EQUIPLOC FROM ITEM IT WHERE IT.ITEM_ID = BIS.ITEM_ID) " .
		"WHERE BIS.STAGE_SET_ID = ? ;");
		
	$SQL->bind_param(1,$stage_set_id);
	$SQL->execute() or die $dbh->errstr;
}

sub getStageSetID {
	my $stage_set_id = "";

	my $SQL = 
	$dbh->prepare("SELECT IFNULL(MAX(STAGE_SET_ID)+1,0) STAGE_SET_ID " .
			"FROM BIS_ITEMS_STAGING;");

	$SQL->execute() or die $dbh->errstr;
	
	my $row = $SQL->fetchrow_hashref();
	$stage_set_id = $row->{STAGE_SET_ID};	
}

sub purgeOldStagedData {
	#Currently purges anything older than 1 hour.
	my $SQL = 
	$dbh->prepare("DELETE  " .
			"FROM BIS_ITEMS_STAGING  " .
			"WHERE UPDATED_DATE < DATE_SUB(NOW(), INTERVAL 1 HOUR);");
	$SQL->execute() or die $dbh->errstr;
}

# Grabs the data that was POST'd under the name 'data'.
my $buffer = "";
read(STDIN, $buffer,$ENV{'CONTENT_LENGTH'});
my @lines = split(/\n/, $buffer);

my $list_name = "";
my $tier_id = "";
my $class_id = "";
my $spec_id = "";
my $slot_id = "";
my $item_id = "";
my $stage_set_id = getStageSetID();

purgeOldStagedData();

# Deal with the data line-by-line
foreach $line (@lines) {
	#print "$line";
	@data = split(/&/, $line);

	foreach $data (@data) {
		($type, $id) = split(/=/, $data);
		#print "2\r";
		#print "$data\r";
		#print "Data type: $type, Data ID: $id\r";
		if ($type eq "LIST_NAME")
		{
			$list_name = uri_unescape($id);
			$list_name =~ tr/+/ /;
		}
		elsif ($type eq "TIER_ID")
		{
			$tier_id = $id;
		}
		elsif ($type eq "CLASS_ID")
		{
			$class_id = $id;
		}
		elsif ($type eq "SPEC_ID")
		{
			$spec_id = $id;
		}
		elsif ($type eq "ITEM_SLOT")
		{
			$slot_id = $id;
		}
		elsif ($type eq "ITEM_ID")
		{
			$item_id = $id;
			my $valid_item = validItem($item_id);
			print ("Item: $item_id, Slot: $slot_id is valid? ", $valid_item,"<BR>");

			if ($item_id ne "")
			{
				if ($valid_item eq "F")
				{
					my $var = system("/usr/bin/perl /home/legion/public_html/hermit/secure/cgi-bin/wh_data_extract.cgi ITEM $item_id");
					print "$var <BR>";
				}
		 	}

			stageItem($stage_set_id, $tier_id, $class_id, $spec_id, $slot_id, $item_id, validItem($item_id), $list_name);
		}
		else
		{
			print "ERROR: Unexpected data type of '$type' passed in.  Shutting down.\r";
			print "<A HREF=\"../bis.shtml\">Click here to start over.</A>";
			exit;
		}
	}
}

auditquery("SUCCESS","Staged bis list: $list_name, tierid: $tier_id, classid: $class_id, specid: $spec_id");

print "<head><meta HTTP-EQUIV=\"REFRESH\" content=\"0; url=../editbislists.shtml?CREATE_LIST=STAGE&STAGE_SET_ID=$stage_set_id\"></head>";

#auditquery("SUCCESS","**Raid info** Raid_id: $raid_id, Date: $date Scheduled: $scheduled Attendees: $attendees, Items loaded: $lootcount, Players parsed: $playercount");
		
$dbh->disconnect();
print "</pre>";
