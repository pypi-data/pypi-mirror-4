#minimize[conjunction(_,N,_) = N @ 1].
#minimize[active(E,V) : obs(E,V,D) : residual(D,V,1,W) = W @ 2,
         not active(E,V) : obs(E,V,D) : residual(D,V,0,W) = W @ 2].
