
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

cimport cpal

from libc.stdlib cimport malloc, free

cimport numpy as np
import numpy as np

DS2R = cpal.PAL__DS2R
DPI = cpal.PAL__DPI
DD2R = cpal.PAL__DD2R

def addet( double rm, double dm, double eq ):
     cdef double rc
     cdef double dc
     cpal.palAddet( rm, dm, eq, &rc, &dc )
     return ( rc, dc )

def airmas( double zd ):
     return cpal.palAirmas( zd )

def amp( double ra, double da, double date, double eq):
     cdef double rm
     cdef double dm
     cpal.palAmp( ra, da, date, eq, &rm, &dm )
     return ( rm, dm )

def ampqk( double ra, double da, np.ndarray[double, ndim=1] amprms not None ):
     cdef double rm
     cdef double dm
     cdef double camprms[21]
     for i in range(21):
          camprms[i] = amprms[i]
     cpal.palAmpqk( ra, da, camprms, &rm, &dm )
     return (rm, dm)

def aop( double rap, double dap, double date, double dut,
         double elongm, double phim, double hm, double xp,
         double yp, double tdk, double pmb, double rh,
         double wl, double tlr ):
     cdef double aob
     cdef double zob
     cdef double hob
     cdef double dob
     cdef double rob
     cpal.palAop( rap, dap, date, dut, elongm, phim, hm,
                  xp, yp, tdk, pmb, rh, wl, tlr,
                  &aob, &zob, &hob, &dob, &rob)
     return (aob, zob, hob, dob, rob )

def aoppa(double date, double dut, double elongm, double phim,
          double hm, double xp, double yp, double tdk, double pmb,
          double rh, double wl, double tlr ):
     cdef double caoprms[14]
     cdef np.ndarray aoprms = np.zeros( [14], dtype=np.float64 )
     cpal.palAoppa( date, dut, elongm, phim, hm, xp, yp, tdk, pmb,
                    rh, wl, tlr, caoprms )
     for i in range(14):
          aoprms[i] = caoprms[i]
     return aoprms

def aoppat( double date, np.ndarray[double, ndim=1] aoprms not None ):
     # We can either copy the array or modify in place.
     # For now we return a new copy
     cdef double caoprms[14]
     for i in range(14):
          caoprms[i] = aoprms[i]
     cpal.palAoppat( date, caoprms )
     cdef np.ndarray result = np.zeros( [14], dtype=np.float64 )
     for i in range(14):
          result[i] = caoprms[i]
     return result

def caldj( int iy, int im, int id ):
     cdef double djm
     cdef int j
     cpal.palCaldj( iy, im, id, &djm, &j )
     if j==0:
          return djm
     else:
          bad = ""
          if j==-1:
               bad = "year"
          elif j==-2:
               bad = "month"
          else:
               bad = "day"
          raise ValueError( "Julian date not computed. Bad {}".format(bad) )

def cldj( int iy, int im, int id ):
     cdef int j
     cdef double djm
     cpal.palCldj( iy, im, id, &djm, &j )
     if j==0:
          return djm
     else:
          bad = ""
          if j==-1:
               bad = "year"
          elif j==-2:
               bad = "month"
          else:
               bad = "day"
          raise ValueError( "Bad {} argument".format(bad) )

