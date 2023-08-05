module liq_ice_air_5

!#########################################################################

!THIS MODULE IMPLEMENTS THE EQUILIBRIUM PROPERTIES OF WET ICE AIR, 
!I.E., BETWEEN LIQUID WATER, ICE AND HUMID AIR

!#########################################################################

!IMPLEMENTATION IN FORTRAN BY D.G. WRIGHT
!FOR PUBLICATION IN OCEAN SCIENCE, AS DESCRIBED IN THE PAPERS

!FEISTEL, R., WRIGHT, D.G., JACKETT, D.R., MIYAGAWA, K., REISSMANN, J.H.,
!WAGNER, W., OVERHOFF, U., GUDER, C., FEISTEL, A., MARION, G.M.:
!NUMERICAL IMPLEMENTATION AND OCEANOGRAPHIC APPLICATION OF THE THERMODYNAMIC
!POTENTIALS OF WATER, VAPOUR, ICE, SEAWATER AND AIR. PART I: BACKGROUND AND EQUATIONS. 
!OCEAN SCIENCES, 2009, IN PREPARATION.

!WRIGHT, D.G., FEISTEL, R., JACKETT, D.R., MIYAGAWA, K., REISSMANN, J.H., 
!WAGNER, W., OVERHOFF, U., GUDER, C., FEISTEL, A., MARION, G.M.:
!NUMERICAL IMPLEMENTATION AND OCEANOGRAPHIC APPLICATION OF THE THERMODYNAMIC
!POTENTIALS OF WATER, VAPOUR, ICE, SEAWATER AND AIR. PART II: THE LIBRARY ROUTINES, 
!OCEAN SCIENCES., 2009, IN PREPARATION.

!FEISTEL, R., KRETZSCHMAR, H.-J., SPAN, R., HAGEN, E., WRIGHT, D.G., HERRMANN, S.:
!THERMODYNAMIC PROPERTIES OF SEA AIR.
!OCEAN SCIENCE DISCUSSION 6(2009)2193-2325.

!#########################################################################

!THIS MODULE REQUIRES THE LIBRARY MODULES:
!     CONSTANTS_0,  FILE CONSTANTS_0.F90
!     CONVERT_0,    FILE CONVERT_0.F90
!     MATHS_0,      FILE MATHS_0.F90
!     AIR_1,        FILE AIR_1.F90
!     FLU_1,        FILE FLU_1.F90
!     ICE_1,        FILE ICE_1.F90
!     AIR_2,        FILE AIR_2.F90
!     FLU_2,        FILE FLU_2.F90
!     ICE_2,        FILE ICE_2.F90
!     AIR_3B,       FILE AIR_3B.F90
!     ICE_LIQ_4,    FILE ICE_LIQ_4.F90

!NESTED USE ASSOCIATIONS
!     AIR_3A,       FILE AIR_3A.F90

!#########################################################################

use constants_0
use convert_0
use maths_0
use air_1
use flu_1
use ice_1
use air_2
use flu_2
use ice_2
use air_3b
use air_3c
use ice_liq_4

use ice_vap_4
use liq_vap_4

use liq_air_4a
use liq_air_4b
use liq_air_4c
use ice_air_4a
use ice_air_4b
use ice_air_4c
use liq_ice_air_4

implicit none
private

character*16, private :: version = 'August 2012'

public :: liq_ice_air_pottemp_si, liq_ice_air_pottemp_equi_si, &
          liq_ice_air_pottemp_equi_sat_si, &
          liq_ice_air_g_entropy_si, liq_ice_air_g_entropy_moist_si, &
          liq_ice_air_massfraction_air_si
          !liq_ice_air_g_entropy_mixed_si, &

contains

function liq_ice_air_pottemp_si(a_si, t_si, p_si, pr_si)
!THIS FUNCTION COMPUTES POTENTIAL TEMPERATURE OF AIR AND CHECK IF THERE IS ICE AT THE ORIGINAL POSITION
!AND AT THE FINAL POSITION

!OUTPUT:
!THETA(A,T,P,PR) ABSOLUTE POTENTIAL TEMPERATURE OF ICE AIR IN K

