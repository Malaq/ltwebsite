#!/usr/bin/perlml

# The libraries we're using
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use DBI;

# Tells the browser that we're outputting HTML
print "Content-type: text/html\n\n";

#print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\" \"http://www.w3.org/TR/html4/strict.dtd\">\n";
#print "<HTML>\n";

# For debug output
#print "<pre>";
print "<A HREF=\"index.shtml\" >";
print "<img src=\"images/lt_logo.gif\">";
print "</A>";
#print "LegionTracker - Trismegistus";
#print "<A HREF=\"http://wowwebstats.com/cdxnr4iegef2w\"> ";
#print "<img src=\"images/a_logo.gif\" align=\"top\" alt=\"WWS icon\">";
#print "</A>";
print "<hr>";
#print "</pre>";
