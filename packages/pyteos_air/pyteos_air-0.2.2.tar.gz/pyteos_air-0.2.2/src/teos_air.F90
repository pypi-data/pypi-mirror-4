!FBL August 2012, University of Toronto
!
!1. Compile the teos with -fPIC:
!   bash compile_LIBRARY.sh
!
!2. Create a library teos.a:
!   ar -rcs teos.a *.o
!
!3. Create a fyp2 signature file:
!   f2py -m pyteos_air -h pyteos_air.pyf pyteos_air.F90 teos.a
!
!4. Compile the python library:
!   f2py teos.a -c pyteos_air.pyf pyteos_air.F90


subroutine air_g(in_name, in_q, in_t, in_p, k, l, m, n, out_val)
    !This subroutine is a wrapper for the Gibbs function formulation of humid air thermodynamics
    !Available routines taking q, t, p as arguments unles otherwise noted:
    !
    ! Air3b:
    ! chempot_vap
    ! compressibilityfactor
    ! contraction
    ! cp
    ! cv
    ! density
    ! enthalpy
    ! entropy
    ! expansion
    ! gibbs
    ! internal_energy
    ! kappa_s: isentropic compressibility
    ! kappa_t: isothermal compressibility
    ! lapserate: dry adiabatic lapse rate of humid air
    ! soundspeed

    ! Air3c:
    ! temperature: temperature from q, entropy, p
    ! 
    use air_3b
    use air_3c
    implicit none
    integer :: k, l, m, n, idk, idl, idm, idn
    real(8) :: in_q(k,l,m,n), in_t(k,l,m,n), in_p(k,l,m,n)
    real(8) :: out_val(k,l,m,n)
    character(len = *) :: in_name

!f2py real(8), intent(out), dimension(k,l,m,n) :: out_val
!f2py real(8), intent(in), dimension(k,l,m,n) :: in_q, in_t, in_p
!f2py character(len = *), intent(in) :: in_name
!f2py integer, intent(in) :: k,l,m,n
    

    do idk=1,k
    do idl=1,l
    do idm=1,m
    do idn=1,n
            select case( in_name )
                !Air 3b
                case( 'chempot_vap' )
                    out_val(idk,idl,idn,idm)=air_g_chempot_vap_si(in_q(idk,idl,idn,idm),&
                    in_t(idk,idl,idn,idm), in_p(idk,idl,idn,idm))
                case( 'compressibilityfactor' )
                    out_val(idk,idl,idn,idm)=air_g_compressibilityfactor_si(in_q(idk,idl,idn,idm),&
                    in_t(idk,idl,idn,idm), in_p(idk,idl,idn,idm))
                case( 'contraction' )
                    out_val(idk,idl,idn,idm)=air_g_contraction_si(in_q(idk,idl,idn,idm),&
                    in_t(idk,idl,idn,idm), in_p(idk,idl,idn,idm))
                case( 'cp' )
                    out_val(idk,idl,idn,idm)=air_g_cp_si(in_q(idk,idl,idn,idm),&
                    in_t(idk,idl,idn,idm), in_p(idk,idl,idn,idm))
                case( 'cv' )
                    out_val(idk,idl,idn,idm)=air_g_cv_si(in_q(idk,idl,idn,idm),&
                    in_t(idk,idl,idn,idm), in_p(idk,idl,idn,idm))
                case( 'density' )
                    out_val(idk,idl,idn,idm)=air_g_density_si(in_q(idk,idl,idn,idm),&
                    in_t(idk,idl,idn,idm), in_p(idk,idl,idn,idm))
                case( 'enthalpy' )
                    out_val(idk,idl,idn,idm)=air_g_enthalpy_si(in_q(idk,idl,idn,idm),&
                    in_t(idk,idl,idn,idm), in_p(idk,idl,idn,idm))
                case( 'entropy' )
                    out_val(idk,idl,idn,idm)=air_g_entropy_si(in_q(idk,idl,idn,idm),&
                    in_t(idk,idl,idn,idm), in_p(idk,idl,idn,idm))
                case( 'expansion' )
                    out_val(idk,idl,idn,idm)=air_g_expansion_si(in_q(idk,idl,idn,idm),&
                    in_t(idk,idl,idn,idm), in_p(idk,idl,idn,idm))
                case( 'gibbs_energy' )
                    out_val(idk,idl,idn,idm)=air_g_gibbs_energy_si(in_q(idk,idl,idn,idm),&
                    in_t(idk,idl,idn,idm), in_p(idk,idl,idn,idm))
                case( 'internal_energy' )
                    out_val(idk,idl,idn,idm)=air_g_internal_energy_si(in_q(idk,idl,idn,idm),&
                    in_t(idk,idl,idn,idm), in_p(idk,idl,idn,idm))
                case( 'kappa_s' )
                    out_val(idk,idl,idn,idm)=air_g_kappa_s_si(in_q(idk,idl,idn,idm),&
                    in_t(idk,idl,idn,idm), in_p(idk,idl,idn,idm))
                case( 'kappa_t' )
                    out_val(idk,idl,idn,idm)=air_g_kappa_t_si(in_q(idk,idl,idn,idm),&
                    in_t(idk,idl,idn,idm), in_p(idk,idl,idn,idm))
                case( 'lapserate' )
                    out_val(idk,idl,idn,idm)=air_g_lapserate_si(in_q(idk,idl,idn,idm),&
                    in_t(idk,idl,idn,idm), in_p(idk,idl,idn,idm))
                case( 'soundspeed' )
                    out_val(idk,idl,idn,idm)=air_g_soundspeed_si(in_q(idk,idl,idn,idm),&
                    in_t(idk,idl,idn,idm), in_p(idk,idl,idn,idm))
                !Air 3c
                case( 'temperature' ) !From Air_3c. Requires entropy instead of temperature
                    out_val(idk,idl,idn,idm)=air_temperature_si(in_q(idk,idl,idn,idm),&
                    in_t(idk,idl,idn,idm), in_p(idk,idl,idn,idm))
                case default
                    write(*,*) 'Unknown function'
            end select
    enddo
    enddo
    enddo
    enddo
 
