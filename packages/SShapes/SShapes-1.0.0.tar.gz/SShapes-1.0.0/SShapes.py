# File: SShapes.py

import math

class SSquare:

    """
    A simple square is modeled in terms one property, its side.
    This class and its sibling classes, which model other shapes,
    can be used
      (1) to solve numeric problems, and
      (2) as a basis for painting nonrepresentational images.
    """

    def __init__(self, side):
        "Create a simple square with a given side length."
        self.side = side

    def getSide(self):
        "Return the side length of this square."
        return self.side

    def setSide(self,side):
        "Change the side length of this square to the specified value."
        self.side = side

    def perimeter(self):
        "Compute and return the perimeter of this square."
        return 4 * self.side

    def area(self):
        "Compute and return the area of this square."
        return math.pow(self.side,2)

    def diagonal(self):
        "Compute and return the length of the diagonal of this square."
        s = self.side
        return math.sqrt(math.pow(s,2)+math.pow(s,2))

    def expand(self,a):
        "Expand this sqaure by adding the given value to its side length."
        self.side = self.side + a

    def shrink(self,a):
        "Shrink this sqaure by adding the given value to its side length."
        self.side = self.side - a

    def inscribingCircle(self):
        "Return the simple circle which inscribes this square."
        radius = self.side / 2.0
        return SCircle(radius)

    def circumscribingCircle(self):
        "Return the simple circle which circumscribes this square."
        radius = self.diagonal() / 2.0
        return SCircle(radius)

    def strep(self):
        "Return a textual representation of this square."
        return "<SSquare: side=" + str(self.side) + ">"


class SCircle:

    """
    A simple circle is modeled in terms one property, its radoius.
    This class and its sibling classes, which model other shapes,
    can be used
      (1) to solve numeric problems, and
      (2) as a basis for painting nonrepresentational images.
    """

    def __init__(self, radius):
        "Create a simple circle with a given radius."
        self.radius = radius

    def getRadius(self):
        "Return the radius length of this circle."
        return self.radius

    def setRadius(self,radius):
        "Change the radius of this circle to the specified value."
        self.radius = radius

    def perimeter(self):
        "Compute and return the perimeter of this circle."
        return 2 * math.pi * self.radius

    def area(self):
        "Compute and return the perimeter of this circle."
        return math.pi * math.pow(self.radius,2)

    def diameter(self):
        "Compute and return the perimeter of this circle."
        return self.radius * 2

    def expand(self,a):
        "Expand this circle by adding the given value to its side radius."
        self.radius = self.radius + a

    def shrink(self,a):
        "Shrink this circle by subtracting the given value from its side radius."
        self.side = self.radius- a

    def inscribingSquare(self):
        "Return the simple square which inscribes this circle."
        key = Square(self.radius)
        side = key.diagonal()
        return SSquare(side)

    def circumscribingSquare(self):
        "Return the simple square which circumscribes this circle."
        return SSquare(self.diameter())

    def strep(self):
       "Return a textual representation of this circle."
       return "<SCircle: radius=" + str(self.radius) + ">"

class SRectangle:

    """
    A simple rectangle is modeled in terms two properties, its height and its
    width.  This class and its sibling classes, which model other shapes,
    can be used
      (1) to solve numeric problems, and
      (2) as a basis for painting nonrepresentational images.
    """

    def __init__(self, height, width):
        "Create a simple rectangle with a given height and width."
        self.height = height
        self.width = width

    def getHeight(self):
        "Return the height length of this square."
        return self.height

    def setHeight(self, h):
        "Change the height of this rectangle to the specified value."
        self.height = h

    def getWidth(self):
        "Return the width length of this square."
        return self.width

    def setWidth(self, w):
        "Change the width of this rectangle to the specified value."
        self.width = w

    def perimeter(self):
        "Compute and return the perimeter of this rectangle."
        return ( 2 * self.height) + ( 2 * self.width )

    def area(self):
        "Compute and return the area of this rectangle."
        return self.height * self.width

    def diagonal(self):
        "Compute and return the diagonal of this rectangle."
        return math.sqrt(math.pow(self.height,2) + math.pow(self.width,2))

    def expand(self, h, w):
        """
        Expand this rectangle by adding h to the height and
        w to the width.
        """
        self.height = self.height + h
        self.width = self.width + w

    def shrink(self, h, w):
        """
        Shrink this rectangle by subtracting h from the height and
        w from the width.
        """
        self.height = self.height - h
        self.width = self.width - w

    def strep(self):
        "Return a textual representation of this rectangle."
        h = str(self.height)
        w = str(self.width)
        return "<SRectangle: height=" + h + " width=" + w + ">"

    
