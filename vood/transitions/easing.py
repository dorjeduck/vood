class Easing:
    @staticmethod
    def none(t: float) -> float:
        """No easing, always returns 0 (static property)"""
        return 0

    """Collection of easing functions for smooth animations

    All easing functions take a value between 0 and 1 and return a transformed
    value that's also between 0 and 1, but with different rates of change.
    """

    @staticmethod
    def linear(t: float) -> float:
        """Linear easing (no easing effect)

        Args:
            t: Time factor between 0 and 1

        Returns:
            Same value as input (t)

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        return t

    @staticmethod
    def in_out(t: float) -> float:
        """Smooth ease in and out using quadratic curve

        Args:
            t: Time factor between 0 and 1

        Returns:
            Eased value between 0 and 1

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        return t * t * (3 - 2 * t)

    @staticmethod
    def out_cubic(t: float) -> float:
        """Fast start, slow end using cubic curve

        Args:
            t: Time factor between 0 and 1

        Returns:
            Eased value between 0 and 1

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        return 1 - pow(1 - t, 3)

    @staticmethod
    def in_cubic(t: float) -> float:
        """Slow start, fast end using cubic curve

        Args:
            t: Time factor between 0 and 1

        Returns:
            Eased value between 0 and 1

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        return t * t * t

    @staticmethod
    def in_out_cubic(t: float) -> float:
        """Smooth cubic easing, combining in and out effects

        Args:
            t: Time factor between 0 and 1

        Returns:
            Eased value between 0 and 1

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2

    # Quadratic easing functions
    @staticmethod
    def in_quad(t: float) -> float:
        """Quadratic ease in - slow start, accelerating

        Creates a gentle acceleration from rest. The animation starts very slowly
        and gradually speeds up. Perfect for objects starting to move or fade in.

        Use cases:
        - Elements appearing/growing from nothing
        - Objects starting to move from rest
        - Gentle fade-ins

        Args:
            t: Time factor between 0 and 1

        Returns:
            Eased value between 0 and 1, following t²

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        return t * t

    @staticmethod
    def out_quad(t: float) -> float:
        """Quadratic ease out - fast start, decelerating

        Starts fast and gradually slows down to a gentle stop. Creates a natural
        feeling deceleration, like an object coming to rest.

        Use cases:
        - Elements settling into place
        - Objects coming to a stop
        - Gentle fade-outs
        - UI elements sliding into final position

        Args:
            t: Time factor between 0 and 1

        Returns:
            Eased value between 0 and 1, following 1-(1-t)²

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        return 1 - (1 - t) * (1 - t)

    @staticmethod
    def in_out_quad(t: float) -> float:
        """Quadratic ease in-out - accelerate then decelerate

        Combines the acceleration of ease-in with the deceleration of ease-out.
        Starts slowly, speeds up in the middle, then slows down at the end.
        Very natural feeling for most animations.

        Use cases:
        - General purpose smooth animations
        - Position changes that should feel natural
        - Size transitions
        - Most UI animations

        Args:
            t: Time factor between 0 and 1

        Returns:
            Eased value between 0 and 1

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2

    # Quartic easing functions
    @staticmethod
    def in_quart(t: float) -> float:
        """Quartic ease in - very slow start with strong acceleration

        More dramatic than quadratic easing. Starts extremely slowly and then
        accelerates rapidly. Creates a strong "wind-up" effect.

        Use cases:
        - Dramatic entrances
        - Building suspense before rapid movement
        - Power-up animations
        - Loading animations that build momentum

        Args:
            t: Time factor between 0 and 1

        Returns:
            Eased value between 0 and 1, following t⁴

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        return t * t * t * t

    @staticmethod
    def out_quart(t: float) -> float:
        """Quartic ease out - very fast start with strong deceleration

        Starts very rapidly and then decelerates strongly to a gentle stop.
        More dramatic than quadratic ease-out. Great for impactful arrivals.

        Use cases:
        - Elements slamming into place then settling
        - Dramatic slide-ins
        - Impact animations
        - Strong emphasis on arrival

        Args:
            t: Time factor between 0 and 1

        Returns:
            Eased value between 0 and 1, following 1-(1-t)⁴

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        return 1 - pow(1 - t, 4)

    @staticmethod
    def in_out_quart(t: float) -> float:
        """Quartic ease in-out - dramatic acceleration and deceleration

        Combines strong ease-in with strong ease-out for very dramatic effect.
        Much more pronounced than quadratic in-out. Creates powerful, cinematic
        movement patterns.

        Use cases:
        - Cinematic camera movements
        - Dramatic scene transitions
        - Hero element animations
        - High-impact visual effects

        Args:
            t: Time factor between 0 and 1

        Returns:
            Eased value between 0 and 1

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        return 8 * t * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 4) / 2

    # Quintic easing functions
    @staticmethod
    def in_quint(t: float) -> float:
        """Quintic ease in - extremely slow start with explosive acceleration

        The most dramatic of the polynomial easing functions. Starts almost
        motionless and then explodes into rapid motion. Creates the strongest
        "build-up then release" effect.

        Use cases:
        - Explosive reveals
        - Maximum suspense building
        - Rocket launch animations
        - Extreme power-up effects

        Args:
            t: Time factor between 0 and 1

        Returns:
            Eased value between 0 and 1, following t⁵

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        return t * t * t * t * t

    @staticmethod
    def out_quint(t: float) -> float:
        """Quintic ease out - explosive start with extreme deceleration

        Starts with maximum speed and then decelerates extremely strongly.
        Creates the most dramatic "impact then settle" effect of the polynomial
        functions.

        Use cases:
        - Maximum impact arrivals
        - Explosive entries that settle
        - Superhero landing effects
        - Heavy object animations

        Args:
            t: Time factor between 0 and 1

        Returns:
            Eased value between 0 and 1, following 1-(1-t)⁵

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        return 1 - pow(1 - t, 5)

    @staticmethod
    def in_out_quint(t: float) -> float:
        """Quintic ease in-out - maximum drama with smooth transition

        The most extreme version of ease in-out. Combines explosive acceleration
        with explosive deceleration for maximum visual impact while maintaining
        smooth transitions.

        Use cases:
        - Epic cinematic movements
        - Maximum impact transitions
        - Hero moments in animations
        - When you need the most dramatic curve possible

        Args:
            t: Time factor between 0 and 1

        Returns:
            Eased value between 0 and 1

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        return 16 * t * t * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 5) / 2

    # Sine easing functions
    @staticmethod
    def in_sine(t: float) -> float:
        """Sine ease in - gentle, natural acceleration

        Based on a quarter sine wave. Provides the most natural feeling
        acceleration - like how objects naturally speed up in the real world.
        Gentler than quadratic, more organic feeling.

        Use cases:
        - Natural object movements
        - Organic animations
        - Subtle fade-ins
        - When you want smooth but not too dramatic

        Args:
            t: Time factor between 0 and 1

        Returns:
            Eased value between 0 and 1, following 1-cos(t*π/2)

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        import math

        return 1 - math.cos((t * math.pi) / 2)

    @staticmethod
    def out_sine(t: float) -> float:
        """Sine ease out - gentle, natural deceleration

        Based on a quarter sine wave. Provides the most natural feeling
        deceleration - like how objects naturally slow down in the real world.
        Perfect for organic, life-like movements.

        Use cases:
        - Natural settling animations
        - Organic fade-outs
        - Realistic physics simulations
        - Gentle UI transitions

        Args:
            t: Time factor between 0 and 1

        Returns:
            Eased value between 0 and 1, following sin(t*π/2)

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        import math

        return math.sin((t * math.pi) / 2)

    @staticmethod
    def in_out_sine(t: float) -> float:
        """Sine ease in-out - perfectly smooth, natural curve

        Based on a half sine wave. Creates the smoothest possible curve for
        in-out animations. No sharp transitions, completely organic feeling.
        Often preferred for subtle, elegant animations.

        Use cases:
        - Elegant UI animations
        - Smooth property changes
        - Natural breathing effects
        - When smoothness is paramount

        Args:
            t: Time factor between 0 and 1

        Returns:
            Eased value between 0 and 1, following -(cos(π*t)-1)/2

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        import math

        return -(math.cos(math.pi * t) - 1) / 2

    # Exponential easing functions
    @staticmethod
    def in_expo(t: float) -> float:
        """Exponential ease in - very slow start, then rapid acceleration"""
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        return 0 if t == 0 else pow(2, 10 * (t - 1))

    @staticmethod
    def out_expo(t: float) -> float:
        """Exponential ease out - rapid start, then very slow end"""
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        return 1 if t == 1 else 1 - pow(2, -10 * t)

    @staticmethod
    def in_out_expo(t: float) -> float:
        """
        Exponential ease in-out - slow start, dramatic acceleration, then dramatic deceleration.

        Combines exponential ease-in and ease-out, creating a smooth transition that starts slowly,
        accelerates dramatically in the middle, then decelerates dramatically to a smooth stop.
        The exponential nature creates very pronounced acceleration/deceleration phases.

        Mathematical form: Uses 2^(20t-10) for first half, 2^(-20t+10) for second half

        Use cases:
        - Cinematic zoom effects that need dramatic impact
        - High-energy transitions between major interface states
        - Emphasizing important state changes with theatrical timing
        - Creating "whoosh" effects in motion graphics
        - Scaling animations that need to feel powerful and impactful

        Like a sports car: gentle acceleration from standstill, then explosive power in the middle,
        followed by powerful braking to a smooth stop.

        Args:
            t: Time factor between 0.0 and 1.0

        Returns:
            Eased value between 0.0 and 1.0

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        if t == 0:
            return 0
        if t == 1:
            return 1
        if t < 0.5:
            return pow(2, 20 * t - 10) / 2
        else:
            return (2 - pow(2, -20 * t + 10)) / 2

    # Circular easing functions
    @staticmethod
    def in_circ(t: float) -> float:
        """Circular ease in - slow start following circular arc"""
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        import math

        return 1 - math.sqrt(1 - pow(t, 2))

    @staticmethod
    def out_circ(t: float) -> float:
        """Circular ease out - fast start following circular arc"""
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        import math

        return math.sqrt(1 - pow(t - 1, 2))

    @staticmethod
    def in_out_circ(t: float) -> float:
        """
        Circular ease in-out - smooth acceleration following circular arc, then smooth deceleration.

        Combines circular ease-in and ease-out, creating a perfectly smooth S-curve that follows
        the mathematical properties of a circle. The acceleration and deceleration phases are
        perfectly symmetrical and create very natural-feeling motion.

        Mathematical form: Uses √(1-t²) for circular arc calculation

        Use cases:
        - Natural object motion that needs to feel physically realistic
        - Smooth camera movements and panning
        - Organic transitions between interface states
        - Animations where you want smooth acceleration without harsh stops
        - Breathing or pulsing effects
        - Element positioning that should feel effortless

        Like a skilled driver: smooth acceleration onto a highway, maintaining steady speed,
        then smooth deceleration to a perfect parking position.

        Args:
            t: Time factor between 0.0 and 1.0

        Returns:
            Eased value between 0.0 and 1.0

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        import math

        if t < 0.5:
            return (1 - math.sqrt(1 - pow(2 * t, 2))) / 2
        else:
            return (math.sqrt(1 - pow(-2 * t + 2, 2)) + 1) / 2

    # Back easing functions (overshoot)
    @staticmethod
    def in_back(t: float) -> float:
        """Back ease in - pulls back before moving forward

        Creates an anticipation effect by briefly moving in the opposite direction
        before accelerating toward the target. Like pulling back a slingshot or
        winding up before throwing. Adds personality and life to animations.

        Use cases:
        - UI elements that "wind up" before appearing
        - Character animations with anticipation
        - Playful button interactions
        - Adding personality to mechanical movements

        Args:
            t: Time factor between 0 and 1

        Returns:
            Eased value that goes slightly negative before reaching 1

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        c1 = 1.70158
        c3 = c1 + 1
        return c3 * t * t * t - c1 * t * t

    @staticmethod
    def out_back(t: float) -> float:
        """Back ease out - overshoots then settles back

        Shoots past the target and then settles back into place. Like a spring
        that compresses too far and bounces back. Creates satisfying overshoot
        effects that feel dynamic and alive.

        Use cases:
        - Elements settling into place with overshoot
        - Spring-like animations
        - Satisfying button feedback
        - Objects that "land" with impact

        Args:
            t: Time factor between 0 and 1

        Returns:
            Eased value that overshoots past 1 before settling

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)

    @staticmethod
    def in_out_back(t: float) -> float:
        """Back ease in-out - pulls back, overshoots, then settles

        Combines anticipation with overshoot. Pulls back at the start, then
        overshoots at the end before settling. Creates maximum personality
        and life in animations.

        Use cases:
        - Hero element animations
        - Playful, character-driven interfaces
        - When you want maximum personality
        - Spring-loaded mechanisms

        Args:
            t: Time factor between 0 and 1

        Returns:
            Eased value with both anticipation and overshoot

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        c1 = 1.70158
        c2 = c1 * 1.525
        if t < 0.5:
            return (pow(2 * t, 2) * ((c2 + 1) * 2 * t - c2)) / 2
        else:
            return (pow(2 * t - 2, 2) * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2

    # Elastic easing functions
    @staticmethod
    def in_elastic(t: float) -> float:
        """
        Elastic ease in - like pulling back a rubber band before release.

        Creates an oscillating motion that starts with small movements in the opposite direction,
        building tension before accelerating toward the target. The elastic effect creates a
        spring-like anticipation that makes the final movement feel more impactful.

        Mathematical form: Uses -2^(10(t-1)) * sin((t-1) * 2π/3) for oscillating decay

        Use cases:
        - UI elements that need playful, bouncy character
        - Attention-grabbing animations for buttons or notifications
        - Game mechanics that simulate elastic or spring-loaded objects
        - Anticipation effects before major actions
        - Cartoon-style animations that need exaggerated character
        - Loading animations that suggest building energy

        Like drawing back a slingshot: small backward movements building tension,
        then rapid acceleration toward the target with overshooting oscillation.

        Args:
            t: Time factor between 0.0 and 1.0

        Returns:
            Eased value between 0.0 and 1.0

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        import math

        if t == 0:
            return 0
        if t == 1:
            return 1
        c4 = (2 * math.pi) / 3
        return -pow(2, 10 * (t - 1)) * math.sin((t - 1) * c4 - c4)

    @staticmethod
    def out_elastic(t: float) -> float:
        """
        Elastic ease out - like a rubber band snapping into place with bouncy overshoot.

        Creates rapid initial movement toward the target, then oscillates around the final
        position with decreasing amplitude until settling. The elastic effect makes arrivals
        feel lively and energetic rather than mechanical.

        Mathematical form: Uses 2^(-10t) * sin(t * 2π/3) + 1 for damped oscillation

        Use cases:
        - UI elements appearing with playful character
        - Button press feedback that feels responsive and alive
        - Modal dialogs or menus that bounce into view
        - Success animations that celebrate completion
        - Dropdown menus with personality
        - Game UI elements that need bounce and appeal

        Like a rubber ball dropped on the ground: quick fall to the surface,
        then several smaller bounces before coming to rest.

        Args:
            t: Time factor between 0.0 and 1.0

        Returns:
            Eased value between 0.0 and 1.0

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        import math

        if t == 0:
            return 0
        if t == 1:
            return 1
        c4 = (2 * math.pi) / 3
        return pow(2, -10 * t) * math.sin(t * c4 - c4) + 1

    @staticmethod
    def in_out_elastic(t: float) -> float:
        """
        Elastic ease in-out - combines elastic anticipation with bouncy arrival.

        Creates a complex motion that starts with oscillating buildup (like drawing back
        a slingshot), rapidly accelerates through the middle, then oscillates around
        the target before settling. Combines the best of both elastic behaviors.

        Mathematical form: Uses scaled sine waves with exponential decay on both ends

        Use cases:
        - High-impact transitions that need maximum personality
        - Game animations for special abilities or power-ups
        - Attention-grabbing modal transitions
        - Playful loading sequences that entertain users
        - Celebration animations that feel extra bouncy
        - UI elements that need to stand out with elastic character

        Like a professional yo-yo trick: complex wind-up with multiple oscillations,
        rapid motion through the middle, then multiple bounces before settling perfectly.

        Args:
            t: Time factor between 0.0 and 1.0

        Returns:
            Eased value between 0.0 and 1.0

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        import math

        if t == 0:
            return 0
        if t == 1:
            return 1
        c5 = (2 * math.pi) / 4.5
        if t < 0.5:
            return -(pow(2, 20 * t - 10) * math.sin((20 * t - 11.125) * c5)) / 2
        else:
            return (pow(2, -20 * t + 10) * math.sin((20 * t - 11.125) * c5)) / 2 + 1

    # Bounce easing functions
    @staticmethod
    def in_bounce(t: float) -> float:
        """
        Bounce ease in - like a ball being thrown upward with decreasing bounces.

        Creates a bouncing motion that starts with several small bounces and builds
        toward the final movement. The effect simulates the reverse of a ball bouncing
        to a stop - instead bouncing with increasing energy toward the target.

        Mathematical form: Uses 1 - out_bounce(1-t) for reverse bounce calculation

        Use cases:
        - Elements that need to build energy before moving
        - Anticipation effects that suggest gathering momentum
        - Game mechanics for charging or powering up
        - UI elements that bounce into action
        - Loading animations that suggest building activity
        - Preparation phases before major transitions

        Like dribbling a basketball with increasing force: small bounces at first,
        building up to powerful movements toward the final position.

        Args:
            t: Time factor between 0.0 and 1.0

        Returns:
            Eased value between 0.0 and 1.0

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        return 1 - Easing.out_bounce(1 - t)

    @staticmethod
    def out_bounce(t: float) -> float:
        """
        Bounce ease out - like a ball bouncing to a stop with realistic physics.

        Creates the classic bouncing ball effect with mathematically accurate bounce
        timing and heights. Each bounce is smaller than the last, following realistic
        physics until the motion settles at the target position.

        Mathematical form: Uses piecewise function with 7.5625 coefficient for realistic bounce

        Use cases:
        - Classic bouncing ball animations
        - UI elements dropping into place naturally
        - Success notifications that bounce to celebrate
        - Drag-and-drop feedback with satisfying landing
        - Menu items bouncing into view
        - Any animation that needs playful, physics-based character

        Like dropping a rubber ball: quick fall, then several decreasing bounces
        (big bounce, medium bounce, small bounce) before settling on the ground.

        Args:
            t: Time factor between 0.0 and 1.0

        Returns:
            Eased value between 0.0 and 1.0

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        n1 = 7.5625
        d1 = 2.75
        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375

    @staticmethod
    def in_out_bounce(t: float) -> float:
        """
        Bounce ease in-out - bounces at both start and end with smooth middle transition.

        Combines bounce-in and bounce-out effects, creating complex motion that bounces
        at the beginning (building energy), smoothly transitions through the middle,
        then bounces at the end (settling into place). Maximum playful character.

        Mathematical form: Uses bounce-in for first half, bounce-out for second half

        Use cases:
        - Maximum impact transitions between major interface states
        - Game animations that need extra personality and fun
        - Celebration sequences that feel extra bouncy and joyful
        - Loading animations that entertain with complex bouncing
        - Special effect transitions that need to stand out
        - UI elements that should feel extremely playful and engaging

        Like a rubber ball in a pinball machine: bounces off the starting bumper,
        flies through the middle space, then bounces several times before settling
        in the target slot.

        Args:
            t: Time factor between 0.0 and 1.0

        Returns:
            Eased value between 0.0 and 1.0

        Raises:
            ValueError: If t is not between 0 and 1
        """
        if not 0 <= t <= 1:
            raise ValueError("Time factor t must be between 0 and 1")
        if t < 0.5:
            return (1 - Easing.out_bounce(1 - 2 * t)) / 2
        else:
            return (1 + Easing.out_bounce(2 * t - 1)) / 2