end subroutine air_g

subroutine air_g_ref(in_name,in_q,in_t,in_p, in_ref, k, l, m, n, out_val)
    !This subroutine is a wrapper for the Gibbs function formulation of humid air thermodynamics.
    !All of these functions require a reference value
    !Available routines:
    !
    ! Air_3c:
    ! potdensity
    ! potenthalpy
    ! pottemp

    use air_3c
    implicit none
    integer :: k, l, m, n, idk, idl, idm, idn
    real(8) :: in_q(k,l,m,n), in_t(k,l,m,n), in_p(k,l,m,n)
    real(8) :: in_ref
    real(8) :: out_val(k,l,m,n)
    character (len = *) :: in_name

!f2py real(8), intent(out), dimension(k,l,m,n) :: out_val
!f2py real(8), intent(in), dimension(k,l,m,n) :: in_q, in_t, in_p
!f2py real(8), intent(in) :: in_ref
!f2py integer, intent(in) :: k,l,m,n
!f2py character(len = *), intent(in) :: in_name

    do idk=1,k
    do idl=1,l
    do idm=1,m
    do idn=1,n
            select case(in_name)
                case( 'potdensity' )
                    out_val(idk,idl,idm,idm)=air_potdensity_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm), in_ref)
                case( 'potenthalpy' )
                    out_val(idk,idl,idm,idm)=air_potenthalpy_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm), in_ref)
                case( 'pottemp' )
                    out_val(idk,idl,idm,idm)=air_pottemp_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm), in_ref)
                case default
                    write(*,*) 'Unknown function'
            end select
    enddo
    enddo
    enddo
    enddo
 
end subroutine air_g_ref

subroutine liq_air_sat(in_name,in_t,in_p, k, l, m, n, out_val)
    !This subroutine is a wrapper for the Gibbs function formulation for wet air saturation.
    !Available routines:
    !
    ! Liq_Air_4a:
    ! massfraction: t and p
    ! condensationpressure: a and t
    ! dewpoint: a and p
    !
    ! Liq_Ice_Air_4:
    ! ifl: isentropic freezing level: q and s
    ! iml: isentropic melting level: q and s

    use liq_air_4a
    implicit none
    integer :: k, l, m, n, idk, idl, idm, idn
    real(8) :: in_t(k,l,m,n), in_p(k,l,m,n)
    real(8) :: out_val(k,l,m,n)
    character (len = *) :: in_name

