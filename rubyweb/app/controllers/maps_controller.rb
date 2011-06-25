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
      redirect_to @map
    else
      render "new"
    end
  end
end
