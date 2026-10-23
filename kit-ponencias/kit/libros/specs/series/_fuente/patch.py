import sys
# uso: python3 patch.py archivo.py  (lee pares de stdin separados por lineas '=>>' y '-----')
f=sys.argv[1]
s=open(f,encoding='utf-8').read()
raw=sys.stdin.read().strip().split('\n-----\n')
for blk in raw:
    a,b=blk.split('\n=>>\n')
    a=a.strip('\n'); b=b.strip('\n')
    if s.count(a)!=1:
        print('NO UNICO/NO ENCONTRADO (%d):'%s.count(a), a[:70]); continue
    s=s.replace(a,b)
open(f,'w',encoding='utf-8').write(s)
