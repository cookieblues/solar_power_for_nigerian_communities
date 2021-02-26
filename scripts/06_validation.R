library(INLA)
library(maptools)
library(ggplot2)

set.seed(100)

df <- read.csv('data/processed/dhs/covariates.csv')
nga_shape <- rgdal::readOGR('data/nigeria_shapefile/gadm36_NGA_0.shp')

# Standardize years
df$DHSYEAR <- df$DHSYEAR - 2012

# Split data
# df <- subset(df, DHSYEAR <= 2015)
# N_train <- round(nrow(df)*0.1)
# shuffled_idxs <- sample(1:nrow(df))
# df_train <- df[shuffled_idxs[1:N_train],]
# df_test <- df[shuffled_idxs[(1+N_train):nrow(df)],]
# COLUMNS: "has_electricity", "ntl", "landcover", "population", "total", "LONGNUM", "LATNUM", "DHSYEAR"
df_train <- subset(df, DHSYEAR <= 3)
df_test <- subset(df, DHSYEAR > 3)
#df_test <- read.csv('data/r_model/prediction_data.csv')
#df_test$DHSYEAR <- df_test$DHSYEAR - 2012

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

# Make projection matrix for test
coop <- as.matrix(df_test[, c('LONGNUM', 'LATNUM')])
Ap <- inla.spde.make.A(mesh = mesh_spatial, loc = coop)


# Prediction data, takes a X by Y grid of pixels from the shape
# bb <- bbox(nga_shape)
# x <- seq(bb[1, 'min'] - 1, bb[1, 'max'] + 1, length.out = 50)
# y <- seq(bb[2, 'min'] - 1, bb[2, 'max'] + 1, length.out = 50)
# coop <- as.matrix(expand.grid(x, y))

# ind <- point.in.polygon(
#   coop[, 1], coop[, 2],
#   nga_segment$loc[, 1], nga_segment$loc[, 2]
# )
# coop <- coop[which(ind == 1), ]
# Ap <- inla.spde.make.A(mesh = mesh_spatial, loc = coop)

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

save(
  df_train,
  df_test,
  stk.full,
  indices,
  res,
  mesh_spatial,
  nga_spde,
  file='data/r_model/validation_data.RData'
)
#load('data/r_model/validation_data.RData')

# Results
# index <- inla.stack.index(stk.full, tag = "pred")$data
# pred_mean <- res$summary.fitted.values[index, "mean"]
# pred_ll <- res$summary.fitted.values[index, "0.025quant"]
# pred_ul <- res$summary.fitted.values[index, "0.975quant"]


# dpm <- rbind(
#   data.frame(
#     east = coop[, 1], north = coop[, 2],
#     value = pred_mean, variable = 'pred_mean'
#   ),
#   data.frame(
#     east = coop[, 1], north = coop[, 2],
#     value = pred_ll, variable = 'pred_ll'
#   ),
#   data.frame(
#     east = coop[, 1], north = coop[, 2],
#     value = pred_ul, variable = 'pred_ul'
#   )
# )
# dpm$variable <- as.factor(dpm$variable)

# ggplot(dpm) + geom_tile(aes(east, north, fill = value)) +
#   coord_fixed(ratio = 1) +
#   scale_fill_gradient(
#     name = "Prob of electricity",
#     low = "blue", high = "orange"
#   ) +
#   theme_bw()

# # Projecting the spatial field
# rang <- apply(mesh_spatial$loc[, c(1, 2)], 2, range)
# proj <- inla.mesh.projector(mesh_spatial,
#   xlim = rang[, 1], ylim = rang[, 2],
#   dims = c(300, 300)
# )
# mean_s <- inla.mesh.project(proj, res$summary.random$s$mean)
# sd_s <- inla.mesh.project(proj, res$summary.random$s$sd)

# df <- expand.grid(x = proj$x, y = proj$y)
# df$mean_s <- as.vector(mean_s)
# df$sd_s <- as.vector(sd_s)

# library(viridis)
# library(cowplot)

# gmean <- ggplot(df, aes(x = x, y = y, fill = mean_s)) +
#   geom_raster() +
#   scale_fill_viridis(na.value = "transparent") +
#   coord_fixed(ratio = 1) + theme_bw()

# gsd <- ggplot(df, aes(x = x, y = y, fill = sd_s)) +
#   geom_raster() +
#   scale_fill_viridis(na.value = "transparent") +
#   coord_fixed(ratio = 1) + theme_bw()