class SPolygon:

    """
    A simple polygon is modeled in terms two properties, its degree and its
    side length.  This class and its sibling classes, which model other shapes,
    can be used
      (1) to solve numeric problems, and
      (2) as a basis for painting nonrepresentational images.
    """

    def __init__(self, degree, side):
        "Create a simple polygon with a given degree and side length."
        self.degree = degree
        self.side = side

    def getDegree(self):
        "Return the degree of this polygon."
        return self.degree

    def setDegree(self, d):
        "Change the degree of this polygon to the specified value."
        self.degree = d

    def getSide(self):
        "Return the side of this polygon."
        return self.side

    def setSide(self, s):
        "Change the side of this polygon to the specified value."
        self.side = s

    def inc(self):
        "Increase the degree of this polygon by 1."
        self.degree = self.degree + 1

    def dec(self):
        "Decrease the degree of this polygon by 1."
        self.degree = self.degree - 1

    def incSide(self):
        "Increase the side of this polygon by 1."
        self.side = self.side + 1

    def decSide(self):
        "Decrease the side of this polygon by 1."
        self.side = self.side - 1

    def perimeter(self):
        "Compute and return the perimeter of this polygon."
        return ( self.degree * self.side )

    def area(self):
        "Compute and return the area of this polygon."
        cc = self.circumscribingCircle()
        t = STriangle(self.side,cc.getRadius(),cc.getRadius())
        return ( t.area() * self.degree )

    def strep(self):
        "Return a textual representation of this polygon."
        d = str(self.degree)
        s = str(self.side)
        return "<SPolygon: degree=" + d + " side=" + s + ">"

    def circumscribingCircle(self):
        "Return the simple circle which inscribes this polygon."
        hs = self.side/2.0
        angleD = ( ( 360.0 / self.degree ) / 2.0 )
        angleR = math.radians(angleD)
        r = ( hs / math.sin(angleR) )
        return SCircle(r)

    def inscribingCircle(self):
        "Return the simple circle which circumscribes this polygon."
        hs = ( self.side / 2.0 )
        angleD = ( ( 360.0 / self.degree ) / 2.0 )
        angleR = math.radians(angleD)
        r = ( hs / math.tan(angleR) )
        return SCircle(r)

class STriangle:

    """
    A simple triangle is modeled in terms three properties, sideA, sideB, and
    sideC.  This class and its sibling classes, which model other shapes,
    can be used
      (1) to solve numeric problems, and
      (2) as a basis for painting nonrepresentational images.
    """

    def __init__(self, x):
        "Create a simple equilateral triangle with side x"
        self.sideA = x
        self.sideB = x
        self.sideC = x

    def __init__(self, x, y):
        "Create a simple isosceles triangle with sides x and y and y"
        self.sideA = x
        self.sideB = y
        self.sideC = y

    def __init__(self, a, b, c):
        "Create a simple triangle with sides a, b, and c."
        self.sideA = a
        self.sideB = b
        self.sideC = c

    def getSideA(self):
        "Return sideA of this triangle."
        return sideA

    def setSideA(self, a):
        "Change sideA of this triangle to a."
        self.sideA = a

    def getSideB(self):
        "Return sideB of this triangle."
        return sideB

    def setSideA(self, b):
        "Change sideB of this triangle to b."
        self.sideB = b

    def getSideC(self):
        "Return sideC of this triangle."
        return sideC

    def setSideA(self, c):
        "Change sideC of this triangle to c."
        self.sideC = c

    def perimeter(self):
        "Compute and return the perimeter of this triangle."
        return ( self.sideA + self.sideB + self.sideC )

    def area(self):
        "Compute and return the area of this triangle."
        a = self.sideA
        b = self.sideB
        c = self.sideC
        s = ( ( a + b + c ) / 2.0 )
        t = ( s * ( s - a ) * ( s - b ) * ( s - c ) )
        return math.sqrt(t)

    def strep(self):
        "Return a textual representation of this triangle."
        a = str(self.sideA)
        b = str(self.sideB)
        c = str(self.sideC)
        return "<STriangle: sideA=" + a + " sideB=" + b + "sideC=" + c + ">"

    
  