def dafin( string, int ipos ):
     """
     Decode a sexagesimal string into an angle.

       (angle, endpos) = pal.dafin( string, startpos )

     where string is the string to be analyzed, startpos
     is the position in the string to start looking
     (starts at 1), endpos is the position in the string
     after the search and angle is the decoded angle in
     radians.

     A ValueError exception is thrown if no angle can
     be found.

     A ValueError exception is thrown if an angle can
     be located but is numerically out of range.

     The interface for this routine is experimental. In
     particular the startpos and endpos variables need
     some thought. startpos could simply be ignored
     as a python slice would work just as well. endpos
     is useful in that you know where to slice the string
     to continue searching for angles. Zero- versus one-
     based indexing is an issue.
     """
     byte_string = string.encode('ascii')
     cdef char * cstring = byte_string
     cdef int cipos = ipos
     cdef double a
     cdef int j
     cpal.palDafin( cstring, &cipos, &a, &j )
     if j==0:
          return ( a, cipos )
     elif j==1:
          raise ValueError( "No angle could be located in string '{}'".format(string) )
     else:
          bad = "unknown"
          if j==-1:
               bad = "degrees"
          elif j==-2:
               bad = "arcminutes"
          elif j==-3:
               bad = "arcseconds"
          raise ValueError( "Bad {} in input string".format(bad) )

def dat( double dju ):
     return cpal.palDat( dju )

def dbear( double a1, double b1, double a2, double b2 ):
     return cpal.palDbear( a1, b1, a2, b2 )

def daf2r( int ideg, int iamin, double asec ):
     cdef double rad
     cdef int j
     cpal.palDaf2r( ideg, iamin, asec, &rad, &j )
     if j==0:
          return rad
     else:
          bad = ""
          if j==1:
               bad = "Degree argument outside range 0-369"
          elif j==2:
               bad = "Minute argument outside range 0-59"
          else:
               bad = "Arcsec argument outside range 0-59.9999..."
          raise ValueError( bad )

def dcc2s( np.ndarray[double, ndim=1] v not None ):
     cdef double cv[3]
     for i in range(3):
          cv[i] = v[i]
     cdef double a
     cdef double b
     cpal.palDcc2s( cv, &a, &b )
     return (a, b)

def dcs2c( double a, double b ):
     cdef double cv[3]
     cpal.palDcs2c( a, b, cv )
     cdef np.ndarray v = np.zeros( [3], dtype=np.float64 )
     for i in range(3):
          v[i] = cv[i]
     return v

def dd2tf( int ndp, double days ):
     cdef char * csign = " "
     cdef int ihmsf[4]
     cpal.palDd2tf( ndp, days, csign, ihmsf )
     sign = csign.decode('UTF-8')
     return ( sign, ihmsf[0], ihmsf[1], ihmsf[2], ihmsf[3] )

def djcal( int ndp, double djm ):
     cdef int iymdf[4]
     cdef int j
     cpal.palDjcal( ndp, djm, iymdf, &j )
     if j==0:
          return ( iymdf[0], iymdf[1], iymdf[2], iymdf[3] )
     else:
          raise ValueError( "Unacceptable date" )

def djcl( double djm ):
     cdef int iy
     cdef int im
     cdef int id
     cdef double fd
     cdef int j
     cpal.palDjcl( djm, &iy, &im, &id, &fd, &j )
     if j==0:
          return ( iy, im, id, fd )
     else:
          raise ValueError( "Unacceptable date" )

def dmat( np.ndarray[double, ndim=2] a not None,
          np.ndarray[double, ndim=1] y not None ):
     # validate the arguments and get the dimension
     ashape = a.shape
     yshape = y.shape
     if ashape[0] != ashape[1]:
          raise ValueError( "Matrix must be square" )
     if yshape[0] != ashape[0]:
          raise ValueError( "Matrix must match number of elements in supplied vector" )

     cdef int n = y.size
     cdef int j
     cdef double d
     cdef int *iw = <int *>malloc( n * sizeof(int) )
     cdef double *ca = <double *>malloc( n * n * sizeof(double))
     cdef double *cy = <double *>malloc( n * sizeof(double))

     if not ca or not iw or not cy:
          if ca:
               free(ca)
          if iw:
               free(iw)
          if cy:
               free(cy)
          raise MemoryError( "Could not get dynamic memory for matrix" )

     # Need to flatten the input 2d matrix
     k = 0;
     for i in range(n):
          cy[i] = y[i]
          for j in range(n):
               ca[k] = a[ i, j ]
               k = k + 1

     cpal.palDmat( n, ca, cy, &d, &j, iw )
     free(iw)

     cdef np.ndarray na = np.zeros( [n,n], dtype=np.float64 )
     cdef np.ndarray ny = np.zeros( [n], dtype=np.float64 )

     if j==0:
          k = 0
          for i in range(n):
               ny[i] = cy[i]
               for j in range(n):
                    na[i,j] = ca[k]
                    k = k + 1
          free(ca)
          free(cy)
          return ( na, ny, d )
     else:
          free(ca)
          free(cy)
          raise ArithmeticError( "Matrix is singular" )

