import math
version = '1.2'
class time():
    def second(self,time,_format):
        time = float(time)
        if _format == 'minute':
            return time * 60
        elif _format == 'hour':
            return time * 3600
        elif _format == 'day':
            return time * 3600 * 24
    def hour(self,time,_format):
        time = float(time)
        if _format == 'second':
            return float(time / 3600)
        elif _format == 'minute':
            return float(time / 60)
        elif _format == 'day':
            return float(time * 24)
    def minute(self,time,_format):
        time = float(time)
        if _format == 'second':
            return float(time / 60)
        elif _format == 'hour':
            return float(time * 60)
        elif _format == 'day':
            return float(time * 60 * 24)
    def day(self,time,_format):
        time = float(time)
        if _format == 'second':
            return float(time / 3600 / 24)
        elif _format == 'minute':
            return float(time/60/24)
        elif _format == 'hour':
            return float(time / 24)
class function():
    def graph(self,function,start=[-3,3]):
        results = []
        for x in range(start[0],start[1]+1):
            res = eval(function)
            results.append([x,res])
        return results
    def tax(current,interest,years):
        res = []
        res.append(float(current)*(0.01*float(interest))*float(years))
        res.append(float(current)*(0.01*float(interest))*float(years) + current)
        return res

class converters():
    def km_miles(self,km):
        return float(km*0.6215)
    def miles_km(self,mi):
        return float(mi*1.609)
    def m_yards(self,m):
        return float(m*1.0936)
    def yards_m(self,y):
        return float(y*0.9144)
    def inch_mm(self,i):
        return float(i*25.4)
    def mm_inch(self,mm):
        return float(mm*0.03937)
    def fahren_celsi(self,f):
        return float((f-32)/(9.0/5.0))
    def celsi_fahren(self,c):
        return float((c*(9.0/5.0))+32)
    def b1(self,n):
        return "01"[n%2]
    def b2(self,n):
        return self.b1(n>>1)+self.b1(n)
    def b3(self,n):
        return self.b2(n>>2)+self.b2(n)
    def b4(self,n):
        return self.b3(n>>4)+self.b3(n)
    def text_binary(self,text):
        bytes = [ self.b4(n) for n in range(256)]
        return ''.join(bytes[ord(c)] for c in text)
class motion():
    def speed(self,distance,time):
        return float(distance)/float(time)
    def time(self,distance,speed):
        return float(distance)/float(speed)
    def distance(self,time,speed):
        return float(time)*float(speed)
    def acceleration(self,v1,v2,t1,t2):
        return float((float(v2)-float(v1))/(float(t2)-float(t1)))
class shapes():
    class square():
        def perimiter(self,width):
            return 4.0*float(width)
        def area(self,width):
            return pow(width,2.0)
    class cube():
        def volume(self,side):
            return pow(side,3.0)
        def area(self,side):
            return (float(side)*float(side))*6.0
    class cone():
        def volume(self,height,radius):
            return (1/3)*math.pi*(radius*radius)*height
        def area(self,radius,sides):
            return (math.pi*radius*sides) + (math.pi*pow(radius,2))
    class rect():
        def perimiter(self,width,height):
            return 2.0*(float(width)+float(height))
        def area(self,width,height):
            return float(width)*float(height)
    class circle():
        def perimiter(self,radius):
            return 2.0*math.pi*float(radius)
        def area(self,radius):
            return math.pi*float(pow(radius*2.0))
    class cylinder():
        def area(self,radius,height):
            return math.pi*float(radius,2.0)*float(height)
        def volume(self,radius,height):
            return math.pi*float(radius*2.0)*float(height)
    class ellipse():
        def area(self,radius1,radius2):
            return math.pi*float(radius1)*float(radius2)
    class sphere():
        def area(self,radius):
            return 4.0*math.pi*pow(radius*2.0)
        def volume(self,radius):
            return (4/3)*math.pi*pow(r,3)
    class rectPrism():
        def volume(self,side1,side2,side3):
            return float(side1)*float(side2)*float(side3)
        def area(self,side1,side2,side3):
            return (2.0*float(side1)*float(side2)) + (2.0*float(side2)*float(side3)) + (2.0*float(side1)*float(side3))
    class triangle():
        def perimiter(self,a,b,c):
            return float(a) + float(b) + float(c)
        def area(self,base,height):
            return (float(base)*float(height))/2.0
