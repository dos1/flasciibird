#!/usr/bin/env python

"""flasciibird.py: ncurses-based port of Flappy Bird."""

__author__      = "Sebastian Krzyszkowiak"
__version__     = "0.0.4"
__copyright__   = "Copyright 2014, Sebastian Krzyszkowiak <dos@dosowisko.net>"
__license__     = "GPLv3+"

# So you're looking at the code anyway? OK then, but don't say I didn't warn you...

import curses, time, random, os

try:
    myscreen = curses.initscr()

    curses.start_color()
    try:
        curses.use_default_colors()
        curses.init_pair(1, -1, -1)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_RED, -1)
        curses.init_pair(5, curses.COLOR_GREEN, -1)
        curses.curs_set(0)
    except:
        pass
    curses.noecho()
    curses.raw()

    myscreen.nodelay(1)

    (maxy, maxx) = myscreen.getmaxyx()

    birdXPos = maxx // 10

    bird = maxy // 2 - 4

    tubes = []

    class Tube:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.box1 = curses.newwin(5, 12, 1, 20)
            self.box2 = curses.newwin(maxy - (5 + 10), 12, 5 + 10, 20)
            self.box1.bkgd(' ', curses.color_pair(2) | curses.A_REVERSE | curses.A_BOLD)
            self.box2.bkgd(' ', curses.color_pair(2) | curses.A_REVERSE | curses.A_BOLD)
            self.passed = False

        def getX(self):
            return self.x

        def getY(self):
            return self.y

        def draw(self):
            w = max(1, min(12, 13 - ((self.x + 12) - maxx + 1)) - max(0, -self.x + 1))
            if self.x > -12:
                self.box1.resize(self.y, w)
                self.box1.mvwin(0, max(0, self.x - 1))
                self.box2.resize(maxy - (self.y + 7), w)
                self.box2.mvwin(self.y + 7, max(0, self.x - 1))

        def refresh(self):
            self.box1.noutrefresh()
            self.box2.noutrefresh()

        def move(self):
            self.x = self.x - 1

        def getPassed(self):
           return self.passed

        def setPassed(self):
           self.passed = True

    def createTube():
        tube = Tube(maxx, int((maxy - 11) * random.random()) + 1)
        tubes.append(tube)

    createTube()

    def drawBird():
        #global bird
        #bird = tubes[0]['y'] + 4
        if bird >= 0 and bird < maxy:
            myscreen.addstr(bird, birdXPos+5, "_", curses.color_pair(4))
        if bird >= -1 and bird < maxy - 1:
            myscreen.addstr(bird+1, birdXPos, "\\.", curses.color_pair(4))
            myscreen.addstr(bird+1, birdXPos+3, "_", curses.color_pair(3) | curses.A_BOLD)
            myscreen.addstr(bird+1, birdXPos+4, "(", curses.color_pair(4))
            myscreen.addstr(bird+1, birdXPos+5, "9", curses.color_pair(1) | curses.A_BOLD)
            myscreen.addstr(bird+1, birdXPos+6, ">", curses.color_pair(3))
        if bird >= -2 and bird < maxy - 2:
            myscreen.addstr(bird+2, birdXPos+1, "\\", curses.color_pair(4))
            myscreen.addstr(bird+2, birdXPos+2, "==", curses.color_pair(5))
            myscreen.addstr(bird+2, birdXPos+4, "_)", curses.color_pair(3) | curses.A_BOLD)
        if bird >= -3 and bird < maxy - 3:
            myscreen.addstr(bird+3, birdXPos+2, "-", curses.color_pair(1))
            myscreen.addstr(bird+3, birdXPos+3, "'", curses.color_pair(5) | curses.A_BOLD)
            myscreen.addstr(bird+3, birdXPos+4, "=", curses.color_pair(1))

    score = 0

    def draw(dead = False):
        myscreen.erase()
        #myscreen.border(1, 1, 0, 1, 1, 1, 1, 1)
        myscreen.addstr(0, maxx // 2 - 6, "FlasciiBird", curses.color_pair(1))
        strscore = "Score: " + str(score)
        myscreen.addstr(maxy - 1, maxx // 2 - len(strscore) // 2 , strscore, curses.color_pair(1) | curses.A_BOLD)
        drawBird()

        if dead:
            lost = "You lost! Score: " + str(score)
            lostWin = curses.newwin(3, len(lost) + 2, maxy // 2 - 1, maxx // 2 - len(lost) // 2 - 2)
            lostWin.border(0)
            lostWin.addstr(1, 1, lost, curses.color_pair(1) | curses.A_BOLD)
        for tube in tubes:
            tube.draw()

        myscreen.noutrefresh()
        for tube in tubes:
            tube.refresh()
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
        bird = maxy // 2 - 4
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
        if tubes[-1].getX() < maxx - 1.2*maxy:
            createTube()
        if tubes[0].getX() < (birdXPos - 11) and not tubes[0].getPassed():
            #curses.beep()
            score = score + 1
            tubes[0].setPassed()
        if (newTime - updateTime) > 0.05:
            for tube in tubes:
                tube.move()
            if tubes[0].getX() < -10:
                del tubes[0]
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
	
        if birdXPos - 10 <= tubes[0].getX() <= birdXPos + 7:
            tol = max(0, tubes[0].getY() + 8 - (bird + 2))
            if bird + 1 < tubes[0].getY() or (bird + 4 >= tubes[0].getY() + 8 and birdXPos - 11 + tol < tubes[0].getX() <= birdXPos + 7 - tol):
                if death():
                    break

        key = myscreen.getch()

    curses.endwin()
except:
    os.system('stty sane')
    raise
