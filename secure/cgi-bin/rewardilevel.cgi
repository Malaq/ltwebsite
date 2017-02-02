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

#collect database information
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

#Process to break up inputs.
$ENV{'REQUEST_METHOD'} =~ tr/a-z/A-Z/;
if ($ENV{'REQUEST_METHOD'} eq "GET")
{
	$buffer = $ENV{'QUERY_STRING'};
}
# Split information into name/value pairs
@pairs = split(/&/, $buffer);
foreach $pair (@pairs)
{
	($name, $value) = split(/=/, $pair);
	$value =~ tr/+/ /;
	$value =~ s/%(..)/pack("C", hex($1))/eg;
	$FORM{$name} = $value;
}

my $item_id = $FORM{ITEM_ID};
my $reward_ilevel = $FORM{REWARD_ILEVEL};
if ($reward_ilevel eq "") {
	$reward_ilevel = "NULL";
}
my $is_token = $FORM{IS_TOKEN};

#print "$item_id, $reward_ilevel, $is_token";

my $update_item_statement =
	$dbh->prepare("UPDATE ITEM " .
		  "SET REWARD_ILEVEL = ?, IS_TOKEN = ? " .
		  "WHERE ITEM_ID = ? ;");

if ($reward_ilevel eq "NULL") {
	$update_item_statement->bind_param(1, undef);
} else {
	$update_item_statement->bind_param(1, $reward_ilevel);
}
if (($is_token eq "") || ($is_token eq "Unselected")) {
	$update_item_statement->bind_param(2, undef);
} else {
	$update_item_statement->bind_param(2, $is_token);
}
$update_item_statement->bind_param(3, $item_id);

#After the query is built, check if it should be run.  If not, you have the query to be logged.
if ($audituser eq "null") {
	auditquery("INVALID USER","Item_ID: $item_id, Reward_ILevel: $reward_ilevel, Is_Token: $is_token");
	die "UNIDENTIFIED USER.  Discarding update, logging audit report";
}
$update_item_statement->execute() or die $dbh->errstr;

auditquery("SUCCESS","Item_ID: $item_id, Reward_ILevel: $reward_ilevel, Is_Token: $is_token");

print "<meta HTTP-EQUIV=\"REFRESH\" content=\"3; url=http://www.legiontracker.com/hermit/secure/admin.shtml\">";
print "Thank you $audituser.<BR/>";
print "The following data was updated and logged.<BR/>";
print "ITEM_ID: $item_id <BR/>";
print "Reward ILevel: \"$reward_ilevel\"";
print "Token Flag: \"$is_token\"<BR/>";
print "You are now being redirected back to LegionTracker.";

$dbh->disconnect();
