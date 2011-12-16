if MozWebSocket?
  window.WS = MozWebSocket
else
  window.WS = WebSocket

window.init = ()->
        flash = $('.flash')
        if flash.length > 0
          setTimeout( ()->
                flash.fadeIn(800)
          , 3000)

window.error = (msg)->
        error = $('#flash_error')
        error.html(msg)
        error.fadeIn(800)
        console.log(msg)
        setTimeout(
                ()->
                        error.fadeOut(800)
                , 10000)

window.notice = (msg)->
        notice = $('#flash_notice')
        notice.html(msg)
        notice.fadeIn(800)
        console.log(msg)
        setTimeout(
                ()->
                        notice.fadeOut(800)
                , 3000)


window.random_color = (text)->
  v = 0
  for k in text
    v += k.charCodeAt()
    v *= 13
    v %= 101477
  r = (v % 2207 ) % 0x7f
  g = (v % 2607 ) % 0x7f
  b = (v % 3323 ) % 0x7f
  color = '#' + ((r << 16) + (g<<8) + b).toString(16)
