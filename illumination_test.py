import pygame
import numpy as np

import gradients
##from gradients import gradient
from gradients import genericFxyGradient

from pygame.locals import *

def segment_intersection(s1, e1, s2, e2):
    """
        line_intersection(s1, e1, s2, e2) -> point 

        s1, e1, s2, e2 are the start and end points of the two segments we want to check for intersection

        in the function, t and r represent the parameters of the parametric functions that describe segment 1 and segment 2 respectively
    """
    dx1 = e1[0] - s1[0]
    dx2 = e2[0] - s2[0]
    dy1 = e1[1] - s1[1]
    dy2 = e2[1] - s2[1]

    n = s2[1] - s1[1] + dy2 * ((s1[0] - s2[0])/dx2) 
    d = dy1 - dy2 * dx1 / dx2

    t = n/d
    r = (s1[0] + dx1 * t - s2[0])/dx2

    return t, r, (s1[0] + dx1 * t, s1[1] + dy1 * t)

class Box:
    def __init__(self, x, y, w, h, boundary = False):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.boundary = boundary

        self.points = np.array([
            [self.x, self.y],
            [self.x + self.w, self.y],
            [self.x + self.w, self.y + self.h],
            [self.x, self.y + self.h]
        ])
    
    def display(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.w, self.h), 1)
    
    def intersect(self, start, end, infinite = False):
        intersections = []
        for i in range (len(self.points)):
        
            s, e = self.points[i], self.points[(i + 1) % len(self.points)]

            t, r, intersection = segment_intersection(s, e, start, end)
            if (0 <= r <= 1 or (infinite and r >= 0)) and (0.0 <= t <= 1):
                intersections.append(intersection)

        return intersections

class Polygon(Box):
    def __init__(self, points, boundary = False):
        self.points = np.array(points)
        self.boundary = boundary
    
    def display(self, screen):
        pygame.draw.polygon(screen, (255, 255, 255), self.points, 1)

class Character:
    def __init__(self):
        pass

if __name__ == "__main__":
    pygame.init()

    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((700, 700))

    illumination = pygame.Surface((300, 300))
    shadow = pygame.Surface((300, 300))

    boxes = [
        Box(250, 250, 50, 50),
        Box(50, 100, 20, 50),
        Box(400, 250, 50, 50),
        Box(250, 50, 30, 30),
        Box(-1, -1, 502, 502, boundary = True),
        Polygon((
            (200, 300),
            (200, 350),
            (250, 350),
            (250, 320),
            (220, 320),
            (220, 300)
        )),

    ]

    for i in range (10):
        boxes.append(
            Polygon(((350, 100 + i * 15), (350, 100 + i * 15 + 10)))
        )

    # compile all the walls
    wall_starts = [] 
    wall_ends = []
    for polygon in boxes:
        for i in range (len(polygon.points)):
            s, e = polygon.points[i], polygon.points[(i + 1) % len(polygon.points)]

            wall_starts.append(s)
            wall_ends.append(e)

    # walls -> n x 2
    wall_starts = np.array(wall_starts).transpose()
    wall_ends = np.array(wall_ends).transpose()

    cursor = np.asarray([250, 250])

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                pygame.quit()
            
            #elif event.type == pygame.MOUSEMOTION:
        cursor = np.asarray(pygame.mouse.get_pos()) + 0.001

        screen.fill((0, 0, 0))
        illumination.fill((0, 0, 0))

        points = []

        for b in boxes:
            #b.display(screen)

            for p in b.points:
                diff = p - cursor
                length = np.sqrt(np.sum(diff ** 2))
                angle = np.math.atan2(diff[1], diff[0])

                left = length * np.array([np.cos(angle - 0.0001), np.sin(angle - 0.0001)]) + cursor
                right = length * np.array([np.cos(angle + 0.0001), np.sin(angle + 0.0001)]) + cursor

                points.append([p, angle])
                points.append([left, angle - 0.0001])
                points.append([right, angle + 0.0001])
            
        points.sort(key = lambda l: l[1])

        to_block = True     # is the line sweeping toward or away from a block?w
        
        c = 0 
        # points -> len(points) x 2
        prev = None
        for p in range (len(points) + 1):
            # check intersection with all walls
            t, r, intersections = segment_intersection(wall_starts, wall_ends, cursor.reshape([2, 1]), points[p % len(points)][0].reshape([2, 1]))

            conditions = (t >= 0) & (t <= 1)
            r = r * conditions
            idx = np.where((r) > 0.01, r, np.inf).argmin()

            #print(intersections)
            min_point = np.array([intersections[0][idx], intersections[1][idx]])

            #if min_point:
                #
            #print(min_point)   

            if p != 0:
                #pygame.draw.line(screen, (100 + int(100 * p / len(points)), 100, 100), cursor.astype(int), min_point)

                pygame.draw.polygon(illumination, (255, 255, 255), [[150, 150], np.array(min_point) - cursor + 150, prev - cursor + 150])
            prev = min_point

            #previous = np.asarray(min_point)

        
        #print(points_no_intersect) 

        shadow.blit(gradients.radial(150, (255, 255, 255, 255), (0, 0, 0, 255)), (0, 0))
        illumination.blit(shadow, (0, 0), special_flags = pygame.BLEND_MULT)

        screen.blit(illumination, cursor.astype(int) - 150,)


        pygame.display.flip()

        clock.tick(45)


            
    