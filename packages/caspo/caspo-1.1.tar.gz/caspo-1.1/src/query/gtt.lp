{gexp(V)} :- stimuli(V).
{gexp(V)} :- inhibitor(V).

active(I,V) :- gexp(V), stimuli(V), I=1..2.
inactive(I,V) :- stimuli(V), I=1..2, not active(I,V).
inactive(I,V) :- inhibitor(V), I=1..2, not gexp(V).

fixed(V) :- stimuli(V).
fixed(V) :- inhibitor(V), not gexp(V).

active(I,V) :- clause(I,S,M,V), not fixed(V),
               active(I,U)   : in(U,1,S),
               inactive(I,U) : in(U,-1,S).

inactive(I,V) :- vertex(V), not fixed(V), I=1..2, not active(I,V).

diff :- active(I1,V), inactive(I2,V), I1 != I2, readout(V).
:- not diff.

#hide.
#show diff.