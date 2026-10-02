# Which fall hits hardest? An ideal rope model

Three identical 80 kg masses fall onto the same ideal elastic rope model. Only the fall changes:

| case | fall | rope paid out | fall factor | peak rope force |
|---|---|---|---|---|
| A | 2 m | 1 m | 2.0 | 9.300 kN |
| B | 6 m | 6 m | 1.0 | 6.832 kN |
| C | 12 m | 24 m | 0.5 | 5.096 kN |

In this model the 12 m fall gives a **45 % lower peak rope force** than the 2 m fall. The rope is
a linear spring of stiffness `k = EA / L`, so more rope out is a softer spring, and the peak force
depends on the fall factor h/L rather than on the fall height. **The order A > B > C holds for any
positive EA; the 45 % does not** — it is conditional on the 80 kg mass and on EA fitted to one
8.8 kN rating (below).

```sh
python -m pip install -r requirements.txt
python reproduce.py
```

The script fits the rope's effective EA, integrates each fall (free fall, then the spring) up to
the **first turnaround only**, checks the result against the energy closed form, and compares
every number with `reference/result.json`. It also runs a deliberately artificial
counterfactual — one fixed spring for all three rope lengths — which reverses the order; it is
there to show the mechanism, not to describe a real rope.

## What this is not

* **Not a rope rating and not climbing safety advice.**
* EA is an effective parameter fitted to ONE number: a rated impact force of 8.8 kN in the
  standard drop test (80 kg, fall factor 1.77), the value listed for an existing single rope.
  It is not a measured stiffness. The fitted spring implies about 38 % elongation at that drop,
  more than the 31 % the same rope lists, so the ideal spring is not the real rope.
* Real ropes are viscoelastic (they damp), carabiners add friction (which raises the effective
  fall factor), and belays slip. None of that is modelled. The standard's impact force is not
  representative of the force in an actual climb.
* Nothing after the first turnaround is computed: no rebound and no hanging.
