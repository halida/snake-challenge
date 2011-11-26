
class HomeController < ApplicationController
  require 'sqlite3'
  @@db = SQLite3::Database.new '../tmp/game.db'

  def index
    @replays = Replay.recent.limit(5)
  end

  def scoreboard
    @dailys =  @@db.execute('select * from (select name, count(*) as count from scores where time > ? group by name) order by count desc limit 10', Date.today.to_time.to_f)
    @weeklys = @@db.execute('select * from (select name, count(*) as count from scores where time > ? group by name) order by count desc limit 10', (Date.today - 7.days).to_time.to_f)
    @monthlys = @@db.execute('select * from (select name, count(*) as count from scores where time > ? group by name) order by count desc limit 10', (Date.today - 30.days).to_time.to_f)
  end

end
