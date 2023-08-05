link(B,S,T) :- clause(_,B,S,T).

ocu((B,S,T),O) :- O = [clause(_,B,S,T)], link(B,S,T).

notall(B,S,T) :- ocu((B,S,T),O), nmodels(N), O<N.

exclusive(a(B1,S1,T1,M1),b(B2,S2,T2,M2)) :- notall(B1,S1,T1), notall(B2,S2,T2), 
                                          not clause(N,B2,S2,T2) : clause(N,B1,S1,T1),
                                          not clause(N,B1,S1,T1) : clause(N,B2,S2,T2), 
                                          notall(B1,S1,T1) < notall(B2,S2,T2),
                                          ocu((B1,S1,T1),M1), ocu((B2,S2,T2),M2), 
                                          M1+M2 == M, nmodels(M).


inclusive(a(B1,S1,T1,M1),b(B2,S2,T2,M2)) :- clause(N,B2,S2,T2) : clause(N,B1,S1,T1) : N = 1..M, 
                                          clause(N,B1,S1,T1) : clause(N,B2,S2,T2) : N = 1..M,
                                          link(B2,S2,T2), link(B1,S1,T1),
                                          link(B2,S2,T2) < link(B1,S1,T1), nmodels(M),
                                          ocu((B1,S1,T1),M1), ocu((B2,S2,T2),M2), M1<M, M2<M.

#hide.
#show exclusive/2.
#show inclusive/2.