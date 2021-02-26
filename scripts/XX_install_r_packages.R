install.packages('INLA', repos=c(getOption('repos'), INLA='https://inla.r-inla-download.org/R/stable'), dep=TRUE)
install.packages('maptools')
install.packages('ggplot2')
install.packages('viridis')
install.packages('cowplot')
install.packages('fields')
install.packages('inlabru')
install.packages('raster')

# Not necessary
install.packages('tidyverse')
install.packages('ggimage')
if(!require(ggregplot)) devtools::install_github("gfalbery/ggregplot")
