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

#die "Intentionally stopping script.";

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

my $config_id = $FORM{CONFIG_ID};
my $value1 = $FORM{VALUE1};
my $value2 = $FORM{VALUE2};

#print "$item_id, $reward_ilevel, $is_token";

my $update_config_stmt =
	$dbh->prepare("UPDATE LT_CONFIG_LOOKUPS " .
		  "SET LOOKUP_VALUE = ?, LOOKUP_VALUE_2 = ? " .
		  "WHERE CONFIG_ID = ? ;");

if ($value1 eq "") {
	$update_config_stmt->bind_param(1, undef);
} else {
	$update_config_stmt->bind_param(1, $value1);
}
if ($value2 eq "") {
	$update_config_stmt->bind_param(2, undef);
} else {
	$update_config_stmt->bind_param(2, $value2);
}
$update_config_stmt->bind_param(3, $config_id);

#After the query is built, check if it should be run.  If not, you have the query to be logged.
if ($audituser eq "null") {
	auditquery("INVALID USER","Config_id: $config_id, Value1: $value1, Value2: $value2");
	die "UNIDENTIFIED USER.  Discarding update, logging audit report";
}
$update_config_stmt->execute() or die $dbh->errstr;
auditquery("SUCCESS","Config_id: $config_id, Value1: $value1, Value2: $value2");

print "<meta HTTP-EQUIV=\"REFRESH\" content=\"3; url=http://www.legiontracker.com/hermit/secure/admin.shtml\">";
print "Thank you $audituser.<BR/>";
print "The following data was updated and logged.<BR/>";
print "Config_id: $config_id <BR/>";
print "Value1: \"$value1\"";
print "Value2: \"$value2\"<BR/>";
print "You are now being redirected back to LegionTracker.";

$dbh->disconnect();
