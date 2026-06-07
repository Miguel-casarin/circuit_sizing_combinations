module teste1(N1, N2, N3, N4, N22);
    input N1;
    wire N1;
    input N2;
    wire N2;
    input N3;
    wire N3;
    input N4;
    wire N4;
    output N22;
    wire N22;
    wire _0_;
    wire _1_;
    wire _2_;
    NOR2_X4 _2_ (
        .A1(N1),
        .A2(N2),
        .ZN(_0_)
    );
    AND2_X2 _3_ (
        .A1(_0_),
        .A2(N3),
        .ZN(_1_)
    );
    XOR2_X1 _4_ (
        .A(_1_),
        .B(N4),
        .Z(_2_)
    );

    INV_X1 _5_ (
        .A(_2_),
        .ZN(N22)
    );
endmodule