!f2py real(8), intent(out), dimension(k,l,m,n) :: out_val
!f2py real(8), intent(in), dimension(k,l,m,n) :: in_t, in_p
!f2py character(len = *), intent(in) :: in_name
!f2py integer, intent(in) :: k,l,m,n

    do idk=1,k
    do idl=1,l
    do idm=1,m
    do idn=1,n
            select case(in_name)
                !Liq_Air_4a:
                case( 'massfraction' )
                    out_val(idk,idl,idm,idm)=liq_air_massfraction_air_si(&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'condensationpressure' )
                    out_val(idk,idl,idm,idm)=liq_air_condensationpressure_si(&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'dewpoint' )
                    out_val(idk,idl,idm,idm)=liq_air_dewpoint_si(&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case default
                    write(*,*) 'Unknown function'
            end select
    enddo
    enddo
    enddo
    enddo
 
end subroutine liq_air_sat

subroutine liq_air_g(in_name, in_q,in_t,in_p, k, l, m, n, out_val)
    !This subroutine is a wrapper for the Gibbs function formulation of wet air thermodynamics
    !Available routines taking q, t, p as arguments unles otherwise noted:
    !
    ! Liq_Air_4a:
    ! massfrac_wmo: mass fraction from rh, t, p
    ! massfrac_cct: mass fraction from rh, t, p
    ! rh_cct
    ! rh_wmo
    ! icl: isentropic condensation level
    ! ict: isentropic condensation temperature

    ! Liq_Air_4b:
    ! density
    ! enthalpy
    ! entropy
    ! expansion
    ! kappa_t
    ! lapserate
    ! liquidfraction
    ! vapourfraction

    use liq_air_4a
    use liq_air_4b
    implicit none
    integer :: k, l, m, n, idk, idl, idm, idn
    real(8) :: in_q(k,l,m,n), in_t(k,l,m,n), in_p(k,l,m,n)
    real(8) :: out_val(k,l,m,n)
    character (len = *) :: in_name

!f2py real(8), intent(out), dimension(k,l,m,n) :: out_val
!f2py real(8), intent(in), dimension(k,l,m,n) :: in_q, in_t, in_p
!f2py character(len = *), intent(in) :: in_name
!f2py integer, intent(in) :: k,l,m,n

    do idk=1,k
    do idl=1,l
    do idm=1,m
    do idn=1,n
            select case( in_name )
                !Liq_Air_4a
                case( 'massfrac_wmo' ) 
                    out_val(idk,idl,idm,idm)=liq_air_a_from_rh_wmo_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'massfrac_cct' ) 
                    out_val(idk,idl,idm,idm)=liq_air_a_from_rh_cct_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'rhl_wmo' ) 
                    out_val(idk,idl,idm,idm)=liq_air_rh_wmo_from_a_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'rhl_cct' ) 
                    out_val(idk,idl,idm,idm)=liq_air_rh_cct_from_a_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'icl' ) 
                    out_val(idk,idl,idm,idm)=liq_air_icl_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'ict' ) 
                    out_val(idk,idl,idm,idm)=liq_air_ict_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                !Liq_Air_4b
                case( 'cp' ) 
                    out_val(idk,idl,idm,idm)=liq_air_g_cp_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'density' ) 
                    out_val(idk,idl,idm,idm)=liq_air_g_density_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'enthalpy' ) 
                    out_val(idk,idl,idm,idm)=liq_air_g_enthalpy_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'entropy' ) 
                    out_val(idk,idl,idm,idm)=liq_air_g_entropy_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'expansion' ) 
                    out_val(idk,idl,idm,idm)=liq_air_g_expansion_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'kappa_t' ) 
                    out_val(idk,idl,idm,idm)=liq_air_g_kappa_t_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'lapserate' ) 
                    out_val(idk,idl,idm,idm)=liq_air_g_lapserate_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'liquidfraction' ) 
                    out_val(idk,idl,idm,idm)=liq_air_liquidfraction_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'vapourfraction' ) 
                    out_val(idk,idl,idm,idm)=liq_air_vapourfraction_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
            end select
    enddo
    enddo
    enddo
    enddo
end subroutine liq_air_g

