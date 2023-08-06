from . import DifferentiableManifold, np, contract, check
from .. import (any_orthogonal_direction, geodesic_distance_on_sphere,
    random_direction, normalize_length, normalize_length_or_zero,
    rotation_from_axis_angle, rot2d)
from numpy.core.numeric import outer


class Sphere(DifferentiableManifold):
    ''' These are hyperspheres of unit radius. '''

    norm_rtol = 1e-5
    atol_geodesic_distance = 1e-8

    @contract(order='(1|2)')
    def __init__(self, order):
        DifferentiableManifold.__init__(self, dimension=order)
        self.N = order + 1

    def __repr__(self):
        return 'S%s' % (self.dimension)

    @contract(a='belongs', b='belongs', returns='>=0')
    def distance(self, a, b):
        return geodesic_distance_on_sphere(a, b)

    @contract(base='belongs', target='belongs', returns='belongs_ts')
    def logmap(self, base, target):
        # TODO: create S1_logmap(base, target)
        # XXX: what should we do in the case there is more than one logmap?
        d = geodesic_distance_on_sphere(target, base)
        if np.allclose(d, np.pi, atol=self.atol_geodesic_distance):
            if self.N == 2:
                xp = np.array([base[1], -base[0]])
            elif self.N == 3:
                xp = any_orthogonal_direction(base)
        else:
            x = target - base
            base, xp = self.project_ts((base, x))
        xp = normalize_length_or_zero(xp)
        xp *= geodesic_distance_on_sphere(target, base)
        return base, xp

    @contract(bv='belongs_ts', returns='belongs')
    def expmap(self, bv):
        base, vel = bv
        angle = np.linalg.norm(vel)
        if angle == 0: # XXX: tolerance
            return base

        if self.N == 2:
            direction = -np.sign(vel[0] * base[1] - base[0] * vel[1])
            R = rot2d(angle * direction)
            result = np.dot(R, base)
        elif self.N == 3:
            axis = -np.cross(normalize_length(vel), base)
            axis = normalize_length(axis)
            R = rotation_from_axis_angle(axis, angle)
            result = np.dot(R, base)
        else:
            assert False

        return result

    @contract(bve='tuple(belongs, *)')
    def project_ts(self, bve): # TODO: test
        base, vel = bve
        P = np.eye(self.N) - outer(base, base)
        return base, np.dot(P, vel)

    def belongs(self, x):
        check('array[N],unit_length', x)

    @contract(returns='belongs')
    def sample_uniform(self):
        return random_direction(self.N)

    @contract(returns='list(belongs)')
    def interesting_points(self):
        if self.N == 2:
            points = []
            points.append(np.array([-1, 0]))
            points.append(np.array([0, 1]))
            points.append(np.array([0, -1]))
            points.append(np.array([+1, 0]))
            points.append(np.array([np.sqrt(2) / 2, np.sqrt(2) / 2]))
            return points
        elif self.N == 3:
            points = []
            points.append(np.array([-1, 0, 0]))
            points.append(np.array([0, 1, 0]))
            points.append(np.array([0, 0, 1]))
            points.append(np.array([0, 0, -1]))
            points.append(np.array([np.sqrt(2) / 2, np.sqrt(2) / 2, 0]))
            return points
        else:
            assert False

    def friendly(self, x):
        if self.N == 2:
            theta = np.arctan2(x[1], x[0])
            return 'Dir(%6.1fdeg)' % np.degrees(theta)
        elif self.N == 3:
            theta = np.arctan2(x[1], x[0])
            elevation = np.arcsin(x[2])
            return 'Dir(%6.1fdeg,el:%5.1fdeg)' % (np.degrees(theta),
                                                      np.degrees(elevation))
        else:
            assert False


class Sphere1(DifferentiableManifold):

    norm_rtol = 1e-5
    atol_geodesic_distance = 1e-8

    def __init__(self):
        DifferentiableManifold.__init__(self, dimension=1)

    def __repr__(self):
        return 'S1'

    @contract(a='S1', b='S1', returns='>=0')
    def distance(self, a, b):
        return geodesic_distance_on_sphere(a, b)

    @contract(base='S1', target='S1', returns='belongs_ts')
    def logmap(self, base, target):
        # TODO: create S1_logmap(base, target)
        # XXX: what should we do in the case there is more than one logmap?
        d = geodesic_distance_on_sphere(target, base)
        if np.allclose(d, np.pi, atol=self.atol_geodesic_distance):
            xp = np.array([base[1], -base[0]])
        else:
            x = target - base
            base, xp = self.project_ts((base, x))
        xp = normalize_length_or_zero(xp)
        xp *= geodesic_distance_on_sphere(target, base)
        return base, xp

    @contract(bv='belongs_ts', returns='belongs')
    def expmap(self, bv):
        base, vel = bv
        angle = np.linalg.norm(vel)
        if angle == 0: # XXX: tolerance
            return base
        direction = -np.sign(vel[0] * base[1] - base[0] * vel[1])
        R = rot2d(angle * direction)
        result = np.dot(R, base)
        return result

    @contract(bx='tuple(belongs, *)')
    def project_ts(self, bx): # TODO: test
        base, x = bx
        P = np.eye(2) - outer(base, base)
        return base, np.dot(P, x)

    @contract(x='S1')
    def belongs(self, x):
        pass

    def sample_uniform(self):
        return random_direction(2)

    def interesting_points(self):
        points = []
        points.append(np.array([-1, 0]))
        points.append(np.array([0, 1]))
        points.append(np.array([0, -1]))
        points.append(np.array([+1, 0]))
        points.append(np.array([np.sqrt(2) / 2, np.sqrt(2) / 2]))
        return points

    def friendly(self, x):
        theta = np.arctan2(x[1], x[0])
        return 'Dir(%6.1fdeg)' % np.degrees(theta)