def de2h( double ha, double dec, double phi ):
     cdef double az
     cdef double el
     cpal.palDe2h( ha, dec, phi, &az, &el )
     return (az, el)

def dh2e( double az, double el, double phi ):
     cdef double ha
     cdef double dec
     cpal.palDh2e( az, el, phi, &ha, &dec )
     return (ha, dec)

def dmoon( double date ):
     cdef double cpv[6]
     cpal.palDmoon( date, cpv )
     cdef np.ndarray pv = np.zeros( [6], dtype=np.float64 )
     for i in range(6):
          pv[i] = cpv[i]
     return pv

def dpav( np.ndarray[double, ndim=1] v1 not None, np.ndarray[double, ndim=1] v2 not None ):
     cdef double cv1[3]
     cdef double cv2[3]
     cdef double result
     for i in range(3):
          cv1[i] = v1[i]
          cv2[i] = v2[i]
     result = cpal.palDpav( cv1, cv2 )
     return result

def dr2af( int ndp, double days ):
     cdef char * csign = " "
     cdef int idmsf[4]
     cpal.palDr2af( ndp, days, csign, idmsf )
     sign = csign.decode('UTF-8')
     return ( sign, idmsf[0], idmsf[1], idmsf[2], idmsf[3] )

def drange( double angle ):
     return cpal.palDrange( angle )

def dranrm( double angle ):
     return cpal.palDranrm( angle )

def ds2tp( double ra, double dec, double raz, double decz ):
     cdef double xi
     cdef double eta
     cdef int j
     cpal.palDs2tp( ra, dec, raz, decz, &xi, &eta, &j )
     if j==0:
          return (xi, eta)
     elif j==1:
          raise ValueError( "Star too far from axis" )
     elif j==2:
          raise ValueError( "Antistar on tangent plane" )
     else:
          raise ValueError( "Antistart too far from axis" )

def dsep( double a1, double b1, double a2, double b2 ):
     return cpal.palDsep( a1, b1, a2, b2 )

def dsepv( np.ndarray[double, ndim=1] v1 not None, np.ndarray[double, ndim=1] v2 not None ):
     cdef double cv1[3]
     cdef double cv2[3]
     cdef double result
     for i in range(3):
          cv1[i] = v1[i]
          cv2[i] = v2[i]
     result = cpal.palDsepv( cv1, cv2 )
     return result

def dtf2d( int ihour, int imin, double sec ):
     cdef double days
     cdef int j
     cpal.palDtf2d( ihour, imin, sec, &days, &j )
     if j==0:
          return days
     else:
          bad = ""
          if j==1:
               bad = "Degree argument outside range 0-369"
          elif j==2:
               bad = "Minute argument outside range 0-59"
          else:
               bad = "Arcsec argument outside range 0-59.9999..."
          raise ValueError( bad )

def dtf2r( int ihour, int imin, double sec ):
     cdef double rad
     cdef int j
     cpal.palDtf2r( ihour, imin, sec, &rad, &j )
     if j==0:
          return rad
     else:
          bad = ""
          if j==1:
               bad = "Degree argument outside range 0-369"
          elif j==2:
               bad = "Minute argument outside range 0-59"
          else:
               bad = "Arcsec argument outside range 0-59.9999..."
          raise ValueError( bad )