subroutine liq_air_h(in_name, in_q,in_s,in_p, k, l, m, n, out_val)
    !This subroutine is a wrapper for the Gibbs function formulation of wet air thermodynamics
    !Available routines taking q, s, p as arguments unles otherwise noted:
    !
    ! Liq_Air_4c:
    ! cp
    ! density
    ! kappa_s
    ! temperature
    ! lapserate

    use liq_air_4c
    implicit none
    integer :: k, l, m, n, idk, idl, idm, idn
    real(8) :: in_q(k,l,m,n), in_s(k,l,m,n), in_p(k,l,m,n)
    real(8) :: out_val(k,l,m,n)
    character (len = *) :: in_name

!f2py real(8), intent(out), dimension(k,l,m,n) :: out_val
!f2py real(8), intent(in), dimension(k,l,m,n) :: in_q, in_s, in_p
!f2py character(len = *), intent(in) :: in_name
!f2py integer, intent(in) :: k,l,m,n

    do idk=1,k
    do idl=1,l
    do idm=1,m
    do idn=1,n
            select case( in_name )
                case( 'cp' ) 
                    out_val(idk,idl,idm,idm)=liq_air_h_cp_si(in_q(idk,idl,idm,idm),&
                    in_s(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'density' ) 
                    out_val(idk,idl,idm,idm)=liq_air_h_density_si(in_q(idk,idl,idm,idm),&
                    in_s(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'kappa_s' ) 
                    out_val(idk,idl,idm,idm)=liq_air_h_kappa_s_si(in_q(idk,idl,idm,idm),&
                    in_s(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'temperature' ) 
                    out_val(idk,idl,idm,idm)=liq_air_h_temperature_si(in_q(idk,idl,idm,idm),&
                    in_s(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'lapserate' ) 
                    out_val(idk,idl,idm,idm)=liq_air_h_lapserate_si(in_q(idk,idl,idm,idm),&
                    in_s(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
            end select
    enddo
    enddo
    enddo
    enddo
end subroutine liq_air_h


subroutine liq_air_g_ref(in_name,in_q,in_t,in_p, in_ref, k, l, m, n, out_val)
    !This subroutine is a wrapper for the Gibbs function formulation of humid air thermodynamics.
    !All of these functions require a reference value
    !Available routines:
    !
    ! Liq_Air_4c
    ! potdensity
    ! potenthalpy
    ! pottemp
    ! pottempequi

    use liq_air_4c
    !use liq_air_5
    implicit none
    integer :: k, l, m, n, idk, idl, idm, idn
    real(8) :: in_q(k,l,m,n), in_t(k,l,m,n), in_p(k,l,m,n)
    real(8) :: in_ref
    real(8) :: out_val(k,l,m,n)
    character (len = *) :: in_name

!f2py real(8), intent(out), dimension(k,l,m,n) :: out_val
!f2py real(8), intent(in), dimension(k,l,m,n) :: in_q, in_t, in_p
!f2py real(8), intent(in) :: in_ref
!f2py integer, intent(in) :: k,l,m,n
!f2py character(len = *), intent(in) :: in_name

    do idk=1,k
    do idl=1,l
    do idm=1,m
    do idn=1,n
            select case(in_name)
                case( 'potdensity' )
                    out_val(idk,idl,idm,idm)=liq_air_potdensity_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm), in_ref)
                case( 'potenthalpy' )
                    out_val(idk,idl,idm,idm)=liq_air_potenthalpy_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm), in_ref)
                case( 'pottemp' )
                    out_val(idk,idl,idm,idm)=liq_air_pottemp_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm), in_ref)
            end select
    enddo
    enddo
    enddo
    enddo
 
end subroutine liq_air_g_ref

subroutine ice_air_sat(in_name,in_t,in_p, k, l, m, n, out_val)
    !This subroutine is a wrapper for the Gibbs function formulation for wet air saturation.
    !Available routines:
    !
    ! Liq_Air_4a:
    ! massfraction: t and p
    ! condensationpressure: a and t
    ! dewpoint: a and p
    !

    use ice_air_4a
    implicit none
    integer :: k, l, m, n, idk, idl, idm, idn
    real(8) :: in_t(k,l,m,n), in_p(k,l,m,n)
    real(8) :: out_val(k,l,m,n)
    character (len = *) :: in_name

