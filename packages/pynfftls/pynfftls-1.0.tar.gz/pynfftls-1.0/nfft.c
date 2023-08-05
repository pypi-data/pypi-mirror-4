/** \file nfft.c
 * Nonuniform Fourier Transforms.
 *
 * \author B. Leroy
 *
 * This file is part of nfftls.
 *
 * Nfftls is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Nfftls is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with nfftls.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Copyright (C) 2012 by B. Leroy
 */
#include <math.h>
#include <complex.h>
#include <nfft/nfft3.h>
#include <stdlib.h>
#include <string.h>

#include "nfft.h"
#include "utils.h"

/* Computation of the positive frequency
* part of the ( unnormalised ) Fourier
* transform of a real times -series (t, y).
*
* Input:
* t the times reduced to [1/2 , 1/2)
* y the measurements (NULL , for
*
computing the FT of the window )
* n the number of measurements
* m the number of positive frequencies
* Output :
* d the Fourier coefficients
*
( preallocated array for (m+1)
*
elements )
*/


void nfft(const double* t, const double* y, int n, int m,  double complex * d)
{
  nfft_plan p;
  nfft_init_1d(&p, 2 * m, n);

  if (y)			/* spectrum */
  {
    for (int i = 0; i < n; i++)
    {
      p.x[i] = t[i];
      p.f[i] = y[i];
    }
  }
  else				/* window */
  {
    for (int i = 0; i < n; i++)
    {
      p.x[i] = t[i];
      p.f[i] = 1.0;
    }
  }
  
  if (p.nfft_flags & PRE_ONE_PSI)
    nfft_precompute_one_psi(&p);

  nfft_adjoint(&p);


  for (int i = 0; i < m; i++)
    d[i] = p.f_hat[i + m];
  /*
   * NFFT plan produces Fourier components for
   * frequencies in an open interval [-m, m[;
   * but here we're working with the closed interval.
   */
  d[m] = conj(p.f_hat[0]);

  nfft_finalize(&p);
}


