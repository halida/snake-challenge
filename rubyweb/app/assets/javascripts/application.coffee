window.init = ()->
        flash = $('.flash')
        return if flash.length <= 0
        setTimeout(
                ()->
                        flash.fadeIn(800)
                , 3000)

window.error = (msg)->
        error = $('#flash_error')
        error.html(msg)
        error.fadeIn(800)
        setTimeout(
                ()->
                        error.fadeOut(800)
                , 3000)

window.random_color = (text)->
  v = 0
  for k in text
    v += k.charCodeAt()
    v *= 13
    v %= 101477
  r = (v % 2207 ) % 0x7f + 0x80
  g = (v % 2607 ) % 0x7f + 0x80
  b = (v % 3323 ) % 0x7f + 0x80
  color = '#' + ((r << 16) + (g<<8) + b).toString(16)
