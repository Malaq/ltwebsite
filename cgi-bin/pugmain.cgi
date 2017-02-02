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
	    "SELECT chr.NAME, chr.CLASS, chr.RANK, " .
            "IFNULL(7da.ATTENDANCE,'0') 7day,  " .
            "IFNULL(7da.SITTING,'0') 7sit,  " .
            "IFNULL(7dl.Main_Spec,0) 7MS,  " .
            "IFNULL(7dl.Alt_Spec,0) 7AS,  " .
            "IFNULL(7dl.Off_Spec,0) 7OS,  " .
            "IFNULL(30da.ATTENDANCE,'0') 30day,  " .
            "IFNULL(30da.SITTING,'0') 30sit,  " .
            "IFNULL(30dl.Main_Spec,0) 30MS,  " .
            "IFNULL(30dl.Alt_Spec,0) 30AS,  " .
            "IFNULL(30dl.Off_Spec,0) 30OS, " .
            "IFNULL(60da.ATTENDANCE,'0') 60day,  " .
            "IFNULL(60da.SITTING,'0') 60sit,  " .
            "IFNULL(60dl.Main_Spec,0) 60MS,  " .
            "IFNULL(60dl.Alt_Spec,0) 60AS,  " .
            "IFNULL(60dl.Off_Spec,0) 60OS " .
            "FROM `CHARACTER` chr " .
            " " .
            "LEFT JOIN " .
            "(select chr.char_id, " .
            "floor((sum(length(REPLACE(ra.ATTENDANCE,'0','')))*100)/(sum(length(ra.ATTENDANCE)))) ATTENDANCE, " .
	    "floor(sum(length(REPLACE(REPLACE(ra.ATTENDANCE,'0',''),'1',''))*100)/(sum(length(ra.ATTENDANCE)))) SITTING, " .
            "concat(concat(sum(length(REPLACE(ra.ATTENDANCE, '0', ''))),'/'),sum(length(ra.ATTENDANCE))) val " .
            "from RAID_ATTENDANCE ra, RAID_CALENDAR rc, `CHARACTER` chr " .
            "where ra.raid_id = rc.raid_id  " .
            "and chr.char_id = ra.char_id " .
            "and rc.date >= DATE(DATE_SUB(LOCALTIME(),INTERVAL 7 DAY )) " .
            "and ra.ATTENDANCE Regexp '[[:digit:]]+' <> 0 " .
            "and rc.scheduled = 1 " .
            "group by chr.char_id) 7da " .
            "ON 7da.CHAR_ID = chr.CHAR_ID " .
            " " .
            "LEFT JOIN " .
            "(select chr.char_id, " .
            "IFNULL(sum(if(spec='Main', 1, 0)),0) Main_Spec,   " .
            "IFNULL(sum(if(spec='Alt', 1, 0)),0) Alt_Spec,   " .
            "IFNULL(sum(if(spec='Off', 1, 0)),0) Off_Spec  " .
            "from ITEMS_LOOTED il, RAID_CALENDAR rc, `CHARACTER` chr " . 
            "where chr.char_id = il.char_id  " .
            "and rc.raid_id = il.raid_id  " .
            "and rc.date >= DATE(DATE_SUB(LOCALTIME(),INTERVAL 7 DAY )) " . 
            "and rc.scheduled = 1  " .
            "group by chr.char_id) 7dl " .
            "ON 7dl.CHAR_ID = chr.CHAR_ID " .
            " " .
            "LEFT JOIN " .
            "(select chr.char_id, " .
            "floor((sum(length(REPLACE(ra.ATTENDANCE,'0','')))*100)/(sum(length(ra.ATTENDANCE)))) ATTENDANCE, " .
	    "floor(sum(length(REPLACE(REPLACE(ra.ATTENDANCE,'0',''),'1',''))*100)/(sum(length(ra.ATTENDANCE)))) SITTING, " .
            "concat(concat(sum(length(REPLACE(ra.ATTENDANCE, '0', ''))),'/'),sum(length(ra.ATTENDANCE))) val " .
            "from RAID_ATTENDANCE ra, RAID_CALENDAR rc, `CHARACTER` chr " .
            "where ra.raid_id = rc.raid_id " . 
            "and chr.char_id = ra.char_id " .
            "and rc.date >= DATE(DATE_SUB(LOCALTIME(),INTERVAL 30 DAY )) " .
            "and ra.ATTENDANCE Regexp '[[:digit:]]+' <> 0 " .
            "and rc.scheduled = 1 " .
            "group by chr.char_id) 30da " .
            "ON 30da.CHAR_ID = chr.CHAR_ID " .
            " " .
            "LEFT JOIN " .
            "(select chr.char_id, " .
            "IFNULL(sum(if(spec='Main', 1, 0)),0) Main_Spec, " .  
            "IFNULL(sum(if(spec='Alt', 1, 0)),0) Alt_Spec, " .  
            "IFNULL(sum(if(spec='Off', 1, 0)),0) Off_Spec " . 
            "from ITEMS_LOOTED il, RAID_CALENDAR rc, `CHARACTER` chr " . 
            "where chr.char_id = il.char_id " . 
            "and rc.raid_id = il.raid_id " . 
            "and rc.date >= DATE(DATE_SUB(LOCALTIME(),INTERVAL 30 DAY )) " . 
            "and rc.scheduled = 1  " .
            "group by chr.char_id) 30dl " .
            "ON 30dl.CHAR_ID = chr.CHAR_ID " .
            " " .
            "LEFT JOIN " .
            "(select chr.char_id, " .
            "floor((sum(length(REPLACE(ra.ATTENDANCE,'0','')))*100)/(sum(length(ra.ATTENDANCE)))) ATTENDANCE, " .
	    "floor(sum(length(REPLACE(REPLACE(ra.ATTENDANCE,'0',''),'1',''))*100)/(sum(length(ra.ATTENDANCE)))) SITTING, " .
            "concat(concat(sum(length(REPLACE(ra.ATTENDANCE, '0', ''))),'/'),sum(length(ra.ATTENDANCE))) val " .
            "from RAID_ATTENDANCE ra, RAID_CALENDAR rc, `CHARACTER` chr " .
            "where ra.raid_id = rc.raid_id  " .
            "and chr.char_id = ra.char_id " .
            "and rc.date >= DATE(DATE_SUB(LOCALTIME(),INTERVAL 60 DAY )) " .
            "and ra.ATTENDANCE Regexp '[[:digit:]]+' <> 0 " .
            "and rc.scheduled = 1 " .
            "group by chr.char_id) 60da " .
            "ON 60da.CHAR_ID = chr.CHAR_ID " .
            " " .
            "LEFT JOIN " .
            "(select chr.char_id, " .
            "IFNULL(sum(if(spec='Main', 1, 0)),0) Main_Spec,   " .
            "IFNULL(sum(if(spec='Alt', 1, 0)),0) Alt_Spec,   " .
            "IFNULL(sum(if(spec='Off', 1, 0)),0) Off_Spec  " .
            "from ITEMS_LOOTED il, RAID_CALENDAR rc, `CHARACTER` chr " . 
            "where chr.char_id = il.char_id  " .
            "and rc.raid_id = il.raid_id  " .
            "and rc.date >= DATE(DATE_SUB(LOCALTIME(),INTERVAL 60 DAY )) " . 
            "and rc.scheduled = 1  " .
            "group by chr.char_id) 60dl " .
            "ON 60dl.CHAR_ID = chr.CHAR_ID " .
            "WHERE chr.RANK not in ('Friend','Alt','Officer Alt','P.U.G.','PvPer','') " . 
            "AND chr.DATE_REMOVED IS NULL " . 
            "AND chr.ACTIVE = 'Y' " . 
	    "OR (chr.RANK in ('Friend','PvPer','P.U.G.','Alt') " .
	    "AND IFNULL(30dl.Main_Spec,0)+IFNULL(30dl.Alt_Spec,0)+IFNULL(30dl.Off_Spec,0) <> 0 )" .
            "ORDER BY chr.NAME;");

		
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
<TH><U><B>7 Day Attn</B></U></TH>
<TH title=\"7 Day Benched %\"><U><B>Sit</B></U></TH>
<TH title=\"Main Spec Loot\"><U><B>MS</B></U></TH>
<TH title=\"Alternate Spec Loot\"><U><B>AS</B></U></TH>
<TH title=\"Off Spec Loot\"><U><B>OS</B></U></TH>
<TH><U><B>30 Day Attn</B></U></TH>
<TH title=\"30 Day Benched %\"><U><B>Sit</B></U></TH>
<TH title=\"Main Spec Loot\"><U><B>MS</B></U></TH>
<TH title=\"Alternate Spec Loot\"><U><B>AS</B></U></TH>
<TH title=\"Off Spec Loot\"><U><B>OS</B></U></TH>
<TH><U><B>60 Day Attn</B></U></TH>
<TH title=\"60 Day Benched %\"><U><B>Sit</B></U></TH>
<TH title=\"Main Spec Loot\"><U><B>MS</B></U></TH>
<TH title=\"Alternate Spec Loot\"><U><B>AS</B></U></TH>
<TH title=\"Off Spec Loot\"><U><B>OS</B></U></TH></TR>\n
</thead>
<tbody>
DELIMETER

	$statement->execute() or die $dbh->errstr;
	my $counter = 0;
	my $ms7d = 0;
	my $as7d = 0;
	my $os7d = 0;
	my $avg7d = 0;
	my $avg7sit= 0;
	my $ms30d = 0;
	my $as30d = 0;
	my $os30d = 0;
	my $avg30d = 0;	
	my $avg30sit= 0;
	my $ms60d = 0;
	my $as60d = 0;
	my $os60d = 0;
	my $avg60d = 0;
	my $avg60sit= 0;
	while (my $row = $statement->fetchrow_hashref()) {
		#print "<TR onMouseOver=\"this.className='highlight'\" onMouseOut=\"this.className='normal'\" onclick=\"location.href='char.shtml?data=$row->{NAME}'\">";
		print "<TR id=\"check_$counter\" onClick=\"toggle($counter);\" onMouseOver=\"this.className='highlight'\" onMouseOut=\"mouseHighlight($counter);\">";
		#print "<TD><input name\"list[]\" id=\"$counter\" type=\"checkbox\" value=\"$counter\" onClick=\"highlightRow(this);\" /></TD>";
		print "<TD style=\"display:none;\"><input name\"list[]\" id=\"$counter\" type=\"checkbox\" value=\"$counter\" onClick=\"toggle($counter);\" /></TD>";
		print "<TD><B><A HREF=\"char.shtml?data=$row->{NAME}\" STYLE=\"text-decoration:none\" class='member_name'> $row->{NAME} </A></B></TD>";
		classColor($row->{CLASS});
		print "<TD class='rank'>$row->{RANK}</TD>";
		#7 day stats
		attendanceColor($row->{'7day'});
		sittingColor($row->{'7sit'});
		lootColor($row->{'7MS'});
		lootColor($row->{'7AS'});
		lootColor($row->{'7OS'});
		#30 day stats
		attendanceColor($row->{'30day'});
		sittingColor($row->{'30sit'});
		lootColor($row->{'30MS'});
		lootColor($row->{'30AS'});
		lootColor($row->{'30OS'});
		#60 day stats
		attendanceColor($row->{'60day'});
		sittingColor($row->{'60sit'});
		lootColor($row->{'60MS'});
		lootColor($row->{'60AS'});
		lootColor($row->{'60OS'});
		print "</TR>\n";
		$counter = $counter+1;
		$avg7d = $avg7d+$row->{'7day'};
		$avg7sit = $avg7sit+$row->{'7sit'};
		$ms7d = $ms7d+$row->{'7MS'};
		$as7d = $as7d+$row->{'7AS'};
		$os7d = $os7d+$row->{'7OS'};
		$avg30d = $avg30d+$row->{'30day'};	
		$avg30sit = $avg30sit+$row->{'30sit'};	
		$ms30d = $ms30d+$row->{'30MS'};
		$as30d = $as30d+$row->{'30AS'};
		$os30d = $os30d+$row->{'30OS'};
		$avg60d = $avg60d+$row->{'60day'};
		$avg60sit = $avg60sit+$row->{'60sit'};
		$ms60d = $ms60d+$row->{'60MS'};
		$as60d = $as60d+$row->{'60AS'};
		$os60d = $os60d+$row->{'60OS'};
	}
	print "</TBODY>";
	$avg7d = round($avg7d/$counter);
	$avg7sit = round($avg7sit/$counter);
	$avg30d = round($avg30d/$counter);
	$avg30sit = round($avg30sit/$counter);
	$avg60d = round($avg60d/$counter);
	$avg60sit = round($avg60sit/$counter);
	print "<tfoot>";
	print "<TR>";
	print "<TD colspan=\"3\">";
	print "Total Raiders: $counter";
	print "</TD>";
	attendanceColor($avg7d);
	sittingColor($avg7sit);
	lootColor($ms7d);
	lootColor($as7d);
	lootColor($os7d);
	attendanceColor($avg30d);
	sittingColor($avg30sit);
	lootColor($ms30d);
	lootColor($as30d);
	lootColor($os30d);
	attendanceColor($avg60d);
	sittingColor($avg60sit);
	lootColor($ms60d);
	lootColor($as60d);
	lootColor($os60d);
	print "</TR>";
	print "</tfoot>";
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
