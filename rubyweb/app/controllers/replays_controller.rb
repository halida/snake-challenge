class ReplaysController < ApplicationController
  def index
    @replays = Replay.recent.page(params[:page]).per(20)
  end

  def show
    @replay = Replay.find(params[:id])
    return render json: JSON.load(@replay.json) if params[:json]
    @room_id = 0
    render "rooms/show"
  end

  def create
    @replay = Replay.new(params[:replay])
    @replay.user = current_user

    if @replay.save
      render json: {status: 'replay saved.', id: @replay.id}
    else
      render json: {status: 'replay save failed', }
    end
  end

end
