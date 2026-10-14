---
name: walking-tour
description: Turn a few nearby places into a walking tour with an order, timings and a total. Use when someone asks for a tour, an itinerary, a route through several places, or how to spend an hour or an afternoon.
---

# Planning a walking tour

Work only from what the tools returned. Never add a place, a time or a fact
of your own.

1. Find the person with `geocode`, unless you already have their coordinates.
2. List candidates with `nearby_places` for the kind they asked for.
3. Choose three stops that differ from each other. Put them in order of
   `distance_m`, nearest first. That is the order of the tour.
4. Call `walking_route` once per leg, in tour order: from the person to stop
   1, from stop 1 to stop 2, from stop 2 to stop 3. Three calls, no more.
5. Allow 20 minutes at a cafe or bakery, 30 at a park, 45 at a museum,
   theatre or attraction, unless the person gave their own times.
6. Add up the walking minutes and the minutes at each stop.

Write the tour like this, and nothing else:

```
Your walking tour: <total minutes> minutes, <total metres> m on foot

1. <place> (<type>)
   walk <minutes> min, <metres> m, then stay <minutes> min
2. ...
```

If the person named a time limit and the total is over it, drop the last
stop, say which one you dropped, and give the new total.
