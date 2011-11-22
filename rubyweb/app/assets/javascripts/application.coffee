window.init = ()->
        flash = $('.flash')
        return if flash.length <= 0
        setTimeout(
                ()->
                        flash.fadeIn(800)
                , 3000)
