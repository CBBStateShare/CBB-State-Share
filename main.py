from sportsipy.ncaab.teams import Teams
from sportsipy.ncaab.roster import Roster
from lxml import html
import requests
import us
from collections import defaultdict
import pandas as pd
import time

team_dataframe_points = pd.DataFrame()
team_dataframe_minutes = pd.DataFrame()
i = 0
teams_list = Teams(2021)
print('%i teams in total' % len(teams_list))
for t in teams_list:
    i += 1
    teamname = t.abbreviation
    print('%s, team %i of %i' % (teamname, i, len(teams_list)))
    team_state_dict_points = defaultdict(int)
    team_total_points = 0.0
    team_state_dict_minutes = defaultdict(int)
    team_total_minutes = 0.0
    teamroster = Roster(teamname).players
    for player in teamroster:
        try:
            dframe = player.dataframe
            player_points = dframe.loc['2021-22','points']
            player_minutes = dframe.loc['2021-22','minutes_played']
        except:
            player_points = 0
            player_minutes = 0
        url = 'https://www.sports-reference.com/cbb/players/%s.html' % player.player_id
        try:
            page = requests.get(url)
        except ConnectionError:
            print('Connection Error, waiting 5 seconds')
            time.sleep(5)
            print('Resuming connection')
            page = requests.get(url)
        tree = html.fromstring(page.content)
        hometown_raw = tree.xpath('//*[@id="meta"]/div[2]/p[3]/text()')
        if not hometown_raw:
            hometown_raw = tree.xpath('//*[@id="meta"]/div/p[3]/text()')
        try:
            hometown = hometown_raw[1].strip()
            statename = str(us.states.lookup(hometown.split(',')[1].strip()))
        except IndexError:
            statename = 'None'
        if statename.strip() == 'None':
            statename = 'Non-US'
        team_state_dict_points[statename] += player_points
        team_total_points += player_points
        team_state_dict_minutes[statename] += player_minutes
        team_total_minutes += player_minutes

    for state in team_state_dict_points:
        point_share = 100 * team_state_dict_points[state] / team_total_points
        team_dataframe_points.loc[teamname, state] = '%.1f%%' % point_share
    for state in team_state_dict_minutes:
        minutes_share = 100 * team_state_dict_minutes[state] / team_total_minutes
        team_dataframe_minutes.loc[teamname, state] = '%.1f%%' % minutes_share

team_dataframe_points = team_dataframe_points.reindex(sorted(team_dataframe_points.columns), axis=1)
team_dataframe_minutes = team_dataframe_minutes.reindex(sorted(team_dataframe_minutes.columns), axis=1)

print(team_dataframe_points)
team_dataframe_points.to_csv('Teams_States-Points.csv', sep='\t', encoding='utf-8')
print(team_dataframe_minutes)
team_dataframe_minutes.to_csv('Teams_States-Minutes.csv', sep='\t', encoding='utf-8')