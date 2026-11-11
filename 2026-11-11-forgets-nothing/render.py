from PIL import Image
n=17;rule=45;OUT='./'
def step(s):
    o=0
    for i in range(n):
        l=(s>>((i-1)%n))&1;c=(s>>i)&1;r=(s>>((i+1)%n))&1
        if (rule>>((l<<2)|(c<<1)|r))&1: o|=1<<i
    return o
rows=[];s=1
while True:
    rows.append(s); s=step(s)
    if s==1: break
assert len(rows)==78812
COLS,RPC,gut,mx,my=17,4636,8,20,20
W=mx*2+COLS*n+(COLS-1)*gut; H=my*2+RPC
paper=(244,239,228); ink=(34,30,40); red=(196,64,44)
im=Image.new('RGB',(W,H),paper); px=im.load()
for k,s in enumerate(rows):
    col,row=divmod(k,RPC)
    x0=mx+col*(n+gut); y=my+row
    lone=bin(s).count('1')==1
    for i in range(n):
        if (s>>i)&1: px[x0+i,y]=red if lone else ink
    if lone:  # small tick above the column marking where the lone seat is
        px[x0+s.bit_length()-1,y-3]=red; px[x0+s.bit_length()-1,y-4]=red
im=im.convert('P',palette=Image.ADAPTIVE,colors=4)
im.save(OUT+'loop.png',optimize=True)
print(W,H)
top=im.convert('RGB').crop((0,0,W,230)).resize((W*2,460),Image.NEAREST); top.save(OUT+'preview.png',optimize=True)
