class ChatController < ApplicationController
  layout :nil 

  def index
  end

  def info
    room_id = String(params[:id] || 0)

    respond_to do |format|
      format.js {
        render :json => {room_id: room_id, username: "guest"}
      }
    end
  end

  # POST
  #
  # params: channel message
  #
  def message
    Juggernaut.publish(params[:channel], params[:message])

    render "index"
  end

end