!f2py real(8), intent(out), dimension(k,l,m,n) :: out_val
!f2py real(8), intent(in), dimension(k,l,m,n) :: in_t, in_p
!f2py character(len = *), intent(in) :: in_name
!f2py integer, intent(in) :: k,l,m,n

    do idk=1,k
    do idl=1,l
    do idm=1,m
    do idn=1,n
            select case(in_name)
                !Ice_Air_4a:
                case( 'massfraction' )
                    out_val(idk,idl,idm,idm)=ice_air_massfraction_air_si(&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'condensationpressure' )
                    out_val(idk,idl,idm,idm)=ice_air_condensationpressure_si(&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'frostpoint' )
                    out_val(idk,idl,idm,idm)=ice_air_frostpoint_si(&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case default
                    write(*,*) 'Unknown function'
            end select
    enddo
    enddo
    enddo
    enddo
 
end subroutine ice_air_sat


subroutine ice_air_g(in_name, in_q,in_t,in_p, k, l, m, n, out_val)
    !This subroutine is a wrapper for the Gibbs function formulation of wet air thermodynamics
    !Available routines taking q, t, p as arguments unles otherwise noted:
    !
    ! Ice_Air_4a:
    ! massfrac_wmo: mass fraction from rh, t, p
    ! massfrac_cct: mass fraction from rh, t, p
    ! rh_cct
    ! rh_wmo
    ! icl: isentropic condensation level
    ! ict: isentropic condensation temperature
    !
    ! Ice_Air_4b:
    ! density
    ! enthalpy
    ! expansion
    ! kappa_t
    ! lapserate
    ! solidfraction
    ! vapourfraction

    use ice_air_4a
    use ice_air_4b
    implicit none
    integer :: k, l, m, n, idk, idl, idm, idn
    real(8) :: in_q(k,l,m,n), in_t(k,l,m,n), in_p(k,l,m,n)
    real(8) :: out_val(k,l,m,n)
    character (len = *) :: in_name

!f2py real(8), intent(out), dimension(k,l,m,n) :: out_val
!f2py real(8), intent(in), dimension(k,l,m,n) :: in_q, in_t, in_p
!f2py integer, intent(in) :: k,l,m,n
!f2py character(len = *), intent(in) :: in_name

    do idk=1,k
    do idl=1,l
    do idm=1,m
    do idn=1,n
            select case( in_name )
                !Ice_Air_4a
                case( 'massfrac_wmo' ) 
                    out_val(idk,idl,idm,idm)=ice_air_a_from_rh_wmo_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'massfrac_cct' ) 
                    out_val(idk,idl,idm,idm)=ice_air_a_from_rh_cct_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'rhl_wmo' ) 
                    out_val(idk,idl,idm,idm)=ice_air_rh_wmo_from_a_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'rhl_cct' ) 
                    out_val(idk,idl,idm,idm)=ice_air_rh_cct_from_a_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'icl' ) 
                    out_val(idk,idl,idm,idm)=ice_air_icl_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'ict' ) 
                    out_val(idk,idl,idm,idm)=ice_air_ict_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                !Ice_Air_4b
                case( 'cp' ) 
                    out_val(idk,idl,idm,idm)=ice_air_g_cp_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'density' ) 
                    out_val(idk,idl,idm,idm)=ice_air_g_density_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'enthalpy' ) 
                    out_val(idk,idl,idm,idm)=ice_air_g_enthalpy_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'entropy' ) 
                    out_val(idk,idl,idm,idm)=ice_air_g_entropy_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'expansion' ) 
                    out_val(idk,idl,idm,idm)=ice_air_g_expansion_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'kappa_t' ) 
                    out_val(idk,idl,idm,idm)=ice_air_g_kappa_t_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'lapserate' ) 
                    out_val(idk,idl,idm,idm)=ice_air_g_lapserate_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'solidraction' ) 
                    out_val(idk,idl,idm,idm)=ice_air_solidfraction_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'vapourfraction' ) 
                    out_val(idk,idl,idm,idm)=ice_air_vapourfraction_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
            end select
    enddo
    enddo
    enddo
    enddo
end subroutine ice_air_g