!INPUTS:
!A_SI      ABSOLUTE DRY-AIR MASS FRACTION IN KG/KG
!T_SI      ABSOLUTE IN-SITU TEMPERATURE IN K
!P_SI      ABSOLUTE IN-SITU PRESSURE IN PA
!PR_SI     ABSOLUTE REFERENCE PRESSURE IN PA

!NOTE: THE ACCURACY OF THIS FUNCTION DEPENDS ON THE ITERATION SETTINGS FOR
!      DENSITY COMPUTED IN AIR_3A,
!      AND ON THE ITERATION SETTINGS FOR TEMPERATURE BY SET_IT_CTRL_ICE_AIR_POTTEMP OF THIS MODULE_SI

real*8 liq_ice_air_pottemp_si, a_si, t_si, p_si, pr_si

real*8 s
real*8 a_sat, iml, ifl

liq_ice_air_pottemp_si = errorreturn

if(a_si < 0d0 .or. a_si >= 1d0) return
if(t_si < 0d0) return
if(p_si < 0d0) return
if(pr_si < 0d0) return


if(p_si == pr_si) then
  liq_ice_air_pottemp_si = t_si
  return
end if

s=liq_ice_air_g_entropy_si(a_si,t_si,p_si)
if(s == errorreturn) return

liq_ice_air_pottemp_si = liq_ice_air_h_temperature_si(a_si, s, pr_si)

end function

function liq_ice_air_h_temperature_si(a_si, eta_si, p_si)

real*8 liq_ice_air_h_temperature_si, a_si, eta_si, p_si
real*8 t_triple

liq_ice_air_h_temperature_si = errorreturn

if(a_si < 0d0 .or. a_si >= 1d0) return
if(p_si < 0d0) return

if(set_liq_ice_air_eq_at_p(p_si) == errorreturn) return
t_triple=liq_ice_air_temperature_si()

!Equilibrium agains ice:
liq_ice_air_h_temperature_si = ice_air_h_temperature_si(a_si, eta_si, p_si)
if(liq_ice_air_h_temperature_si/=errorreturn.and.liq_ice_air_h_temperature_si<t_triple) return

liq_ice_air_h_temperature_si = liq_air_h_temperature_si(a_si, eta_si, p_si)
if(liq_ice_air_h_temperature_si/=errorreturn.and.liq_ice_air_h_temperature_si>t_triple) return

liq_ice_air_h_temperature_si = air_temperature_si(a_si, eta_si, p_si)

end function


function liq_ice_air_massfraction_air_si(t_si, p_si)
real*8 liq_ice_air_massfraction_air_si, t_si, p_si
real*8 t_triple

liq_ice_air_massfraction_air_si = errorreturn

if(t_si < 0d0) return
if(p_si < 0d0) return

if(set_liq_ice_air_eq_at_p(p_si) == errorreturn) return
t_triple=liq_ice_air_temperature_si()
if(t_triple==errorreturn) return
if(t_si<t_triple) then
    liq_ice_air_massfraction_air_si=ice_air_massfraction_air_si(t_si,p_si)
else
   liq_ice_air_massfraction_air_si=liq_air_massfraction_air_si(t_si,p_si)
endif

end function

function liq_ice_air_g_entropy_moist_si(a_si, t_si, p_si)
!THIS FUNCTION COMPUTES THE ENTROPY OF MIXED ICE/LIQUID/WET AIR

real*8 liq_ice_air_g_entropy_moist_si, a_si, t_si, p_si
real*8 a_sat, rh_max, theta_e

liq_ice_air_g_entropy_moist_si = errorreturn

if(a_si < 0d0 .or. a_si >= 1d0) return
if(t_si < 0d0) return
if(p_si < 0d0) return

!Find the equivalent potential temperature:
theta_e=liq_ice_air_pottemp_equi_si(a_si,t_si,p_si,p_si)

a_sat=liq_ice_air_massfraction_air_si(theta_e,p_si)

rh_max=1d-3
a_sat = 1d0/(rh_max*(1d0/a_sat-1d0)+1d0)

