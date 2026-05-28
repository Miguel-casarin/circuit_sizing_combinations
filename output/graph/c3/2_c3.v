
module c3(N1, N2, N3, N4, N22);
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
  AND2_X4 _2_ (
    .A1(N1),
    .A2(N2),
    .ZN(_0_)
  );
  AND2_X1 _3_ (
    .A1(_0_),
    .A2(N3),
    .ZN(_1_)
  );
  AND2_X1 _4_ (
    .A1(_1_),
    .A2(N4),
    .ZN(N22)
  );
endmodule
