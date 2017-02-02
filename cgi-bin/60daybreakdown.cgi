#!/usr/bin/perlml

# The libraries we're using
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use DBI;

# Tells the browser that we're outputting HTML
print "Content-type: text/html\n\n";

# For debug output
#print "<pre>";
#my $rowcolor = '#A69C8B';
my $rowcolor = '#463C2B';
#my $rowcolor = 'silver';

sub round {
    my($number) = shift;
    return int($number + .5);
}

#Class Coloring
sub classColor {
	my $tempclass = shift;
	my $classclr = 'black';
	my $imagename = '';
	my $key = '0';
	#my $classbg = 'black';
	#my $classbg = '#867C6B';
	#my $classbg = 'silver';
	if ($tempclass eq 'Druid') {
		$classclr='#FF7D0A';
		$imagename = 'druid.gif';
		$key = '9';
	} elsif ($tempclass eq 'Hunter') {
		$classclr='#ABD473';
		$imagename = 'hunter.gif';
		$key = '8';
	} elsif ($tempclass eq 'Mage') {
		$classclr='#69CCF0';
		$imagename = 'mage.gif';
		$key = '7';
	} elsif ($tempclass eq 'Paladin') {
		$classclr='#F58CBA';
		$imagename = 'paladin.gif';
		$key = '6';
	} elsif ($tempclass eq 'Priest') {
		$classclr='#FFFFFF';
		$imagename = 'priest.gif';
		$key = '5';
	} elsif ($tempclass eq 'Rogue') {
		$classclr='#FFF569';
		$imagename = 'rogue.gif';
		$key = '4';
	} elsif ($tempclass eq 'Shaman') {
		$classclr='#2459FF';
		$imagename = 'shaman.gif';
		$key = '3';
	} elsif ($tempclass eq 'Warlock') {
		$classclr='#9482C9';
		$imagename = 'warlock.gif';
		$key = '2';
	} elsif ($tempclass eq 'Warrior') {
		$classclr='#C79C6E';
		$imagename = 'warrior.gif';
		$key = '1';
	} elsif ($tempclass eq 'Death Knight') {
		$classclr='#C41F3B';
		$imagename = 'deathknight.gif';
		$key = '10';
	}
	#print "<TD BGCOLOR=$rowcolor>";
	print "<TD sorttable_customkey=\"$key\">";
	print "<B>";
	#print "<font color=$classclr>$tempclass</font>";
	print "<img src=\"images/$imagename\" align=\"center\" title=\"$tempclass\">";
	print "</B>";
	print "</TD>";
}

#Attendance Coloring
sub attendanceColor {
	my $attendance = shift;
	my $attendance_type = '';
	if ($attendance > 84) {
		$attendance_type = 'high_attendance';
	} elsif ($attendance > 59) {
		$attendance_type = 'medium_attendance';
	} else {
		$attendance_type = 'low_attendance';
	}
	print "<TD class='$attendance_type' align=\"right\">$attendance%</TD>";
}

#Sitting Coloring
sub sittingColor {
	my $attendance = shift;
#	my $attendance_type = '';
#	if ($attendance > 84) {
#		$attendance_type = 'high_attendance';
#	} elsif ($attendance > 59) {
#		$attendance_type = 'medium_attendance';
#	} else {
#		$attendance_type = 'low_attendance';
#	}
	#print "<TD class='$attendance_type' align=\"right\">$attendance%</TD>";
	print "<TD class='sitting_neutral' align=\"right\">$attendance%</TD>";
}

#Loot Coloring
sub lootColor {
	my $temploot = shift;
	my $loot_type = '';
	my $bold1 = '';
	my $bold2 = '';
	if ($temploot > 0) {
		$loot_type='loot';
	} else {
		$loot_type='no_loot';
	}
	print "<TD class='$loot_type'>$temploot</TD>";
}

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