subroutine ice_air_h(in_name, in_q,in_s,in_p, k, l, m, n, out_val)
    !This subroutine is a wrapper for the Gibbs function formulation of wet air thermodynamics
    !Available routines taking q, s, p as arguments unles otherwise noted:
    !
    ! Liq_Air_4c:
    ! cp
    ! density
    ! kappa_s
    ! temperature
    ! lapserate

    use ice_air_4c
    implicit none
    integer :: k, l, m, n, idk, idl, idm, idn
    real(8) :: in_q(k,l,m,n), in_s(k,l,m,n), in_p(k,l,m,n)
    real(8) :: out_val(k,l,m,n)
    character (len = *) :: in_name

!f2py real(8), intent(out), dimension(k,l,m,n) :: out_val
!f2py real(8), intent(in), dimension(k,l,m,n) :: in_q, in_s, in_p
!f2py character(len = *), intent(in) :: in_name
!f2py integer, intent(in) :: k,l,m,n

    do idk=1,k
    do idl=1,l
    do idm=1,m
    do idn=1,n
            select case( in_name )
                case( 'cp' ) 
                    out_val(idk,idl,idm,idm)=ice_air_h_cp_si(in_q(idk,idl,idm,idm),&
                    in_s(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'density' ) 
                    out_val(idk,idl,idm,idm)=ice_air_h_density_si(in_q(idk,idl,idm,idm),&
                    in_s(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'kappa_s' ) 
                    out_val(idk,idl,idm,idm)=ice_air_h_kappa_s_si(in_q(idk,idl,idm,idm),&
                    in_s(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'temperature' ) 
                    out_val(idk,idl,idm,idm)=ice_air_h_temperature_si(in_q(idk,idl,idm,idm),&
                    in_s(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'lapserate' ) 
                    out_val(idk,idl,idm,idm)=ice_air_h_lapserate_si(in_q(idk,idl,idm,idm),&
                    in_s(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
            end select
    enddo
    enddo
    enddo
    enddo
end subroutine ice_air_h

subroutine ice_air_g_ref(in_name,in_q,in_t,in_p, in_ref, k, l, m, n, out_val)
    !This subroutine is a wrapper for the Gibbs function formulation of humid air thermodynamics.
    !All of these functions require a reference value
    !Available routines:
    !
    ! Liq_Air_4c
    ! potdensity
    ! potenthalpy
    ! pottemp

    use ice_air_4c
    implicit none
    integer :: k, l, m, n, idk, idl, idm, idn
    real(8) :: in_q(k,l,m,n), in_t(k,l,m,n), in_p(k,l,m,n)
    real(8) :: in_ref
    real(8) :: out_val(k,l,m,n)
    character (len = *) :: in_name

!f2py real(8), intent(out), dimension(k,l,m,n) :: out_val
!f2py real(8), intent(in), dimension(k,l,m,n) :: in_q, in_t, in_p
!f2py real(8), intent(in) :: in_ref
!f2py integer, intent(in) :: k,l,m,n
!f2py character(len = *), intent(in) :: in_name

    do idk=1,k
    do idl=1,l
    do idm=1,m
    do idn=1,n
            select case(in_name)
                case( 'potdensity' )
                    out_val(idk,idl,idm,idm)=ice_air_potdensity_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm), in_ref)
                case( 'potenthalpy' )
                    out_val(idk,idl,idm,idm)=ice_air_potenthalpy_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm), in_ref)
                case( 'pottemp' )
                    out_val(idk,idl,idm,idm)=ice_air_pottemp_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm), in_ref)
            end select
    enddo
    enddo
    enddo
    enddo
 
end subroutine ice_air_g_ref

subroutine liq_ice_air_sat(in_name,in_t,in_p, k, l, m, n, out_val)
    !This subroutine is a wrapper for the Gibbs function formulation for wet air saturation.
    !Available routines:
    !
    ! Liq_Air_4a:
    ! massfraction: t and p
    ! condensationpressure: a and t
    ! dewpoint: a and p
    !
    ! Liq_Ice_Air_4:
    ! ifl: isentropic freezing level: q and s
    ! iml: isentropic melting level: q and s

    use liq_ice_air_4
    use liq_ice_air_5
    implicit none
    integer :: k, l, m, n, idk, idl, idm, idn
    real(8) :: in_t(k,l,m,n), in_p(k,l,m,n)
    real(8) :: out_val(k,l,m,n)
    character (len = *) :: in_name

