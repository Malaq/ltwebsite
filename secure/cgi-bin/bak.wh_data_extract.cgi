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

my $search_item_id = param('ITEM_ID');
my $search_zone_id = param('ZONE_ID');
my $search_npc_id = param('NPC_ID');
my $search_zones_id = param('ZONES');
my $wh_url = "";
my $unit_id = "";
my $unit = "";

if ($search_item_id ne "")
{
	$wh_url = "http://www.wowhead.com/item=$search_item_id";
	$unit_id = $search_item_id;
	$unit = "Item";
}
elsif ($search_zone_id ne "")
{
	$wh_url = "http://www.wowhead.com/zone=$search_zone_id";
	$unit_id = $search_zone_id;
	$unit = "Zone";
}
elsif ($search_npc_id ne "")
{
	$wh_url = "http://www.wowhead.com/npc=$search_npc_id";
	$unit_id = $search_npc_id;
	$unit = "NPC";
}
elsif ($search_zones_id ne "")
{
	$wh_url = "http://www.wowhead.com/zones=$search_zones_id";
	$unit_id = $search_zones_id;
	$unit = "Raid Content";
}
else
{
	print "No parameters passed.  Exiting.";
	exit;
}

print "Using URL: <A HREF=\"$wh_url\" target=\"_blank\">$wh_url</A> <BR>";

#my $wh_url = "http://www.wowhead.com/zones=3.3";
#my $wh_url = "http://www.wowhead.com/item=59506";

my $html_out = get($wh_url);
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
foreach ($p->tree) {
	if ($_->{content} =~ "og:title")
	{
		my $line = $_->{content};
		if ($line =~ m/content="(.*?)"/)
		{
			$item_name = $1;
			print "$unit\[$unit_id\]: $item_name<BR>";
		}

	}
	elsif (($_->{content} eq "Heroic") && ($search_item_id ne "") && ($item_is_heroic eq ""))
	{
		my $line = $_->{content};
		print "Item is Heroic<br>";
		$item_is_heroic = "T";
	}
	elsif (($search_zones_id ne "") && ($_->{content} =~ "Zones - World of Warcraft") && ($expansion_name eq ""))
	{
		my $line = $_->{content};
		if ($line =~ m/(.+?) - Zones - World of Warcraft/)
		{
			$expansion_name = $1;
			print "Expansion name: $expansion_name<BR>";
		}
	}
	elsif (($_->{content} =~ "currency-for") || ($_->{content} =~ "dropped-by") || ($_->{content} =~ "sold-by") || ($_->{content} =~ "template: 'zone', id: 'zones'") || ($_->{content} =~ "template: 'item', id: 'drops'"))
	{
		my $line = $_->{content};
		#print "1<BR>";
		my @listviews = ($line =~ m/new Listview\(.+\)/g);
		foreach $listview (@listviews)
		{
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
						print "$purchase_item_name(level:$purchase_item_level)\[id:$purchase_item_id\]<BR>";
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
						}
						print "$npc_name\[$npc_id\] located in zone_id[$npc_zone_id]<BR>";
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
						print "$npc_name\[<A HREF=\"./wh_data_extract.cgi?NPC_ID=$npc_id\">$npc_id</A>\] located in zone_id[<A HREF=\"./wh_data_extract.cgi?ZONE_ID=$npc_zone_id\">$npc_zone_id</A>]<BR>";
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
						print get($temp_url);
						print "$npc_name\[<A HREF=\"$temp_url\">$npc_id</A>\]<BR>";
					}
				}
			}
			# Only look at items that are dropped off of bosses
			elsif (($listview =~ m/template: 'item', id: 'drops'/) && ($search_npc_id ne ""))
			{
				print "ITEMS IN ZONE<BR>";
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
							print "$npc<BR>";
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
							print "<BR>";
						}
					}
				}
			}
			elsif ($listview =~ m/template: 'npc', id: 'npcs'/)
			{
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
						}
						#do nothing with non-boss npc's
					}
				}
			}
		}
	}
}

# Database handle
#my $dbh = DBI->connect("dbi:mysql:database=$database;host=$hostname;port=$dbport", $username, $password) or print $DBI::errstr;

#$dbh->disconnect();
#print "</pre>";
