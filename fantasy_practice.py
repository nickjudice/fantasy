import requests
import pandas as pd
import numpy as np

def winner(x):
  if x>0:
    return 'W'
  if x==0:
    return 'Tie'
  else:
    return 'L'

def get_season(year_):

  #api
  league_id = 124582
  year = year_
  url = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/" + str(league_id) + "?seasonId=" + str(year)
        
  r = requests.get(url, params={"view": "mMatchup"})
  d = r.json()[0]
  
  #unroll json
  df = [[
        game['matchupPeriodId'],
        game['home']['teamId'], game['home']['totalPoints'],
        game['away']['teamId'], game['away']['totalPoints']
      ] for game in d['schedule']]
  df = pd.DataFrame(df, columns=['Week', 'Team1', 'Score1', 'Team2', 'Score2'])
  
  #calculate margins and wins
  df3 = df.assign(Margin1 = df['Score1'] - df['Score2'],
                  Margin2 = df['Score2'] - df['Score1'])
                  
  df3 = (df3[['Week', 'Team1', 'Margin1']]
    .rename(columns={'Team1': 'Team', 'Margin1': 'Margin'})
    .append(df3[['Week', 'Team2', 'Margin2']]
    .rename(columns={'Team2': 'Team', 'Margin2': 'Margin'})))
    
  df3['Win/Loss'] = df3['Margin'].apply(winner)
  w1 = df3.groupby(['Team', 'Win/Loss']).count().reset_index()
  w1_tot = pd.pivot_table(w1, values='Week', index=['Team'], columns= ['Win/Loss'], aggfunc=np.sum).reset_index()
  
  # calculate points for and against
  tm= []
  score= []
  against= []
  
  for i in df['Team1'].unique():
  
      x = (df[(df['Team1']==i)]['Score1'].sum() + df[(df['Team2']==i)]['Score2'].sum())#/len(df['Week'].unique())
      y = (df[(df['Team1']==i)]['Score2'].sum() + df[(df['Team2']==i)]['Score1'].sum())#/len(df['Week'].unique())
      tm.append(i)
      score.append(round(x,2))
      against.append(round(y,2))
      
  avg_scores = pd.DataFrame(list(zip(tm,score,against)),columns=['Team ID', 'Points For', 'Points Allowed'])
  
  #merge and add to draft order
  league_his = avg_scores.merge(w1_tot, left_on='Team ID', right_on='Team')
  
  r = requests.get(url, params={"view": "mSettings"})
  settings = r.json()[0]
  
  l = settings['settings']['draftSettings']['pickOrder']
  m = (np.arange(10)+1).tolist()
  
  league_his = league_his.sort_values(by='Team ID', ascending=True) 
  league_his['Pick Number'] = [x for _,x in sorted(zip(l,m))]
  league_his['Year']=year_
  
  if 'Tie' in league_his.columns:
    return league_his[['Team ID', 'W', 'L', 'Tie', 'Points For', 'Points Allowed', 'Pick Number', 'Year']].sort_values(by='W', ascending=False)
  else:
    return league_his[['Team ID', 'W', 'L', 'Points For', 'Points Allowed', 'Pick Number', 'Year']].sort_values(by='W', ascending=False)

get_season(2021).fillna(0)
                                
#years = np.arange(2020,2021)
#league_his_tot = get_season(2019)
#num_years = len(years)
                                
#for i in years:
 #   league_his_tot = pd.concat([league_hit_tot, get_season(i)], axis=0, ignore_index=True)
#league_his_tot['Tie']=league_his_tot['Tie'].fillna(0)
                               
#totals = league_his_tot.groupby('Team ID').sum().reset_index()

#totals['Points For Total'] = round(totals['Points For'],2)
#totals['Points Allowed Total'] = round(totals['Points Allowed'],2)
                                
#totals = totals.drop(['Year', 'Pick Number', 'Points For'], axis=1)
#totals[['Team ID', 'W', 'L', 'Tie', 'Points For Total', 'Points Allowed Total']].sort_values(by='W', ascending=False)                               
