# The Colony Cycle

This document describes the simulation's central feedback loop of **forage → find → carry → deposit → reproduce → forage**.

## The Cycle

```
                    ┌─────────────────┐
                    │   reproduces    │
                    │  (when fed)     │
                    │      ▼          │
                    │   QUEEN         │
                    │      │          │
                    │      ▼          │
                    │   spawns ants   │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │  empty-handed   │
        ┌──────────►│      ant        │◄────────┐
        │           │  (foraging)     │         │
        │           └────────┬────────┘         │
        │                    │                  │
        │                    ▼                  │
        │           ┌─────────────────┐         │
        │           │  finds food     │         │
        │           └────────┬────────┘         │
        │                    │                  │
        │                    ▼                  │
        │           ┌─────────────────┐         │
        │           │   eats some     │         │
        │           │ (scout reward)  │         │
        │           └────────┬────────┘         │
        │                    │                  │
        │                    ▼                  │
        │           ┌─────────────────┐         │
        │           │  carrying food  │         │
        │           │  + lays trail   │         │
        │           └────────┬────────┘         │
        │                    │                  │
        │                    ▼                  │
        │           ┌─────────────────┐         │
        │           │ deposits food   │         │
        │           │   at nest       │         │
        │           └────────┬────────┘         │
        │                    │                  │
        │                    ▼                  │
        │           ┌─────────────────┐         │
        │           │ colony reserves │         │
        │           │      go up      │         │
        │           └────────┬────────┘         │
        │                    │                  │
        │                    └──────────────────┘
        │
        └────── ant rests, or sets out again
```

## Objects

### The Ant

Each ant has individual state:

- **Energy**: a number that ticks down each step. At zero, the ant dies. Eating food directly out in the world boosts it modestly. Visiting the nest (when reserves allow) tops it up.
- **Carrying status**: empty-handed or carrying food. Affects what the ant wants to do.
- **Age**: clock ticks lived. Old ants die (senesce) regardless of energy.

### The Colony

The colony is the persists across individual ant lives. It has:

- **Food reserves**: total food deposited by all ants. This is the colony's energy.
- **Population**: list of living ants.
- **A queen**: stationary at the nest, generates new ants when reserves permit.

A colony with empty reserves cannot reproduce whereas a colony with full reserves grows.

### The Nest

A specific tile region at the center of the world. It's where:
- Ants spawn (the queen lives here).
- Ants deposit food (reserves accumulate here).
- Ants top up their energy (when reserves are sufficient).


### Food

Scattered through the dirt as small clusters (caches). Each food tile holds one unit. When an ant steps onto a food tile, the food is removed from that tile and put into the ant's possession (`carrying_food = True`).

### Pheromones

Per-tile chemical markers:

- **Food trails**: laid by ants returning to the nest with food. Foragers smell these and head *up* the gradient (toward the food source).

## The Feedback Loops

Three nested loops drive emergent behavior:

### Loop 1: Trail-following (fast, per-tick)

A single ant foraging follows trails. If a trail leads to food, they eat some, pick up more, and walk back, reinforcing the trail. Other foraging ants now have a stronger trail to follow.

### Loop 2: Energy economy (medium, over many ticks)

Individual ants need energy to survive. Successful foragers (who keep finding food) boost their own energy via the scout reward. Unsuccessful foragers slowly starve. The colony continually loses ants who weren't good at finding food, and tends to keep ants who were. There's no genetic algorithm, though, so this is attrition more than any sort of selection.

### Loop 3: Population (slow, over many many ticks)

When colony reserves are high, the queen reproduces. New ants explore in new directions, potentially discovering new food sources, raising reserves further. When reserves are low, the queen stops reproducing, and the colony contracts as ants die from energy loss.

## Tunable Parameters

Specified in `config.py`:

- `STARTING_ENERGY` — how much energy a new ant has.
- `ENERGY_DECAY_PER_TICK` — how quickly an idle ant starves.
- `SCOUT_REWARD` — energy boost for eating in the field.
- `REPRODUCTION_THRESHOLD` — colony reserves needed to spawn a new ant.
- `REPRODUCTION_COST` — reserves consumed per new ant.
- `MAX_AGE` — senescence ceiling.
- `PHEROMONE_DEPOSIT` — strength laid by a carrying ant per step.
- `PHEROMONE_DECAY` — how much trails fade per tick.
- `FOOD_DENSITY` — how much food is in the world at start.
- `ROCK_DENSITY` — how rocky the world is.