class statistics():
    def average(self,numbers,accuracy=3):
        a = len(numbers)
        total = 0.0
        for x in numbers:
            total += x
        return round(total / a,accuracy)
    def percent(self,correct,total):
        return round(float((float(correct)/float(total))*100),2)
class sequences():
    def csv(self,sequence,start,end):
        x = start
        result = ''
        while x <= end:
            result = result + str(findTerm(sequence,x)) + ','
            x = x + 1
        result = result[:-1]
        return result
    def create(self,d,o,t1,n):
        sequence = []
        x = 1
        while x <= n:
            if o == '/':
                if x == 1:
                    sequence.append(t1)
                    x = x + 1
                sequence.append(float(t1) / pow(float(d),float(x) - 1.0))
                t = 3
            if o == '*':
                if x == 1:
                    sequence.append(t1)
                    x = x + 1
                sequence.append(t1 * pow(d,x - 1))
                t = 2
            if o == '-':
                o = '+'
                d = -d
            if o == '+':
                sequence.append(t1 + ((x - 1) * d))
                t = 1
            x = x + 1
        return {'t':t,'l':sequence,'d':d}
    def createFromString(self,sequence):
        if type(sequence) == str:
            sequence = sequence.split(',')
        x = 0
        for n in sequence:
            if n != '':
                sequence[x] = int(n)
            x = x + 1
        x = 0
        x2 = 0
        y = 0
        a = ''
        b = ''
        c = ''
        e = ''
        for each in sequence:
            if each != '':
                if c == '':
                    c = y
                if a == '':
                    a = each
                    x = 0
                elif b == '':
                    b = each
                    x2 = x
                elif e == '':
                    e = each
                    break
            x = x + 1
            y = y + 1
        if e == '':
            if x != 0:
                d = (b - a) / (x2)
            else:
                d = b - a
            t = 1
        else:
            if x != 0:
                d = (b - a) / x2
                d2 = (e - b) / x2
            else:
                d = b - a
                d2 = e - b
            if d != d2:
                t = 2
                if x != 0:
                    d = (float(b) / pow(float(a),float(1/float(x2))))
                else:
                    d = float(b) / float(a)
            else:
                t = 1
        sequence2 = sequence
        if t == 1:
            if c > 0:
                x2 = c
                y = 1
                while x2 >= 0:
                    sequence2[x2] = sequence[c] - (d * (y - 1))
                    y = y + 1
                    x2 = x2-1      
            y = 1
            x2 = c
            while x2 < len(sequence):
                sequence2[x2] = sequence[c] + (d * (y - 1))
                y = y + 1
                x2 = x2+1    
            return {'l':sequence2,'d':d,'t':1}
        if t == 2:
            if c > 0:
                x2 = c
                y = 1
                while x2 >= 0:
                    sequence2[x2] = round(sequence[c] / pow(d,y-1),5)
                    y = y + 1
                    x2 = x2-1      
            y = 1
            x2 = c
            while x2 < len(sequence):
                sequence2[x2] = round(sequence[c] * pow(d,y-1),5)
                y = y + 1
                x2 = x2+1    
            return {'l':sequence2,'d':d,'t':2}
    def findTerm(self,sequence,n):
        if sequence['t'] == 1:
            return int(sequence['l'][0]) + ((n - 1) * sequence['d'])
        elif sequence['t'] == 2:
            return round(float(sequence['l'][0]) * pow(sequence['d'],n-1),5)
        elif sequence['t'] == 3:
            return round(float(sequence['l'][0]) /pow(float(sequence['d']),float(n)-1.0),5)
