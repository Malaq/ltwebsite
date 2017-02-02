#!/usr/bin/perlml

# The libraries we're using
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use DBI;
use LWP::Simple;
use HTML::SimpleParse;


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

sub URLEncode {
my $theURL = $_[0];
$theURL =~ s/([\W])/"%" . uc(sprintf("%2.2x",ord($1)))/eg;
return $theURL;
}

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

sub zoneExist
{
	my $zone_id = shift;
	if ($zone_id eq "")
	{
		return "F";
	}

	$SQL = 
	$dbh->prepare("SELECT ZONE_ID " .
			"FROM ZONES " .
			"WHERE ZONE_ID = ?;");
	$SQL->bind_param(1,$zone_id);
	$SQL->execute() or print $dbh->errstr;

	my $row = $SQL->fetchrow_hashref();
	print "Zone ids: $row->{ZONE_ID}, $zone_id;";
	if ($row->{ZONE_ID} eq $zone_id)
	{
		return "T";
	}
	else
	{
		return "F";
	}
}

sub insertZone{
	my $zone_id = shift;
	my $zone_name = shift;
	my $expansion_id = shift;

	$SQL = 
	$dbh->prepare("INSERT INTO ZONES(ZONE_ID, ZONE_NAME, EXPANSION_ID) " .
		      "VALUES (?, ?, ?);");
	$SQL->bind_param(1,$zone_id);
	$SQL->bind_param(2,$zone_name);
	$SQL->bind_param(3,$expansion_id);
	$SQL->execute() or print $dbh->errstr;
}

sub insertItem{
	my $item_id = shift;
	my $item_name = shift;
	my $item_level = shift;
	my $heroic = shift;
	my $is_heroic = "F";

	if ($herioc eq "(Heroic(1))")
	{
		$is_heroic = "T";
	}

	$SQL = 
	$dbh->prepare("SELECT ITEM_ID, ITEM_NAME, ITEM_LEVEL, IS_HEROIC " .
		      "FROM ITEM " .
		      "WHERE ITEM_ID = ?;");
	$SQL->bind_param(1,$item_id);
	$SQL->execute() or print $dbh->errstr;
	my $row = $SQL->fetchrow_hashref();

	if ($row->{ITEM_ID} eq $item_id)
	{
		if ((($row->{ITEM_NAME} ne $item_name) || ($row->{ITEM_LEVEL} ne $item_level) || ($row->{IS_HEROIC} ne $is_heroic)) && ($item_level ne "0") && ($item_level ne ""))
		{
			print "UPDATE ITEM HERE!!!! OLD DB item: I_N: $row->{ITEM_NAME}, I_L: $row->{ITEM_LEVEL}, IS_H: $row->{IS_HEROIC} <BR>";
			#print "UPDATE ITEM HERE!!!! NEW DB item: I_N: $item_name, I_L: $item_level, IS_H: $is_heroic <BR>";
			$SQL = 
			$dbh->prepare("UPDATE ITEM " .
					"SET ITEM_NAME = ?, " .
					"    ITEM_LEVEL = ?, " .
					"    IS_HEROIC = ? " .
					"WHERE ITEM_ID = ?;");
			$SQL->bind_param(1,$item_name);
			$SQL->bind_param(2,$item_level);
			$SQL->bind_param(3,$is_heroic);
			$SQL->bind_param(4,$item_id);
			$SQL->execute() or print $dbh->errstr;
		}
	}
	else
	{
		$SQL = 
		$dbh->prepare("INSERT INTO ITEM(ITEM_ID, ITEM_NAME, ITEM_LEVEL, IS_HEROIC) " .
			      "VALUES (?, ?, ?, ?);");
		$SQL->bind_param(1,$item_id);
		$SQL->bind_param(2,$item_name);
		$SQL->bind_param(3,$item_level);
		$SQL->bind_param(4,$is_heroic);
		$SQL->execute() or print $dbh->errstr;
	}
}

sub insertSource{
	my $item_id = shift;
	my $npc_id = shift;
	my $source_id = shift;
	my $source_type = shift;


	#$SQL = 
	#$dbh->prepare("INSERT INTO ITEM_SOURCES(ITEM_ID, NPC_ID, SOURCE_ID, SOURCE_TYPE) " .
	#	      "VALUES (?, ?, ?, ?);");
	$SQL = 
	$dbh->prepare("INSERT INTO ITEM_SOURCES(ITEM_ID, NPC_ID, SOURCE_ID, SOURCE_TYPE) " .
		      "VALUES (?, ?, ?, ?) " .
		      "ON DUPLICATE KEY " .
		      "UPDATE SOURCE_TYPE = ?;");
	$SQL->bind_param(1,$item_id);
	$SQL->bind_param(2,$npc_id);
	$SQL->bind_param(3,$source_id);
	$SQL->bind_param(4,$source_type);
	$SQL->bind_param(5,$source_type);
	$SQL->execute() or print $dbh->errstr;
}