def dtp2s( double xi, double eta, double raz, double decz):
     cdef double ra
     cdef double dec
     cpal.palDtp2s( xi, eta, raz, decz, &ra, &dec )
     return (ra,dec)

def dtps2c( double xi, double eta, double ra, double dec ):
     cdef double raz1
     cdef double decz1
     cdef double raz2
     cdef double decz2
     cdef int n
     cpal.palDtps2c( xi, eta, ra, dec, &raz1, &decz1, &raz2, &decz2, &n )
     if n==0:
          return (None, None, None, None)
     elif n==1:
          return (raz1, decz1, None, None)
     else:
          return (raz1, decz1, raz2, decz2 )

def dt( double epoch ):
     return cpal.palDt( epoch )

def dtt( double dju ):
     return cpal.palDtt( dju )

def ecmat( double date ):
     cdef double crmat[3][3]
     cpal.palEcmat( date, crmat )
     cdef np.ndarray rmat = np.zeros( [3,3], dtype=np.float64 )
     for i in range(3):
          for j in range(3):
               rmat[i,j] = crmat[i][j]
     return rmat

def epb( double date ):
     return cpal.palEpb(date)

def epb2d( double epb ):
     return cpal.palEpb2d(epb)

def epco( k0, k, double e ):
     k0_bytes = k0.encode('ascii')
     k_bytes = k.encode('ascii')
     cdef char * ck0 = k0_bytes
     cdef char * ck = k_bytes
     return cpal.palEpco( ck0[0], ck[0], e )

def epj( double date ):
     return cpal.palEpj(date)

def epj2d( double epj ):
     return cpal.palEpj2d(epj)

def eqecl( double dr, double dd, double date ):
     cdef double dl
     cdef double db
     cpal.palEqecl( dr, dd, date, &dl, &db )
     return (dl, db)

def eqeqx( double date ):
     return cpal.palEqeqx( date )

def eqgal( double dr, double dd ):
     cdef double dl
     cdef double db
     cpal.palEqgal( dr, dd, &dl, &dd )
     return (dl, dd)

def etrms( double ep ):
     cdef double cev[3]
     cpal.palEtrms( ep, cev )
     cdef np.ndarray ev = np.zeros( [3], dtype=np.float64 )
     for i in range(3):
          ev[i] = cev[i]
     return ev

def fk45z( double r1950, double d1950, double bepoch ):
     cdef double r2000
     cdef double d2000
     cpal.palFk45z( r1950, d1950, bepoch, &r2000, &d2000 )
     return (r2000, d2000)

def fk524( double r2000, double d2000, double dr2000,
           double dd2000, double p2000, double v2000 ):
     cdef double r1950
     cdef double d1950
     cdef double dr1950
     cdef double dd1950
     cdef double p1950
     cdef double v1950
     cpal.palFk524( r2000, d2000, dr2000, dd2000, p2000, v2000,
                    &r1950, &d1950, &dr1950, &dd1950,
                    &p1950, &v1950 )
     return (r1950, d1950, dr1950, dd1950, p1950, v1950 )

def fk5hz( double r5, double d5, double epoch):
     cdef double rh
     cdef double dh
     cpal.palFk5hz( r5, d5, epoch, &rh, &dh )
     return (rh, dh)

def fk54z(double r2000, double d2000, double bepoch):
     cdef double r1950
     cdef double d1950
     cdef double dr1950
     cdef double dd1950
     cpal.palFk54z( r2000, d2000, bepoch, &r1950, &d1950,
                    &dr1950, &dd1950 )
     return (r1950, d1950, dr1950, dd1950 )

def galeq( double dl, double db ):
     cdef double dr
     cdef double dd
     cpal.palGaleq( dl, db, &dr, &dd )
     return (dr, dd)

def galsup( double dl, double db ):
     cdef double dsl
     cdef double dsb
     cpal.palGalsup( dl, db, &dsl, &dsb )
     return (dsl, dsb)

