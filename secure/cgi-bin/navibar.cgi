#!/usr/bin/perlml

# The libraries we're using
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use DBI;

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

my $forum_address = "";
my $wol_address = "";
my $wmo_address = "";

my $settings_query = 
	$dbh->prepare("SELECT LOOKUP_NAME, LOOKUP_VALUE " .
		      "FROM LT_CONFIG_LOOKUPS " .
		      "WHERE SCRIPT = 'navibar.cgi';");


$settings_query->execute() or die $dbh->errstr;
while (my $row = $settings_query->fetchrow_hashref()) {
	if($row->{LOOKUP_NAME} eq "FORUM_ADDRESS"){
		$forum_address = $row->{LOOKUP_VALUE};
	} elsif($row->{LOOKUP_NAME} eq "WOL_ADDRESS") {
		$wol_address = $row->{LOOKUP_VALUE};
	} elsif($row->{LOOKUP_NAME} eq "WMO_ADDRESS") {
		$wmo_address = $row->{LOOKUP_VALUE};
	}
}

$dbh->disconnect();


# Tells the browser that we're outputting HTML
print "Content-type: text/html\n\n";

print "<fieldset>";
print "<legend>Navigation</legend>";
print "<A HREF=\"admin.shtml\" STYLE=\"text-decoration:none\">";
print "<B>Admin Page</B>";
print "</A><br>";
print "<A HREF=\"bis.shtml\" STYLE=\"text-decoration:none\">";
print "<B>BIS Admin</B>";
print "</A><br>";
print "<A HREF=\"charSpecs.shtml\" STYLE=\"text-decoration:none\">";
print "<B>*Character Specs</B>";
print "</A><br>";
print "<P><B>* - New Reports</B></P>";
print "</fieldset>";

print "<fieldset>";
print "<legend>External Links</legend>";
if ($wol_address ne "") {
print "<A HREF=\"$wol_address\" TARGET=\"_blank\" STYLE=\"text-decoration:none\"> ";
print "<B>World of Logs</B>";
print "</A><br>";
}
if ($wmo_address ne "") {
print "<A HREF=\"$wmo_address\" TARGET=\"_blank\" STYLE=\"text-decoration:none\"> ";
print "<B>WoW Meter Online</B>";
print "</A><br>";
}
if ($forum_address ne "") {
print "<A HREF=\"$forum_address\" TARGET=\"_blank\" STYLE=\"text-decoration:none\">";
print "<B>Forums</B>";
print "</A>";
}
print "</fieldset>";

print "<P>";

print <<PAYPAL;
<form action="https://www.paypal.com/cgi-bin/webscr" method="post" align="CENTER">
<input type="hidden" name="cmd" value="_s-xclick">
<input type="hidden" name="encrypted" value="-----BEGIN PKCS7-----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-----END PKCS7-----">
<input type="image" src="https://www.paypal.com/en_US/i/btn/btn_donateCC_LG.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">
<img alt="" border="0" src="https://www.paypal.com/en_US/i/scr/pixel.gif" width="1" height="1">
</form>
PAYPAL

print <<DELIMETER;
<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("UA-7581504-1");
pageTracker._trackPageview();
} catch(err) {}</script>
DELIMETER

