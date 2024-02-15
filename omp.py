import math
import numpy as np

prec = 1e-7


class Orient:
    def omx_to_ang(self, o):
        if math.fabs(o[0, 0]) > prec:
            head = math.atan2(o[1, 0], o[0, 0])
        else:
            head = math.pi / 2 * np.sign(o[1, 0])
        if math.fabs(o[0, 0] + o[1, 0]) > prec:
            pitch = -math.atan2(o[2, 0], (o[0, 0] + o[1, 0]) / (math.cos(head) + math.sin(head)))
        else:
            pitch = math.pi / 2 * np.sign(o[2, 0])
        if math.fabs(o[2, 2]) > prec:
            roll = math.atan2(o[2, 1], o[2, 2])
        else:
            roll = math.pi / 2 * np.sign(o[2, 1])
        return np.array([roll, pitch, head])

    def ang_to_omx(self, ang):
        if ang.size < 3:
            return []

        roll = ang[0]  # крен
        el_roll = np.eye(3)
        el_roll[1, 1] = math.cos(roll)
        el_roll[1, 2] = -math.sin(roll)
        el_roll[2, 1] = math.sin(roll)
        el_roll[2, 2] = math.cos(roll)

        pitch = ang[1]  # дифферент
        el_pitch = np.eye(3)
        el_pitch[0, 0] = math.cos(pitch)
        el_pitch[0, 2] = math.sin(pitch)
        el_pitch[2, 0] = -math.sin(pitch)
        el_pitch[2, 2] = math.cos(pitch)

        head = ang[2]  # курс
        el_head = np.eye(3)
        el_head[0, 0] = math.cos(head)
        el_head[0, 1] = -math.sin(head)
        el_head[1, 0] = math.sin(head)
        el_head[1, 1] = math.cos(head)

        om = np.matmul(np.matmul(el_head, el_pitch), el_roll)
        return om


class Passage:
    def semi_to_body(self, ORIENT, VEC_IN):
        mxo = ORIENT.transpose()
        return np.dot(mxo, VEC_IN)  # VEC_OUT

    def body_to_semi(self, ORIENT, VEC_IN):
        return np.dot(ORIENT, VEC_IN)  # VEC_OUT


class Math:
    def mvprod(self, vec):
        mvp = np.zeros(9).reshape(3, 3)
        mvp[0, 1] = -vec[2]
        mvp[0, 2] = vec[1]
        mvp[1, 0] = vec[2]
        mvp[1, 2] = -vec[0]
        mvp[2, 0] = -vec[1]
        mvp[2, 1] = vec[0]

        return mvp

    def mgenvel(self, vec, avec):
        m303 = np.zeros(9).reshape(3, 3)
        vel_vprod = self.mvprod(vec)
        avel_vprod = self.mvprod(avec)
        mgv1 = np.hstack((avel_vprod, m303))
        mgv2 = np.hstack((vel_vprod, avel_vprod))
        mgv = np.vstack((mgv1, mgv2))

        return mgv