def ge50( double dl, double db ):
     cdef double dr
     cdef double dd
     cpal.palGe50( dl, db, &dr, &dd )
     return (dr, dd)

def geoc( double p, double h ):
     cdef double r
     cdef double z
     cpal.palGeoc( p, h, &r, &z )
     return (r, z)

def gmst( double ut1 ):
     return cpal.palGmst( ut1 )

def gmsta( double date, double ut1 ):
     return cpal.palGmsta( date, ut1 )

def hfk5z( double rh, double dh, double epoch ):
     cdef double r5
     cdef double d5
     cdef double dr5
     cdef double dd5
     cpal.palHfk5z( rh, dh, epoch, &r5, &d5, &dr5, &dd5 )
     return (r5, d5, dr5, dd5)

# We need to return the sign in order to work out whether -0
# is a negative integer (important when parsing "-0 22 33.0"
# sexagesimal format. I'm assuming that no-one is going to really
# use the intin() function.
# We also need to handle overflow. If we raise an exception on
# overflow we can't continue to traverse the string so we have
# to return the position to continue but then document the
# magic value of LONG_MAX and LONG_MIN somehow but where would
# that go? For now raise an exception.
def intin( string, int nstrt ):
     cdef long ireslt
     cdef int j
     string_bytes = string.encode('ascii')
     cdef char * cstring = string_bytes
     cpal.palIntin( cstring, &nstrt, &ireslt, &j)
     sign = 0
     if j==0:
          sign = 1
     elif j==-1:
          sign = -1
     elif j==1:
          return (None, nstrt, None)
     else:
          raise OverflowError( "Integer too large for pal.intin() function" )
     return ( ireslt, nstrt, sign )

def map(double rm, double dm, double pr, double pd, double px, double rv, double eq, double date ):
     cdef double ra
     cdef double da
     cpal.palMap( rm, dm, pr, pd, px, rv, eq, date, &ra, &da )
     return (ra, da)

def mappa( double eq, double date ):
     cdef double camprms[21]
     cdef np.ndarray amprms = np.zeros( [21], dtype=np.float64 )
     cpal.palMappa( eq, date, camprms )
     for i in range(21):
          amprms[i] = camprms[i]
     return amprms

def mapqk( double rm, double dm, double pr, double pd, double px, double rv, np.ndarray[double, ndim=1] amprms not None):
     cdef double ra
     cdef double da
     cdef double camprms[21]
     for i in range(21):
          camprms[i] = amprms[i]
     cpal.palMapqk( rm, dm, pr, pd, px, rv, camprms, &ra, &da )
     return (ra, da)

def mapqkz( double rm, double dm, np.ndarray[double, ndim=1] amprms not None):
     cdef double ra
     cdef double da
     cdef double camprms[21]
     for i in range(21):
          camprms[i] = amprms[i]
     cpal.palMapqkz( rm, dm, camprms, &ra, &da )
     return (ra, da)


def nut( double date ):
     cdef double crmatn[3][3]
     cpal.palNut( date, crmatn )
     cdef np.ndarray rmatn = np.zeros( [3,3], dtype=np.float64 )
     for i in range(3):
          for j in range(3):
               rmatn[i,j] = crmatn[i][j]
     return rmatn

def nutc( double date):
     cdef double dpsi
     cdef double deps
     cdef double eps0
     cpal.palNutc( date, &dpsi, &deps, &eps0 )
     return (dpsi, deps, eps0)

