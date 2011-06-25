require 'json'
require 'net/http'

@http = Net::HTTP.new("50.56.97.47", 80)

def turn
  current_direction = @info["snakes"][@me["seq"]]["direction"]
  p "current direction: #{current_direction}"
  
  request = Net::HTTP::Post.new("/room/1/turn")
  request.set_form_data(:id => @me["id"], :round => @info["round"], :direction => rand(3))
  response = @http.request(request)
  result = JSON.parse(response.body)
  @turn, @info = result[0], result[1]
end

def add
  request = Net::HTTP::Post.new("/room/1/add")
  request.set_form_data(:name => "RandomRuby", :type => "ruby")
  response = @http.request(request)
  result = JSON.parse(response.body)
  @me, @info = result[0], result[1]
end

add
while true
 sleep 0.2
 turn
end
