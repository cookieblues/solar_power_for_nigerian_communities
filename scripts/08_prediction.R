library(INLA)
library(maptools)
library(ggplot2)
library(raster)

set.seed(100)

df_train <- read.csv('data/processed/dhs/covariates.csv')
nga_shape <- rgdal::readOGR('data/nigeria_shapefile/gadm36_NGA_0.shp')

# Standardize years
df_train$DHSYEAR <- df_train$DHSYEAR - 2012

# Spatial mesh
nga_border <- unionSpatialPolygons(nga_shape, rep(1, nrow(nga_shape)))
nga_segment <- inla.sp2segment(nga_border)
mesh_spatial <- inla.mesh.2d(boundary = nga_segment, cutoff = 1.4, max.edge = 1.5, offset = c(0.1, 1))
#mesh_spatial <- inla.mesh.2d(boundary = nga_segment, cutoff = 0.5, max.edge = c(0.1, 1), offset = c(0.1, 1))

# Build SPDE model on the mesh
nga_spde <- inla.spde2.matern(mesh = mesh_spatial, alpha = 2)
# Make indices
indices <- inla.spde.make.index('s', n.spde = nga_spde$n.spde)

# Make projection matrix for train
coo <- as.matrix(df_train[, c('LONGNUM', 'LATNUM')])
A <- inla.spde.make.A(mesh = mesh_spatial, loc = coo)

# Stack with data for estimation and prediction
stk.e <- inla.stack(
    data = list(y = df_train$has_electricity),
    A = list(A, 1, 1, 1, 1, 1),
    effects = list(
        #data.frame(b0 = rep(1, nrow(coo))),
        s = indices,
        list(pop = df_train$population),
        list(lluc = df_train$landcover),
        list(year = df_train$DHSYEAR),
        list(ntl = df_train$ntl),
        list(pia = df_train$pia)
    ),
    tag = "train"
)

stk.full <- inla.stack(stk.e)

# Model formula
formula <- y ~ -1 + pop + factor(lluc) + year + ntl + pia + f(s, model = nga_spde)

# INLA call
res <- inla(
    formula,
    data = inla.stack.data(stk.full),
    family = 'binomial',
    Ntrials = c(df_train$total),
    control.predictor = list(
        A = inla.stack.A(stk.full),
        compute = TRUE
    ),
    verbose = TRUE,
    # control.compute = list(
    #     dic=TRUE,
    #     cpo=TRUE,
    #     config=TRUE
    # )
    control.compute=list(config = TRUE)
)

#load('data/r_model/validation_data.RData')


beta_fixed <- res$summary.fixed$mean
# #beta_names <- res$names.fixed

# rename
lulc <- rep(NA, nrow(df_train))
for (i in 2:8) {
  lulc[df_train$ctyp == i] <- beta_fixed[i]
}
df_train$Z <- df_train$pop * beta_fixed[1] +
              df_train$DHSYEAR * beta_fixed[9] +
              df_train$ntl * beta_fixed[10] +
              df_train$pia * beta_fixed[11] +
              lulc


predictor_z <- y ~ -1 + offset(Z) + f(u.field, model=nga_spde)

u.f <- inla.spde.make.index(name = 'u.field', n.spde = nga_spde$n.spde) # random field model 5 and 6
A_z <- inla.spde.make.A(mesh = mesh_spatial, loc = as.matrix(df_train[, c('LONGNUM', 'LATNUM')])) # A model 6


# Stacks
stack_z <- inla.stack(
    data = list(y = df_train$has_electricity),
    A = list(A_z, 1),
    effects = list(u.f, list(Z = df_train$Z)),
    tag = 'train'
)
stack_latn <- inla.stack(
    data = list(y = NA),
    A = list(1),
    effects = list(u.f),
    tag = 'latn'
)
stack_model <- do.call(inla.stack, list(stack_z, stack_latn))
ix_train <- inla.stack.index(stack_model, tag='train')
ix_latn <- inla.stack.index(stack_model, tag='latn')

# # Fit model
model <- inla(
    predictor_z,
    data = inla.stack.data(stack_model),
    family = 'binomial',
    Ntrials = c(df_train$total, rep(1, nrow(stack_latn$A))),
    control.predictor = list(A=inla.stack.A(stack_model) , compute=TRUE),
    control.inla = list(h=.03),
    control.compute = list(config = TRUE),
    verbose = TRUE
)

#save(model, file='data/r_model/model_predictions.RData')
#load('data/r_model/model_predictions.RData')
#source('code/5_inla_mesh.R')
#sigma_u <- 0.2811558



cnst <- list()
for (i in 1:7) {
    print(paste0('Starting year ', i))
    yi <- i + 2012
    
    lulc <- raster(paste0('data/r_model/lulc/', yi, '.tif'))
    for (j in 2:8) {
        lulc[lulc[] == j] <- beta_fixed[j]
    }
    
    ntl <- raster(paste0('data/r_model/ntl/', yi, '.tif'))
    #ntl[ntl[] > 100] <- NA
    pia <- raster(paste0('data/r_model/pia/', yi, '.tif'))
    pop <- raster(paste0('data/r_model/pop/', yi, '.tif'))
    mask <- !is.na(pop[]) & !is.na(pia[]) & !is.na(ntl[]) & !is.na(lulc[])
    #pop[is.na(pop)] <- 0
    #pop[!mask] <- NA
    new_cnst <- lulc[mask] + beta_fixed[1]*pop[mask] + beta_fixed[9]*i + beta_fixed[10]*ntl[mask] + beta_fixed[11]*pia[mask]
    cnst[[i]] <- new_cnst

    print('Done with predictor calculations.')

    # Projector matrix to interpolate nodes in mesh_spatial
    afr_mask <- xyFromCell(ntl, (1:length(mask))[mask])
    A_mask <- inla.spde.make.A(mesh = mesh_spatial, loc = as.matrix(afr_mask))

    num_samples <- 200
    post_samples <- inla.posterior.sample(n = num_samples, result = model)
    obj_names <- rownames(post_samples[[1]]$latent)
    rand_u_ix <- grepl('u.field', obj_names)
    #save(cnst, post_samples, obj_names, rand_u_ix, file = 'code_output/eta_simulations.RData')
    print('Done with posterior sampling.')

    empty_layer <- pop
    empty_layer[] <- NA
    eta_samples <- matrix(NA, nrow = nrow(A_mask) , ncol = num_samples)

    aux <- rep(0, nrow(A_mask))
    for (j in 1:num_samples) {
        aux <- aux + 1 / (1 + exp(-as.numeric(A_mask %*% post_samples[[j]]$latent[rand_u_ix] + cnst[[i]])))
    }
    print('Start writing array to raster.')
    eta_samples[,i] <- aux/num_samples
    empty_layer[mask] <- eta_samples[, i]
    names(empty_layer) <- paste0('Electricity_', i + 2012)
    filename <- paste0('data/r_model/electricity/electricity_', i + 2012, sep = '')
    writeRaster(empty_layer, filename, format = 'GTiff', overwrite = TRUE)
}
