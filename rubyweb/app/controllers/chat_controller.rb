class ChatController < ApplicationController
  layout :nil 

  def index
  end

  def info
    respond_to do |format|
      format.js {
        render {room_id: params[:id], username: "guest"}
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
