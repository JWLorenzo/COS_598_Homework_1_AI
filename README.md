# COS_598_Homework_1

Name: Jacob Lorenzo
Date: 2/21/25
Instructor: Dr. Hutchinson
Assignment: Homework 1

# Disclaimer:

The code is still a bit buggy, primarily because the red agent bounces off the walls. Interestingly, the issue seems to disappear between runs. (After a third revision, I removed the flickery behavior. Occasionally, it hits an angle wrong and goes out of bounds).

# My Experience:

This assignment turned out to be more challenging than expected. At first glance, it seemed straightforward, but it ended up being one of the few assignments this semester that had me burning the midnight oil. Using a unit circle to calculate bounce angles for the red agent was particularly tricky.

The textbook provided a wealth of useful information, and I implemented the seek and wander behaviors based on its concepts. This is especially evident in the yellow agent's movement, as it tends to follow a circular traversal pattern. The wall-avoidance behavior, however, was more trial and error. Ultimately, I modified the behavior so that when an enemy approaches the edge, it selects a new target from a smaller, centralized area of the screen.

# Guard Patrol Behaviors:

This unit spins with an increasing line-of-sight cone, simulating a kind of "momentum." As the player collects the objectives, the cone grows faster. I was inspired by Terraria’s Eye of Cthulhu, which has a darting movement pattern. Once it spots the player, it lunges and can chain attacks if it continues detecting the player. The idea also came from me rolling around Boardman 138 in a desk chair while helping students. Despite being the simplest to implement, this agent is surprisingly the most challenging and interesting to deal with. (Dodging it is a nightmare.)

Originally, I wanted this unit to move in a sine wave pattern, but due to time constraints and complexity, I opted for a movement style akin to a DVD screensaver to bounce around the environment.

Yellow is the most traditional AI type, directly adapted from Chapter 3's wandering movement. It acts as a "boss" unit, enhancing the blue agent by extending its vision range.

Each guard has two states. When they spot the player, the blue and yellow agents enter a traditional chase mode, utilizing their movement styles to pursue. The red agent, however, acts more like a spotlight. It locks onto the player's position and tracks them without making physical contact.

# Communication:

The red and yellow agents serve as scouts. The scouts feed information back to the blue agent, which acts as the team’s “sniper.” The red agent provides location tracking, allowing the blue unit to take over as the main pursuer.

Additionally, when a unit spots the player, it triggers voice lines if applicable. The blue agent also communicates with the yellow agent, prompting it to respond with a comedic line.

I chose not to have the units immediately jump at the player when they picked up objectives. Instead, the objectives act as a speed modifier.




