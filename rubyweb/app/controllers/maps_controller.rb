class MapsController < ApplicationController
  def index
    @maps = Map.all
  end
  
  def new
    @map = Map.new
  end

  def show
    map
  end
  
  def create
    @map = Map.new params[:map]
    if @map.save
      flash[:notice] = "A new map was created"
      redirect_to @map
    else
      flash[:error] = "Error creating the map"
      render "new"
    end
  end

  def update
    map
    data = JSON.parse params[:map_builder_data]
    data = data.merge(params[:map].slice("width","height"))
    p data
    
    if map.update_attributes data
      flash[:notice] = "Map was updated"
    else
      flash[:error] = "Map was not updated"
    end
    redirect_to map
  end

  def map
    @map ||= Map.find params[:id]
  end
end
