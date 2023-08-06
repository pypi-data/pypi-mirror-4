# -*- coding: utf-8 -*-
'''

  product:  Feng Shui 
  
  Copyright (C) 2012 Cornelius Kölbel
  contact:  http://www.cornelinux.de
            corny@cornelinux.de

  Description:  This is the package for feng shui calculations


    Todo:
        bazi
            http://chinesische-astrologie.net/chinesische_astrologie/horoskop_horoskope.html
            http://www.fengshui-ratgeber.de/bazi-horoskop-rechner/
            
        fliegende sterne
            http://www.fengshui-ratgeber.de/bazi-horoskop-rechner/

'''

import re

year_starts_at_feb_05 = [ 1910, 1911, 1912, 1915, 1919, 
                         1920, 1923,  1924, 1927, 1928,
                         1931, 1932, 1935, 1936, 1939,
                         1940, 1943, 1944, 1948, 
                         1952, 1956, 
                         1960, 1964, 1968,
                         1972, 1976, 
                         1980,  
                         ]

def Quersumme(zahl):
    result = 0
    while zahl:
        result += zahl % 10
        zahl = int(zahl / 10)
    return result

def mini_quersumme(year, jahrhundert):
    calc = Quersumme( year - jahrhundert ) 
    while calc >= 10:
        calc = Quersumme( calc )
    return calc

def get_year_from_date(date):
    '''
    get the chinese year from a given date
    '''
    year = 0
    m = re.match("(\d{1,2})\.(\d{1,2})\.(\d{4})", date )
    if m:
        day     = int( m.groups()[0] )
        month   = int( m.groups()[1] )
        year    = int( m.groups()[2] )        
        # new year starts at 4th of february
        if month == 1:
            year = year - 1
        if month == 2 and day < 4:
            year = year - 1
            
        if month == 2 and day == 4 and year in year_starts_at_feb_05:
            year = year -1
    else:
        raise Exception("No valid date passed! %s" % date)
    
    return year
        

def ming_gua(sex, birthdate):
    '''
    see http://www.flyingstars-fengshui.com/minggua.htm
    
    sex 0 : female
    sex 1 : male
    
    birthdate, european: 2.1.1980
    
    '''
    mgua = -1
    
    m = re.match("(\d{1,2})\.(\d{1,2})\.(\d{4})", birthdate )
    
    if m:
        day     = int( m.groups()[0] )
        month   = int( m.groups()[1] )
        year    = int( m.groups()[2] )
        
        # new year starts at 4th of february
        if month == 1:
            year = year - 1
        if month == 2 and day < 4:
            year = year - 1
            
        if month == 2 and day == 4 and year in year_starts_at_feb_05:
            year = year -1
        
        
        if sex==1:
            # male
            if year <= 1999 and year > 1900:
                calc = mini_quersumme(year, 1900)                      
                mgua = 10 - calc             
            elif year == 2000:
                mgua = 9
            elif year >2000 and year <= 2099:
                calc = mini_quersumme(year, 2000)
                mgua = 9 - calc
                 
            if mgua == 5:
                mgua = 2
        
        elif sex==0:
            # female
            if year <=1999 and year > 1900:
                calc = mini_quersumme(year, 1900)
                calc = calc + 5
                mgua = mini_quersumme(calc, 0)
            elif year == 2000:
                mgua = 6
            elif year > 2000 and year <= 2099:
                calc = mini_quersumme(year, 2000)
                calc = calc +6
                mgua = mini_quersumme(calc, 0)
                
            if mgua == 5:
                mgua = 8
            
        else:
            raise Exception("No valid sex! Must be 0 - female- or 1 -male -")
        
    else:
        raise Exception("No valid date to calculate Ming Gua! %s" % birthdate)
    
    return mgua


def check_order_backward(star, sector, period):
    ret = False
    # special case: 5 follows the period star!
    if star == 5:
        star  = period
    
    if (star & 1 and sector in [2,3]) or (not star & 1 and sector == 1):
        # odd number, ordering backward
        ret = True
        
    return ret
    
