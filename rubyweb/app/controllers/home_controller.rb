require 'net/http'

class HomeController < ApplicationController
  require 'sqlite3'
  @@db = SQLite3::Database.new '../tmp/game.db'

  def index
    @replays = Replay.recent.limit(5)
  end

  def scoreboard
    params = {op: 'scores', room: 0}
    @data = JSON.load Net::HTTP.post_form(URI.parse("http://#{ServerConfig['game_server']}/cmd"), params).body
    puts @data
  end

  def replay
  end

end
