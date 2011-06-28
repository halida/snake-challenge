snake-challenge项目说明
====================================
本项目实现用ai的方式来玩贪吃蛇游戏.

游戏介绍
------------------------------------
贪吃蛇游戏, 有以下特性:

- 蛇有2种(python/ruby), 豆子也有2种(egg/gem), 吃自己对应的豆子+1长度, 否则-1长度.
- 回合制进行, 服务器等待每条蛇发出命令(或者超时)才进行下一轮.
- 当只有1条蛇剩下, 或者到达600轮的时候游戏结束.
- 蛇死掉后就变成尸体了, 和墙的效果一样.

sprint之后的:

- 有传送门
- 食物的长度可变.

架构
------------------------------------
整体架构是这样的:

- 游戏引擎, web服务器, 参与者的AI都分开做不同的进程.
- 如果在本机运行, 所有的跨进程操作都利用zeromq.
- 如果接入web, 需要执行一个web服务器, 来给利用web接口的ai做服务.

一个图示 ::

    游戏引擎 --zeromq-- web服务器 --http-- web接口的ai
    游戏引擎 --zeromq-- zeromq接口的ai, pygame显示, 记录log的工具等等

游戏引擎

  提供/tmp/game_puber.ipc, /tmp/game_oper.ipc 2个队列(采用zeromq), 
  oper队列是REP类型的, 接收来自客户端的请求,
  puber队列是PUB类型的, 当游戏进行了一轮之后, 会在这个队列发布当前地图的信息.


AI API接口
------------------------------------
API分为多个函数: map/add/turn/info, 发送数据和接收数据都采用json格式.

add
````````````````````````````````````
添加新的蛇, 发送数据 ::

    {"name": 蛇的名称, "type": "python" 或者 "ruby"}

接受到的数据 ::

    {
      "seq": 0,   // 当前蛇的顺序(下面info里面snakes的位置)
      "id": "???" // 蛇的ID, 用来在发送控制命令的时候做验证.
    }

如果出现错误, 会返回 ::

    {
      "status": 错误信息,
    }

错误信息有:

- 蛇type错误: snake type error
- 数量已满: no place for new snake.

turn
````````````````````````````````````
控制蛇方向, 发送数据 ::

    {
      "id": 蛇ID,
      "direction": 蛇头的方向(0-4分别对应: 左上右下),
      "round": 对应的回合数, 如果和当前回合不一致, server会丢弃该命令, 防止超时. 如果-1的话不做检查.
    }

返回 ::

    {
      "status": 结果,
    }

结果:

- ok: 操作成功
- id错误: noid
- 超时了, 当前轮数不正确: round error, current round: %d
- 蛇不能往后面退: noturnback

map
````````````````````````````````````
获取游戏的地图, 数据格式 ::

    {
      "walls": [[10, 5], ...] // 墙的位置
    }

info
`````````````````````````````````````
获取游戏实时数据, 数据格式 ::

    {u'eggs': [[9, 8], ...],  // 当前游戏中的egg位置
     u'gems': [[7, 37], ...], // 当前游戏中的gem位置
     u'nydus': [[1, 1], [2, 2], ....] // 当前游戏中的坑道门位置 [[进x, 进y], [出x, 出y], .....]
     u'round': 192, // 当前游戏的轮数, 600轮的时候游戏结束
     u'snakes': // 当前游戏中所有蛇的信息
                [{u'alive': True, // 蛇是否还活着?
                  u'body': [[16, 16], // 蛇身体的位置
                            [16, 17],
                            [16, 18],
                            [16, 19],
                            [16, 20]],
                  u'direction': 1, // 蛇头的方向(0-4分别对应: 左上右下)
                  u'length': 5, // 蛇的长度
                  u'name': u'simple ai2', // 蛇的名称
                  u'type': u'python'}, // 蛇的类型(ruby/python)
                ... 
                ],
     u'status': u'running'} // 当前游戏的状态(waitforplayer/running/finished)
    
通讯方式
------------------------------------
AI可以通过2种方式接入, 本地机器的话, 可以用zeromq队列接入, 或者通过web server中转, 通讯方式虽然不同, 具体API还是一致的.

zeromq方式
````````````````````````````````````
- ipc:///tmp/game_puber.ipc 发布队列
- ipc:///tmp/game_oper.ipc 操作请求队列

oper用来做操作(add/turn/map), game server会立刻返回结果, 

ai发送命令的时候, 需要在数据结构里面加上"room": 房间号. 

puber用来监听服务器当前状态, 一轮结束后, game server会在该队列发布info信息.

发布的info信息头部会加上 "room:0(空格)", 用来标识哪个房间的信息. ai需要自己过滤出自己的房间.

如果房间号错误, 会返回 ::

    {"status": "room number error: 错误的房间号"}
    
web方式
````````````````````````````````````
访问 http://localhost/room/0/(map/info/add/turn) 就可以了.
    
要注意, add/turn返回的数据除了上面API部分列出来的返回数据以外, 还会附带有info数据, 示例 ::

    [{"status": "ok"}, {...}]

这个过程是阻塞的, 游戏更新之后, 才会返回数据. 这样的话, 客户端就变成一问一答的方式, 比较好实现.

游戏环境安装
------------------------------------
需要:

python部分

  - zeromq 2.0.10
  - pyzmq
  - python-pygame

ruby部分
  - json
  - zmq
  - sinatra


zeromq安装
````````````````````````````````````
因为ubuntu源里面的zeromq好像不是最新的, 我是直接上: http://www.zeromq.org/intro:get-the-software 上面下载2.0.10版本的(python绑定最高是2.1.1, 但是没有下载, 于是我选择这个版本).

然后就是解压编译安装. 需要g++以及uuid-dev. 安装完毕后, 需要手动做一下链接库的链接, 不然无法用pyzmq:

:: 

    ln -s /usr/local/lib/libzmq.so.0 /usr/lib/libzmq.so.0 

pyzmq
````````````````````````````````````
需要指定2.0.10版本

    sudo easy_install pyzmq==2.0.10

pygame
````````````````````````````````````
pygame用来本机显示游戏场景.

::

   sudo apt-get install python-pygame

ruby web server
````````````````````````````````````
需要安装rails!!

太复杂了, 具体见 http://server.linjunhalida.com/blog/article/rails_ubuntu_%E5%AE%89%E8%A3%85/

rails目录是rubyweb.

终于可以跑了
------------------------------------
开启多个终端, 每个终端分别执行 ::

    # 游戏引擎
    make game 
    # 加入第一个测试AI
    make ai
    # 加入第二个测试AI
    make ai

    # 用pygame来做本地游戏场景显示
    make show

    # 用web服务器来显示
    # 开启web服务器
    make web
    # 开启websocket服务器
    make websocket

然后你就可以看到2条蛇在追逐豆子了... 安装好累呀...

