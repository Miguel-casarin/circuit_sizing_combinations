module teste3(N1, N2, N4);
    input N1;
    wire N1;
    input N2;
    wire N2;
    output N4;
    wire N4;
    wire _0_;
    INV_X2 _0_ (
        .A(N1),
        .ZN(_0_)
    );

    XOR2_X2 _1_ (
        .A(_0_),
        .B(N2),
        .Z(N4)
    );
endmodule