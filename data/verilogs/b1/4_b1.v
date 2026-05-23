module c2(N1, N2, N4);
input N1;
input N2;
output N4;
wire _0_;
NAND2_X2 _1_ (
    .A1(N2),
    .A2(N1),
    .ZN(_0_)
);
INV_X2 _2_ (
    .A(_0_),
    .ZN(N4)
);
endmodule
