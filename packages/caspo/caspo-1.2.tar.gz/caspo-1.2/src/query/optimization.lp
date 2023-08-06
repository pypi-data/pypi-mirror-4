#const p = 2.
#const maxsize = -1.

dfactor(F) :- F = #pow(10, p).

:- maxsize + 1 [conjunction(_,N,_) = N], maxsize >= 0.

residual(D,V,1,#pow(F-D,2)) :- obs(E,V,D), dfactor(F), D<F.
residual(D,V,0,#pow(D,2))   :- obs(E,V,D), D>0.

#minimize[conjunction(_,N,_) = N @ 1].
#minimize[active(E,V) : obs(E,V,D) : residual(D,V,1,W) = W @ 2,
         not active(E,V) : obs(E,V,D) : residual(D,V,0,W) = W @ 2].
