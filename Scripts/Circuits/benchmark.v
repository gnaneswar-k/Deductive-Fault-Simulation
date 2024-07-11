module benchmark (A,B,C,D,E,F,OUT);

input A,B,C,D,E,F;
output OUT;
wire g,h,m,k,l,p,q,s,r,u,w;

or OR_1(g,C,D);
and AND_1(h,C,g);
and AND_2(k,g,D);
or OR_2(m,h,k);
xor XOR_1(l,E,F);
nor NOR_1(p,A,B,m);
or OR_3(q,B,m);
or OR_4(s,l,m);
and AND_3(r,A,p);
and AND_4(u,A,m);
and AND_5(w,q,s);
xor XOR_2(OUT,r,u,w);

endmodule