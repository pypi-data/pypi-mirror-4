from wasabi.geom.vector import v, Vector

from wasabi.geom.spatialhash import SpatialHash


GRAVITY = 1000

inf = float('inf')
NaN = float('NaN')

def is_nan(v):
    return v != v

def is_inf(v):
    return v == inf


class Body(object):
    """A dynamic rectangle whose velocity, position are controlled by Physics.

    Bodies should be manipulated by applying forces, etc.

    Each body has mass, which causes inertia.
    """

    on_collide = None

    def __init__(self, rect, mass, pos=v(0, 0), controller=None, groups=0x0001, mask=0x00ff):
        assert mass > 0
        self.pos = pos
        self.rect = rect
        self.mass = mass

        # Select what can collide with what
        self.groups = groups
        self.mask = mask

        self.controller = controller
        self.v = Vector((0, 0))
        self.on_floor = False
        self.reset_forces()

    def get_rect(self):
        """Get the current rectangle of the body."""
        return self.rect.translate(self.pos)

    def reset_forces(self):
        """Reset the forces acting on the body.
        
        Subclasses can override this method to apply forces that apply
        constantly (gravity, wind, bouyancy etc).
        """
        self.f = Vector((0, -GRAVITY * self.mass))

    def apply_force(self, f):
        """Apply a force to the body for the next update of the simulation.
        
        :param f: The force vector to apply.

        """
        self.f += f

    def apply_impulse(self, impulse):
        """Apply an impulse to the body.
        
        This causes an instant change in the velocity of the body.

        :param impulse: The impulse vector to apply.
        """
        self.v += impulse

    def update(self, dt):
        if is_inf(self.mass):
            return

        u = self.v
        self.v += dt * self.f / self.mass

        self.v = Vector((self.v.x * 0.05 ** dt, self.v.y))

        self.on_floor = False

        self.pos += 0.5 * (u + self.v) * dt

    def set_collision_handler(self, handler):
        """Set a callback to be called when this body collides with another.

        The callback must accept these arguments::
            
            handler(b, dt)

        where `b` is the other Body involved in the collision, and `dt` is the
        simulation's time step.

        """
        self.on_collide = handler


class FloatingBody(Body):
    """A dynamic body on which gravity does not apply."""
    def reset_forces(self):
        self.f = v(0, 0)


class StaticBody(object):
    """A static body represents an immovable object.

    Static bodies should be added to the Physics with
    :py:meth:`Physics.add_static` rather than `.add_body`.

    """
    def __init__(self, rectangles, pos=v(0, 0)):
        self.pos = pos
        self.rectangles = rectangles


