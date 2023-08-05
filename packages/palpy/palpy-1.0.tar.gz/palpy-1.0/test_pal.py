# Test script for PAL interface

# Copyright (C) 2012 Tim Jenness and Science and Technology
# Facilities Council.

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import unittest
import palpy as pal
import numpy as np

class TestPAL(unittest.TestCase) :

    def test_addet(self):
        rm = 2.0
        dm = -1.0
        eq = 1975.0
        ( r1, d1 ) = pal.addet( rm, dm, eq )
        self.assertAlmostEqual( r1 - rm, 2.983864874295250e-6, 11 )
        self.assertAlmostEqual( d1 - dm, 2.379650804185118e-7, 11 )

        ( r2, d2 ) = pal.subet( r1, d1, eq )
        self.assertAlmostEqual( r2 - rm, 0.0, 11 )
        self.assertAlmostEqual( d2 - dm, 0.0, 11 )

    def test_afin(self):
        (d, i) = pal.dafin( "12 34 56.7 |", 1 )
        self.assertEqual( i, 12 )
        self.assertAlmostEqual( d, 0.2196045986911432, 12 )

        (d, i) = pal.dafin( "45 00 00.000 ", 1 )
        self.assertEqual( i, 14 )
        self.assertAlmostEqual( d, pal.DPI / 4.0, 12 )

        (d, i) = pal.dafin( "30.2 < just decimal degrees", 1 )
        self.assertEqual( i, 6 )
        self.assertAlmostEqual( d, 30.2 * pal.DD2R, 12 )

        (d, i) = pal.dafin( "  30 23.6 < decimal armin", 1 )
        self.assertEqual( i, 11 )
        self.assertAlmostEqual( d, (30 + 23.6/60)*pal.DD2R, 12 )

        (d, i) = pal.dafin( " offset into string: 45.0 <<<", 22 )
        self.assertEqual( i, 27 )
        self.assertAlmostEqual( d, pal.DPI / 4.0, 12 )

        self.assertRaises( ValueError, pal.dafin, " not a sexagesimal string ", 1 )
        self.assertRaises( ValueError, pal.dafin, " 750.4 21 0.0 bad degrees ", 1 )
        self.assertRaises( ValueError, pal.dafin, " 45 30.5 0.0 bad arcminutes ", 1 )
        self.assertRaises( ValueError, pal.dafin, " 45 -30 0.0 bad arcminutes ", 1 )
        self.assertRaises( ValueError, pal.dafin, " 45 72 0.0 too many arcminutes ", 1 )
        self.assertRaises( ValueError, pal.dafin, " 45 43 85.0 too many arcseconds ", 1 )


    def test_airmass(self):
        self.assertAlmostEqual( pal.airmas( 1.2354 ),
                                3.015698990074724, 11 );

    def test_amp(self):
        (rm, dm) = pal.amp( 2.345, -1.234, 50100., 1990. )
        self.assertAlmostEqual( rm, 2.344472180027961, 6 )
        self.assertAlmostEqual( dm, -1.233573099847705, 7 )
        (rm, dm ) = pal.amp( 1.234, -0.567, 55927., 2010. )
        self.assertAlmostEqual( rm, 1.2335120411026936349, 12 )
        self.assertAlmostEqual( dm, -0.56702908706930343907, 12 )

    def test_ampqk(self):
        amprms = pal.mappa( 2010.0, 55927.0 )
        (rm, dm) = pal.ampqk( 1.234, -0.567, amprms )
        self.assertAlmostEqual( rm, 1.2335120411026936349, 11 )
        self.assertAlmostEqual( dm, -0.56702908706930343907, 11 )

    def test_aop(self):
        dap = -0.1234
        date = 51000.1
        dut = 25.0
        elongm = 2.1
        phim = 0.5
        hm = 3000.0
        xp = -0.5e-6
        yp = 1.0e-6
        tdk = 280.0
        pmb = 550.0
        rh = 0.6
        tlr = 0.006

        aopres = [
            [
                1.812817787123283034,
                1.393860816635714034,
                -1.297808009092456683,
                -0.122967060534561,
                2.699270287872084
                ],
                [
                    2.019928026670621442,
                    1.101316172427482466,
                    -0.9432923558497740862,
                    -0.1232144708194224,
                    2.344754634629428
                    ],
        [
            2.019928026670621442,
            1.101267532198003760,
            -0.9432533138143315937,
            -0.1231850665614878,
            2.344715592593984
            ]
        ]
        aoptol = [ [ 10, 7, 7, 8, 7 ],
                   [ 10, 10, 10, 10, 10],
                   [ 10, 10, 10, 10, 10]
                   ]

        for i in range(len(aopres)):
            # Not very pythonic
            if i == 0:
                rap = 2.7
                wl = 0.45
            elif i==1:
                rap = 2.345
            else:
                wl = 1.0e6

            result = pal.aop( rap, dap, date, dut, elongm, phim, hm, xp, yp,
                              tdk, pmb, rh, wl, tlr )

            for j in range(len(result)):
                self.assertAlmostEqual( result[j], aopres[i][j], aoptol[i][j] )

        date = 48000.3
        wl = 0.45

        aoprms = pal.aoppa( date, dut, elongm, phim, hm, xp, yp, tdk, pmb,
                            rh, wl, tlr )

        aoppares = [ 0.4999993892136306,  0.4794250025886467,  0.8775828547167932,
                     1.363180872136126e-6, 3000., 280., 550., 0.6, 0.45, 0.006,
                     0.0001562803328459898, -1.792293660141e-7, 2.101874231495843,
                     7.601916802079765 ]
        aoppatol = [ 13, 13, 13, 13, 10, 11, 11, 13, 13, 15, 13, 13, 12, 8]
        self.assertEqual( len(aoprms), len(aoppares) )
        for i in range(len(aoprms)):
            self.assertAlmostEqual( aoprms[i], aoppares[i], aoppatol[i] )

        (rap, dap) = pal.oap( "r", 1.6, -1.01, date, dut, elongm, phim,
                              hm, xp, yp, tdk, pmb, rh, wl, tlr )
        self.assertAlmostEqual( rap, 1.601197569844787, 10 )
        self.assertAlmostEqual( dap, -1.012528566544262, 10 )

        (rap, dap) = pal.oap( "h", -1.234, 2.34, date, dut, elongm, phim,
                              hm, xp, yp, tdk, pmb, rh, wl, tlr )
        self.assertAlmostEqual( rap, 5.693087688154886463, 10 )
        self.assertAlmostEqual( dap, 0.8010281167405444, 10 )

        (rap, dap) = pal.oap( "a", 6.1, 1.1, date, dut, elongm, phim,
                              hm, xp, yp, tdk, pmb, rh, wl, tlr )
        self.assertAlmostEqual( rap, 5.894305175192448940, 10 )
        self.assertAlmostEqual( dap, 1.406150707974922, 10 )

        (rap, dap) = pal.oapqk( "r", 2.1, -0.345, aoprms )
        self.assertAlmostEqual( rap, 2.10023962776202, 10 )
        self.assertAlmostEqual( dap, -0.3452428692888919, 10 )

        (rap, dap) = pal.oapqk( "h", -0.01, 1.03, aoprms )
        self.assertAlmostEqual( rap, 1.328731933634564995, 10 )
        self.assertAlmostEqual( dap, 1.030091538647746, 10 )

        (rap, dap) = pal.oapqk( "a", 4.321, 0.987, aoprms )
        self.assertAlmostEqual( rap, 0.4375507112075065923, 10 )
        self.assertAlmostEqual( dap, -0.01520898480744436, 10 )

        aoprms = pal.aoppat( date + pal.DS2R, aoprms )
        self.assertAlmostEqual( aoprms[13], 7.602374979243502, 8 )

    def test_bear(self):
        a1 = 1.234
        b1 = -0.123
        a2 = 2.345
        b2 = 0.789
        self.assertAlmostEqual( pal.dbear( a1, b1, a2, b2),
                                0.7045970341781791, 12 )
        d1 = pal.dcs2c( a1, b1 )
        d2 = pal.dcs2c( a2, b2 )
        self.assertAlmostEqual( pal.dpav( d1, d2 ), 0.7045970341781791, 12 )

    def test_caldj(self):
        djm = pal.caldj( 1999, 12, 31 )
        self.assertEqual( djm, 51543 )

        self.assertRaises( ValueError, pal.caldj, -5000, 12, 31 )
        self.assertRaises( ValueError, pal.caldj, 1970, 13, 1 )
        self.assertRaises( ValueError, pal.caldj, 1970, 1, 32 )

    def test_caf2r(self):
        dr = pal.daf2r( 76, 54, 32.1 )
        self.assertAlmostEqual( dr, 1.342313819975276, 12 )

    def test_cc2s(self):
        (da, db) = pal.dcc2s( np.array( [100., -50., 25. ] ) )
        self.assertAlmostEqual( da, -0.4636476090008061, 12 )
        self.assertAlmostEqual( db, 0.2199879773954594, 12 )

    def test_cd2tf(self):
        ( sign, hours, minutes, seconds, fraction ) = pal.dd2tf( 4, -0.987654321 )
        self.assertEqual( sign, "-" )
        self.assertEqual( hours, 23 )
        self.assertEqual( minutes, 42 )
        self.assertEqual( seconds, 13 )
        self.assertEqual( fraction, 3333 )

    def test_cldj(self):
        d = pal.cldj( 1899, 12, 31 )
        self.assertEqual( d, 15019 )
        self.assertRaises( ValueError, pal.cldj, -5000, 12, 31 )
        self.assertRaises( ValueError, pal.cldj, 1970, 13, 1 )
        self.assertRaises( ValueError, pal.cldj, 1970, 1, 32 )

    def test_cr2af(self):
        (sign, deg, min, sec, f) = pal.dr2af( 4, 2.345 )
        self.assertEqual( sign, "+" )
        self.assertEqual( deg, 134 )
        self.assertEqual( min, 21 )
        self.assertEqual( sec, 30 )
        self.assertEqual( f, 9706 )

    def test_ctf2d(self):
        dd = pal.dtf2d( 23, 56, 59.1 )
        self.assertAlmostEqual( dd, 0.99790625, 12 )
        self.assertRaises( ValueError, pal.dtf2d, 24, 1, 32 )
        self.assertRaises( ValueError, pal.dtf2d, 23, -1, 32 )
        self.assertRaises( ValueError, pal.dtf2d, 23, 1, 60 )

    def test_ctf2r(self):
        dr = pal.dtf2r( 23, 56, 59.1 )
        self.assertAlmostEqual( dr, 6.270029887942679, 12 )
        self.assertRaises( ValueError, pal.dtf2r, 24, 1, 32 )
        self.assertRaises( ValueError, pal.dtf2r, 23, -1, 32 )
        self.assertRaises( ValueError, pal.dtf2r, 23, 1, 60 )

    def test_dat(self):
        self.assertEqual( pal.dat( 43900 ), 18 )
        self.assertAlmostEqual( pal.dtt( 40404 ), 39.709746, 12 )
        self.assertAlmostEqual( pal.dt( 500 ), 4686.7, 10 )
        self.assertAlmostEqual( pal.dt( 1400 ), 408, 11 )
        self.assertAlmostEqual( pal.dt( 1950 ), 27.99145626 )

    def test_djcal(self):
        djm = 50123.9999
        ( y, m, d, f ) = pal.djcal( 4, djm )
        self.assertEqual( y, 1996 )
        self.assertEqual( m, 2 )
        self.assertEqual( d, 10 )
        self.assertEqual( f, 9999 )

        ( y, m, d, f ) = pal.djcl( djm )
        self.assertEqual( y, 1996 )
        self.assertEqual( m, 2 )
        self.assertEqual( d, 10 )
        self.assertAlmostEqual( f, 0.9999, 7 )

    def test_dmat(self):
        da = np.array(
           [ [ 2.22,     1.6578,     1.380522 ],
            [  1.6578,   1.380522,   1.22548578 ],
            [  1.380522, 1.22548578, 1.1356276122 ] ]
        )
        dv = np.array( [ 2.28625, 1.7128825, 1.429432225 ] )
        (da, dv, dd) = pal.dmat( da, dv )
        self.assertAlmostEqual( dd, 0.003658344147359863, 12 )
        self.assertAlmostEqual( dv[0], 1.002346480763383, 12 )
        self.assertAlmostEqual( dv[1], 0.03285594016974583489, 12 )
        self.assertAlmostEqual( dv[2], 0.004760688414885247309, 12 )

        da = np.array( [ [ 0., 1. ], [ 0., 1. ] ] )
        dv = np.array( [ 1., 1. ] )
        self.assertRaises( ArithmeticError, pal.dmat, da, dv )

    def test_e2h(self):
        dp = -0.7
        hin = -0.3
        din = -1.1
        (da, de) = pal.de2h( hin, din, dp )
        self.assertAlmostEqual( da, 2.820087515852369, 12 )
        self.assertAlmostEqual( de, 1.132711866443304, 12 )

        (dh, dd) = pal.dh2e( da, de, dp )
        self.assertAlmostEqual( dh, hin, 12 )
        self.assertAlmostEqual( dd, din, 12 )

    def test_ecmat(self):
        expected = np.array( [
            [ 1.0,                    0.0,                   0.0 ],
            [ 0.0, 0.91749307789883549624, 0.3977517467060596168 ],
            [ 0.0, -0.3977517467060596168, 0.91749307789883549624 ] ] );

        rmat = pal.ecmat( 55966.46 )
        np.testing.assert_array_almost_equal( rmat, expected, decimal=12 )

    def test_epb(self):
        self.assertAlmostEqual( pal.epb( 45123 ), 1982.419793168669, 8)

    def test_epb2d(self):
        self.assertAlmostEqual( pal.epb2d(1975.5), 42595.5995279655, 7)

    def test_epco(self):
        self.assertAlmostEqual( pal.epco("B","J", 2000), 2000.001277513665, 7 )
        self.assertAlmostEqual( pal.epco("J","B", 1950), 1949.999790442300, 7 )
        self.assertAlmostEqual( pal.epco("J","j", 2000), 2000, 7 )

    def test_epj(self):
        self.assertAlmostEqual( pal.epj(42999), 1976.603696098563, 7)

    def test_epj2d(self):
        self.assertAlmostEqual( pal.epj2d(2010.077), 55225.124250, 6 )

    def test_eqecl(self):
        (dl, db) = pal.eqecl( 0.789, -0.123, 46555 )
        self.assertAlmostEqual( dl, 0.7036566430349022, 6 )
        self.assertAlmostEqual( db, -0.4036047164116848, 6 )

    def test_eqeqx(self):
        self.assertAlmostEqual( pal.eqeqx( 53736 ), -0.8834195072043790156e-5, 15 )

    def test_eqgal(self):
        (dl, db) = pal.eqgal( 5.67, -1.23 )
        self.assertAlmostEqual( dl, 5.612270780904526, 12 )
        self.assertAlmostEqual( db, -0.6800521449061520, 12 )

    def test_etrms(self):
        ev = pal.etrms( 1976.9 )
        self.assertAlmostEqual( ev[0], -1.621617102537041e-6, 18 )
        self.assertAlmostEqual( ev[1], -3.310070088507914e-7, 18 )
        self.assertAlmostEqual( ev[2], -1.435296627515719e-7, 18 )

    def test_evp(self):
        pass

    def test_fk45z(self):
        (r2000, d2000) = pal.fk45z( 1.2, -0.3, 1960 )
        self.assertAlmostEqual( r2000, 1.2097812228966762227, 11 )
        self.assertAlmostEqual( d2000, -0.29826111711331398935, 12 )

    def test_fk52h(self):
        inr5 = 1.234
        ind5 = -0.987
        epoch = 1980
        (rh, dh) = pal.fk5hz( inr5, ind5, epoch )
        self.assertAlmostEqual( rh, 1.234000136713611301, 13 )
        self.assertAlmostEqual( dh, -0.9869999702020807601, 13 )
        (r5, d5, dr5, dd5) = pal.hfk5z( rh, dh, epoch )
        self.assertAlmostEqual( r5, inr5, 13 )
        self.assertAlmostEqual( d5, ind5, 13 )
        self.assertAlmostEqual( dr5, 0.000000006822074, 13 )
        self.assertAlmostEqual( dd5, -0.000000002334012, 13 )

    def test_fk54z(self):
        (r1950, d1950, dr1950, dd1950) = pal.fk54z( 1.2, -0.3, 1960 )
        self.assertAlmostEqual( r1950, 1.1902221805755279771, 12 )
        self.assertAlmostEqual( d1950, -0.30178317645793828472, 12 )
        self.assertAlmostEqual( dr1950, -1.7830874775952945507e-08, 12 )
        self.assertAlmostEqual( dd1950, 7.196059425334821089e-09, 12 )

    def test_flotin(self):
        pass

    def test_galeq(self):
        (dr, dd) = pal.galeq( 5.67, -1.23 )
        self.assertAlmostEqual( dr, 0.04729270418071426, 12 )
        self.assertAlmostEqual( dd, -0.7834003666745548, 12 )

    def test_galsup(self):
        (dsl, dsb) = pal.galsup( 6.1, -1.4 )
        self.assertAlmostEqual( dsl, 4.567933268859171, 12 )
        self.assertAlmostEqual( dsb, -0.01862369899731829, 12 )

    def test_geoc(self):
        lat = 19.822838905884 * pal.DD2R
        alt = 4120.0
        (r, z) = pal.geoc( lat, alt )
        self.assertAlmostEqual( r, 4.01502667039618e-05, 10 )
        self.assertAlmostEqual( z, 1.43762411970295e-05, 10 )

    def test_ge50(self):
        (dr, dd) = pal.ge50( 6.1, -1.55 )
        self.assertAlmostEqual( dr, 0.1966825219934508, 12 )
        self.assertAlmostEqual( dd, -0.4924752701678960, 12 )

    def test_gmst(self):
        self.assertAlmostEqual( pal.gmst( 53736 ), 1.754174971870091203, 12 )
        self.assertAlmostEqual( pal.gmsta( 53736, 0 ), 1.754174971870091203, 12 )

    def test_intin(self):
        s = "  -12345, , -0  2000  +     "
        i = 1
        (n, i, sign) = pal.intin( s, i )
        self.assertEqual( i, 10 )
        self.assertEqual( n, -12345 )
        self.assertLess( sign, 0 )

        (n, i, sign) = pal.intin( s, i )
        self.assertEqual( i, 12 )
        self.assertIsNone( n )

        (n, i, sign) = pal.intin( s, i )
        self.assertEqual( i, 17 )
        self.assertEqual( n, 0 )
        self.assertLess( sign, 0 )

        (n, i, sign) = pal.intin( s, i )
        self.assertEqual( i, 23 )
        self.assertEqual( n, 2000 )
        self.assertGreater( sign, 0 )

        (n, i, sign) = pal.intin( s, i )
        self.assertEqual( i, 29 )
        self.assertIsNone( n )
        self.assertIsNone( sign )

    def test_map(self):
        (ra, da) = pal.map( 6.123, -0.999, 1.23e-5, -0.987e-5,
                            0.123, 32.1, 1999, 43210.9 )
        self.assertAlmostEqual( ra, 6.117130429775647, 6 )
        self.assertAlmostEqual( da, -1.000880769038632, 7 )

    def test_mappa(self):
        expected = np.array( [1.9986310746064646082,
                          -0.1728200754134739392,
                          0.88745394651412767839,
                          0.38472374350184274094,
                          -0.17245634725219796679,
                          0.90374808622520386159,
                          0.3917884696321610738,
                          2.0075929387510784968e-08,
                          -9.9464149073251757597e-05,
                          -1.6125306981057062306e-05,
                          -6.9897255793245634435e-06,
                          0.99999999489900059935,
                          0.99999983777998024959,
                          -0.00052248206600935195865,
                          -0.00022683144398381763045,
                          0.00052248547063364874764,
                          0.99999986339269864022,
                          1.4950491424992534218e-05,
                          0.00022682360163333854623,
                          -1.5069005133483779417e-05,
                          0.99999997416198904698 ] )
        amprms = pal.mappa( 2010.0, 55927 )
        np.testing.assert_array_almost_equal( amprms, expected, decimal=12 )

    def test_mapqkz(self):
        amprms = pal.mappa( 2010, 55927 )
        (ra, da) = pal.mapqkz( 1.234, -0.567, amprms )
        self.assertAlmostEqual( ra, 1.2344879748414849807, 12 )
        self.assertAlmostEqual( da, -0.56697099554368701746, 12 )

        (ra, da) = pal.mapqk( 1.234, -0.567, 0., 0., 0., 0., amprms )
        self.assertAlmostEqual( ra, 1.2344879748414849807, 7 )
        self.assertAlmostEqual( da, -0.56697099554368701746, 7 )

    def test_moon(self):
        expected = np.array( [
             0.00229161514616454,
             0.000973912029208393,
             0.000669931538978146,
             -3.44709700068209e-09,
             5.44477533462392e-09,
             2.11785724844417e-09
             ] )
        pv = pal.dmoon( 48634.4687174074 )
        np.testing.assert_array_almost_equal( pv, expected, decimal=12 )

    def test_nut(self):
        expected = np.array( [
            [  9.999999969492166e-1, 7.166577986249302e-5,  3.107382973077677e-5 ],
            [ -7.166503970900504e-5, 9.999999971483732e-1, -2.381965032461830e-5 ],
            [ -3.107553669598237e-5, 2.381742334472628e-5,  9.999999992335206818e-1 ]
        ] )

        rmatn = pal.nut( 46012.32 )
        np.testing.assert_array_almost_equal( rmatn, expected, 3 )

        (dpsi, deps, eps0) = pal.nutc( 54388.0 )
        self.assertAlmostEqual( eps0, 0.4090749229387258204, 14 )

        (dpsi, deps, eps0) = pal.nutc( 53736.0 )
        self.assertAlmostEqual( dpsi, -0.9630912025820308797e-5, 13 )
        self.assertAlmostEqual( deps, 0.4063238496887249798e-4, 13 )

    def test_obs(self):
        obsdata = pal.obs()
        mmt = obsdata["MMT"]
        self.assertEqual( mmt["name"], "MMT 6.5m, Mt Hopkins" )
        self.assertAlmostEqual( mmt["long"], 1.935300584055477, 8 )
        self.assertAlmostEqual( mmt["lat"], 0.5530735081550342238, 10 )
        self.assertAlmostEqual( mmt["height"], 2608, 10 )

        self.assertEqual( len(obsdata), 83 )

    def test_pa(self):
        self.assertAlmostEqual( pal.pa( -1.567, 1.5123, 0.987 ),
                                -1.486288540423851, 12 )
        self.assertAlmostEqual( pal.pa( 0, 0.789, 0.789 ), 0, 12 )

    def test_planet(self):
        pass

    def test_pm(self):
        (ra, dec) = pal.pm( 5.43, -0.87, -0.33e-5, 0.77e-5, 0.7,
                              50.3*365.2422/365.25, 1899, 1943 )
        self.assertAlmostEqual( ra, 5.429855087793875, 10 )
        self.assertAlmostEqual( dec, -0.8696617307805072, 10 )

        (ra, dec) = pal.pm( 0.01686756, -1.093989828, -1.78323516e-5,
                            2.336024047e-6, 0.74723, -21.6,
                            pal.epj( 50083.0 ), pal.epj( 53736.0 ) )
        self.assertAlmostEqual( ra, 0.01668919069414242368, 13 )
        self.assertAlmostEqual( dec, -1.093966454217127879, 13 )

    def test_prebn(self):
        expected = np.array( [
            [ 9.999257613786738e-1, -1.117444640880939e-2, -4.858341150654265e-3 ],
            [ 1.117444639746558e-2,  9.999375635561940e-1, -2.714797892626396e-5 ],
            [ 4.858341176745641e-3, -2.714330927085065e-5,  9.999881978224798e-1 ]
        ] )
        rmatp = pal.prebn( 1925, 1975 )
        np.testing.assert_array_almost_equal( rmatp, expected, 12 )

    def test_prec(self):
        expected = np.array( [
            [ 0.9999856154510, -0.0049192906204,    -0.0021376320580 ],
            [  0.0049192906805,  0.9999879002027,    -5.2297405698747e-06 ],
            [ 0.0021376319197, -5.2859681191735e-06, 0.9999977152483 ] ] )
        rmat = pal.prec( 1990, 2012 )
        np.testing.assert_array_almost_equal( rmat, expected, 12 )

    def test_preces(self):
        (ra, dc) = pal.preces( "FK4", 1925, 1950, 6.28, -1.123 )
        self.assertAlmostEqual( ra, 0.002403604864728447, 12 )
        self.assertAlmostEqual( dc, -1.120570643322045, 12 )

        (ra, dec) = pal.preces( "FK5", 2050, 1990, 0.0123, 1.0987 )
        self.assertAlmostEqual( ra, 6.282003602708382, 5 )
        self.assertAlmostEqual( dc, -1.120570643322045, 6 )

    def test_pvobs(self):
        expected = np.array( [ -4.7683600138836167813e-06,
                           1.0419056712717953176e-05,
                           4.099831053320363277e-05,
                          -7.5976959740661272483e-10,
                          -3.4771429582640930371e-10,
                           0.0 ] )
        pv = pal.pvobs( 1.3, 10000, 2 )
        np.testing.assert_array_almost_equal( pv, expected, decimal=12 )

    def test_range(self):
        self.assertAlmostEqual( pal.drange( -4 ), 2.283185307179586, 12 )

    def test_ranorm(self):
        self.assertAlmostEqual( pal.dranrm( -0.1 ), 6.183185307179587, 12 )

    def test_rv(self):
        self.assertAlmostEqual( pal.rverot( -0.777, 5.67, -0.3, 3.19 ),
                                 -0.1948098355075913, 6 )
        self.assertAlmostEqual( pal.rvgalc( 1.11, -0.99 ),
                                158.9630759840254, 3 )
        self.assertAlmostEqual( pal.rvlg( 3.97, 1.09 ),
                                -197.818762175363, 3 )
        self.assertAlmostEqual( pal.rvlsrd( 6.01, 0.1 ),
                                -4.082811335150567, 4 )
        self.assertAlmostEqual( pal.rvlsrk( 6.01, 0.1 ),
                                -5.925180579830265, 4 )

    def test_rvgalc(self):
        self.assertAlmostEqual( pal.rvgalc(2.7, -1.0), 213.98084425751144977, 12 )

    def test_rvlg(self):
        self.assertAlmostEqual( pal.rvlg(2.7, -1.0), 291.79205281252404802, 12 )

    def test_rvlsrd(self):
        self.assertAlmostEqual( pal.rvlsrd(2.7, -1.0), 9.620674692097630043, 12 )

    def test_rvlsrk(self):
        self.assertAlmostEqual( pal.rvlsrk(2.7, -1.0), 12.556356851411955233, 12 )

    def test_sep(self):
        d1 = np.array( [ 1.0, 0.1, 0.2 ] )
        d2 = np.array( [ -3.0, 1e-3, 0.2 ] )
        (ad1, bd1) = pal.dcc2s( d1 )
        (ad2, bd2) = pal.dcc2s( d2 )

        self.assertAlmostEqual( pal.dsep( ad1, bd1, ad2, bd2 ),
                                2.8603919190246608, 7 )
        self.assertAlmostEqual( pal.dsepv( d1, d2 ),
                                2.8603919190246608, 7 )

    def test_supgal(self):
        (dl, db) = pal.supgal( 6.1, -1.4 )
        self.assertAlmostEqual( dl, 3.798775860769474, 12 )
        self.assertAlmostEqual( db,  -0.1397070490669407, 12 )

    def test_tp(self):
        dr0 = 3.1
        dd0 = -0.9
        dr1 = dr0 + 0.2
        dd1 = dd0 - 0.1
        (dx, dy) = pal.ds2tp( dr1, dd1, dr0, dd0 )
        self.assertAlmostEqual( dx, 0.1086112301590404, 12 )
        self.assertAlmostEqual( dy, -0.1095506200711452, 12 )

        (dr2, dd2) = pal.dtp2s( dx, dy, dr0, dd0 )
        self.assertAlmostEqual( dr2 - dr1, 0.0, 12 )
        self.assertAlmostEqual( dd2 - dd1, 0.0, 12 )

        (dr01, dd01, dr02, dd02) = pal.dtps2c( dx, dy, dr2, dd2 )
        self.assertAlmostEqual( dr01, dr0, 12 )
        self.assertAlmostEqual( dd01, dd0 )
        self.assertIsNone( dr02 )
        self.assertIsNone( dd02 )

    def test_vecmat(self):
        pass


if __name__ == '__main__':
    unittest.main()
