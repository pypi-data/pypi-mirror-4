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
