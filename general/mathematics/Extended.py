def Euler(a,b)-> (int,int): # type: ignore
    if a%b==0:
        return (0,1)
    u,v = Euler(b,a%b)
    return (v,u - v * (a//b))
print(Euler(26513,32321))