require "json"
require 'zmq'

class RoomsController < ApplicationController

  def index
  end

  def add
    add_result = zmq_req_send('add', 
                              {:name => params[:name], 
                                :type => params[:type]})
    render :text => add_result
  end

  def show
    @room_id = params[:id]
    @game_server = Room::GAME_SERVER
    @chat_server = Room::CHAT_SERVER
  end

  def map
    result = zmq_req_send 'map'
    render :text => result
  end

  def info
    result = zmq_req_send 'info'
    render :text => result
  end

  def turn
    turn_result = zmq_req_send('turn', {:id => params[:snake_id], :direction => params[:direction].to_i, :round => params[:round].to_i})
    
    render :text => turn_result
  end

  private
  def zmq_req_send(op, options = {})
    $zmq_req.send(options.merge(:op => op, :room => params[:room_id].to_i).to_json)
    $zmq_req.recv
  end

  def zmq_sub_set
    $zmq_sub.setsockopt(ZMQ::SUBSCRIBE, "room:#{params[:room_id]} ")
  end

  def zmq_sub_recv
    $zmq_sub.recv[7..-1]
  end
  
end