def flying_stars(year, facing):
    '''
    calculates the flying starts for a building.
        in:
            year:     year of building
            facing:    degree of the facing 0..359
    '''
    period = 0
    year = int(year)
    # determine period:
    if year in range(1864,1883+1):
        period = 1
    elif year in range(1884,1903+1):
        period = 2
    elif year in range(1904,1923+1):
        period = 3
    elif year in range(1924,1943+1):
        period = 4
    elif year in range(1944,1963+1):
        period = 5
    elif year in range(1964,1983+1):
        period = 6
    elif year in range(1984,2003+1):
        period = 7
    elif year in range(2004,2023+1):
        period = 8
    elif year in range(2024-2043+1):
        period = 9
    else:
        raise Exception("the year you specified (%i) can not be used to determine a certain period!")

    # determine facing, we do *10 to use the comma 
    facing = float(facing)
    direction = ""
    sector = 0
    if facing > 157.5 and facing < 202.5:
        # south
        direction = "S"
        water = 2
        mountain = 8
        if facing > 157.5 and facing < 172.5:
            sector = 1
        elif facing > 172.5 and facing < 187.5:
            sector = 2
        elif facing > 187.5 and facing < 202.5:
            sector = 3
    elif facing > 202.5 and facing < 247.5:
        # southwest
        direction = "SW"
        water = 3
        mountain = 7
        if facing > 202.5 and facing < 217.5:
            sector = 1
        elif facing > 217.5 and facing < 232.5:
            sector = 2
        elif facing > 232.5 and facing < 247.5:
            sector = 3
    elif facing > 247.5 and facing < 292.5:
        # west
        direction = "W"
        water = 6
        mountain = 4
        if facing > 247.5 and facing < 262.5:
            sector = 1
        elif facing > 262.5 and facing < 277.5:
            sector = 2
        elif facing > 277.5 and facing < 292.5:
            sector = 3
    elif facing > 292.5 and facing < 337.5:
        # northwest
        direction = "NW"
        water = 9
        mountain = 1
        if facing > 292.5 and facing < 307.5:
            sector = 1
        elif facing > 307.5 and facing < 322.5:
            sector = 2
        elif facing > 322.5 and facing < 337.5:
            sector = 3
    elif facing > 337.5 and facing < 22.5:
        # north
        direction = "N"
        water = 8
        mountain = 2
        # Fixme: well, being 400 degree would also be NORTH! ;-)
        if facing > 337.5 and facing < 352.5:
            sector = 1
        elif facing > 352.5 and facing < 7.5:
            sector = 2
        elif facing > 7.5 and facing < 22.5:
            sector = 3
    elif facing > 22.5 and facing < 67.5:
        # northeast
        direction = "NE"
        water = 7
        mountain = 3
        if facing > 22.5 and facing < 37.5:
            sector = 1
        elif facing > 37.5 and facing < 52.5:
            sector = 2
        elif facing > 52.5 and facing < 67.5:
            sector = 3
    elif facing > 67.5 and facing < 112.5:
        # east
        direction = "E"
        water = 4
        mountain = 6
        if facing > 67.5 and facing < 82.5:
            sector = 1
        elif facing > 82.5 and facing < 97.5:
            sector = 2
        elif facing > 97.5 and facing < 112.5:
            sector = 3
    elif facing > 112.5 and facing < 157.5:
        # southeast
        direction = "SE"
        water = 1
        mountain = 9
        if facing > 112.5 and facing < 127.5:
            sector = 1
        elif facing > 127.5 and facing < 142.5:
            sector = 2
        elif facing > 142.5 and facing < 157.5:
            sector = 3
    else:
        raise Exception("Your facing is located directly on the edge of the sectors: %s" % str(facing))
    
    # basis stars
    star_path  = [5,9,6,7,2,8,3,4,1]
    
    po = [ [1,2,3,4,5,6,7,8,9],
           [2,3,4,5,6,7,8,9,1],
           [3,4,5,6,7,8,9,1,2],
           [4,5,6,7,8,9,1,2,3],
           [5,6,7,8,9,1,2,3,4],
           [6,7,8,9,1,2,3,4,5],
           [7,8,9,1,2,3,4,5,6],
           [8,9,1,2,3,4,5,6,7],
           [9,1,2,3,4,5,6,7,8] ]
    
    # order for backward (odd numbers)
    po_back = [ [1,9,8,7,6,5,4,3,2],
                [2,1,9,8,7,6,5,4,3],
                [3,2,1,9,8,7,6,5,4],
                [4,3,2,1,9,8,7,6,5],
                [5,4,3,2,1,9,8,7,6],
                [6,5,4,3,2,1,9,8,7],
                [7,6,5,4,3,2,1,9,8],
                [8,7,6,5,4,3,2,1,9],
                [9,8,7,6,5,4,3,2,1] ]
    
    basis_stars  = [0]*9
    
    for i in range(0,9):
        basis_stars[ star_path[i]-1 ] = po[ period-1 ][i] 

    # water stars
    water_star = basis_stars[water-1]
    water_stars = [0]*9
    po_water = po
    
    if check_order_backward( water_star, sector, period ):
        po_water = po_back 
        
    for i in range(0,9):
            water_stars[ star_path[i]-1] = po_water[ water_star-1][i]
    
    # mountatin stars
    mountain_star = basis_stars[mountain-1]
    mountain_stars = [0]*9
    po_mountain = po
    if check_order_backward(mountain_star, sector, period):
        # odd number, ordering backward
        po_mountain = po_back
    
    for i in range(0,9):
        mountain_stars[ star_path[i]-1] = po_mountain[ mountain_star-1][i]
    
    
    return { "period" : period, 
             "direction" : direction,
             "sector" : sector,
             "basis_stars" : basis_stars,
             "water_stars" : water_stars,
             "mountain_stars" : mountain_stars }
    
def dump_stars( dic ):
    '''
    Dump the flying stars
    '''
    m = dic["mountain_stars"]
    w = dic["water_stars"]
    b = dic["basis_stars"]
    text =  "+-----+-----+-----+\n"
    text += "| %i %i | %i %i | %i %i |\n" % (m[0],w[0],m[1],w[1],m[2],w[2])
    text += "|  %i  |  %i  |  %i  |\n"    % (b[0],b[1],b[2])
    text += "+-----+-----+-----+\n"
    text += "| %i %i | %i %i | %i %i |\n" % (m[3],w[3],m[4],w[4],m[5],w[5])
    text += "|  %i  |  %i  |  %i  |\n"    % (b[3],b[4],b[5])
    text += "+-----+-----+-----+\n"
    text += "| %i %i | %i %i | %i %i |\n" % (m[6],w[6],m[7],w[7],m[8],w[8])
    text += "|  %i  |  %i  |  %i  |\n"    % (b[6],b[7],b[8])
    text += "+-----+-----+-----+\n"
    return text
    