#!/usr/bin/perlml
# The libraries we're using
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);

# Tells the browser that we're outputting HTML
print "Content-type: text/html\n\n\n";

read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});

print "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\"> \n";
print "<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\" lang=\"en\"> \n";
print "	<head> \n";
print "		<title>Trismegistus Attendance and Loot</title> \n";
print "		<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\"> \n";
print "		<script type=\"text/javascript\" src=\"../webtoolkit.scrollabletable.js\"></script> \n";
print "		<script type=\"text/javascript\" src=\"../webtoolkit.sortabletable.js\"></script> \n";
print "		<script type=\"text/javascript\" src=\"../sorttable.js\"></script> \n";
print "		<script type=\"text/javascript\" src=\"../tabber.js\"></script> \n";
print "		<link rel=\"stylesheet\" type=\"text/css\" href=\"../../style.css\" />\n";
print "	</head> \n";
print "	<body bgcolor=\"C0C0C0\"> \n";
print "		<div id='topbar'> \n";
system("cd ..;/usr/bin/perl cgi-bin/topbar.cgi ");
#print "			<!--#include virtual=\"/topbar.cgi\"--> \n";
print "		</div> \n";
print "		<div id='navbar'> \n";
print "			<!--#include virtual=\"navibar.cgi\"--> \n";
print "		</div> \n";
print "		<div id='main_frame'> \n";
print "			<!--#include virtual=\"bisTierList.cgi?$buffer\"--> \n";
print "		</div> \n";
print "	</body> \n";
print "</html> \n";