# Numeric lookup is only useful when scanning through the
# list of telescopes. The python interface does not need this.
# Instead obs() returns a dict (which may be a bit less efficient
# than an iterable but it's easy) with a dict inside. No arguments.
def obs():
     cdef int n = 1
     cdef char c
     cdef char cident[11]
     cdef char cname[41]
     cdef double w
     cdef double p
     cdef double h
     cdef int retval = 0

     result = {}

     while True:
          retval = cpal.palObs( n, &c, cident, 11, cname, 41,
                                &w, &p, &h )
          n=n+1 # Next telescope

          if retval != 0:
               break
          newtel = { 'name': cname.decode('UTF-8'),
                     'long': w,
                     'lat': p,
                     'height': h }
          result[cident.decode('UTF-8')] = newtel

     return result

def oap( type, double ob1, double ob2, double date,
         double dut, double elongm, double phim, double hm,
         double xp, double yp, double tdk, double pmb,
         double rh, double wl, double tlr ):
     cdef double rap
     cdef double dap
     byte_string = type.encode('ascii')
     cdef char * ctype = byte_string
     cpal.palOap( ctype, ob1, ob2, date, dut, elongm, phim,
                  hm, xp, yp, tdk, pmb, rh, wl, tlr, &rap, &dap )
     return ( rap, dap )

def oapqk( type, double ob1, double ob2, np.ndarray[double, ndim=1] aoprms not None ):
     cdef double rap
     cdef double dap
     byte_string = type.encode('ascii')
     cdef char * ctype = byte_string
     cdef double caoprms[14]
     for i in range(14):
          caoprms[i] = aoprms[i]
     cpal.palOapqk( ctype, ob1, ob2, caoprms, &rap, &dap )
     return ( rap, dap )

def pa( double ha, double dec, double phi):
     return cpal.palPa( ha, dec, phi )

def pm( double r0, double d0, double pr, double pd,
        double px, double rv, double ep0, double ep1 ):
     cdef double r1
     cdef double d1
     cpal.palPm( r0, d0, pr, pd, px, rv, ep0, ep1, &r1, &d1 )
     return (r1, d1)

def prebn( double bep0, double bep1 ):
     cdef double crmatp[3][3]
     cpal.palPrebn( bep0, bep1, crmatp )
     cdef np.ndarray rmatp = np.zeros( [3,3], dtype=np.float64 )
     for i in range(3):
          for j in range(3):
               rmatp[i,j] = crmatp[i][j]
     return rmatp

def prec( double ep0, double ep1 ):
     cdef double crmatp[3][3]
     cpal.palPrec( ep0, ep1, crmatp )
     cdef np.ndarray rmatp = np.zeros( [3,3], dtype=np.float64 )
     for i in range(3):
          for j in range(3):
               rmatp[i,j] = crmatp[i][j]
     return rmatp

def preces( sys, double ep0, double ep1, double ra, double dc ):
     byte_string = sys.encode('ascii')
     cdef char * csys = byte_string
     cpal.palPreces( csys, ep0, ep1, &ra, &dc )
     return (ra, dc)

def pvobs( double p, double h, double stl ):
     cdef double cpv[6]
     cpal.palPvobs( p, h, stl, cpv )
     cdef np.ndarray pv = np.zeros( [6], dtype=np.float64 )
     for i in range(6):
          pv[i] = cpv[i]
     return pv

def rverot( double phi, double ra, double da, double st ):
     return cpal.palRverot( phi, ra, da, st )

def rvgalc( double r2000, double d2000 ):
     return cpal.palRvgalc( r2000, d2000 )

def rvlg( double r2000, double d2000 ):
     return cpal.palRvlg( r2000, d2000 )

def rvlsrd( double r2000, double d2000 ):
     return cpal.palRvlsrd( r2000, d2000 )

def rvlsrk( double r2000, double d2000 ):
     return cpal.palRvlsrk( r2000, d2000 )



def subet( double rc, double dc, double eq ):
     cdef double rm
     cdef double dm
     cpal.palSubet( rc, dc, eq, &rm, &dm )
     return ( rm, dm )

def supgal( double dsl, double dsb ):
     cdef double dl
     cdef double db
     cpal.palSupgal( dsl, dsb, &dl, &db )
     return (dl, db)
