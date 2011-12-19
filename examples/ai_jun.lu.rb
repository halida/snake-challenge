# This code is created by jun.lu <jun.lu.coder@gmail.com>
# And donated to snakechallenge project for demo use.
# Any further usage sould be authorized by the author.

require 'json'
require 'net/http'

$SERVER = "10.77.77.103"
$PORT = 9999
$DIRS = [[-1, 0], [0, -1], [1, 0], [0, 1]]
$DIRAVAILABLE = [[0, 1, 3], [0, 1, 2], [1, 2, 3], [0, 2, 3]]

class CoderSnakeAI
    def initialize(room)
        @conn = Net::HTTP.new($SERVER, $PORT)
        @room = room
        @dir = 1
        @lastround = -1
    end
    
    def cmd(cmd, data = {})
        data['op'] = cmd
        data['room'] = @room
        request = Net::HTTP::Post.new("/cmd")
        request.set_form_data(data)
        response = @conn.request(request)
        return JSON.parse(response.body)
    end
    
    def add
        @me = cmd("add", name:"CoderSnakeAI", type:"ruby")
        puts @me
    end
    
    def useold(id, seq)
        @me = {}
        @me['id'] = id
        @me['seq'] = seq
    end
    
    def map
        @map = cmd("map")
        @width = @map['size'][0]
        @height = @map['size'][1]
        @portal = []
        lastx = -1
        for pos in @map['portals']
            if (lastx < 0)
                lastx = pos[0]
                lasty = pos[1]
                next
            end
            @portal[lastx * @height + lasty] = pos
            @portal[pos[0] * @height + pos[1]] = [lastx, lasty]
            lastx = -1
        end
    end
    
    def info
        @info = cmd("info")
    end
    
    def turn(dir)
        return cmd("turn", id: @me["id"], round: @lastround, direction: dir)
    end
    
    def initcalcmap
        @calcmap = []
        for i in 0..@width * @height - 1
            @calcmap[i] = {}
        end
        for egg in @info['eggs']
            @calcmap[egg[0] * @height + egg[1]]['eat'] = 0
        end
        for gem in @info['gems']
            @calcmap[gem[0] * @height + gem[1]]['eat'] = 1
        end
    end
    
    def getwallleft(length, sprint)
        if (sprint == 0)
            return length
        end
        if (sprint > 0)
            if (length <= sprint * 3)
                return (length + 2) / 3
            end
            return 20 + length - sprint * 3
        end
        return -sprint + length
    end
    
    def getsprint(snake)
        sprint = snake['sprint']
        return 0 if (sprint == nil)
        return sprint
    end
    
    def addsnaketowall(snake, seq)
        length = snake['body'].length
        sprint = getsprint(snake)
        if (seq != @me['seq'])
            mydir = snake['direction']
            needeat = 0
            needeat = 1 if (snake['type'] == 'ruby')
            eat = false
            for dir in $DIRAVAILABLE[mydir]
                nextx = snake['body'][0][0] + $DIRS[dir][0]
                nexty = snake['body'][0][1] + $DIRS[dir][1]
                nextx = fixx(nextx)
                nexty = fixy(nexty)
                portal = @portal[nextx * @height + nexty]
                if (portal != nil)
                    nextx = portal[0]
                    nexty = portal[1]
                end
                calcslot = @calcmap[nextx * @height + nexty];
                calcslot['wallleft'] = 1;
                calcslot['seq'] = 0x7FFFFFFF
                calcslot['actualseq'] = seq
                eat = true if (calcslot['eat'] == needeat)
            end
        
            length = length + 1 if eat
        end
        
        for body in snake['body']
            @calcmap[body[0] * @height + body[1]]['wallleft'] = getwallleft(length, sprint)
            @calcmap[body[0] * @height + body[1]]['seq'] = seq
            length = length - 1
        end
    end
    
    def fixx(x)
        return x + @width if (x < 0)
        return x - @width if (x >= @width)
        return x
    end
    
    def fixy(y)
        return y + @height if (y < 0)
        return y - @height if (y >= @height)
        return y
    end
    
    def calcreachtime
        posqueue = []
        tail = 0
        seq = 0
        for startsnake in @info['snakes']
            if (startsnake['alive'])
                posqueue[tail] = startsnake['body'][0]
                posqueue[tail][2] = startsnake['direction']
                posqueue[tail][3] = seq
                tail = tail + 1
            end
            seq = seq + 1
        end
        nowturn = 0
        head = 0
        nextturn = 0
        while (head < tail)
            if (head == nextturn)
                nowturn = nowturn + 1
                nextturn = tail
            end
            nowx = posqueue[head][0]
            nowy = posqueue[head][1]
            nowdir = posqueue[head][2]
            nowseq = posqueue[head][3]
            snake = @info['snakes'][nowseq]
            sprint = getsprint(snake)
            if (sprint > 0)
                if (nowturn > sprint + 20)
                    step = 1
                else
                    if (nowturn > sprint)
                        step = 0
                    else
                        step = 3
                    end
                end
            else
                if (sprint < 0)
                    if (nowturn > -sprint)
                        step = 1
                    else
                        step = 0
                    end
                else
                    step = 1
                end
            end
            if (step == 0)
                posqueue[tail] = posqueue[head]
                tail = tail + 1
                head = head + 1
                next
            end
            for dir in $DIRAVAILABLE[nowdir]
                nextx = nowx + $DIRS[dir][0] * step
                nexty = nowy + $DIRS[dir][1] * step
                nextx = fixx(nextx)
                nexty = fixy(nexty)
                portal = @portal[nextx * @height + nexty]
                if (portal != nil)
                    nextx = portal[0]
                    nexty = portal[1]
                end
                calcslot = @calcmap[nextx * @height + nexty]
                wallleft = calcslot['wallleft']
                if (wallleft != nil)
                    next if (wallleft == 0x7FFFFFFF)
                    next if (nowturn < wallleft)
                    if (nowturn == wallleft)
                        wallseq = calcslot['seq']
                        if ((wallseq != 0x7FFFFFFF) or (calcslot['actualseq'] != nowseq))
                            next if (wallseq >= nowseq)
                        end
                    end                    
                end
                reach = calcslot['reach']
                if (reach != nil)
                    next if (reach[1] != nil)
                    next if (reach[0][1] == nowseq)
                    reach[1] = []
                    reach[1][0] = nowturn
                    reach[1][1] = nowseq
                    next
                end
                reach = []
                calcslot['reach'] = reach
                reach[0] = []
                reach[0][0] = nowturn
                reach[0][1] = nowseq
                posqueue[tail] = [nextx, nexty, dir, nowseq]
                tail = tail + 1
            end
            head = head + 1
        end
    end
    
    def calcwallleft
        for wall in @map['walls']
            @calcmap[wall[0] * @height + wall[1]]['wallleft'] = 0x7FFFFFFF
        end
        index = 0
        for snake in @info['snakes']
            if snake['alive']
                addsnaketowall(snake, index)
            else
                for body in snake['body']
                    @calcmap[body[0] * @height + body[1]]['wallleft'] = 0x7FFFFFFF
                end
            end
            index = index + 1
        end
    end
    
    def getspace(startx, starty, startdir, myseq)
        calcslot = @calcmap[startx * @height + starty]
        if (calcslot['space'] != nil)
            return calcslot['space']
        end
        posqueue = []
        head = 0
        tail = 1
        nowturn = 1
        nextturn = 0
        posqueue[0] = [startx, starty, startdir]
        
        while (head < tail)
            if (head == nextturn)
                nowturn = nowturn + 1
                nextturn = tail
            end
            nowx = posqueue[head][0]
            nowy = posqueue[head][1]
            nowdir = posqueue[head][2]
            for dir in $DIRAVAILABLE[nowdir]
                nextx = nowx + $DIRS[dir][0]
                nexty = nowy + $DIRS[dir][1]
                nextx = fixx(nextx)
                nexty = fixy(nexty)
                portal = @portal[nextx * @height + nexty]
                if (portal != nil)
                    nextx = portal[0]
                    nexty = portal[1]
                end
                calcslot = @calcmap[nextx * @height + nexty]
                next if (calcslot['space'] != nil)
                wallleft = calcslot['wallleft']
                if (wallleft != nil)
                    next if (wallleft == 0x7FFFFFFF)
                    next if (nowturn < wallleft)
                    if (nowturn == wallleft)
                        wallseq = calcslot['seq']
                        if ((wallseq != 0x7FFFFFFF) or (calcslot['actualseq'] != myseq))
                            next if (wallseq >= myseq)
                        end
                    end
                end
                reach = calcslot['reach']
                if (reach != nil)
                    next if reach[0][1] != myseq
                end
                calcslot['space'] = 1
                posqueue[tail] = [nextx, nexty, dir]
                tail = tail + 1
            end
            head = head + 1
        end
        
        for pos in posqueue
           @calcmap[pos[0] * @height + pos[1]]['space'] = tail
        end
        
        return tail
    end
    
    def dumpreach
        puts "--------------------------reach info----------------------------"
        for x in 0..@width - 1
            for y in 0..@height - 1
                calcslot = @calcmap[x * @height + y]
                reach = calcslot['reach']
                if (reach == nil)
                    print "-"
                else
                    print reach[0][1]
                end
            end
            puts ""
        end
        puts "--------------------------reach info----------------------------"
    end
    
    def getdist(fromx, fromy, tox, toy, startdir, myseq, headwallcheck)
        return 0 if (fromx == tox) and (fromy == toy)
        if (headwallcheck)
            calcslot = @calcmap[fromx * @height + fromy]
            wallleft = calcslot['wallleft']
            if (wallleft != nil)
                return -1 if (wallleft == 0x7FFFFFFF)
                return -1 if (1 <= wallleft)
                if (1 == wallleft)
                    wallseq = calcslot['seq']
                    return -1 if (wallseq > myseq)
                end
            end            
        end

        posqueue = []
        head = 0
        tail = 1
        nowturn = 1
        nextturn = 0
        posqueue[0] = [fromx, fromy, startdir]
        hash = []
        hash[fromx * @height + fromy] = true
        while (head < tail)
            if (head == nextturn)
                nowturn = nowturn + 1
                nextturn = tail
            end
            nowx = posqueue[head][0]
            nowy = posqueue[head][1]
            nowdir = posqueue[head][2]
            for dir in $DIRAVAILABLE[nowdir]
                nextx = nowx + $DIRS[dir][0]
                nexty = nowy + $DIRS[dir][1]
                nextx = fixx(nextx)
                nexty = fixy(nexty)
                portal = @portal[nextx * @height + nexty]
                if (portal != nil)
                    nextx = portal[0]
                    nexty = portal[1]
                end
                return nowturn if ((nextx == tox) and (nexty == toy))
                next if (hash[nextx * @height + nexty])
                hash[nextx * @height + nexty] = true
                calcslot = @calcmap[nextx * @height + nexty]
                wallleft = calcslot['wallleft']
                if (wallleft != nil)
                    next if (wallleft == 0x7FFFFFFF)
                    next if (nowturn < wallleft)
                    if (nowturn == wallleft)
                        wallseq = calcslot['seq']
                        if ((wallseq != 0x7FFFFFFF) or (calcslot['actualseq'] != myseq))
                            next if (wallseq >= myseq)
                        end
                    end
                end
                posqueue[tail] = [nextx, nexty, dir]
                tail = tail + 1
            end
            head = head + 1
        end
        return -1
    end
    
    def step
        info
        return if (@info['round'] == @lastround)
        @lastround = @info['round']
        puts "round = #{@lastround}"
        initcalcmap
        calcwallleft
        calcreachtime
        puts "calc finish"
        mysnake = @info['snakes'][@me['seq']]
        myseq = @me['seq']
        mydir = mysnake['direction']
        mylength = mysnake['length']
        puts "myalive #{mysnake['alive']}"
        forbiddenlevel = [100, 100, 100, 100]
        for testdir in $DIRAVAILABLE[mydir]
            nextx = mysnake['body'][0][0] + $DIRS[testdir][0]
            nexty = mysnake['body'][0][1] + $DIRS[testdir][1]
            nextx = fixx(nextx)
            nexty = fixy(nexty)
            portal = @portal[nextx * @height + nexty]
            if (portal != nil)
                nextx = portal[0]
                nexty = portal[1]
            end
            calcslot = @calcmap[nextx * @height + nexty]
            wallleft = calcslot['wallleft']
            if (wallleft != nil)
                if (wallleft == 0x7FFFFFFF)
                    forbiddenlevel[testdir] = 1
                    puts "dir: #{testdir}, wallleft: #{wallleft}"
                    next
                end
                if (wallleft > 1)
                    forbiddenlevel[testdir] = 1
                    puts "dir: #{testdir}, wallleft: #{wallleft}"
                    next
                end
                if (wallleft == 1)
                    wallseq = calcslot['seq']
                    if ((wallseq != 0x7FFFFFFF) or (calcslot['actualseq'] != myseq))
                        if (wallseq >= myseq)
                            forbiddenlevel[testdir] = 1
                            puts "dir: #{testdir}, wallleft: #{wallleft}"
                            next
                        end
                    end
                end             
            end
            space = getspace(nextx, nexty, testdir, myseq)
            if (space < mylength)
                forbiddenlevel[testdir] = 2
            end
        end
        puts "forbiddenlevel: #{forbiddenlevel}"
        if (mysnake['type'] == 'ruby')
            gems = @info['gems']
        else
            gems = @info['eggs']
        end
        z = 0
        mindist = 0x7FFFFFFF
        mindir = -1
        for gem in gems
            reach = @calcmap[gem[0] * @height + gem[1]]['reach']
            next if (reach == nil)
            puts "#{reach}, #{z}"
            z = z + 1
            next if (reach[0][1] != myseq)
            puts "closest at (#{gem[0]}, #{gem[1]}), dist = #{reach[0][0]}"
            nowdist = @calcmap[gem[0] * @height + gem[1]]['reach'][0][0]
            for dir in $DIRAVAILABLE[mydir]
                next if forbiddenlevel[dir] <= 2
                nextx = mysnake['body'][0][0] + $DIRS[dir][0]
                nexty = mysnake['body'][0][1] + $DIRS[dir][1]
                nextx = fixx(nextx)
                nexty = fixy(nexty)
                portal = @portal[nextx * @height + nexty]
                if (portal != nil)
                    nextx = portal[0]
                    nexty = portal[1]
                end
                newdist = getdist(nextx, nexty, gem[0], gem[1], dir, myseq, true)
                puts "new dist #{newdist}"
                next if (newdist < 0)
                next if (newdist > nowdist)
                if (newdist < mindist)
                    mindist = newdist
                    mindir = dir
                end
            end
        end
        if (mindir >= 0)
            turn(mindir)
            return
        end
        mindist = 0x7FFFFFFF
        mingem = nil
        for targetgem in gems
            nowdist = getdist(mysnake['body'][0][0], mysnake['body'][0][1], targetgem[0], targetgem[1], mydir, myseq, false)
            next if (nowdist < 0)
            next if (nowdist > mindist)
            mindist = nowdist
            mingem = targetgem
        end

        if (mingem != nil)
            for nextdir in $DIRAVAILABLE[mydir]
                next if forbiddenlevel[nextdir] <= 2
                nextx = mysnake['body'][0][0] + $DIRS[nextdir][0]
                nexty = mysnake['body'][0][1] + $DIRS[nextdir][1]
                nextx = fixx(nextx)
                nexty = fixy(nexty)
                portal = @portal[nextx * @height + nexty]
                if (portal != nil)
                    nextx = portal[0]
                    nexty = portal[1]
                end
                newdist = getdist(nextx, nexty, mingem[0], mingem[1], nextdir, myseq, true)
                next if (newdist < 0)
                next if (newdist >= mindist)
                puts "new dist #{newdist}, min dist, #{mindist}, mingem, #{mingem}"
                puts "#{nextx}, #{nexty}, #{@calcmap[nextx * @height + nexty]['wallleft']}"
                turn(nextdir)
                return
            end
        end
        
        puts "choose last"
        maxlevel = 0
        maxdir = 0
        for lastdir in $DIRAVAILABLE[mydir]
            if (forbiddenlevel[lastdir] > maxlevel)
                maxlevel = forbiddenlevel[lastdir]
                maxdir = lastdir
            end
        end
        puts "maxlevel: #{maxlevel}, maxdir: #{maxdir}"
        turn(maxdir)
    end
end

coderai = CoderSnakeAI.new(0)
#coderai.useold("8bc4c11b8b6440f4a0636dc0da26309d", 4)
coderai.add
coderai.map
while(true)
    coderai.step
end

