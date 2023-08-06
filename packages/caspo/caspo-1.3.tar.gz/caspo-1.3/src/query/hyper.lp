sub(set(U,S,nil),1,V)            :- edge(U,V,S).
sub(set(U,SU,set(W,SW,T)),N+1,V) :- edge(U,V,SU), 
                                    sub(set(W,SW,T),N,V), U < W.

in(U,S,set(U,S,T))   :- sub(set(U,S,T),N,V).
in(W,SW,set(U,SU,T)) :- in(W,SW,T), sub(set(U,SU,T),N,V).