sub insertCurrency{
	my $source_item_id = shift;
	my $reward_item_id = shift;

	$SQL = 
	$dbh->prepare("INSERT INTO CURRENCY_FOR(SOURCE_ITEM_ID, REWARD_ITEM_ID) " .
		      "VALUES (?, ?);");
	$SQL->bind_param(1,$source_item_id);
	$SQL->bind_param(2,$reward_item_id);
	$SQL->execute() or print $dbh->errstr;
}

sub insertNPC{
	my $npc_id = shift;
	my $npc_name = shift;
	my $zone_id = shift;
	my $is_boss = shift;

	$SQL = 
	$dbh->prepare("INSERT INTO NPC(NPC_ID, NPC_NAME, IS_BOSS) " .
		      "VALUES (?, ?, ?);");
	$SQL->bind_param(1,$npc_id);
	$SQL->bind_param(2,$npc_name);
	$SQL->bind_param(3,$is_boss);
	$SQL->execute() or print $dbh->errstr;

	if ($zone_id ne "")
	{
		$SQL = 
		$dbh->prepare("INSERT INTO NPC_IN_ZONE(NPC_ID, ZONE_ID) " .
			      "VALUES (?, ?);");
		$SQL->bind_param(1,$npc_id);
		$SQL->bind_param(2,$zone_id);
		$SQL->execute() or print $dbh->errstr;
	}
}

sub insertExpansion{
	my $expansion_id = shift;
	my $expansion_name = shift;
	my $wowhead_id = shift;

	$SQL = 
	$dbh->prepare("INSERT INTO EXPANSION(EXPANSION_ID, EXPANSION_NAME, WOWHEAD_ID) " .
		      "VALUES (?, ?, ?);");
	$SQL->bind_param(1,$expansion_id);
	$SQL->bind_param(2,$expansion_name);
	$SQL->bind_param(3,$wowhead_id);
	$SQL->execute() or print $dbh->errstr;
}

sub getTierBIS{
	my $tier_id = shift;

	$SQL =
	$dbh->prepare("SELECT bi.ITEM_ID " .
		"FROM BIS_ITEMS bi, BIS_LISTS bl " .
		"where bi.BIS_LIST_ID = bl.BIS_LIST_ID " .
		"  and bl.TIER_ID = ? " .
		"  and bl.ACTIVE_FLAG = 'T' " .
		"  and bi.ITEM_ID <> 0 " .
		"group by bi.ITEM_ID;");
	
	$SQL->bind_param(1,$tier_id);
	$SQL->execute() or print $dbh->errstr;
	while (my $row = $SQL->fetchrow_hashref()) {
		#print "$row->{ITEM_ID}<BR>";
		get_and_parse_html($row->{ITEM_ID}, "Item");
	}
		
}

my $search_item_id = param('ITEM_ID');
my $search_zone_id = param('ZONE_ID');
my $search_npc_id = param('NPC_ID');
my $search_zones_id = param('ZONES');
my $bis_tier_id = param('BIS_TIER');
my $xml = "F";

