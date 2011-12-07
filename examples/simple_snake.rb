require 'json'
require 'net/http'

DIRS = [[-1, 0], [0, -1], [1, 0], [0, 1]]

class SimpleSnake
  def initialize
    @conn = Net::HTTP.new("localhost", 9999)
    @room = 0
    @d = 0
  end

  def cmd cmd, data={}
    data['op'] = cmd
    data['room'] = @room
    request = Net::HTTP::Post.new("/cmd")
    request.set_form_data(data)
    response = @conn.request(request)
    result = JSON.parse(response.body)
  end

  def cmd_add
    @me = cmd "add", name:"SimpleRuby", type:"ruby"
  end

  def cmd_map
    @map = cmd "map"
  end

  def cmd_info
    @info = cmd "info"
  end

  def cmd_turn d
    cmd "turn", id: @me["id"], :round => -1, :direction => d
  end

  def step
    snake = @info['snakes'][@me["seq"]]
    head = snake['body'][0]
    dir = DIRS[@d]
    nexts = [1,2,3,4].map do |i|
      [head[0] + dir[0]*i,
       head[1] + dir[1]*i]
    end

    blocks = []
    blocks += @map['walls']
    for snake in @info['snakes']
      blocks += snake['body']
    end

    # change direction when there is block ahead
    for n in nexts
      for b in blocks
        if b[0] == n[0] and b[1] == n[1]
          return @d = (@d + 1) % 4
        end
      end
    end
    return @d
  end
end


rs = SimpleSnake.new
rs.cmd_map
puts rs.cmd_add

while true
  sleep 0.3
  rs.cmd_info
  puts rs.cmd_turn rs.step
end
