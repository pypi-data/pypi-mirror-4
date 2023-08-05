

def usage():
    return '''usage: datahaven [options] [command] [arguments]
    
Commands:
  start
  stop
  show
  register <account name>
  recover <private-key-filename> [idurl or username]
  backup list
  backup idlist
  backup start <folder>
  backup add <folder>
  backup delete <folder>
  backup delete <backup ID>
  backup delete local <backup ID>
  backup update
  schedule <folder> <schedule in compact format>
  restore <backup ID> [destination ".tar" file path]
  stats <folder>
  stats <backup ID>
  stats remote <backup ID>
  stats local <backup ID>
  suppliers list
  suppliers call
  supplier replace <username, number or idurl>
  supplier change <username, number or idurl> <username or idurl>
  states
  set <option> [value]
  version
  help
'''    


def help():
    return '''usage: datahaven [options] [command] [arguments]

Commands:
  start                 start DataHaven.NET

  stop                  stop DataHaven.NET

  show                  start DataHaven.NET and show the main window

  register <account name>
                        generate a new private key and register new account

  recover <private-key-filename> [idurl or username]
                        recover existing account with your private key file

  backup list           show list of your backup folders

  backup start <folder> start a new backup of the given folder

  backup add <folder>   add backup folder, but not start new backup

  backup delete <folder>
                        remove all backups of the folder

  backup delete <backup ID>
                        remove given backup

  backup delete local <backup ID>
                        remove only local files for this backup,
                        but keep "remote copy" on suppliers HDD.
                        
  backup update         request all suppliers to update info for all backups 

  schedule <folder> [schedule in compact format]
                        set or get a schedule for a folder to start backups automatically

  restore <backup ID> [.tar file location]
                        restore a given backup
                        
  stats <backup ID>     show condition of given backup
  
  stats remote <backup ID>
                        show remote files stats for this backup

  stats local <backup ID>
                        show local files stats for this backup

  suppliers list        show list of your suppliers

  suppliers call        send a packets to checks out who is alive

  supplier replace <username, number or idurl>
                        replace a single supplier with new one

  supplier change <username, number or idurl> <username or idurl>
                        ask to change one supplier to another, by your choice
                        
  states                print states machines info
  
  set <option> [value]  to modify program setting

  version               display current software version

  help                  print this message
  
  help schedule         print format description to set scheduled backup
  
  help settings         print settings list

'''


def schedule_format():
    return '''
Schedule compact format:
[mode].[interval].[time].[details]

mode:
  n-none, h-hourly, d-daily, w-weekly, m-monthly, c-continuously
  
interval:
  just a number - how often to restart the task, default is 1
    
time:
  [hour]:[minute]
  
details:
  for weeks: Mon Tue Wed Thu Fri Sat Sun
  for months: Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec
  
some examples:
  none                    no schedule
  hourly.3                each 3 hours
  daily.4.10:15.          every 4th day at 10:15
  w.1.3:00.MonSat         every Monday and Saturday at 3:00 in the night
  weekly.4.18:45.MonTueWedThuFriSatSun
                          every day in each 4th week in 18:45
  m.5.12:34.JanJul        5th Jan and 5th July at 12:34
  c.300                   every 300 seconds (10 minutes)
'''
    
def settings_help():
    return '''set [option] [value]          

examples:
  set donated 4GB                          set donated space
  set needed                               print your needed space size
  set general.general-backups 4            set number of backup copies for every folder
  set suppliers                            print number of your suppliers
  set logs.stream-enable False             turn off web server for program logs
  set list                                 list all available options

'''