module (N1, N2, N3, N4, N5, N7);
    input N1;
    wire N1;

    // primeiro cainho
    INV_X1 _0_ (
        .A(N1),
        .ZN(_0_)
    );

    INV_X1 _1_ (
        .A(_0_),
        .ZN(_1_)
    );

    NOR2_X1 _2_ (
        .A1(_1_),
        .A2(N2),
        .ZN(_2_)
    );

    XOR2_X1 _3_ (
        .A(N3),
        .B(_2_),
        .Z(_3_)
    );

    INV_X1 _4_ (
        .A(_3_),
        .ZN(_4_)
    );

    // segundo caminho
    AND2_X1 _4_ (
        .A1(_4_),
        .A2(N4),
        .ZN(_5_)
    );

    NAND2_X1 _5_ (
        .A1(),
        .A2(),
        .ZN()
    );

    INV_X1 _6_ (
        .A(),
        .ZN()
    );

    // liga os dois caminhos
    XOR2_X1 _7_ (
        .A(),
        .B(),
        .Z()
    );

    OR2_X1 _8_ (
        .A1(),
        .A2(),
        .ZN(N7)
    );

    

endmodule