!f2py real(8), intent(out), dimension(k,l,m,n) :: out_val
!f2py real(8), intent(in), dimension(k,l,m,n) :: in_t, in_p
!f2py character(len = *), intent(in) :: in_name
!f2py integer, intent(in) :: k,l,m,n

    do idk=1,k
    do idl=1,l
    do idm=1,m
    do idn=1,n
            select case(in_name)
                !Liq_Ice_air_4:
                case( 'iml' )
                    out_val(idk,idl,idm,idm)=liq_ice_air_iml_si(&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'ifl' )
                    out_val(idk,idl,idm,idm)=liq_ice_air_ifl_si(&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'massfraction' )
                    out_val(idk,idl,idm,idm)=liq_ice_air_massfraction_air_si(&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case default
                    write(*,*) 'Unknown function'
            end select
    enddo
    enddo
    enddo
    enddo
 
end subroutine liq_ice_air_sat


subroutine liq_ice_air_g_ref(in_name,in_q,in_t,in_p, in_ref, k, l, m, n, out_val)
    !This subroutine is a wrapper for the Gibbs function formulation of humid air thermodynamics.
    !All of these functions require a reference value
    !Available routines:
    !
    ! Liq_Ice_Air_5
    ! pottemp
    ! pottemp_equi

    use liq_ice_air_5
    implicit none
    integer :: k, l, m, n, idk, idl, idm, idn
    real(8) :: in_q(k,l,m,n), in_t(k,l,m,n), in_p(k,l,m,n)
    real(8) :: in_ref
    real(8) :: out_val(k,l,m,n)
    character (len = *) :: in_name

!f2py real(8), intent(out), dimension(k,l,m,n) :: out_val
!f2py real(8), intent(in), dimension(k,l,m,n) :: in_q, in_t, in_p
!f2py real(8), intent(in) :: in_ref
!f2py integer, intent(in) :: k,l,m,n
!f2py character(len = *), intent(in) :: in_name

    do idk=1,k
    do idl=1,l
    do idm=1,m
    do idn=1,n
            select case(in_name)
                case( 'pottemp' )
                    out_val(idk,idl,idm,idm)=liq_ice_air_pottemp_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm), in_ref)
                case( 'pottemp_equi' )
                    out_val(idk,idl,idm,idm)=liq_ice_air_pottemp_equi_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm), in_ref)
                case( 'pottemp_equi_sat' )
                    out_val(idk,idl,idm,idm)=liq_ice_air_pottemp_equi_sat_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm), in_ref)
                !case( 'entropy_mixed' )
                !    out_val(idk,idl,idm,idm)=liq_ice_air_g_entropy_mixed_si(in_q(idk,idl,idm,idm),&
                !    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm), in_ref)
            end select
    enddo
    enddo
    enddo
    enddo
 
end subroutine liq_ice_air_g_ref

subroutine liq_ice_air_g(in_name,in_q,in_t,in_p, k, l, m, n, out_val)
    !This subroutine is a wrapper for the Gibbs function formulation of humid air thermodynamics.
    !All of these functions require a reference value
    !Available routines:
    !
    ! Liq_Ice_Air_5
    ! entropy

    use liq_ice_air_5
    implicit none
    integer :: k, l, m, n, idk, idl, idm, idn
    real(8) :: in_q(k,l,m,n), in_t(k,l,m,n), in_p(k,l,m,n)
    real(8) :: out_val(k,l,m,n)
    character (len = *) :: in_name

!f2py real(8), intent(out), dimension(k,l,m,n) :: out_val
!f2py real(8), intent(in), dimension(k,l,m,n) :: in_q, in_t, in_p
!f2py real(8), intent(in) :: in_ref
!f2py integer, intent(in) :: k,l,m,n
!f2py character(len = *), intent(in) :: in_name

    do idk=1,k
    do idl=1,l
    do idm=1,m
    do idn=1,n
            select case(in_name)
                case( 'entropy' )
                    out_val(idk,idl,idm,idm)=liq_ice_air_g_entropy_si(in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
                case( 'entropy_moist' )
                    out_val(idk,idl,idm,idm)=liq_ice_air_g_entropy_moist_si(&
                    in_q(idk,idl,idm,idm),&
                    in_t(idk,idl,idm,idm), in_p(idk,idl,idm,idm))
            end select
    enddo
    enddo
    enddo
    enddo
 
end subroutine liq_ice_air_g
