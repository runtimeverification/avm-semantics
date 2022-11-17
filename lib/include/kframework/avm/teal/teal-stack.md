TEAL Stack
==========

```k
module TEAL-STACK
  imports INT
  imports BOOL
  imports TEAL-TYPES-SYNTAX
```

This module models the TEAL stack as a cons-list.
The elements of the stack are values of sort `TValue`, i.e. either `TUInt64` or `TBytes`.

- `.TStack` serves as the empty stack, and
- `_:_` serves as the "cons" operator.

```k
  syntax TStack ::= ".TStack" [klabel(.TStack), symbol, smtlib(_dotTStack)]
                  | TValue ":" TStack [klabel(_:_TStack), smtlib(_TStack_)]
  // --------------------------------------------------------------------
```

- `#take(N , WS)` keeps the first $N$ elements of a `TStack`.
  If there are not enough elements, the resulting stack will be shorter than $N$.
- `#drop(N , WS)` removes the first $N$ elements of a `TStack`.

```k
  syntax TStack ::= #take ( Int , TStack ) [klabel(takeTStack), function, total]
  // --------------------------------------------------------------------------------------------
  rule [#take.zero]:      #take(N, _Stack)          => .TStack
    requires N <=Int 0
  rule [#take.base]:      #take(N, .TStack)         => .TStack
    requires N >Int 0
  rule [#take.recursive]: #take(N, (X : XS):TStack) => X : #take(N -Int 1, XS)
    requires N >Int 0

  syntax TStack ::= #drop ( Int , TStack ) [klabel(dropTStack), function, total]
  // --------------------------------------------------------------------------------------------
  rule #drop(N, XS:TStack)       => XS
    requires N <=Int 0
  rule #drop(N, .TStack)         => .TStack
    requires N >Int 0
  rule #drop(N, (_ : XS):TStack) => #drop(N -Int 1, XS)
      requires N >Int 0
```

## Element Access

- `S [ N ]` accesses element $N$ (counting from the top of the stack) of $S$.
```k
  syntax TValue ::= TStack "[" Int "]" [function]
  // -----------------------------------------------------------
  rule (X : _):TStack [ N ] => X                  requires N ==Int 0
  rule XS             [ N ] => #drop(N, XS) [ 0 ] requires N  >Int 0
                                                   andBool N  <Int #sizeTStack(XS)
```

- `S { N }` accesses element $N$ (counting from the bottom of the stack) of $S$.
```k
  syntax TValue ::= TStack "{" Int "}" [function]
  // --------------------------------------------
  rule (X : XS):TStack { N } => X
    requires N ==Int #sizeTStack(XS)
  rule XS              { N } => #drop((#sizeTStack(XS) -Int N) -Int 1, XS) [ 0 ]
    requires N  <Int #sizeTStack(XS)
```

- `S { N <- M }` set element $N$ (counting from the bottom of the stack) of $S$ to $M$.
```k
  syntax TStack ::= TStack "{" Int "<-" TValue "}" [function]
  // --------------------------------------------------------
  rule XS:TStack { N <- M } => #take((#sizeTStack(XS) -Int N) -Int 1, XS) M : #drop(#sizeTStack(XS) -Int N, XS) 
```

```k
  syntax Int ::= #sizeTStack ( TStack )       [function, total, smtlib(sizeTStack)]
               | #sizeTStack ( TStack , Int ) [function, total, klabel(sizeTStackAux),
                                               smtlib(sizeTStackAux)]
  // --------------------------------------------------------------------------------------------
  rule #sizeTStack ( XS ) => #sizeTStack(XS, 0)
  rule #sizeTStack ( .TStack, SIZE ) => SIZE
  rule #sizeTStack ( _ : XS, SIZE )     => #sizeTStack(XS, SIZE +Int 1)
```

## Stack reverse

```k
  syntax TStack ::= #reverse(TStack)         [function, total]
                  | #reverse(TStack, TStack) [function, total]
  // --------------------------------------------------------------
  rule #reverse(XS)          => #reverse(XS, .TStack)
  rule #reverse(.TStack, YS) => YS
  rule #reverse(X : XS , YS) => #reverse(XS, X : YS)
```

## Stack concatenation

```k
  syntax TStack ::= TStack TStack                    [function, total]
                 | #concatTStackImpl(TStack, TStack) [function, total]
  // ------------------------------------------------------------------------------
  rule XS YS => #concatTStackImpl(#reverse(XS), YS)

  rule #concatTStackImpl(.TStack, YS) => YS
  rule #concatTStackImpl(X : XS , YS) => #concatTStackImpl(XS, X : YS)

```

```k
endmodule
```
