Valid
=====

```
c age 30, has d has e has f has g, i.
a.
a has, has c.
a has b has c.
```

Invalid
=======

FIXME!!

```
c has x, d has e.
a has b, c has e has e has f.
a has z, b, has c has x, d has e has f has g, has i.
```

Both have the same error - after the comma only 2 forms are allowed:

```
..., OBJ
..., PRED OBJ
```

so `c has x, d has e.` can be treated only as `c has x, PRED OBJ <but-whati-is-e?!>`.
The error for the first failing example is:

```
In OBJ, 7th token at 1:18: Unexpected token DOT ., expected ATOM/STRING
```

Queries
=======

```
get all $name, $age.  / get first ...
$name age $age.
$name has car.
$age < 50.
car older "2 years".
```

or

```
get as q1.
$name age $age.

get union q1 this.
$name age $age.
```

or

```
get as q1.
$name has wife.

$name older "40 years" not q1.

```

or `some with age > 20, < 40.` or `age union of > 20, < 40.` or `age intersect of > 20, < 40.`
or `each with age > 20, < 40.`

-------------------

1: a has b, c.
2: a has b, has c.
3: a has b, c has d.
4: a has b, has c has d.
5: a has b, c has d has e.
6: a has b, has c has d has e.
7: a has b, c has d has e has f.

a has b, c has d, e.

-----------------------

class Para: - paragraph. Sections of the Ast - different datasets. MB call it Sect/Section.