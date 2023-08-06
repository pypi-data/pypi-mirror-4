{conjunction(C,N,V)} :- sub(C,N,V).

:- conjunction(C1,N,V), conjunction(C2,M,V), 
   N < M, in(U,S,C2) : in(U,S,C1).
   
exp(E) :- exp(E,_,_).
fixed(E,V) :- exp(E), stimulus(V).
fixed(E,V) :- inhibitor(V), exp(E,V,0).

active(E,V) :- exp(E,V,1), stimulus(V).
active(E,V) :- exp(E), conjunction(S,M,V), not fixed(E,V),
               active(E,U) : in(U,1,S),
               not active(E,U) : in(U,-1,S).

#const maxsize = -1.
#const maxresidual = -1.


residual(D,V,1,#pow(F-D,2)) :- obs(E,V,D), dfactor(F), D<F.
residual(D,V,0,#pow(D,2))   :- obs(E,V,D), D>0.

:- maxsize + 1 [conjunction(_,N,_) = N], maxsize >= 0.
:- maxresidual + 1 [active(E,V) : obs(E,V,D) : residual(D,V,1,W) = W, not active(E,V) : obs(E,V,D) : residual(D,V,0,W) = W], 
   maxresidual >= 0.