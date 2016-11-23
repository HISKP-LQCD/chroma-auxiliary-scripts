# Extract `const std::string name` from `chroma`

The various monomials, solvers and measurements in the Chroma library have a
`const std::string name` in their `cpp` files. In order to get an overview of
the quantities implemented, this Python 3 script extracts all those (using `git
grep`). The results are stored as a `dict` data structure. Exports for GraphViz
(`dia`) and TikZ are implemented.

Part of the resulting graph looks like this:

![](names.png)
