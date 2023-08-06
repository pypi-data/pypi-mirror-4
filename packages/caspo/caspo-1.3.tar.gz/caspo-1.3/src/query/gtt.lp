model(I) :- conjunction(I,_,_,_).

input(V) :- stimulus(V), conjunction(_,C,_,_), in(V,_,C).
input(V) :- inhibitor(V), conjunction(_,C,_,_), in(V,_,C).

{exp(V)} :- input(V).

active(I,V) :- exp(V), stimulus(V), model(I).

fixed(V) :- stimulus(V).
fixed(V) :- inhibitor(V), exp(V).

active(I,V) :- conjunction(I,S,M,V), not fixed(V),
               active(I,U)   : in(U,1,S),
               not active(I,U) : in(U,-1,S).

diff :- active(I1,V), not active(I2,V), I1 != I2, readout(V), model(I1;I2).
:- not diff.

#hide.