my $statement =
	$dbh->prepare(
$SQL = 
	"SELECT NAME AS NAME, " .
	"			 CLASS AS CLASS, " .
	"			 RANK AS RANK, " .
	"			MAX(CASE WHEN DAYOFWEEK = 'Wed' THEN floor((ATTENDANCE*100)/TOTAL) END) AS Wed, " .
	"			MAX(CASE WHEN DAYOFWEEK = 'Thu' THEN floor((ATTENDANCE*100)/TOTAL) END) AS Thu, " .
	"			MAX(CASE WHEN DAYOFWEEK = 'Sun' THEN floor((ATTENDANCE*100)/TOTAL) END) AS Sun, " .
	"			MAX(CASE WHEN DAYOFWEEK = 'Mon' THEN floor((ATTENDANCE*100)/TOTAL) END) AS Mon, " .
	"			MAX(CASE WHEN DAYOFWEEK = 'THUSUNMON' THEN floor((ATTENDANCE*100)/TOTAL) END) AS 'THU/SUN/MON' " .
	"FROM( " .
	"	SELECT CHR.NAME, " .
	"				 CHR.CLASS,  " .
	"				 CHR.RANK, " .
	"				 DATE_FORMAT(RC.DATE, '%a') AS DAYOFWEEK, " .
	"				 sum(length(REPLACE(RA.ATTENDANCE, '0', ''))) ATTENDANCE, " .
	"				 sum(length(RA.ATTENDANCE)) TOTAL " .
	"	FROM RAID_ATTENDANCE RA, `CHARACTER` CHR, RAID_CALENDAR RC " .
	"	WHERE RA.CHAR_ID = CHR.CHAR_ID " .
	"	AND RC.RAID_ID = RA.RAID_ID " .
	"	AND ATTENDANCE Regexp '[[:digit:]]+' <> 0 " .
	"	AND SCHEDULED = 1 " .
	"	AND RC.DATE >= DATE(DATE_SUB(LOCALTIME(),INTERVAL 60 DAY )) " .
	"	AND CHR.ACTIVE = 'Y' " .
	"	AND CHR.DATE_REMOVED IS NULL " .
	"	AND CHR.RANK NOT IN ('Friend','Alt','Officer Alt','PvPer') " .
	"	GROUP BY 1,2,3,4 " .
	"UNION " .
	"	SELECT CHR.NAME,  " .
	"				 CHR.CLASS,  " .
	"				 CHR.RANK, " .
	"				 'THUSUNMON' AS DAYOFWEEK, " .
	"				 sum(length(REPLACE(RA.ATTENDANCE, '0', ''))) ATTENDANCE, " .
	"				 sum(length(RA.ATTENDANCE)) TOTAL " .
	"	FROM RAID_ATTENDANCE RA, `CHARACTER` CHR, RAID_CALENDAR RC " .
	"	WHERE RA.CHAR_ID = CHR.CHAR_ID " .
	"	AND RC.RAID_ID = RA.RAID_ID " .
	"	AND ATTENDANCE Regexp '[[:digit:]]+' <> 0 " .
	"	AND SCHEDULED = 1 " .
	"	AND RC.DATE >= DATE(DATE_SUB(LOCALTIME(),INTERVAL 60 DAY )) " .
	"	AND CHR.ACTIVE = 'Y' " .
	"	AND CHR.DATE_REMOVED IS NULL " .
	"	AND CHR.RANK NOT IN ('Friend','Alt','Officer Alt','PvPer') " .
	"	AND DATE_FORMAT(RC.DATE, '%a') IN ('Thu','Sun','Mon') " .
	"	GROUP BY 1,2,3 " .
	"	ORDER BY 1) A1 " .
	"GROUP BY 1,2,3;");

		
#"WHERE chr.RANK not in ('Friend','Alt','Officer Alt','P.U.G.', '') " . 
#<TR>
#<TD colspan=\"3\">Character Data</TD>
#<TD colspan=\"4\">7 Day Data</TD>
#<TD colspan=\"4\">30 Day Data</TD>
#<TD colspan=\"4\">60 Day Data</TD>
#</TR>
	print <<DELIMETER;
