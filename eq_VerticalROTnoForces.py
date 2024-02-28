# OMX EULER OMX + [w]*OMX*dt + Ortogonalisation + Roration test
import math
import numpy as np
import matplotlib.pyplot as plt
import omp

orient = omp.Orient()
passage = omp.Passage()
mth = omp.Math()


class Main:
    def __new__(self, initial_state):

        # Time and Mode
        Time = 0.0
        TimeMax = 350.  # 92. #92. #108. #84.0
        TimeStep = .01

        # 0 - Body, 1 - Earth, 2 - Course:
        FM_APP_Mode = 1
        GENVEL0_APP_Mode = 1
        # # # #

        # CONSTANTS
        AoG = 9.81  # m/s^2, acceleration of gravity
        CNV_TONN2KG = 1000.
        CNV_DEG2RAD = math.pi/180.
        CNV_SEC2MIN = 60.
        CNV_KNOT2MPERS = 1852.0 / CNV_SEC2MIN / CNV_SEC2MIN  # http://fb.ru/article/54711/chto-takoe-morskaya-milya-i-chemu-raven-morskoy-uzel.

        # Ship Data
        # Name - Bulk carrier 20
        displacement_tonnage = initial_state['Displacement tonnage'] # mass, t
        # 28725.2 # mass, t
        mass = CNV_TONN2KG * displacement_tonnage  # kg
        Ixx = 2.187382163e+010  # kg/m^2
        Iyy = 3.930906696e+011  # kg/m^2
        Izz = 4.0516875e+011  # kg/m^2
        Rxx = math.sqrt(Ixx / mass)  # print('\nRxx', Rxx)
        Ryy = math.sqrt(Iyy / mass)  # print('\nRyy', Ryy)
        Rzz = math.sqrt(Izz / mass)  # print('\nRzz', Rzz)

        # Initial State
        X_0 = initial_state['X'] # m
        Y_0 = initial_state['Y'] # m
        Z_0 = initial_state['Z'] # m

        location = np.array([X_0, Y_0, Z_0], dtype='float64')
        #print('\nLOCATION', LOCATION, LOCATION.dtype, LOCATION.shape, LOCATION.size, LOCATION.data)
        rol_0 = 0.0  # deg
        pit_0 = 2.0  # deg
        hdg_0 = 0.0  # deg
        rol_0 = CNV_DEG2RAD * rol_0  # rad
        pit_0 = CNV_DEG2RAD * pit_0  # rad
        hdg_0 = CNV_DEG2RAD * hdg_0  # rad #    print('\nHDG_0', HDG_0)
        ANGLES = np.array([rol_0, pit_0, hdg_0], dtype='float64')
        print('\nANGLES', ANGLES, ANGLES.dtype, ANGLES.shape, ANGLES.size)
        OMX = orient.ang_to_omx(ANGLES)
        o_OMX = OMX.copy
        #EULER_OMX = OMX.copy() # EULER_OMX.base is OMX
        #EULER_OMX_1 = OMX.copy() # EULER_OMX.base is OMX
        #o_EULER_OMX = EULER_OMX.copy()
        print('\nOMX', OMX, OMX.dtype, OMX.shape, OMX.size)

        ANGVEL_X0 = CNV_DEG2RAD * 0. # rad/s
        ANGVEL_Y0 = CNV_DEG2RAD * 0. # rad/s
        ANGVEL_Z0 = CNV_DEG2RAD * 4.2 # rad/s

        ANGVEL0 = np.array([ANGVEL_X0, ANGVEL_Y0, ANGVEL_Z0], dtype='float64')
        print('\nANGVEL0', ANGVEL0, ANGVEL0.dtype, ANGVEL0.shape, ANGVEL0.size)

        if GENVEL0_APP_Mode == 1:
            avel_SEMI = ANGVEL0.copy()
            ANGVEL = passage.semi_to_body(OMX, avel_SEMI)

        Speed_0 = 0.0 / CNV_KNOT2MPERS # knots
        Speed_0 = CNV_KNOT2MPERS * Speed_0 # m/s
        #ROT_0 = 0.0/CNV_DEG2RAD # deg/min - rate of HDG change
        #ROT_0 = CNV_DEG2RAD * ROT_0 / CNV_SEC2MIN # 1/s - rate of HDG change

        # genvel - обобщенная скорость в с.с.к.     #vel = np.arange(1, 4, 1) * 10
        # Body-Fixed Velocities
        vel_BODY = np.array([Speed_0, 0.0, 0.0], dtype='float64')
        #vel_BODY = [1.725, -0.521, 0.0]
        print('\nvel_BODY', vel_BODY, vel_BODY.dtype, vel_BODY.shape, vel_BODY.size)
        #avel_BODY = np.array([0.0, 0.0, ROT_0], dtype='float64')
        avel_BODY = ANGVEL.copy()
        #avel_BODY = [0.0, 0.0, 0.005306]
        print('\navel_BODY', avel_BODY, avel_BODY.dtype, avel_BODY.shape, avel_BODY.size)
        genvel_BODY = np.hstack((vel_BODY, avel_BODY))
        print('\ngenvel_BODY', genvel_BODY, genvel_BODY.dtype, genvel_BODY.shape, genvel_BODY.size)

        # genvelE - обобщенная скорость в земной.с.к.
        # Semi-Body-Fixed Velocities
        vel_SEMI = passage.body_to_semi(OMX, vel_BODY)
        print('\nvel_SEMI', vel_SEMI, vel_SEMI.dtype, vel_SEMI.shape, vel_SEMI.size)
        avel_SEMI = passage.body_to_semi(OMX, avel_BODY)
        print('\navel_SEMI', avel_SEMI, avel_SEMI.dtype, avel_SEMI.shape, avel_SEMI.size)
        genvel_SEMI = np.hstack((vel_SEMI, avel_SEMI)) #    print('\ngenvel_SEMI', genvel_SEMI)
        print('\ngenvel_SEMI', genvel_SEMI, genvel_SEMI.dtype, genvel_SEMI.shape, genvel_SEMI.size)

        # векторное произведение     #vel_SEMIxBODY = np.cross(vel_SEMI, vel_BODY)    #print('\nvel_SEMIxBODY', vel_SEMIxBODY)

        # Premotion
        #InitShip(); imxgvelC(); iimag(); inertfor(); force(); acceler();

        # Матрица обобщенных скоростей в с.с.к.
        mxgenvel_BODY = mth.mgenvel(vel_BODY, avel_BODY) #
        print('\nmxgenvel_BODY', mxgenvel_BODY, mxgenvel_BODY.dtype, mxgenvel_BODY.shape, mxgenvel_BODY.size)

        # imag - матрица обобщенных масс
        gmass = np.eye(6, dtype='float64') # imag
        gmass *= mass
        gmass[3, 3] = Ixx
        gmass[4, 4] = Iyy
        gmass[5, 5] = Izz
        print('\ngmass', gmass, gmass.dtype, gmass.shape, gmass.size)

        # inertfor - ОПРЕДЕЛЕНИЕ  И Н Е Р Ц И О Н Н Ы Х  С И Л
        #v1 = np.dot(gmass, genvel_BODY)
        #print('\nv1', v1)
        #IFORCE_BODY = np.dot(mxgenvel_BODY, v1)
        #print('\nIFORCE_BODY', IFORCE_BODY)
        IFORCE_BODY = np.dot(mxgenvel_BODY, np.dot(gmass, genvel_BODY))
        print('\nIFORCE_BODY', IFORCE_BODY, IFORCE_BODY.dtype, IFORCE_BODY.shape, IFORCE_BODY.size)

        # force
        # При этом сам Python-Unit (PitchRollTester3) считает моменты сил так:
        # время 0-4с: момент по крену 50000 т*м, по дифференту 250000 т*м
        # время 4-12с: момент по крену -50000 т*м, по дифференту -250000 т*м
        # и так далее через каждые 8 секунд знак моментов меняется на противоположный.

        AFORCE = np.zeros(6)
        AFORCE_BODY = np.zeros(6)
        Amom_BODY = np.zeros(3, dtype='float64')
        Amom_SEMI = np.zeros(3, dtype='float64')
        Amom_CRS = np.zeros(3, dtype='float64')

        Mx = 0.0 # CNV_tonn2kg * 50000.0 * AoG # N*m
        My = 0.0 #CNV_tonn2kg * 250000.0 * AoG # N*m
        Mz = 0.0 #CNV_tonn2kg * 300000.0 * AoG # N*m
        AFORCE[3] = Mx
        AFORCE[4] = My
        AFORCE[5] = Mz
        print('\nAFORCE', AFORCE, AFORCE.dtype, AFORCE.shape, AFORCE.size)

        FORCE_BODY = np.zeros(6, dtype='float64')
        print('\nFORCE_BODYY', FORCE_BODY, FORCE_BODY.dtype, FORCE_BODY.shape, FORCE_BODY.size)
        ACC_BODY = np.zeros(6, dtype='float64')
        print('\nACC_BODY', ACC_BODY, ACC_BODY.dtype, ACC_BODY.shape, ACC_BODY.size)

        i = 0
        Coeff = 1.
        Nstep = TimeMax/TimeStep + 1
        mx = np.arange(Nstep)
        my = np.arange(Nstep)
        mz = np.arange(Nstep)
        mx0 = np.arange(Nstep)
        my0 = np.arange(Nstep)
        mz0 = np.arange(Nstep)
        time = np.arange(Nstep)
        #time = np.arange(Nstep, dtype='float64')
        #time[Nstep] = TimeMax
        a = np.arange(Nstep)
        I_X_BODY = np.arange(Nstep)
        I_Y_BODY = np.arange(Nstep)
        I_Z_BODY = np.arange(Nstep)
        I_MX_BODY = np.arange(Nstep)
        I_MY_BODY = np.arange(Nstep)
        I_MZ_BODY = np.arange(Nstep)
        aax_BODY = np.arange(Nstep)
        aay_BODY = np.arange(Nstep)
        aaz_BODY = np.arange(Nstep)
        Roll_AVEL = np.arange(Nstep)
        Pitch_AVEL = np.arange(Nstep)
        HDG_AVEL = np.arange(Nstep)
        Roll_ANGLE = np.arange(Nstep)
        Pitch_ANGLE = np.arange(Nstep)
        HDG_ANGLE = np.arange(Nstep)

        while Time <= TimeMax:
            Roll_ANGLE[i] = ANGLES[0]
            Pitch_ANGLE[i] = ANGLES[1]
            HDG_ANGLE[i] = ANGLES[2]
            Roll_AVEL[i] = avel_BODY[0]
            Pitch_AVEL[i] = avel_BODY[1]
            HDG_AVEL[i] = avel_BODY[2]

            if i >= 2:
                aaaa = i

            #a[i] = 0.0
            #if (Time>4.0 ):
            #    a[i] = (Time-4.0) % 8.0
            #    if a[i] <= TimeStep*1.:
            #        AFORCE = -1.0 * AFORCE
                    #print('\n-AFORCE', i, Time, AFORCE)

            if Time > 10.0:
                AFORCE = 0.0 * AFORCE

            #print('\nAFORCE', i, Time, AFORCE)

            #AFORCE_BODY[0] = AFORCE[0]
            #AFORCE_BODY[1] = AFORCE[1]
            #AFORCE_BODY[2] = AFORCE[2]
            #AFORCE_BODY[3] = AFORCE[3]
            #AFORCE_BODY[4] = AFORCE[4]
            #AFORCE_BODY[5] = AFORCE[5]

            if FM_APP_Mode == 1:
                Amom_SEMI[0] = AFORCE[3]
                Amom_SEMI[1] = AFORCE[4]
                Amom_SEMI[2] = AFORCE[5]
                Amom_BODY = passage.semi_to_body(OMX, Amom_SEMI)
                AFORCE_BODY[3] = Amom_BODY[0]
                AFORCE_BODY[4] = Amom_BODY[1]
                AFORCE_BODY[5] = Amom_BODY[2]

            elif FM_APP_Mode == 2:
                Amom_CRS[0] = AFORCE[3]
                Amom_CRS[1] = AFORCE[4]
                Amom_CRS[2] = AFORCE[5]
                ANG_COURSE = np.zeros(3, dtype='float64')
                ANG_COURSE[2] = ANGLES[2]
                #print('\nAngles', i, ANG_COURSE, ANGLES)
                OMX_COURSE = orient.ang_to_omx(ANG_COURSE)
                Amom_SEMI = passage.body_to_semi(OMX_COURSE, Amom_CRS)
                Amom_BODY = passage.semi_to_body(OMX, Amom_SEMI)
                AFORCE_BODY[3] = Amom_BODY[0]
                AFORCE_BODY[4] = Amom_BODY[1]
                AFORCE_BODY[5] = Amom_BODY[2]


            mx[i] = AFORCE_BODY[3]
            my[i] = AFORCE_BODY[4]
            mz[i] = AFORCE_BODY[5]
            mx0[i] = AFORCE[3]
            my0[i] = AFORCE[4]
            mz0[i] = AFORCE[5]

            time[i] = Time
            Time = Time + TimeStep

            #AF_BODY_3[0] = AFORCE_BODY



            # force
            FORCE_BODY = AFORCE_BODY - IFORCE_BODY
            I_X_BODY[i] = IFORCE_BODY[0]
            I_Y_BODY[i] = IFORCE_BODY[1]
            I_Z_BODY[i] = IFORCE_BODY[2]
            I_MX_BODY[i] = IFORCE_BODY[3]
            I_MY_BODY[i] = IFORCE_BODY[4]
            I_MZ_BODY[i] = IFORCE_BODY[5]


            # acceller
            ACC_BODY = np.linalg.solve(gmass, FORCE_BODY)
            linacc_BODY = np.array([ACC_BODY[0], ACC_BODY[1], ACC_BODY[2]], dtype='float64') #        print('\nlinacc_BODY', linacc_BODY)
            angacc_BODY = np.array([ACC_BODY[3], ACC_BODY[4], ACC_BODY[5]], dtype='float64') #        print('\nangacc_BODY', angacc_BODY)
            aax_BODY[i] = angacc_BODY[0]
            aay_BODY[i] = angacc_BODY[1]
            aaz_BODY[i] = angacc_BODY[2]

            linacc_SEMI = passage.body_to_semi(OMX, linacc_BODY) #        print('\nlinacc_SEMI', linacc_SEMI)
            angacc_SEMI = passage.body_to_semi(OMX, angacc_BODY) #        print('\nangacc_SEMI', angacc_SEMI)

            # gen_motion /*  G  E  N  E  R  A  L     M  O  T  I  O  N  */
            # TIME_SD+=stept;
            # premotion();                                         /* FREE_RMX;*/
            d_LOCATION = vel_SEMI * TimeStep # multvc   ( VEL_SD, stept, w_vo3x1 );
            location = location + d_LOCATION # reductEl ( SUM, POS_SD, w_vo3x1, POS_SD );

            #d_ANGLES = avel_SEMI * TimeStep # multvc   ( AVELC_SD, stept, w_vo3x1 ); #        print('\navel_SEMI', avel_SEMI, avel_SEMI.dtype, avel_SEMI.shape, avel_SEMI.size)
            #d_ANGLES = avel_BODY * TimeStep # multvc   ( AVELC_SD, stept, w_vo3x1 ); #        print('\navel_BODY', avel_BODY, avel_BODY.dtype, avel_BODY.shape, avel_BODY.size)
            #o_OMX = OMX # assignm  ( ORIENT_SD, IDENTICAL, w_mo3x3 );
            #d_OMX = ang2omx(d_ANGLES) # orienti  ( S_to_O,  w_vo3x1, w_mt3x3 );
            #OMX = np.dot(o_OMX, d_OMX) # multm    ( w_mo3x3, w_mt3x3, ORIENT_SD );

            # d_EULER_OMX.base is OMX
            #doRotM_dt_W = mvprod(avel_BODY) # time derivative of the rotation matrix dA/dt
            #E_M = np.eye(3)
            #doRotM_W = doRotM_dt_W * TimeStep
            #doRotM = E_M + doRotM_W
            #doRotM = np.dot(E_M, doRotM_W)
            #o_OMX = OMX #.copy # assignm  ( ORIENT_SD, IDENTICAL, w_mo3x3 );
            #OMX = np.dot(doRotM, o_OMX)
            #EULER_OMX_1 = doRotM * o_EULER_OMX

            # OMX + [w]*OMX*dt - EULER_1
            W_M = mth.mvprod(avel_SEMI) # time derivative of the rotation matrix dA/dt
            doRotM_dt_W = np.dot(W_M, OMX)
            add_OMX = doRotM_dt_W * TimeStep
            OMX = OMX + add_OMX

            #OMX = EULER_OMX # !!!!!!!!!!!!!!!!!

            ANGLES = orient.omx_to_ang(OMX) # orienti  ( O_to_S, ANGLES_SD, ORIENT_SD);
            OMX = orient.ang_to_omx(ANGLES) # ORTOGONALISATION

            # =========== проба https://en.wikipedia.org/wiki/Rotation_formalisms_in_three_dimensions
            # Rotation_matrix_%E2%86%94_angular_velocities
            #mvp_avel = mvprod(avel_BODY)
            #dAng_dt = np.dot(mvp_avel, o_OMX)


            # EL(ANGLES_SD,0,0)=0; EL(ANGLES_SD,1,0)=0;
            # orienti  ( S_to_O, ANGLES_SD, ORIENT_SD );

            # Body-Fixed Velocities
            d_genvel_BODY = ACC_BODY * TimeStep # multvc   ( CONGACC_SD, stept, v_wo6x1 );
            genvel_BODY = genvel_BODY + d_genvel_BODY # reductEl ( SUM, GENVELC_SD, v_wo6x1, GENVELC_SD );
            vel_BODY[0] = genvel_BODY[0]
            vel_BODY[1] = genvel_BODY[1]
            vel_BODY[2] = genvel_BODY[2]
            avel_BODY[0] = genvel_BODY[3]
            avel_BODY[1] = genvel_BODY[4]
            avel_BODY[2] = genvel_BODY[5]
            #avel_BODY = [genvel_BODY[3], genvel_BODY[4], genvel_BODY[5]]
            # Semi-Body-Fixed Velocities
            vel_SEMI = passage.body_to_semi(OMX, vel_BODY) # passage  ( C_to_H, ORIENT_SD, w_vo3x1, VELC_SD, VEL_SD );
            avel_SEMI = passage.body_to_semi(OMX, avel_BODY) # passage  ( C_to_H, ORIENT_SD, w_vo3x1, AVELC_SD, AVEL_SD );
            #genvel_SEMI = np.hstack((vel_SEMI, avel_SEMI))
            genvel_SEMI[0] = vel_SEMI[0]
            genvel_SEMI[1] = vel_SEMI[1]
            genvel_SEMI[2] = vel_SEMI[2]
            genvel_SEMI[3] = avel_SEMI[0]
            genvel_SEMI[4] = avel_SEMI[1]
            genvel_SEMI[5] = avel_SEMI[2]

            # premotion();                                         /* FREE_RMX;*/
            #  InitShip(); imxgvelC(); iimag(); inertfor(); force(); acceler();
            # imxgvelC(); Матрица обобщенных скоростей в с.с.к.
            mxgenvel_BODY = mth.mgenvel(vel_BODY, avel_BODY) #
            # imag - матрица обобщенных масс
            # const
            # inertfor - ОПРЕДЕЛЕНИЕ  И Н Е Р Ц И О Н Н Ы Х  С И Л
            #v1 = np.dot(gmass, genvel_BODY)
            #print('\nv1', v1)
            #IFORCE_BODY = np.dot(mxgenvel_BODY, v1)
            #print('\nIFORCE_BODY', IFORCE_BODY)
            IFORCE_BODY = np.dot(mxgenvel_BODY, np.dot(gmass, genvel_BODY))

            i = i + 1

            #print('\n',i)
        #time[i] = Time

        #FORCE_BODY = AFORCE_BODY - IFORCE_BODY
        #print('\nFORCE_BODY', FORCE_BODY)
        #ACC_BODY = np.linalg.solve(gmass, FORCE_BODY)
        #print('\nACC_BODY', ACC_BODY)

        # graphs
        fig, axs = plt.subplots(nrows=4, ncols=4)

        # Plot 1
        axs[0, 0].plot(time, mx, 'r')
        axs[0, 0].plot(time, mx0, 'g')
        axs[0, 0].set_xlabel("Time, s")
        axs[0, 0].set_ylabel("Mx, N*m")
        axs[0, 0].set_title('Mx(t), N*m')

        # Plot 2
        axs[0, 1].plot(time, my, 'r')
        axs[0, 1].plot(time, my0, 'g')
        axs[0, 1].set_xlabel("Time, s")
        axs[0, 1].set_ylabel("My, N*m")
        axs[0, 1].set_title("My(t), N*m")

        # Plot 3
        axs[0, 2].plot(time, mz, 'r')
        axs[0, 2].plot(time, mz0, 'g')
        axs[0, 2].set_xlabel("Time, s")
        axs[0, 2].set_ylabel("Mz, N*m")
        axs[0, 2].set_title("Mz(t), N*m")

        # Plot 4
        axs[0, 3].plot(time, a, 'r')
        axs[0, 3].set_xlabel("Time, s")
        axs[0, 3].set_ylabel("a")
        axs[0, 3].set_title("a")

        # plot 5
        axs[1, 0].plot(time, I_MX_BODY, 'r')
        axs[1, 0].set_xlabel("Time, s")
        axs[1, 0].set_ylabel("I_MX_BODY, N*m")
        axs[1, 0].set_title("I_MX_BODY, N*m")

        # plot 6
        axs[1, 1].plot(time, I_MY_BODY, 'r')
        axs[1, 1].set_xlabel("Time, s")
        axs[1, 1].set_ylabel("I_MY_BODY, N*m")
        axs[1, 1].set_title("I_MY_BODY, N*m")

        # plot 7
        axs[1, 2].plot(time, I_MZ_BODY, 'r')
        axs[1, 2].set_xlabel("Time, s")
        axs[1, 2].set_ylabel("I_MZ_BODY, N*m")
        axs[1, 2].set_title("I_MZ_BODY, N*m")

        # plot 8
        axs[1, 3].plot(time, aax_BODY, 'r')
        axs[1, 3].set_xlabel("Time, s")
        axs[1, 3].set_ylabel("aax_BODY, 1/s^2")
        axs[1, 3].set_title("aax_BODY, 1/s^2")

        # plot 9
        axs[2, 0].plot(time, aay_BODY, 'r')
        axs[2, 0].set_xlabel("Time, s")
        axs[2, 0].set_ylabel("aay_BODY, 1/s^2")
        axs[2, 0].set_title("aay_BODY, 1/s^2")

        # plot 10
        axs[2, 1].plot(time, aaz_BODY, 'r')
        axs[2, 1].set_xlabel("Time, s")
        axs[2, 1].set_ylabel("aaz_BODY, 1/s^2")
        axs[2, 1].set_title("aaz_BODY, 1/s^2")

        # plot 11
        axs[2, 2].plot(time, Roll_AVEL / CNV_DEG2RAD, 'r')
        axs[2, 2].set_xlabel("Time, s")
        axs[2, 2].set_ylabel("Roll_AVEL, deg")
        axs[2, 2].set_title("Roll_AVEL, deg")

        # plot 12
        axs[2, 3].plot(time, Pitch_AVEL / CNV_DEG2RAD, 'r')
        axs[2, 3].set_xlabel("Time, s")
        axs[2, 3].set_ylabel("Pitch_AVEL, deg")
        axs[2, 3].set_title("Pitch_AVEL, deg")

        # plot 13
        axs[3, 0].plot(time, HDG_AVEL / CNV_DEG2RAD, 'r')
        axs[3, 0].set_xlabel("Time, s")
        axs[3, 0].set_ylabel("HDG_AVEL, deg")
        axs[3, 0].set_title("HDG_AVEL, deg")

        # plot 14
        axs[3, 1].plot(time, Roll_ANGLE / CNV_DEG2RAD, 'r')
        axs[3, 1].set_xlabel("Time, s")
        axs[3, 1].set_ylabel("Roll_ANGLE, deg")
        axs[3, 1].set_title("Roll_ANGLE, deg")

        # plot 15
        axs[3, 2].plot(time, Pitch_ANGLE / CNV_DEG2RAD, 'r')
        axs[3, 2].set_xlabel("Time, s")
        axs[3, 2].set_ylabel("Pitch_ANGLE, deg")
        axs[3, 2].set_title("Pitch_ANGLE, deg")

        # plot 16
        axs[3, 3].plot(time, HDG_ANGLE / CNV_DEG2RAD, 'r')
        axs[3, 3].set_xlabel("Time, s")
        axs[3, 3].set_ylabel("HDG_ANGLE, deg")
        axs[3, 3].set_title("HDG_ANGLE, deg")

        plt.grid(True, linestyle='-', color='0.75')
        plt.tight_layout()
        if __name__ == "__main__":
            plt.show()

        # # # # # # #

        OMXtt = np.dot(OMX, OMX.transpose())
        print(OMXtt)
        print(orient.omx_to_ang(OMX))

        #np.savetxt('myfile.txt', (Time, HDG_ANGLE / CNV_DEG2RAD), fmt='%.18g', delimiter=' ', newline=os.linesep)
        #np.savetxt('myfile.txt', [Time, HDG_ANGLE / CNV_DEG2RAD], fmt='%.18g', delimiter=' ')
        #np.savetxt('myfile1.txt', str('np.transpose([time, HDG_ANGLE ])'))
        np.savetxt('eq_VerticalROTnoForces.txt', np.transpose([time, mx, my, I_MX_BODY, I_MY_BODY, I_MZ_BODY, aax_BODY, aay_BODY, aaz_BODY, Roll_AVEL / CNV_DEG2RAD, Pitch_AVEL / CNV_DEG2RAD, HDG_AVEL / CNV_DEG2RAD, Roll_ANGLE / CNV_DEG2RAD, Pitch_ANGLE / CNV_DEG2RAD, HDG_ANGLE / CNV_DEG2RAD]))
        #np.savetxt('myfile1.txt', [time, HDG_ANGLE ])

        # time, s
        # Mx(t), N*m
        # My(t), N*m
        # I_MX_BODY, N*m
        # I_MY_BODY, N*m
        # I_MZ_BODY, N*m
        # angaccX-BODY, 1/s^2
        # angaccY-BODY, 1/s^2
        # angaccZ-BODY, 1/s^2
        # Roll_AVEL, deg
        # Pitch_AVEL, deg
        # HDG_AVEL, deg
        # Roll_ANGLE, deg
        # Pitch_ANGLE, deg
        # HDG_ANGLE, deg

        return fig
    
    
"""
    >>> orient(0), orient(1)
    ([], [])
    >>> orient(2), orient(3)
    ([2], [2, 3])
    >>> orient(20)
    [2, 3, 5, 7, 11, 13, 17, 19]
=================
[ 0.1  0.2  0.3]
[[ 0.93629336 -0.27509585  0.21835066]
 [ 0.28962948  0.95642509 -0.03695701]
 [-0.19866933  0.0978434   0.97517033]]
[[  1.00000000e+00  -2.94902991e-17   2.77555756e-17]
 [ -2.94902991e-17   1.00000000e+00   0.00000000e+00]
 [  2.77555756e-17   0.00000000e+00   1.00000000e+00]]
[ 0.1  0.2  0.3]
#"""