!Compute the entropy of the equivalent potential temperature:
liq_ice_air_g_entropy_moist_si = liq_ice_air_g_entropy_si(a_sat, theta_e, p_si)

end function

function liq_ice_air_g_entropy_si(a_si, t_si, p_si)
!THIS FUNCTION COMPUTES THE ENTROPY OF MIXED ICE/LIQUID/WET AIR

real*8 liq_ice_air_g_entropy_si, a_si, t_si, p_si
real*8 a_sat, t_triple

liq_ice_air_g_entropy_si = errorreturn

if(a_si < 0d0 .or. a_si >= 1d0) return
if(t_si < 0d0) return
if(p_si < 0d0) return

a_sat=liq_ice_air_massfraction_air_si(t_si,p_si)

if(set_liq_ice_air_eq_at_p(p_si) == errorreturn) return
t_triple=liq_ice_air_temperature_si()
if(t_triple==errorreturn) return

if(a_sat<=a_si.or.a_sat==errorreturn) then
        !no condensation
        liq_ice_air_g_entropy_si=air_g_entropy_si(a_si, t_si, p_si)
else
    if(t_si<t_triple) then
        !condensation against ice
        liq_ice_air_g_entropy_si=ice_air_g_entropy_si(a_si, t_si, p_si)
    elseif(t_si>t_triple) then
        !condensation against liquid
        liq_ice_air_g_entropy_si=liq_air_g_entropy_si(a_si, t_si, p_si)
    else
        !at triple point
        liq_ice_air_g_entropy_si=liq_ice_air_entropy_si()
    endif
endif

end function

!function liq_ice_air_g_entropy_mixed_si(a_si, t_si, p_si, rh_wmo_max)
!THIS FUNCTION COMPUTES THE ENTROPY OF MIXED ICE/LIQUID/WET AIR

!real*8 liq_ice_air_g_entropy_mixed_si, a_si, t_si, p_si, rh_wmo_max
!real*8 a_sat, t_triple
!real*8 g_t

!liq_ice_air_g_entropy_mixed_si = errorreturn

!if(a_si < 0d0 .or. a_si >= 1d0) return
!if(t_si < 0d0) return
!if(p_si < 0d0) return

!a_sat=liq_ice_air_massfraction_air_si(t_si,p_si)

!a_sat = 1d0/(rh_wmo_max*(1d0/a_sat-1d0)+1d0)

!if(set_liq_ice_air_eq_at_p(p_si) == errorreturn) return
!t_triple=liq_ice_air_temperature_si()
!if(t_triple==errorreturn) return
!
!if(a_sat<=a_si.or.a_sat==errorreturn) then
!        !no condensation
!        liq_ice_air_g_entropy_mixed_si = air_g_entropy_si(a_si, t_si, p_si) 
!else
!    if(t_si<t_triple) then
!        !condensation against ice
!        g_t = ice_air_g_si(0, 1, 0, a_si, t_si, p_si, rh_wmo_max)
!        if(g_t == errorreturn) return
!
!        liq_ice_air_g_entropy_mixed_si = -g_t
!    elseif(t_si>t_triple) then
!        !condensation against liquid
!        g_t = liq_air_g_si(0, 1, 0, a_si, t_si, p_si, rh_wmo_max)
!        if(g_t == errorreturn) return
!
!        liq_ice_air_g_entropy_mixed_si = -g_t
!    else
!        !at triple point
!        liq_ice_air_g_entropy_mixed_si=liq_ice_air_entropy_si()
!    endif
!endif

!end function

function liq_ice_air_g_cp_si(a_si, t_si, p_si)
!THIS FUNCTION COMPUTES THE ENTROPY OF MIXED ICE/LIQUID/WET AIR

real*8 liq_ice_air_g_cp_si, a_si, t_si, p_si
real*8 a_sat, t_triple

liq_ice_air_g_cp_si = errorreturn

if(a_si < 0d0 .or. a_si >= 1d0) return
if(t_si < 0d0) return
if(p_si < 0d0) return