sub get_and_parse_html {
my $wh_url = "";
my $unit_id = shift or "";
my $unit = shift or "";

if (($search_item_id ne "") || ($unit eq "Item"))
{
#	$search_item_id = $unit_id;
	$wh_url = "http://www.wowhead.com/item=${search_item_id}${unit_id}";
	$unit_id = "${search_item_id}${unit_id}";
	$unit = "Item";
}
elsif (($search_item_id ne "") || ($unit eq "ItemXML"))
{
#	$search_item_id = $unit_id;
	print "Item XML $unit_id, $search_item_id";
	$wh_url = "http://www.wowhead.com/item=${unit_id}&xml";
	$unit_id = "${search_item_id}${unit_id}";
	$unit = "ItemXML";
	$xml = "T";
}
elsif (($search_zone_id ne "") || ($unit eq "Zone"))
{
#	$search_zone_id = $unit_id;
	$wh_url = "http://www.wowhead.com/zone=${search_zone_id}${unit_id}";
	$unit_id = "${search_zone_id}${unit_id}";
	$unit = "Zone";
}
elsif (($search_npc_id ne "") || ($unit eq "NPC"))
{
#	$search_npc_id = $unit_id;
	$wh_url = "http://www.wowhead.com/npc=${search_npc_id}${unit_id}";
	$unit_id = "${search_npc_id}${unit_id}";
	$unit = "NPC";
}
elsif (($search_zones_id ne "") || ($unit eq "Raid Content"))
{
#	$search_zones_id = $unit_id;
	$wh_url = "http://www.wowhead.com/zones=${search_zones_id}${unit_id}";
	$unit_id = "${search_zones_id}${unit_id}";
	$unit = "Raid Content";
}
elsif ($ARGV[0] eq "ITEM")
{
	print "Parsing item, please wait...<BR>";
	#get_and_parse_html($ARGV[1], "ItemXML");
	get_and_parse_html($ARGV[1], "Item");
	exit;
}
elsif ($bis_tier_id ne "")
{
	print "Parsing tier $bis_tier_id<BR>";
	print "DO NOT CLICK ANY LINKS, please let this page finish loading.<BR>";
	print "You will be returned to the BIS list page once it is complete. <BR><BR>";
	#getTierBIS($bis_tier_id);

	my $tier_id = $bis_tier_id;

	#bug in recursive calls.  SQL was being hijacked by another subprogram
	#renaming it allowed recursive calls to work.
	$SQL1 =
	$dbh->prepare("SELECT bi.ITEM_ID " .
		"FROM BIS_ITEMS bi, BIS_LISTS bl " .
		"where bi.BIS_LIST_ID = bl.BIS_LIST_ID " .
		"  and bl.TIER_ID = ? " .
		"  and bl.ACTIVE_FLAG = 'T' " .
		"  and bi.ITEM_ID <> 0 " .
		"group by bi.ITEM_ID;");
	
	$SQL1->bind_param(1,$tier_id);
	$SQL1->execute() or print $dbh->errstr;
	while (my $row = $SQL1->fetchrow_hashref()) {
		print "$row->{ITEM_ID}<BR>";
		get_and_parse_html($row->{ITEM_ID}, "Item");
	}
	
	print "<head><meta HTTP-EQUIV=\"REFRESH\" content=\"0; url=../bis.shtml?TIER_ID=$tier_id\"></head>";
	exit;
}
else
{
	print "No parameters passed.  Exiting.";
	$dbh->disconnect();
	exit;
}

$search_item_id = "";
$search_zone_id = "";
$search_npc_id = "";
$search_zones_id = "";

	my $in_url = $wh_url;
#	my $unit_id = shift;
#	my $unit = shift;
#print "Using URL: <A HREF=\"$wh_url\" target=\"_blank\">$wh_url</A> <BR>";
print "Using URL: <A HREF=\"$in_url\" target=\"_blank\">$in_url</A> <BR>";
print "Unit: $unit <BR>";

#my $wh_url = "http://www.wowhead.com/zones=3.3";
#my $wh_url = "http://www.wowhead.com/item=59506";

my $html_out = get($in_url);
#$html_out =~ s/\n/\r/g;
#my @item_string = grep { "g_getIngameLink" } $html_out;

#print @item_string;
#exit;

open(OUTF,">input.txt") or &dienice("Can't open input.txt for writing: $!");
print OUTF $html_out;
close(OUTF);

$p = new HTML::SimpleParse( $html_out, 'fix_case' => -1);
$p->text( $html_out );
$p->parse;
#%hash = $p->parse_args( $html_out );
#$p->output;
#
#
# It seems that this is looping through things but not finding all the line breaks.  I believe the parser
# is breaking things up by HTML tags only.  We need to break down some things even further than that.
# 
my $item_name = "";
my $expansion_name = "";
my $item_is_heroic = "";
if ($xml eq "T")
{
	print "Parsing XML<BR>";
	foreach ($p->tree) 
	{
		print "mlc - $_->{content}<BR>";
	}
}
else
{
foreach ($p->tree) {
	if ($_->{content} =~ "og:title")
	{
		my $line = $_->{content};
		if ($line =~ m/content="(.*?)"/)
		{
			#Zone Name, Item Name, Whatever the title of the page is.
			$item_name = $1;
			print "1 - $unit\[$unit_id\]: $item_name<BR>";
			if ($unit eq "NPC")
			{
				insertNPC($unit_id, $item_name, "", "F");
			}
			elsif($unit eq "Zone")
			{
				insertZone($unit_id, $item_name, "");
			}
			elsif($unit eq "Item")
			{
				insertItem($unit_id, $item_name, "", "");
				#Commented back in for BIS list population, however this will result in empty item levels until the game parses them.
			}
			elsif($unit eq "Raid Content")
			{
				insertExpansion($unit_id, $item_name, $unit_id);
			}
		}

	}
#	elsif ($_->{content} =~ "lkafdnmsd")
#	{
#		my $npcs = "";
#		my $npcs_id = "";
#		my $line = $_->{content};
#	
#		if ($line =~ m/"name_enus"/)
#		{
#			print "<BR>MLCMIN_TEST: $line<BR>";
#	
#			foreach $npcs ($line =~ m/name_enus:'(.+?)'/g)
#			{
#				print "MLCMIN";
#				print "<BR>Line: $npcs in zone $unit_id<BR>";
#			}
#	
#		}
#	}
	elsif (($_->{content} eq "Heroic") && ($unit eq "Item") && ($item_is_heroic eq ""))
	{
		#I don't see this line in the last run
		my $line = $_->{content};
		print "Item is Heroic<br>";
		$item_is_heroic = "T";
	}
	elsif (($unit eq "Raid Content") && ($_->{content} =~ "Zones - World of Warcraft") && ($expansion_name eq ""))
	{
		#Expansion Prints here
		my $line = $_->{content};
		if ($line =~ m/(.+?) - Zones - World of Warcraft/)
		{
			$expansion_name = $1;
			print "Expansion name: $expansion_name<BR>";
			insertExpansion($unit_id, $expansion_name, $unit_id);
		}
	}
	elsif (($_->{content} =~ "currency-for") || ($_->{content} =~ "dropped-by") || ($_->{content} =~ "sold-by") || ($_->{content} =~ "template: 'zone', id: 'zones'") || ($_->{content} =~ "template: 'item', id: 'drops'") || ($_->{content} =~ "template: 'item', id: 'sells'"))
	{
		#This seems to be item sources
		my $line = $_->{content};
		#print "1<BR>";
		my @listviews = ($line =~ m/new Listview\(.+\)/g);
		foreach $listview (@listviews)
		{
			#print "mlc - $listview<BR>";
			print "<BR>";
			# At this point the listviews are broken up, now you have to determine which is dropped-by, sold-by, and currency-for
			if ($listview =~ m/id: 'currency-for'/)
			{
				print "CURRENCY FOR<BR>";
				foreach $npcs ($listview =~ m/data: \[(.+)\]/g)
				{
					#Break down the list of NPCs to individuals
					foreach $npc ($npcs =~ m/{(.+?)}/g)
					{
						my $purchase_item_name = "";
						my $purchase_item_id = "";
						my $npc_zone_id = "";
						if ($npc =~ m/"name":"\d(.+?)"/)
						{
							$purchase_item_name = $1;
						}
						if ($npc =~ m/"id":(.+?),/)
						{
							$purchase_item_id = $1;
						}
						if ($npc =~ m/"location":\[(.+?)\]/)
						{
							$npc_zone_id = $1;
						}
						if ($npc =~ m/"level":(.+?),/)
						{
							$purchase_item_level = $1;
						}
						print "$unit_id - $purchase_item_name(level:$purchase_item_level)\[id:<A HREF=\"./wh_data_extract.cgi?ITEM_ID=$purchase_item_id\">$purchase_item_id</A>\]<BR>";
						insertCurrency($unit_id, $purchase_item_id);
						print "<BR>";
					}
				}
			}
			elsif ($listview =~ m/id: 'sold-by'/)
			{
				print "SOLD BY<BR>";
				foreach $npcs ($listview =~ m/data: \[(.+)\]/g)
				{
					#Break down the list of NPCs to individuals
					foreach $npc ($npcs =~ m/{(.+?)}/g)
					{
						my $npc_name = "";
						my $npc_id = "";
						my $npc_zone_id = "";
						if ($npc =~ m/"name":"(.+?)"/)
						{
							$npc_name = $1;
						}
						if ($npc =~ m/"id":(.+?),/)
						{
							$npc_id = $1;
						}
						if ($npc =~ m/"location":\[(.+?)\]/)
						{
							$npc_zone_id = $1;
							if ($npc_zone_id =~ m/(.+?),/)
							{
								$npc_zone_id = $1;
							}
						}
						print "$npc_name\[<A HREF=\"./wh_data_extract.cgi?NPC_ID=$npc_id\">$npc_id</A>\] located in zone_id[<A HREF=\"./wh_data_extract.cgi?ZONE_ID=$npc_zone_id\">$npc_zone_id</A>]<BR>";
						insertNPC($npc_id, $npc_name, $npc_zone_id, "F");
						insertSource($unit_id, $npc_id, "", "SOLD");

						my $zone_exists = zoneExist($npc_zone_id);
						if ($zone_exists eq "F")
						{
							get_and_parse_html($npc_zone_id, "Zone");
						}
						else
						{
							print "Zone already exists in DB";
						}
					}
				}
			}
			elsif ($listview =~ m/id: 'dropped-by'/)
			{
				print "DROPPED BY<BR>";
				foreach $npcs ($listview =~ m/data: \[(.+)\]/g)
				{
					#Break down the list of NPCs to individuals
					foreach $npc ($npcs =~ m/{(.+?)}/g)
					{
						my $npc_name = "";
						my $npc_id = "";
						my $npc_zone_id = "";
						my $is_boss = "F";
						if ($npc =~ m/"name":"(.+?)"/)
						{
							$npc_name = $1;
						}
						if ($npc =~ m/"id":(.+?),/)
						{
							$npc_id = $1;
						}
						if ($npc =~ m/"location":\[(.+?)\]/)
						{
							$npc_zone_id = $1;
						}
						if ($npc =~ m/"boss":\[(.+?)\]/)
						{
							$is_boss = "T";
						}
						print "$npc_name\[<A HREF=\"./wh_data_extract.cgi?NPC_ID=$npc_id\">$npc_id</A>\] located in zone_id[<A HREF=\"./wh_data_extract.cgi?ZONE_ID=$npc_zone_id\">$npc_zone_id</A>]<BR>";

						insertNPC($npc_id, $npc_name, $npc_zone_id, $is_boss);
						insertSource($unit_id, $npc_id, "", "DROP");
						#I do not have a recursive call here, because you likely got to this section
						#by seeing the item as an item off a boss, this could cause an infinite recursive loop.
					}
				}
			}
			elsif ($listview =~ m/template: 'zone', id: 'zones'/)
			{
				print "ZONES IN CONTENT<BR>";
				foreach $npcs ($listview =~ m/data: \[(.+)\]/g)
				{
					#Break down the list of NPCs to individuals
					foreach $npc ($npcs =~ m/{(.+?)}/g)
					{
						my $npc_name = "";
						my $npc_id = "";
						my $npc_zone_id = "";
						if ($npc =~ m/"name":"(.+?)"/)
						{
							$npc_name = $1;
						}
						if ($npc =~ m/"id":(.+?),/)
						{
							$npc_id = $1;
						}
						if ($npc =~ m/"location":\[(.+?)\]/)
						{
							$npc_zone_id = $1;
						}
						my $temp_url = "./wh_data_extract.cgi?ZONE_ID=$npc_id";
						#print get($temp_url);
						print "$npc_name\[<A HREF=\"$temp_url\">$npc_id</A>\]<BR>";

						insertZone($npc_id, $npc_name, $unit_id);

						get_and_parse_html($npc_id, "Zone");
					}
				}
			}
			# Only look at items that are dropped off of bosses
			#elsif (($listview =~ m/template: 'item', id: 'drops'/) && ($search_npc_id ne ""))
			elsif (($listview =~ m/template: 'item', id: 'drops'/) && ($unit eq "NPC"))
			#elsif (($listview =~ m/template: 'item', id: 'drops'/))
			{
				#print "ITEMS IN ZONE<BR>";
				print "DROPS ITEMS:<BR>";
				#print "Unit: $unit <BR>";
				foreach $npcs ($listview =~ m/data: \[(.+)\]/g)
				{
					#Break down the list of NPCs to individuals
					foreach $npc ($npcs =~ m/{(.+?)}/g)
					{
						my $npc_name = "";
						my $npc_id = "";
						my $npc_zone_id = "";
						my $ilevel = "";
						my $is_herioc = "";
						if ($npc =~ m/"name":"\d(.+?)"/)
						{
							$npc_name = $1;
						}
						if ($npc =~ m/"id":(.+?),/)
						{
							$npc_id = $1;
						}
						if ($npc =~ m/"location":\[(.+?)\]/)
						{
							$npc_zone_id = $1;
						}
						if ($npc =~ m/"level":(.+?),/)
						{
							$ilevel = $1;
						}
						if ($npc =~ m/"heroic":(.+?),/)
						{
							#print "$npc<BR>";
							$is_heroic = "(Heroic($1))";
						}
						else
						{
							$is_heroic = "";
						}
						if ($npc_name ne "")
						{
							#print "$npc<BR>";
							print "$npc_name\[<A HREF=\"./wh_data_extract.cgi?ITEM_ID=$npc_id\">$npc_id</A>\] Item Level: $ilevel $is_heroic<BR>";
							insertItem($npc_id, $npc_name, $ilevel, $is_heroic);
							insertSource($npc_id, $unit_id , "", "DROP");
							print "<BR>";

							#Do not comment this line back in until you can control it.  This will cause a recursive search of nearly the entire wowhead website.
							get_and_parse_html($npc_id, "Item");
						}
					}
				}
			}
			elsif (($listview =~ m/template: 'item', id: 'sells'/) && ($unit eq "NPC"))
			#elsif (($listview =~ m/template: 'item', id: 'drops'/))
			{
				#print "ITEMS IN ZONE<BR>";
				print "SELLS ITEMS:<BR>";
				#print "Unit: $unit <BR>";
				foreach $npcs ($listview =~ m/data: \[(.+)\]/g)
				{
					#Break down the list of NPCs to individuals
					foreach $npc ($npcs =~ m/{(.+?)}/g)
					{
						my $npc_name = "";
						my $npc_id = "";
						my $npc_zone_id = "";
						my $ilevel = "";
						my $is_herioc = "";
						if ($npc =~ m/"name":"\d(.+?)"/)
						{
							$npc_name = $1;
						}
						if ($npc =~ m/"id":(.+?),/)
						{
							$npc_id = $1;
						}
						if ($npc =~ m/"location":\[(.+?)\]/)
						{
							$npc_zone_id = $1;
						}
						if ($npc =~ m/"level":(.+?),/)
						{
							$ilevel = $1;
						}
						if ($npc =~ m/"heroic":(.+?),/)
						{
							#print "$npc<BR>";
							$is_heroic = "(Heroic($1))";
						}
						else
						{
							$is_heroic = "";
						}
						if ($npc_name ne "")
						{
							#print "$npc<BR>";
							print "$npc_name\[<A HREF=\"./wh_data_extract.cgi?ITEM_ID=$npc_id\">$npc_id</A>\] Item Level: $ilevel $is_heroic<BR>";
							insertItem($npc_id, $npc_name, $ilevel, $is_heroic);
							insertSource($npc_id, $unit_id , "", "SOLD");
							print "<BR>";

							#Do not comment this line back in until you can control it.  This will cause a recursive search of nearly the entire wowhead website.
							get_and_parse_html($npc_id, "Item");
						}
					}
				}
			}
			elsif ($listview =~ m/template: 'npc', id: 'npcs'/)
			{
				#NPC's go here
				print "Bosses in zone:<BR>";
				foreach $npcs ($listview =~ m/data: \[(.+)\]/g)
				{
					#Break down the list of NPCs to individuals
					foreach $npc ($npcs =~ m/{(.+?)}/g)
					{
						my $npc_name = "";
						my $npc_id = "";
						my $npc_zone_id = "";
						my $is_boss = "";
						#print "9 $npc<BR>";
						if ($npc =~ m/"boss":(.+?),/)
						{
							$is_boss = $1;
						
							if ($npc =~ m/"name":"(.+?)"/)
							{
								$npc_name = $1;
							}
							if ($npc =~ m/"id":(.+?),/)
							{
								$npc_id = $1;
							}
							if ($npc =~ m/"location":\[(.+?)\]/)
							{
								$npc_zone_id = $1;
							}
							#print "$npc_name\[<A HREF=\"http://www.wowhead.com/npc=$npc_id\">$npc_id</A>\]<BR>";
							print "$npc_name\[<A HREF=\"./wh_data_extract.cgi?NPC_ID=$npc_id\">$npc_id</A>\]<BR>";

							insertNPC($npc_id, $npc_name, $unit_id, "T");

							get_and_parse_html($npc_id, "NPC");
						}
						#do nothing with non-boss npc's
					}
				}
			}
		}
	}
}
}
}

get_and_parse_html();

# Database handle
#my $dbh = DBI->connect("dbi:mysql:database=$database;host=$hostname;port=$dbport", $username, $password) or print $DBI::errstr;

#$dbh->disconnect();
#print "</pre>";
