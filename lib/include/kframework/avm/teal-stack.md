TEAL Stack
===========

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
  syntax TStack ::= ".TStack" [smtlib(_dotTStack)]
                  | TValue ":" TStack [klabel(_:_TStack), smtlib(_TStack_)]
  // --------------------------------------------------------------------
```

- `#take(N , WS)` keeps the first $N$ elements of a `TStack`.
  If there are not enough elements, the resulting stack will be shorter than $N$.
- `#drop(N , WS)` removes the first $N$ elements of a `TStack`.

```k
  syntax TStack ::= #take ( Int , TStack ) [klabel(takeTStack), function, functional]
  // --------------------------------------------------------------------------------------------
  rule [#take.zero]:      #take(N, _Stack)          => .TStack
    requires N <=Int 0
  rule [#take.base]:      #take(N, .TStack)         => .TStack
    requires N >Int 0
  rule [#take.recursive]: #take(N, (X : XS):TStack) => X : #take(N -Int 1, XS)
    requires N >Int 0

  syntax TStack ::= #drop ( Int , TStack ) [klabel(dropTStack), function, functional]
  // --------------------------------------------------------------------------------------------
  rule #drop(N, XS:TStack)       => XS
    requires N <=Int 0
  rule #drop(N, .TStack)         => .TStack
    requires N >Int 0
  rule #drop(N, (_ : XS):TStack) => #drop(N -Int 1, XS)
      requires N >Int 0
```

## Element Access

- `S [ N ]` accesses element $N$ of $S$.
```k
  syntax TValue ::= TStack "[" Int "]" [function]
  // -----------------------------------------------------------
  rule (X : _):TStack [ N ] => X                  requires N ==Int 0
  rule XS             [ N ] => #drop(N, XS) [ 0 ] requires N  >Int 0
                                                   andBool N  <Int #sizeTStack(XS)
```

```k
  syntax Int ::= #sizeTStack ( TStack )       [function, functional, smtlib(sizeTStack)]
               | #sizeTStack ( TStack , Int ) [function, functional, klabel(sizeTStackAux),
                                               smtlib(sizeTStackAux)]
  // --------------------------------------------------------------------------------------------
  rule #sizeTStack ( XS ) => #sizeTStack(XS, 0)
  rule #sizeTStack ( .TStack, SIZE ) => SIZE
  rule #sizeTStack ( _ : XS, SIZE )     => #sizeTStack(XS, SIZE +Int 1)
```

```k
endmodule
```
