require "json"
require 'zmq'
require "sinatra"

before do
  @ctx = ZMQ::Context.new

  @zmq_req = @ctx.socket(ZMQ::REQ)
  @zmq_req.connect('ipc:///tmp/game_oper.ipc')

  @zmq_sub = @ctx.socket(ZMQ::SUB)
  @zmq_sub.connect('ipc:///tmp/game_puber.ipc')
end

after do
  @zmq_req.close
  @zmq_sub.close
  @ctx.close
end

get '/room/:room_id/map' do
  zmq_req_send 'map'
end

get '/room/:room_id/info' do
  zmq_req_send 'info'
end

post '/room/:room_id/add' do
  zmq_sub_set
  add_result = zmq_req_send('add', {:name => params[:name], :type => params[:type]})
  "[#{add_result}, #{zmq_sub_recv}]"
end

post '/room/:room_id/turn' do
  zmq_sub_set
  turn_result = zmq_req_send('turn', {:id => params[:id], :direction => params[:direction].to_i, :round => params[:round].to_i})
  if turn_result == '{"status": "ok"}'
    info = zmq_sub_recv
  else
    info = zmq_req_send 'info'
  end
  
  "[#{turn_result}, #{info}]"
end

get '/room/:room_id/' do
  File.read(File.join('public', 'room.html'))
end

get '/' do
  File.read(File.join('public', 'index.html'))
end

private

def zmq_req_send(op, options = {})
  @zmq_req.send(options.merge(:op => op, :room => params[:room_id].to_i).to_json)
  @zmq_req.recv
end

def zmq_sub_set
  @zmq_sub.setsockopt(ZMQ::SUBSCRIBE, "room:#{params[:room_id]} ")
end

def zmq_sub_recv
  @zmq_sub.recv[7..-1]
end
