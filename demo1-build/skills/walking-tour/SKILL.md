---
name: walking-tour
description: Turn two nearby places into a short walking tour with an order, timings and a total. Use when someone asks for a tour, an itinerary, a route through several places, or how to spend an hour.
---

# Planning a short walking tour

Everything you need is on this page. This skill has no other files, so do
not load any resources. Work only from what the tools returned. Never add a
place, a time or a fact of your own.

1. Find the person with `geocode`, unless you already have their coordinates.
2. List candidates with `nearby_places` for the kind they asked for, or
   "fun" if they did not say.
3. Choose two stops that differ from each other. The nearer one is stop 1.
4. Call `walking_route` twice, both in the same step: from the person to
   stop 1, and from stop 1 to stop 2.
5. Allow 20 minutes at a cafe or bakery, 30 at a park, 45 at a museum,
   theatre or attraction, unless the person gave their own times.
6. Add up the walking minutes and the minutes at each stop.

Write the tour like this, as plain text without the ``` marks, and nothing else:

```
Your walking tour: <total minutes> minutes, <total metres> m on foot

1. <place> (<type>)
   walk <minutes> min, <metres> m, then stay <minutes> min
2. <place> (<type>)
   walk <minutes> min, <metres> m, then stay <minutes> min
```

If the person named a time limit and the total is over it, keep only stop 1
and give the new total.
