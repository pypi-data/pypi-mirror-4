model(I) :- conjunction(I,_,_,_).

{gexp(V)} :- stimulus(V).
{gexp(V)} :- inhibitor(V).

active(I,V) :- gexp(V), stimulus(V), model(I).

fixed(V) :- stimulus(V).
fixed(V) :- inhibitor(V), gexp(V).

active(I,V) :- conjunction(I,S,M,V), not fixed(V),
               active(I,U)   : in(U,1,S),
               not active(I,U) : in(U,-1,S).

diff :- active(I1,V), not active(I2,V), I1 != I2, readout(V), model(I1;I2).
:- not diff.

#hide.
#show diff.