a_sat=liq_ice_air_massfraction_air_si(t_si,p_si)

if(set_liq_ice_air_eq_at_p(p_si) == errorreturn) return
t_triple=liq_ice_air_temperature_si()
if(t_triple==errorreturn) return

if(t_si<t_triple) then
    !equilibrium against ice
    if(a_sat<=a_si.or.a_sat==errorreturn) then
        !no condensation
        liq_ice_air_g_cp_si=air_g_cp_si(a_si, t_si, p_si)
    else
        !condensation against ice
        liq_ice_air_g_cp_si=ice_air_g_cp_si(a_si, t_si, p_si)
    endif
elseif(t_si>t_triple) then
    !equilibrium against liquid
    if(a_sat<=a_si .or. a_sat==errorreturn) then
        !no condensation
        liq_ice_air_g_cp_si=air_g_cp_si(a_si, t_si, p_si)
    else
        !condensation against liquid
        liq_ice_air_g_cp_si=liq_air_g_cp_si(a_si, t_si, p_si)
    endif
else
    !at triple point
    liq_ice_air_g_cp_si=liq_ice_air_entropy_si()
endif

end function

function liq_ice_air_pottemp_equi_si(a_si, t_si, p_si, pr_si)
!THIS FUNCTION COMPUTES THE EQUIVALENT TEMPERATURE OF AIR AT FIXED PRESSURE AND FIXED DRY AIR MASS FRACTION.

!OUTPUT:
!TEQ(A,T,P,PR) ABSOLUTE EQUIVALENT TEMPERATURE OF ICE AIR OR LIQUID AIR IN K

!INPUTS:
!A_SI      ABSOLUTE DRY-AIR MASS FRACTION IN KG/KG
!T_SI      ABSOLUTE IN-SITU TEMPERATURE IN K
!P_SI      ABSOLUTE IN-SITU PRESSURE IN PA
!PR_SI     REFERENCE PRESSURE IN PA

real*8 liq_ice_air_pottemp_equi_si, a_si, t_si, p_si, pr_si

real*8 s, tmin, p_toa, t_toa, t_triple, a_sat, rh_max

liq_ice_air_pottemp_equi_si = errorreturn

if(a_si < 0d0 .or. a_si >= 1d0) return
if(t_si < 0d0) return
if(p_si < 0d0) return
if(pr_si < 0d0) return

s = liq_ice_air_g_entropy_si(a_si, t_si, p_si)

if(s == errorreturn) return

!Find the level at which the dry temperature is equal to tmin:
tmin=200d0
p_toa = aux_ice_air_pressure_si(a_si, s, tmin)

!Find the temperature at that location:
t_toa = liq_ice_air_pottemp_si(a_si, t_si, p_si, p_toa)

a_sat=liq_ice_air_massfraction_air_si(t_toa,p_toa)

rh_max=1d-3
a_sat = 1d0/(rh_max*(1d0/a_sat-1d0)+1d0)
liq_ice_air_pottemp_equi_si=liq_ice_air_pottemp_si(a_sat, t_toa, p_toa, pr_si)

end function

!function liq_ice_air_pottemp_equi_ams_si(a_si, t_si, p_si, pr_si)
!THIS FUNCTION COMPUTES THE EQUIVALENT TEMPERATURE OF AIR AT FIXED PRESSURE AND FIXED DRY AIR MASS FRACTION.

!OUTPUT:
!TEQ(A,T,P,PR) ABSOLUTE EQUIVALENT TEMPERATURE OF ICE AIR OR LIQUID AIR IN K

!INPUTS:
!A_SI      ABSOLUTE DRY-AIR MASS FRACTION IN KG/KG
!T_SI      ABSOLUTE IN-SITU TEMPERATURE IN K
!P_SI      ABSOLUTE IN-SITU PRESSURE IN PA
!PR_SI     REFERENCE PRESSURE IN PA

