simple_snake =
  d: 0
  dirs: [[-1, 0], [0, -1], [1, 0], [0, 1]]
  map: undefined
  user_seq: undefined

  init: (us)->
    this.user_seq = us

  setmap: (map)->
    this.map = map

  step: (info)->
    snake = info.snakes[this.user_seq]
    head = snake.body[0]
    dir = this.dirs[this.d]
    nexts = ([
        head[0] + dir[0]*i,
        head[1] + dir[1]*i
        ] for i in [1..4])
    blocks = this.map.walls.concat []
    for snake in info.snakes
      blocks.push.apply(blocks, snake.body)

    for n in nexts
      for b in blocks
        if b[0] == n[0] and b[1] == n[1]
          this.d = (this.d + 1) % 4
          return this.d

    return this.d

window.simple_snake = simple_snake