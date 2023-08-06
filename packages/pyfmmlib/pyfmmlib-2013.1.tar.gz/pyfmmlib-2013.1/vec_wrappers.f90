subroutine triangle_norm_vec(triangles, trinorm, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  real*8, intent(in) :: triangles(3,3,nvcount)
  real*8, intent(out) :: trinorm(3,nvcount)

  !$omp parallel do
  do ivcount = 1, nvcount
    call triangle_norm( &
      triangles(1, 1, ivcount), trinorm(1, ivcount) &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine triangle_area_vec(triangles, triarea, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  real*8, intent(in) :: triangles(3,3,nvcount)
  real*8, intent(out) :: triarea(nvcount)

  !$omp parallel do
  do ivcount = 1, nvcount
    call triangle_area( &
      triangles(1, 1, ivcount), triarea(ivcount) &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine ylgndr_vec(nmax, x, y, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  integer, intent(in) :: nmax
  real *8, intent(in) :: x(nvcount)
  real *8, intent(out) :: y(0:nmax,0:nmax,nvcount)

  !$omp parallel do
  do ivcount = 1, nvcount
    call ylgndr( &
      nmax, x(ivcount), y(0, 0, ivcount) &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine hank103_vec(z, h0, h1, ifexpon, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  complex*16, intent(in) :: z(nvcount)
  complex*16, intent(out) :: h0(nvcount)
  complex*16, intent(out) :: h1(nvcount)
  integer, intent(in) :: ifexpon

  !$omp parallel do
  do ivcount = 1, nvcount
    call hank103( &
      z(ivcount), h0(ivcount), h1(ivcount), ifexpon &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine legefder_vec(x, val, der, pexp, n, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  real*8, intent(in) :: x(nvcount)
  real*8, intent(out) :: val(nvcount)
  real*8, intent(out) :: der(nvcount)
  real*8, intent(in) :: pexp(n+1)
  integer, intent(in) :: n

  !$omp parallel do
  do ivcount = 1, nvcount
    call legefder( &
      x(ivcount), val(ivcount), der(ivcount), pexp, n &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine lpotgrad2dall_vec(ifgrad, ifhess, sources, charge, nsources, targets, pot, grad, hess, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  integer, intent(in) :: ifgrad
  integer, intent(in) :: ifhess
  real *8, intent(in) :: sources(2,nsources)
  complex *16, intent(in) :: charge(nsources)
  integer, intent(in) :: nsources
  real *8, intent(in) :: targets(2,nvcount)
  complex *16, intent(out) :: pot(nvcount)
  complex *16, intent(out) :: grad(2,nvcount)
  complex *16, intent(out) :: hess(3,nvcount)

  !$omp parallel do
  do ivcount = 1, nvcount
    call lpotgrad2dall( &
      ifgrad, ifhess, sources, charge, nsources, targets(1, ivcount),  &
      pot(ivcount), grad(1, ivcount), hess(1, ivcount) &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine lpotfld3dall_vec(iffld, sources, charge, nsources, targets, pot, fld, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  integer, intent(in) :: iffld
  real *8, intent(in) :: sources(3,nsources)
  complex *16, intent(in) :: charge(nsources)
  integer, intent(in) :: nsources
  real *8, intent(in) :: targets(3,nvcount)
  complex *16, intent(out) :: pot(nvcount)
  complex *16, intent(out) :: fld(3,nvcount)

  !$omp parallel do
  do ivcount = 1, nvcount
    call lpotfld3dall( &
      iffld, sources, charge, nsources, targets(1, ivcount), pot(ivcount),  &
      fld(1, ivcount) &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine hpotgrad2dall_vec(ifgrad, ifhess, sources, charge, nsources, targets, zk, pot, grad, hess, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  integer, intent(in) :: ifgrad
  integer, intent(in) :: ifhess
  real *8, intent(in) :: sources(2,nsources)
  complex *16, intent(in) :: charge(nsources)
  integer, intent(in) :: nsources
  real *8, intent(in) :: targets(2,nvcount)
  complex *16, intent(in) :: zk
  complex *16, intent(out) :: pot(nvcount)
  complex *16, intent(out) :: grad(2,nvcount)
  complex *16, intent(out) :: hess(3,nvcount)

  !$omp parallel do
  do ivcount = 1, nvcount
    call hpotgrad2dall( &
      ifgrad, ifhess, sources, charge, nsources, targets(1, ivcount),  &
      zk, pot(ivcount), grad(1, ivcount), hess(1, ivcount) &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine hpotfld3dall_vec(iffld, sources, charge, nsources, targets, zk, pot, fld, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  integer, intent(in) :: iffld
  real *8, intent(in) :: sources(3,nsources)
  complex *16, intent(in) :: charge(nsources)
  integer, intent(in) :: nsources
  real *8, intent(in) :: targets(3,nvcount)
  complex *16, intent(in) :: zk
  complex *16, intent(out) :: pot(nvcount)
  complex *16, intent(out) :: fld(3,nvcount)

  !$omp parallel do
  do ivcount = 1, nvcount
    call hpotfld3dall( &
      iffld, sources, charge, nsources, targets(1, ivcount), zk, pot(ivcount),  &
      fld(1, ivcount) &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine lpotgrad2dall_dp_vec(ifgrad, ifhess, sources, dipstr, dipvec, nsources, targets, pot, grad, hess, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  integer, intent(in) :: ifgrad
  integer, intent(in) :: ifhess
  real *8, intent(in) :: sources(2,nsources)
  complex *16, intent(in) :: dipstr(nsources)
  real*8, intent(in) :: dipvec(2,nsources)
  integer, intent(in) :: nsources
  real *8, intent(in) :: targets(2,nvcount)
  complex *16, intent(out) :: pot(nvcount)
  complex *16, intent(out) :: grad(2,nvcount)
  complex *16, intent(out) :: hess(3,nvcount)

  !$omp parallel do
  do ivcount = 1, nvcount
    call lpotgrad2dall_dp( &
      ifgrad, ifhess, sources, dipstr, dipvec, nsources, targets(1, ivcount),  &
      pot(ivcount), grad(1, ivcount), hess(1, ivcount) &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine lpotfld3dall_dp_vec(iffld, sources, dipstr, dipvec, nsources, targets, pot, fld, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  integer, intent(in) :: iffld
  real *8, intent(in) :: sources(3,nsources)
  complex *16, intent(in) :: dipstr(nsources)
  real*8, intent(in) :: dipvec(3,nsources)
  integer, intent(in) :: nsources
  real *8, intent(in) :: targets(3,nvcount)
  complex *16, intent(out) :: pot(nvcount)
  complex *16, intent(out) :: fld(3,nvcount)

  !$omp parallel do
  do ivcount = 1, nvcount
    call lpotfld3dall_dp( &
      iffld, sources, dipstr, dipvec, nsources, targets(1, ivcount), pot(ivcount),  &
      fld(1, ivcount) &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine hpotgrad2dall_dp_vec(ifgrad, ifhess, sources, dipstr, dipvec, nsources, targets, zk, pot, grad, hess, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  integer, intent(in) :: ifgrad
  integer, intent(in) :: ifhess
  real *8, intent(in) :: sources(2,nsources)
  complex *16, intent(in) :: dipstr(nsources)
  real*8, intent(in) :: dipvec(2,nsources)
  integer, intent(in) :: nsources
  real *8, intent(in) :: targets(2,nvcount)
  complex *16, intent(in) :: zk
  complex *16, intent(out) :: pot(nvcount)
  complex *16, intent(out) :: grad(2,nvcount)
  complex *16, intent(out) :: hess(3,nvcount)

  !$omp parallel do
  do ivcount = 1, nvcount
    call hpotgrad2dall_dp( &
      ifgrad, ifhess, sources, dipstr, dipvec, nsources, targets(1, ivcount),  &
      zk, pot(ivcount), grad(1, ivcount), hess(1, ivcount) &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine hpotfld3dall_dp_vec(iffld, sources, dipstr, dipvec, nsources, targets, zk, pot, fld, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  integer, intent(in) :: iffld
  real *8, intent(in) :: sources(3,nsources)
  complex *16, intent(in) :: dipstr(nsources)
  real*8, intent(in) :: dipvec(3,nsources)
  integer, intent(in) :: nsources
  real *8, intent(in) :: targets(3,nvcount)
  complex *16, intent(in) :: zk
  complex *16, intent(out) :: pot(nvcount)
  complex *16, intent(out) :: fld(3,nvcount)

  !$omp parallel do
  do ivcount = 1, nvcount
    call hpotfld3dall_dp( &
      iffld, sources, dipstr, dipvec, nsources, targets(1, ivcount), zk,  &
      pot(ivcount), fld(1, ivcount) &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine h3dtaeval_vec(zk, rscale, center, locexp, nterms, ztarg, pot, iffld, fld, ier, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  complex*16, intent(in) :: zk
  real*8, intent(in) :: rscale
  real*8, intent(in) :: center(3)
  complex*16, intent(in) :: locexp(0:nterms,-nterms:nterms)
  integer, intent(in) :: nterms
  real*8, intent(in) :: ztarg(3,nvcount)
  complex*16, intent(out) :: pot(nvcount)
  integer, intent(in) :: iffld
  complex*16, intent(out) :: fld(3,nvcount)
  integer, intent(out) :: ier(nvcount)

  !$omp parallel do
  do ivcount = 1, nvcount
    call h3dtaeval( &
      zk, rscale, center, locexp, nterms, ztarg(1, ivcount), pot(ivcount),  &
      iffld, fld(1, ivcount), ier(ivcount) &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine l2dtaeval_vec(rscale, center, mpole, nterms, ztarg, pot, ifgrad, grad, ifhess, hess, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  real*8, intent(in) :: rscale
  real*8, intent(in) :: center(2)
  complex*16, intent(in) :: mpole(-nterms:nterms)
  integer, intent(in) :: nterms
  real*8, intent(in) :: ztarg(2,nvcount)
  complex*16, intent(out) :: pot(nvcount)
  integer, intent(in) :: ifgrad
  complex*16, intent(out) :: grad(2,nvcount)
  integer, intent(in) :: ifhess
  complex*16, intent(out) :: hess(3,nvcount)

  !$omp parallel do
  do ivcount = 1, nvcount
    call l2dtaeval( &
      rscale, center, mpole, nterms, ztarg(1, ivcount), pot(ivcount),  &
      ifgrad, grad(1, ivcount), ifhess, hess(1, ivcount) &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine l2dmpeval_vec(rscale, center, mpole, nterms, ztarg, pot, ifgrad, grad, ifhess, hess, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  real*8, intent(in) :: rscale
  real*8, intent(in) :: center(2)
  complex*16, intent(in) :: mpole(-nterms:nterms)
  integer, intent(in) :: nterms
  real*8, intent(in) :: ztarg(2,nvcount)
  complex*16, intent(out) :: pot(nvcount)
  integer, intent(in) :: ifgrad
  complex*16, intent(out) :: grad(2,nvcount)
  integer, intent(in) :: ifhess
  complex*16, intent(out) :: hess(3,nvcount)

  !$omp parallel do
  do ivcount = 1, nvcount
    call l2dmpeval( &
      rscale, center, mpole, nterms, ztarg(1, ivcount), pot(ivcount),  &
      ifgrad, grad(1, ivcount), ifhess, hess(1, ivcount) &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine l3dtaevalhess_1tgtperexp(rscale, center, mpole, nterms, ztarg, pot, ifgrad, grad, ifhess, hess, ier, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  real*8, intent(in) :: rscale(nvcount)
  real*8, intent(in) :: center(3,nvcount)
  complex *16, intent(in) :: mpole(0:nterms,-nterms:nterms,nvcount)
  integer, intent(in) :: nterms
  real*8, intent(in) :: ztarg(3,nvcount)
  complex*16, intent(out) :: pot(nvcount)
  integer, intent(in) :: ifgrad
  complex*16, intent(out) :: grad(3,nvcount)
  integer, intent(in) :: ifhess
  complex*16, intent(out) :: hess(6,nvcount)
  integer, intent(out) :: ier

  !$omp parallel do
  do ivcount = 1, nvcount
    call l3dtaevalhess( &
      rscale(ivcount), center(1, ivcount), mpole(0, -nterms, ivcount),  &
      nterms, ztarg(1, ivcount), pot(ivcount), ifgrad, grad(1, ivcount),  &
      ifhess, hess(1, ivcount), ier &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine h2dtaeval_vec(zk, rscale, center, mpole, nterms, ztarg, pot, ifgrad, grad, ifhess, hess, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  complex*16, intent(in) :: zk
  real*8, intent(in) :: rscale
  real*8, intent(in) :: center(2)
  complex*16, intent(in) :: mpole(-nterms:nterms)
  integer, intent(in) :: nterms
  real*8, intent(in) :: ztarg(2,nvcount)
  complex*16, intent(out) :: pot(nvcount)
  integer, intent(in) :: ifgrad
  complex*16, intent(out) :: grad(2,nvcount)
  integer, intent(in) :: ifhess
  complex*16, intent(out) :: hess(3,nvcount)

  !$omp parallel do
  do ivcount = 1, nvcount
    call h2dtaeval( &
      zk, rscale, center, mpole, nterms, ztarg(1, ivcount), pot(ivcount),  &
      ifgrad, grad(1, ivcount), ifhess, hess(1, ivcount) &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine h2dmpeval_vec(zk, rscale, center, mpole, nterms, ztarg, pot, ifgrad, grad, ifhess, hess, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  complex*16, intent(in) :: zk
  real*8, intent(in) :: rscale
  real*8, intent(in) :: center(2)
  complex*16, intent(in) :: mpole(-nterms:nterms)
  integer, intent(in) :: nterms
  real*8, intent(in) :: ztarg(2,nvcount)
  complex*16, intent(out) :: pot(nvcount)
  integer, intent(in) :: ifgrad
  complex*16, intent(out) :: grad(2,nvcount)
  integer, intent(in) :: ifhess
  complex*16, intent(out) :: hess(3,nvcount)

  !$omp parallel do
  do ivcount = 1, nvcount
    call h2dmpeval( &
      zk, rscale, center, mpole, nterms, ztarg(1, ivcount), pot(ivcount),  &
      ifgrad, grad(1, ivcount), ifhess, hess(1, ivcount) &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine h3dtaeval_1tgtperexp(zk, rscale, center, mpole, nterms, ztarg, pot, ifgrad, grad, ier, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  complex*16, intent(in) :: zk
  real*8, intent(in) :: rscale(nvcount)
  real*8, intent(in) :: center(3,nvcount)
  complex *16, intent(in) :: mpole(0:nterms,-nterms:nterms,nvcount)
  integer, intent(in) :: nterms
  real*8, intent(in) :: ztarg(3,nvcount)
  complex*16, intent(out) :: pot(nvcount)
  integer, intent(in) :: ifgrad
  complex*16, intent(out) :: grad(3,nvcount)
  integer, intent(out) :: ier

  !$omp parallel do
  do ivcount = 1, nvcount
    call h3dtaeval( &
      zk, rscale(ivcount), center(1, ivcount), mpole(0, -nterms, ivcount),  &
      nterms, ztarg(1, ivcount), pot(ivcount), ifgrad, grad(1, ivcount),  &
      ier &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine l2dmpmp_vec(rscale1, center1, expn1, nterms1, rscale2, center2, expn2, nterms2, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  real*8, intent(in) :: rscale1(nvcount)
  real*8, intent(in) :: center1(2,nvcount)
  complex*16, intent(in) :: expn1(0:nterms1,nvcount)
  integer, intent(in) :: nterms1
  real*8, intent(in) :: rscale2(nvcount)
  real*8, intent(in) :: center2(2,nvcount)
  complex*16, intent(out) :: expn2(0:nterms2,nvcount)
  integer, intent(in) :: nterms2

  !$omp parallel do
  do ivcount = 1, nvcount
    call l2dmpmp( &
      rscale1(ivcount), center1(1, ivcount), expn1(0, ivcount), nterms1,  &
      rscale2(ivcount), center2(1, ivcount), expn2(0, ivcount), nterms2 &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine l2dmploc_vec(rscale1, center1, expn1, nterms1, rscale2, center2, expn2, nterms2, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  real*8, intent(in) :: rscale1(nvcount)
  real*8, intent(in) :: center1(2,nvcount)
  complex*16, intent(in) :: expn1(0:nterms1,nvcount)
  integer, intent(in) :: nterms1
  real*8, intent(in) :: rscale2(nvcount)
  real*8, intent(in) :: center2(2,nvcount)
  complex*16, intent(out) :: expn2(0:nterms2,nvcount)
  integer, intent(in) :: nterms2

  !$omp parallel do
  do ivcount = 1, nvcount
    call l2dmploc( &
      rscale1(ivcount), center1(1, ivcount), expn1(0, ivcount), nterms1,  &
      rscale2(ivcount), center2(1, ivcount), expn2(0, ivcount), nterms2 &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine l2dlocloc_vec(rscale1, center1, expn1, nterms1, rscale2, center2, expn2, nterms2, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  real*8, intent(in) :: rscale1(nvcount)
  real*8, intent(in) :: center1(2,nvcount)
  complex*16, intent(in) :: expn1(0:nterms1,nvcount)
  integer, intent(in) :: nterms1
  real*8, intent(in) :: rscale2(nvcount)
  real*8, intent(in) :: center2(2,nvcount)
  complex*16, intent(out) :: expn2(0:nterms2,nvcount)
  integer, intent(in) :: nterms2

  !$omp parallel do
  do ivcount = 1, nvcount
    call l2dlocloc( &
      rscale1(ivcount), center1(1, ivcount), expn1(0, ivcount), nterms1,  &
      rscale2(ivcount), center2(1, ivcount), expn2(0, ivcount), nterms2 &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine h2dmpmp_vec(zk, rscale1, center1, expn1, nterms1, rscale2, center2, expn2, nterms2, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  complex*16, intent(in) :: zk
  real*8, intent(in) :: rscale1(nvcount)
  real*8, intent(in) :: center1(2,nvcount)
  complex*16, intent(in) :: expn1(-(nterms1):nterms1,nvcount)
  integer, intent(in) :: nterms1
  real*8, intent(in) :: rscale2(nvcount)
  real*8, intent(in) :: center2(2,nvcount)
  complex*16, intent(out) :: expn2(-(nterms2):nterms2,nvcount)
  integer, intent(in) :: nterms2

  !$omp parallel do
  do ivcount = 1, nvcount
    call h2dmpmp( &
      zk, rscale1(ivcount), center1(1, ivcount), expn1(-(nterms1), ivcount),  &
      nterms1, rscale2(ivcount), center2(1, ivcount), expn2(-(nterms2), ivcount),  &
      nterms2 &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine h2dmploc_vec(zk, rscale1, center1, expn1, nterms1, rscale2, center2, expn2, nterms2, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  complex*16, intent(in) :: zk
  real*8, intent(in) :: rscale1(nvcount)
  real*8, intent(in) :: center1(2,nvcount)
  complex*16, intent(in) :: expn1(-(nterms1):nterms1,nvcount)
  integer, intent(in) :: nterms1
  real*8, intent(in) :: rscale2(nvcount)
  real*8, intent(in) :: center2(2,nvcount)
  complex*16, intent(out) :: expn2(-(nterms2):nterms2,nvcount)
  integer, intent(in) :: nterms2

  !$omp parallel do
  do ivcount = 1, nvcount
    call h2dmploc( &
      zk, rscale1(ivcount), center1(1, ivcount), expn1(-(nterms1), ivcount),  &
      nterms1, rscale2(ivcount), center2(1, ivcount), expn2(-(nterms2), ivcount),  &
      nterms2 &
      )
  enddo
  !$omp end parallel do

  return
end

subroutine h2dlocloc_vec(zk, rscale1, center1, expn1, nterms1, rscale2, center2, expn2, nterms2, nvcount)
  implicit none
  integer, intent(in) :: nvcount
  integer ivcount
  complex*16, intent(in) :: zk
  real*8, intent(in) :: rscale1(nvcount)
  real*8, intent(in) :: center1(2,nvcount)
  complex*16, intent(in) :: expn1(-(nterms1):nterms1,nvcount)
  integer, intent(in) :: nterms1
  real*8, intent(in) :: rscale2(nvcount)
  real*8, intent(in) :: center2(2,nvcount)
  complex*16, intent(out) :: expn2(-(nterms2):nterms2,nvcount)
  integer, intent(in) :: nterms2

  !$omp parallel do
  do ivcount = 1, nvcount
    call h2dlocloc( &
      zk, rscale1(ivcount), center1(1, ivcount), expn1(-(nterms1), ivcount),  &
      nterms1, rscale2(ivcount), center2(1, ivcount), expn2(-(nterms2), ivcount),  &
      nterms2 &
      )
  enddo
  !$omp end parallel do

  return
end
