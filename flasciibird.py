#!/usr/bin/env python2

"""flasciibird.py: ncurses-based port of Flappy Bird."""

__author__      = "Sebastian Krzyszkowiak"
__version__     = "0.0.2"
__copyright__   = "Copyright 2014, Sebastian Krzyszkowiak <dos@dosowisko.net>"
__license__     = "GPLv3+"

# So you're looking at the code anyway? OK then, but don't say I didn't warn you...

import curses, time, random, os

try:
    myscreen = curses.initscr()

    curses.start_color()
    try:
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_YELLOW, -1)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_WHITE)
        curses.curs_set(0)
    except:
        pass
    curses.noecho()
    curses.raw()

    myscreen.nodelay(1)

    birdXPos = myscreen.getmaxyx()[1] / 10

    bird = myscreen.getmaxyx()[0] / 2 - 4

    tubes = []

    (maxy, maxx) = myscreen.getmaxyx()

    def createTube():
        tube = {}
        tube['x'] = myscreen.getmaxyx()[1]
        tube['y'] = int((maxy - 11) * random.random()) + 1
        tube['box1'] = curses.newwin(5, 12, 1, 20)
        tube['box2'] = curses.newwin(maxy - (5 + 10), 12, 5 + 10, 20)
        tube['passed'] = False
        tubes.append(tube)

    createTube()

    def drawBird():
        #global bird
        #bird = tubes[0]['y'] + 4
        if bird > 0 and bird < maxy:
            myscreen.addstr(bird, birdXPos+5, "_", curses.color_pair(1))
        if bird > -1 and bird < maxy - 1:
            myscreen.addstr(bird+1, birdXPos, "\.", curses.color_pair(1))
        if bird > -2 and bird < maxy - 2:
            myscreen.addstr(bird+1, birdXPos+3, "_(9>", curses.color_pair(1))
        if bird > -3 and bird < maxy - 3:
            myscreen.addstr(bird+2, birdXPos+1, "\==_)", curses.color_pair(1))
        if bird > -4 and bird < maxy - 4:
            myscreen.addstr(bird+3, birdXPos+2, "-'=", curses.color_pair(1))


    def drawTube(tube):
        x = tube['x']
        y = tube['y']
        box1 = tube['box1']
        box2 = tube['box2']
        w = max(1, min(12, 13 - ((x + 12) - maxx + 1)) - max(0, -x + 1))
        if x > -12:
            box1.resize(y, w)
            box1.mvwin(0, max(0, x - 1))
            box1.bkgd(curses.A_REVERSE, curses.color_pair(2))

            box2.resize(maxy - (y + 7), w)
            box2.mvwin(y + 7, max(0, x - 1))
            box2.bkgd(curses.A_REVERSE, curses.color_pair(2))

    score = 0

    def draw(dead = False):
        myscreen.erase()
        #myscreen.border(1, 1, 0, 1, 1, 1, 1, 1)
        myscreen.addstr(0, maxx / 2 - 6, "FlasciiBird")
        myscreen.addstr(maxy - 1, maxx / 2 - len(str(score)) / 2 , str(score))
        drawBird()

        if dead:
            lost = "You lost! Score: " + str(score)
            lostWin = curses.newwin(3, len(lost) + 2, maxy / 2 - 1, maxx / 2 - len(lost) / 2 - 2)
            lostWin.border(0)
            lostWin.addstr(1, 1, lost)
        for tube in tubes:
            drawTube(tube)

        myscreen.noutrefresh()
        for tube in tubes:
            tube['box1'].noutrefresh()
            tube['box2'].noutrefresh()
        if dead:
            lostWin.noutrefresh()
        curses.doupdate()

    def debugDeath():
        draw()
        time.sleep(0.5)
        return False

    def death():
        global score, tubes, bird, oldTime, updateTime, lastFlapTime, flapping, flap, speed
        curses.flash()
        curses.beep()
        myscreen.nodelay(0)
        draw(True)
        key = myscreen.getch()
        while key != 10 and key != 27:
            key = myscreen.getch()
        if key == 27:
            return True
        score = 0
        tubes = []
        bird = myscreen.getmaxyx()[0] / 2 - 4
        oldTime = updateTime = lastFlapTime = time.time()
        createTube()
        flapping = False
        flap = 0
        speed = 10.0
        myscreen.nodelay(1)
        return False

    speed = 10.0
    flap = 0

    key = 0
    oldTime = updateTime = lastFlapTime = time.time()

    draw()

    flapping = False

    while key != 27:
        newTime = time.time()
        if key != -1:
            flapping = True
        if flapping and newTime - lastFlapTime > 0.25:
            #curses.beep()
            flap = 4
            lastFlapTime = newTime
            flapping = False
        if tubes[-1]['x'] < maxx - 1.2*maxy:
            createTube()
        if tubes[0]['x'] < (birdXPos - 11) and not tubes[0]['passed']:
            #curses.beep()
            score = score + 1
            tubes[0]['passed'] = True
        if (newTime - updateTime) > 0.05:
            for tube in tubes:
                tube['x'] = tube['x'] - 1
            if tubes[0]['x'] < -10:
                tubes.pop(0)
            speed = speed + 1
            if flap:
                bird = bird - 1
                flap = flap - 1
                speed = 7.5
                draw()
            updateTime = newTime
        if not flap and speed > 0:
            if (newTime - oldTime) > 1 / speed:
                bird = bird + 1
                oldTime = newTime
                draw()
        elif not flap and speed < 0:
            if (newTime - oldTime) > 1 / -speed:
                bird = bird - 1
                oldTime = newTime
                draw()

        if bird > maxy - 4:
            if death():
                break
	
        if birdXPos - 10 <= tubes[0]['x'] <= birdXPos + 7:
            tol = max(0, tubes[0]['y'] + 8 - (bird + 2))
            if bird + 1 < tubes[0]['y'] or (bird + 4 >= tubes[0]['y'] + 8 and birdXPos - 11 + tol < tubes[0]['x'] <= birdXPos + 7 - tol):
                if death():
                    break

        key = myscreen.getch()

    curses.endwin()
except:
    os.system('stty sane')
    raise