class Physics(object):
    def __init__(self):
        self.static_geometry = []
        self.static_objects = []
        self.static_hash = SpatialHash()
        self.dynamic = []

    def add_body(self, body):
        """Add a dynamic body to the world.

        :param body: The Body to add.
        """
        self.dynamic.append(body)

    def remove_body(self, body):
        """Remove a Body from the world.

        :param body: The Body to remove.
        """
        self.dynamic.remove(body)

    def add_static(self, body):
        """Add static geometry to the world.
    
        :param body: The StaticBody to add.
        """
        self.static_objects.append(body)
        geom = []
        for o in body.rectangles:
            r = o.translate(body.pos)
            self.static_hash.add_rect(r, (r, body))
            self.static_geometry.append(r)
            geom.append(r)
        body._geom = geom

    def remove_static(self, body):
        """Remove static geometry from the world.
    
        :param body: The StaticBody to remove.
        """
        self.static_objects.remove(body)
        for r in body._geom:
            self.static_geometry.remove(r)
            self.static_hash.remove_rect(r, (r, body))

    def ray_query(self, segment, mask=0xffff):
        """Query dynamic and static bodies that intersect the given
        :py:class:`Segment <wasabi.geom.lines.Segment>`.

        The return value is a list of tuples (distance, object), sorted in
        ascending order of distance. Each tuple represents an intersection with
        a new object.

        For each tuple, `distance` is the distance of the point of first
        intersection of the object along the segment.

        If the hit is with a dynamic object then `object` will be the Body that
        was hit.
    
        If the hit is with static geometry then `object` will be StaticBody (the
        class, not an instance).

        :param segment: The segment to query.
        :param mask: A collision bitmask. When set, only dynamic objects whose
                group bitmask ANDed with the mask bitmask will be returned. All
                static objects are returned.

        """
        intersections = []
        for o in self.static_geometry:
            d = segment.intersects(o)
            if d:
                intersections.append((d, o))

        for o in self.dynamic:
            if o.groups & mask:
                d = segment.intersects(o.get_rect())
                if d:
                    intersections.append((d, o.controller))
        intersections.sort()
        return intersections

    def collide_static(self, d):
        r = d.get_rect()
        col = self.static_hash.potential_intersection(r)
        for s, body in col:
            mtd = r.intersects(s)
            if mtd:
                d.pos += mtd
                x, y = d.v
                if mtd.y:
                    y = 0
                    if mtd.y > 0:
                        d.on_floor = True
                if mtd.x:
                    x = 0
                d.v = Vector((x, y))

    def collide_dynamic(self, a, b):
        if not (a.groups & b.mask or a.mask & b.groups):
            return

        mtd = a.get_rect().intersects(b.get_rect())
        if mtd:
            return (a, mtd, b)

    def _resolve_collision(self, c):
        """Move the objects involved in a collision so as not to intersect."""
        a, mtd, b = c
        ma = a.mass
        mb = b.mass
        tm = ma + mb  # total mass
        frac = mb / tm

        if is_inf(a.mass):
            frac = 0
        elif is_inf(b.mass):
            frac = 1

        # Move the objects so as not to intersect
        a.pos += frac * mtd
        b.pos -= (1 - frac) * mtd

        if mtd.y > 0:
            a.on_floor = True
        else:
            b.on_floor = True

    def _collide_velocities(self, c):
        """Work out the new velocities of objects in a collision."""
        a, mtd, b = c
        perp = mtd.perpendicular()
        ua = mtd.project(a.v)
        ub = mtd.project(b.v)
        ma = a.mass
        mb = b.mass
        tm = ma + mb  # total mass
    
        if is_inf(tm):
            a.v = a.v - ua
            b.v = b.v - ub
            return True

        # Inelastic collision, see http://en.wikipedia.org/wiki/Inelastic_collision
        com = (ma * ua + mb * ub) / tm

        dv = ub - ua
        cor = 0.2

        dm = cor * mb * dv / tm
        a.v = perp.project(a.v) + dm + com
        b.v = perp.project(b.v) - dm + com
        return True

    def _call_collision_callback(self, a, b, dt):
        ch = a.on_collide
        if ch is not None:
            ch(b, dt)

    def _do_collisions(self, dt):
        for d in self.dynamic:
            self.collide_static(d)

        collisions = []
        for i, d in enumerate(self.dynamic):
            for d2 in self.dynamic[i + 1:]:
                c = self.collide_dynamic(d, d2)
                if c:
                    a, mtd, b = c
                    self._call_collision_callback(a, b, dt)
                    self._call_collision_callback(b, a, dt)
                    self._collide_velocities(c)
                    collisions.append(c)

        for i in xrange(5):
            if not collisions:
                break
            colliding = set()
            for c in collisions:
                self._resolve_collision(c)
                colliding.add(c[0])
                colliding.add(c[2])

            for d in colliding:
                self.collide_static(d)

            collisions = []
            for d in colliding:
                for d2 in self.dynamic:
                    if d is not d2:
                        c = self.collide_dynamic(d, d2)
                        if c:
                            collisions.append(c)

    def update(self, dt):
        """Update all dynamic objects added to this Physics system.

        :param dt: The amount of time (in seconds) to advance the simulation.

        """
        for d in self.dynamic:
            d.update(dt)

        self._do_collisions(dt)

        for d in self.dynamic:
            d.reset_forces()

