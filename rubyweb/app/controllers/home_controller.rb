class HomeController < ApplicationController
  def index
    @replays = Replay.recent.limit(5)
  end
end
