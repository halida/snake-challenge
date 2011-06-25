$zmq_context = ZMQ::Context.new

$zmq_req = $zmq_context.socket(ZMQ::REQ)
$zmq_req.connect('ipc:///tmp/game_oper.ipc')

$zmq_sub = $zmq_context.socket(ZMQ::SUB)
$zmq_sub.connect('ipc:///tmp/game_puber.ipc')
