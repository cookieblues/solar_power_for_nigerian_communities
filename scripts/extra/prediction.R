library(INLA)
library(maptools)
library(ggplot2)

set.seed(100)

nga_shape <- rgdal::readOGR('data/nigeria_shapefile/gadm36_NGA_0.shp')
df_train <- read.csv('data/processed/dhs/covariates.csv')
df_test <- read.csv('data/r_model/prediction_data.csv')

# Standardize years
df_train$DHSYEAR <- df_train$DHSYEAR - 2012
df_test$DHSYEAR <- df_test$DHSYEAR - 2012

# Spatial mesh
nga_border <- unionSpatialPolygons(nga_shape, rep(1, nrow(nga_shape)))
nga_segment <- inla.sp2segment(nga_border)
#mesh_spatial <- inla.mesh.2d(boundary = nga_segment, max.edge = c(0.1, 3), cutoff = 2.9)
mesh_spatial <- inla.mesh.2d(boundary = nga_segment, cutoff = 0.25, max.edge = c(0.1, 1), offset = c(0.1, 1))

# Build SPDE model on the mesh
nga_spde <- inla.spde2.matern(mesh = mesh_spatial, alpha = 2)
# Make indices
indices <- inla.spde.make.index('s', n.spde = nga_spde$n.spde)

# Make projection matrix for train
coo <- as.matrix(df_train[, c('LONGNUM', 'LATNUM')])
A <- inla.spde.make.A(mesh = mesh_spatial, loc = coo)

# Make projection matrix for test
coop <- as.matrix(df_test[, c('LONGNUM', 'LATNUM')])
Ap <- inla.spde.make.A(mesh = mesh_spatial, loc = coop)

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

stk.p <- inla.stack(
    data = list(y = NA),
    A = list(Ap, 1, 1, 1, 1, 1),
    effects = list(
        #data.frame(b0 = rep(1, nrow(coop))),
        s = indices,
        list(pop = df_test$population),
        list(lluc = df_test$landcover),
        list(year = df_test$DHSYEAR),
        list(ntl = df_test$ntl),
        list(pia = df_test$pia)
    ),
    tag = "test"
)

stk.full <- inla.stack(stk.e, stk.p)

# Model formula
formula <- y ~ -1 + pop + factor(lluc) + year + ntl + pia + f(s, model = nga_spde)

# INLA call
res <- inla(
    formula,
    data = inla.stack.data(stk.full),
    family = 'binomial',
    Ntrials = c(df_train$total, df_test$total),
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

index <- inla.stack.index(stk.full, tag = "test")$data

pred_mean <- res$summary.fitted.values[index, "mean"]
pred_ll <- res$summary.fitted.values[index, "0.025quant"]
pred_ul <- res$summary.fitted.values[index, "0.975quant"]

pred_mean <- 1/(1+exp(-pred_mean))
pred_ll <- 1/(1+exp(-pred_ll))
pred_ul <- 1/(1+exp(-pred_ul))