!real*8 liq_ice_air_pottemp_equi_ams_si, a_si, t_si, p_si, pr_si
!
!real*8 equi_temp
!
!liq_ice_air_pottemp_equi_ams_si = errorreturn
!
!if(a_si < 0d0 .or. a_si >= 1d0) return
!if(t_si < 0d0) return
!if(p_si < 0d0) return
!if(pr_si < 0d0) return
!
!equi_temp=exp(-(1d0-a_si)*Rv/cp
!
!liq_ice_air_pottemp_equi_si=liq_ice_air_pottemp_si(a_si, t_si, p_toa, pr_si)
!
!end function


function liq_ice_air_pottemp_equi_sat_si(a_si, t_si, p_si, pr_si)
!THIS FUNCTION COMPUTES THE SATURATION EQUIVALENT TEMPERATURE OF AIR AT FIXED PRESSURE AND FIXED DRY AIR MASS FRACTION.

!OUTPUT:
!TEQ(A,T,P,PR) ABSOLUTE EQUIVALENT TEMPERATURE OF ICE AIR OR LIQUID AIR IN K

!INPUTS:
!A_SI      ABSOLUTE DRY-AIR MASS FRACTION IN KG/KG
!T_SI      ABSOLUTE IN-SITU TEMPERATURE IN K
!P_SI      ABSOLUTE IN-SITU PRESSURE IN PA
!PR_SI     REFERENCE PRESSURE IN PA

real*8 liq_ice_air_pottemp_equi_sat_si, a_si, t_si, p_si, pr_si

real*8 s, a_sat, t_triple

liq_ice_air_pottemp_equi_sat_si = errorreturn

if(a_si < 0d0 .or. a_si >= 1d0) return
if(t_si < 0d0) return
if(p_si < 0d0) return
if(pr_si < 0d0) return

!Find the saturation air mass fraction:
a_sat=liq_ice_air_massfraction_air_si(t_si,p_si)

if(a_si>a_sat) then
    liq_ice_air_pottemp_equi_sat_si=liq_ice_air_pottemp_equi_si(a_sat, t_si, p_si, pr_si)
else
    liq_ice_air_pottemp_equi_sat_si=liq_ice_air_pottemp_equi_si(a_si, t_si, p_si, pr_si)
endif

end function

!=========================================================================
function aux_ice_air_pressure_si(wa_si, eta_si, t_si)
!==========================================================================

!THIS FUNCTION ESTIMATES THE PRESSURE OF ICE AIR FROM ITS DRY-AIR FRACTION WA_SI IN KG/KG,
!ITS SPECIFIC ENTROPY ETA_SI IN J/(KG K), AND ITS ABSOLUTE TEMPERATURE, T_SI IN K

real*8 aux_ice_air_pressure_si, wa_si, eta_si, t_si
real*8 numer, denom, p, tf

real*8 tt, pt, cpa, cpi, sat, sit, ra

tt = tp_temperature_si           !TRIPLE-POINT TEMPERATURE IN K
pt = tp_pressure_iapws95_si      !TRIPLE-POINT PRESSURE IN Pa

cpa = 1003.68997553091d0         !TRIPLE-POINT HEAT CAPACITY OF AIR IN J/(KG K)
cpi = 2096.78431621667d0         !TRIPLE-POINT HEAT CAPACITY OF ICE IN J/(KG K)

sat = 1467.66694249983d0         !TRIPLE-POINT ENTROPY OF AIR IN J/(KG K)
sit = -1220.69433939648d0        !TRIPLE-POINT ENTROPY OF ICE IN J/(KG K)

ra = gas_constant_air_si

aux_ice_air_pressure_si = errorreturn
if(t_si <= 0d0) return
if(wa_si < 0d0 .or. wa_si > 1d0) return

!ASSUME CONSTANT HEAT CAPACITY CP OF ICE AND AIR, USE IDEAL-GAS EQUATION,
!NEGLECT THE VAPOUR FRACTION IN HUMID AIR:

denom = cpa

p = pt*exp((denom*log(t_si/tt) - eta_si + sit + wa_si*(sat-sit))/(wa_si*ra))

!CHECK IF T_SI IS BELOW FREEZING POINT????

aux_ice_air_pressure_si = p

end function

end module liq_ice_air_5
