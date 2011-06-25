class MapsController < ApplicationController
  def new
    @map = Map.new
  end

  def show
    @map = Map.find params[:id]
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
end
