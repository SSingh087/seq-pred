import numpy as np
import scipy
import matplotlib.pyplot as plt
from astropy.cosmology import default_cosmology
import lenstronomy.Util.util as util
import lenstronomy.Util.image_util as image_util
from lenstronomy.Cosmo.lens_cosmo import LensCosmo
from lenstronomy.LensModel.lens_model import LensModel
from lenstronomy.LightModel.Profiles.shapelets import ShapeletSet
from lenstronomy.LightModel.light_model import LightModel
from lenstronomy.LightModel.Profiles.interpolation import Interpol
import PIL
from tqdm import tqdm

z_lens = 0.05
z_source = .02
M200 = 10**15
concentration = 3
numPix = 100
deltaPix = 0.05
high_res_factor = 2
n_max = 50
beta = 1
factor = 1
sigma = 5

cen = np.linspace(-1,1,11)
for i in (range(30,91,30)):
  for j in tqdm(range(30,91,30)):
    for k in range(1,2): 
      for ii in (range(1,11)):
          main_halo_type = 'SIE'  # You have many other possibilities available. Check out the SinglePlane class!
          kwargs_lens_main = {'theta_E': 1., 'e1': 0.1, 'e2': 0, 'center_x': cen[ii], 'center_y': 0}
          kwargs_shear = {'gamma1': 0.05, 'gamma2': 0}
          lens_model_list = [main_halo_type, 'SHEAR']
          kwargs_lens_list = [kwargs_lens_main, kwargs_shear]

          lensModel = LensModel(lens_model_list)
          x_grid, y_grid = util.make_grid(numPix=500, deltapix=0.05)
          kappa = lensModel.kappa(x_grid, y_grid, kwargs_lens_list)
          kappa = util.array2image(kappa)

          cosmo = default_cosmology.get()          
          lensCosmo = LensCosmo(z_lens=z_lens, z_source=z_source, cosmo=cosmo)

          Rs_angle_clump, theta_Rs_clump = lensCosmo.nfw_physical2angle(M=M200, c=concentration)
          rho0_clump, Rs_clump, c_clump, r200_clump, M200_clump = lensCosmo.nfw_angle2physical(Rs_angle_clump, theta_Rs_clump)
          loc = "P_0_"+str(i)+'_'+str(j)+'_'+str(k)+"_("+str(ii)
          ngc_data = PIL.Image.open(<loc>)
          ngc_data = np.asarray(ngc_data)/255
          ngc_conv = scipy.ndimage.filters.gaussian_filter(ngc_data, sigma, mode='nearest', truncate=6)

          numPix_large = int(len(ngc_conv)/factor)
          n_new = int((numPix_large-1)*factor)
          ngc_cut = ngc_conv[0:n_new,0:n_new]
          x, y = util.make_grid(numPix=numPix_large-1, deltapix=1)
          ngc_data_resized = image_util.re_size(ngc_cut, factor)  

          image_1d = util.image2array(ngc_data_resized) 
          shapeletSet = ShapeletSet()
          coeff_ngc = shapeletSet.decomposition(image_1d, x, y, n_max, beta, 1., center_x=0, center_y=0) 

          image_reconstructed = shapeletSet.function(x, y, coeff_ngc, n_max, beta, center_x=0, center_y=0)
          image_reconstructed_2d = util.array2image(image_reconstructed)

          theta_x_high_res, theta_y_high_res = util.make_grid(numPix=numPix*high_res_factor,
                                                              deltapix=deltaPix/high_res_factor)
          beta_x_high_res, beta_y_high_res = lensModel.ray_shooting(theta_x_high_res, theta_y_high_res,
                                                                      kwargs=kwargs_lens_list)
          source_lensed = shapeletSet.function(beta_x_high_res, beta_y_high_res,
                                              coeff_ngc, n_max, beta=.05,
                                              center_x=cen[ii], center_y=0)

          source_lensed = util.array2image(source_lensed)
          kwargs_interp = {'image': ngc_data_resized, 'center_x': 0, 'center_y': 0, 'scale': 0.005, 'phi_G':0.2}

          interp_light = Interpol()
          source_lensed_interp = interp_light.function(beta_x_high_res, beta_y_high_res, **kwargs_interp)
          source_lensed_interp = util.array2image(source_lensed_interp)

          light_model_list = ['SERSIC_ELLIPSE', 'SERSIC_ELLIPSE','NIE']
          kwargs_lens_light = [
              {'amp':  .3, 'R_sersic': 0.04, 'n_sersic': 0.3, 'e1': 0, 'e2': 0, 'center_x': 0, 'center_y': 0},
              {'amp': .01, 'R_sersic': 0.05, 'n_sersic': 0.2, 'e1': 0, 'e2': 0, 'center_x': 0, 'center_y': 0},
              {'amp': .05, 'e1':.5, 'e2':.4, 's_scale':1}
          ]
          lensLightModel = LightModel(light_model_list=light_model_list)

          flux_lens_light = lensLightModel.surface_brightness(theta_x_high_res, theta_y_high_res, kwargs_lens_light)
          flux_lens_light = util.array2image(flux_lens_light)
          image_combined = source_lensed_interp + flux_lens_light
