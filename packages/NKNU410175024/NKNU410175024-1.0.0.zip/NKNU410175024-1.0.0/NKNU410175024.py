'''
Created on 2012/10/24

@author: annie
'''




k=input('Please enter a integer:1.while  2.for ' )
j=int(k)

if j==1:
    i=0
    while i<8:
      i += 1
      print("*"*i)
    


    i=0
    while i<6:
        i += 1
        print(" "*(6-i)," *"*i)
        
    i=0
    while i<20:
         i += 1
         print(" "*(20-i)," *"*i)
        
    i=0
    while i<11:
        i += 1
        print(" "*(11-i)," *"*i)
        
        
        
        
        
    i=0
    while i<11:
        i += 1
        print(" "*(11-i)," *"*i)
        
        
        
        
    i=0
    while i<2:
        i += 1
        print("  "*(4-i),"  *"*i) 
        
    y=0
    while y<6:
        y += 1
        print(" "*(6-y),"*"*1," "*(2*y),"*"*1)
            
    print("* "*10)
        
        
elif j==2:
    for x in range(8):
        print("*"*(x+1))
        
    
    for x in range(6):
        print(" "*(5-x)," *"*x)
        
    
    
    for x in range(20):
        print(" "*(19-x)," *"*x)
        
        
    for x in range(11):
        print(" "*(10-x)," *"*x)

   
    for x in range(1,3):
        print(" "*(7-x)," * "*x)

    for y in range(1,6):
        print(" "*(5-y)," *"*1," "*(2*y),"* "*1),

    count=[" * "]
    print(count[0]*6)


else:
    print("false")