<fieldset>
<legend><font color=white>Raiding Members</font></legend>
<form name=\"myform\" id=\"myform\" action=\"checkboxes.asp\" method=\"post\">
<script src=\"sorttable.js\"></script>\n
<TABLE class=\"sortable normal\" ALIGN=LEFT id=\"mainTable\">
<colgroup span=\"3\">
<colgroup span=\"5\" style=\"border: 3px solid #35354F;\">
<colgroup span=\"5\" style=\"border: 3px solid #35354F;\">
<colgroup span=\"5\" style=\"border: 3px solid #35354F;\">
<thead>
<TR>
<TH CLASS=\"sorttable_nosort\" style=\"display:none;\"><input type=\"checkbox\" id=\"checkall\" onclick=\"if(this.checked) checkAll(); else clearAll();\" /></TH>
<TH><U><B>Name</B></U></TH>
<TH><U><B>Class</B></U></TH>
<TH><U><B>Rank</B></U></TH>
<TH title=\"Wednesday Attendance %\"><U><B>Wed</B></U></TH>
<TH title=\"Thursday Attendance %\"><U><B>Thu</B></U></TH>
<TH title=\"Sunday Attendance %\"><U><B>Sun</B></U></TH>
<TH title=\"Monday Attendance %\"><U><B>Mon</B></U></TH>
<TH title=\"Progression Attendance %\"><U><B>THU/SUN/Mon</B></U></TH>
</thead>
<tbody>
DELIMETER

	$statement->execute() or die $dbh->errstr;
	my $counter = 0;
	my $wed = 0;
	my $thu = 0;
	my $sun = 0;
	my $mon = 0;
	my $prog = 0;
	while (my $row = $statement->fetchrow_hashref()) {
		print "<TR id=\"check_$counter\" onClick=\"toggle($counter);\" onMouseOver=\"this.className='highlight'\" onMouseOut=\"mouseHighlight($counter);\">";
		print "<TD style=\"display:none;\"><input name\"list[]\" id=\"$counter\" type=\"checkbox\" value=\"$counter\" onClick=\"toggle($counter);\" /></TD>";
		print "<TD><B><A HREF=\"char.shtml?data=$row->{NAME}\" STYLE=\"text-decoration:none\" class='member_name'> $row->{NAME} </A></B></TD>";
		classColor($row->{CLASS});
		print "<TD class='rank'>$row->{RANK}</TD>";
		#7 day stats
		attendanceColor($row->{'Wed'});
		attendanceColor($row->{'Thu'});
		attendanceColor($row->{'Sun'});
		attendanceColor($row->{'Mon'});
		attendanceColor($row->{'THU/SUN/MON'});
		print "</TR>\n";
		$counter = $counter+1;
		$wed = $wed+$row->{'Wed'};
		$thu = $thu+$row->{'Thu'};
		$sun = $sun+$row->{'Sun'};
		$mon = $mon+$row->{'Mon'};
		$prog = $prog+$row->{'THU/SUN/MON'};
	}
	print "</TBODY>";
	
	if ($counter == 0) {
		print "<TR>";
		print "<TD colspan=\"8\"><B>There have been no raids recorded in the past 60 days.</B></TD>";
		print "</TR>";
	} else {
		$wed = round($wed/$counter);
		$thu = round($thu/$counter);
		$sun = round($sun/$counter);
		$mon = round($mon/$counter);
		$prog = round($prog/$counter);

		print "<tfoot>";
		print "<TR>";
		print "<TD colspan=\"3\">";
		print "Total Raiders: $counter";
		print "</TD>";
		attendanceColor($wed);
		attendanceColor($thu);
		attendanceColor($sun);
		attendanceColor($mon);
		attendanceColor($prog);
		print "</TR>";
		print "</tfoot>";
	}

	print "</TABLE>";
	#print "<script type=\"text/javascript\">";
	#print "var t = new ScrollableTable(document.getElementById('mainTable'),100);";
	#print "</script>";
	#print "<script type=\"text/javascript\">";
	#print "var t = new SortableTable(document.getElementById('mainTable'),100);";
	#print "</script>";
	#print "</fieldset>";
	print "<BR CLEAR=all>";
	print "<input type=\"button\" name=\"Compare\" value=\"Compare Selected\" onClick=\"hideUnchecked();\">";
	print "<BR>";
	print "<input type=\"button\" name=\"Select_All\" value=\"Select All\" onClick=\"checkAll();\">";
	print "<input type=\"button\" name=\"Show_All\" value=\"Reset\" onClick=\"showAll();\">";
	print "</form>";
	print "</fieldset>";
	$statement->finish();
$dbh->disconnect();
#print "</pre>";
