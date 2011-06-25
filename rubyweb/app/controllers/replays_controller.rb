class ReplaysController < ApplicationController
  # GET /replays
  # GET /replays.xml
  def index
    @replays = Replay.page(params[:page]).per(20)
  end

  # GET /replays/1
  # GET /replays/1.xml
  def show
    @replay = Replay.find(params[:id])

    respond_to do |format|
      format.html # show.html.erb
      format.json  { render :json => @replay.to_json }
    end
  end

  # POST /replays
  # POST /replays.xml
  def create
    @replay = Replay.new(params[:replay])

    respond_to do |format|
      if @replay.save
        format.html { redirect_to(@replay, :notice => 'Replay was successfully created.') }
        format.json  { render :json => { :id => @replay.id, :status => 1 } }
      else
        format.html { render :action => "new" }
        format.json  { render :json => { :status => 0 } }
      end
    end
  end

end
