library(INLA)
library(maptools)
library(ggplot2)
library(inlabru)

set.seed(100)

df <- read.csv('data/processed/dhs/covariates.csv')
nga_shape <- rgdal::readOGR('data/nigeria_shapefile/gadm36_NGA_0.shp')

# Split data
# df <- subset(df, DHSYEAR <= 2015)
# N_train <- round(nrow(df)*0.1)
# shuffled_idxs <- sample(1:nrow(df))
# df_train <- df[shuffled_idxs[1:N_train],]
# df_test <- df[shuffled_idxs[(1+N_train):nrow(df)],]
df_train <- subset(df, DHSYEAR <= 2015)
df_test <- subset(df, DHSYEAR > 2015)

# Spatial mesh
nga_border <- unionSpatialPolygons(nga_shape, rep(1, nrow(nga_shape)))
nga_segment <- inla.sp2segment(nga_border)
mesh_spatial <- inla.mesh.2d(boundary = nga_segment, cutoff = 1.4, max.edge = 1.5, offset = c(0.1, 1))
plot(mesh_spatial)
plot(nga_border, add=TRUE)

# Assessment
out <- inla.mesh.assessment(mesh_spatial,
                            spatial.range = 2,
                            alpha = 2,
                            dims = c(500, 500))
ggplot() + gg(out, aes(color = edge.len)) + coord_equal()


# Plot
plot(mesh_spatial)
plot(nga_border, add=TRUE)

