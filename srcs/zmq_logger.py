#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: log_server
记录以及回放服务器
"""
from ailib import *

    
def logger(controller, filename="game.log", quit_on_finish=True):
    """
    用来记录log
    """
    c = controller
    # log file
    f = open(filename, 'w+')

    def save_map():
        m = c.map()
        logging.debug(m)
        f.write('map: ')
        f.write(json.dumps(m))
        f.write('\n')
        return m

    def save_info():
        info = c.info()
        logging.debug(info)
        f.write('info: ')
        f.write(json.dumps(info))
        f.write('\n')
        return info

    clock = Clock(30)
    info = None
    status = None
    round = -1
    
    while True:
        try:
            clock.tick()
            # get map on init
            if not status:
                save_map()

            # loop get info..
            info = c.info()
            if info['round'] == round:
                time.sleep(0.3)
                continue
            round = info['round']
            logging.debug(info)
            
            # get map again when start new game
            if status == 'finished' and info['status'] == 'waitforplayer':
                save_map()

            # save info
            f.write('info: ')
            f.write(json.dumps(info))
            f.write('\n')
            
            # quit on game finished
            if quit_on_finish and info['status'] == 'finished':
                f.close()
                return
            status = info['status']
        except KeyboardInterrupt:
            f.close()
            return

usage = """\
    $zmq_logger.py [connect type] [room number] [filename]
    connect type is in [web, zero]
"""

def main():
    if len(sys.argv) < 3: print usage
    controller = sys.argv[1]
    try:
        room = int(sys.argv[2])
    except:
        print usage
        
    if controller == 'web':
        Controller = WebController
    elif controller == 'zero':
        Controller = ZeroController
    else:
        print usage

    filename=sys.argv[3]
        
    logger(Controller(room),
           filename=filename,
           quit_on_finish=False)
    
if __name__=="__main__":
    main()
