library(INLA)
library(fields)
library(viridis)

# Function to plot fields
local.plot.field = function(field, mesh, xlim=c(0, 16), ylim=c(2,16), ...){
  stopifnot(length(field) == mesh$n)
  # - error when using the wrong mesh
  proj = inla.mesh.projector(mesh, xlim = xlim, 
                             ylim = ylim, dims=c(300, 300))
  # - Can project from the mesh onto a 300x300 plotting grid 
  field.proj = inla.mesh.project(proj, field)
  # - Do the projection
  image.plot(list(x = proj$x, y=proj$y, z = field.proj), 
             xlim = xlim, ylim = ylim, col = plasma(101), ...)  
}

# Load data
load('data/r_model/validation_data.RData')


# Plot
#local.plot.field(res$summary.random[['s']][['mean']], mesh_spatial)



# Make predictions
pred_train <- c()
pred_test <- c()

ix_train <- inla.stack.index(stk.full, tag="train")
for(i in seq(nrow(df_train))){
  pred_train[i] <- inla.emarginal(inla.link.invlogit,
                                  res$marginals.linear.predictor[ix_train$data][[i]])
}
ix_test <- inla.stack.index(stk.full, tag="test")
for(i in seq(nrow(df_test))){
  pred_test[i] <- inla.emarginal(inla.link.invlogit,
                                  res$marginals.linear.predictor[ix_test$data][[i]])
}



# Simulations train
sim0 <- c()
ksim <- 100
for(j in 1:ksim){
  sim_sub <- rep(NA, nrow(df_train))
  for(i in 1:nrow(df_train)){
    sim_sub[i] <- rbinom(n = 1, size = 1, prob = (df_train$has_electricity/df_train$total)[i])
  }
  sim0 <- c(sim0, sim_sub)
}
trn0 <- rep(pred_train, ksim)
nsim0 <- ksim * nrow(df_train)

# ROC
false_pos <- c()
true_pos <- c()
for(threshold in 0:10/10){
  false_pos <- c(false_pos, sum(sim0 == 0 & trn0 > threshold)/ sum(sim0 == 0) )
  true_pos <- c(true_pos, sum(sim0 == 1 & trn0 > threshold) / sum(sim0 == 1) )
}
plot(false_pos, true_pos, type = "bo")


# Confusion matrix V1
threshold = 0.5
round(matrix(100 * c(sum(sim0 == 0 & trn0 <= threshold)/nsim0, # true negatives
                     sum(sim0 == 0 & trn0 > threshold)/nsim0, # false negatives
                     sum(sim0 == 1 & trn0 <= threshold)/nsim0, # false positives
                     sum(sim0 == 1 & trn0 > threshold)/nsim0), # true positives
             nrow = 2, byrow = TRUE), 2)

tp1 <- sum(sim0 == 1 & trn0 > threshold)
fp1 <- sum(sim0 == 1 & trn0 <= threshold)
tn1 <- sum(sim0 == 0 & trn0 <= threshold)
fn1 <- sum(sim0 == 0 & trn0 > threshold)

# Precision of with electricity
tp1/(tp1 + fp1)
# Recall of with electricity
tp1/(tp1 + fn1)
# Precision of without electricity
tn1/(tn1 + fn1)
# Recall of without electricity
tn1/(tn1 + fp1)



# Simulations test
sim1 <- c()
ksim <- 100
for(j in 1:ksim){
  sim_sub <- rep(NA, nrow(df_test))
  for(i in 1:nrow(df_test)){
    sim_sub[i] <- rbinom(n = 1, size = 1, prob = (df_test$has_electricity/df_test$total)[i])
  }
  sim1 <- c(sim1, sim_sub)
}
tst <- rep(pred_test, ksim)
nsim1 <- ksim * nrow(df_test)


# Confusion matrix V1
round(matrix(100 * c(sum(sim1 == 0 & tst <= threshold)/nsim1,
                     sum(sim1 == 0 & tst > threshold)/nsim1,
                     sum(sim1 == 1 & tst <= threshold)/nsim1,
                     sum(sim1 == 1 & tst > threshold)/nsim1),
             nrow = 2, byrow = TRUE), 2)

tp1 <- sum(sim1 == 1 & tst > threshold)
fp1 <- sum(sim1 == 1 & tst <= threshold)
tn1 <- sum(sim1 == 0 & tst <= threshold)
fn1 <- sum(sim1 == 0 & tst > threshold)

# Precision of with electricity
tp1/(tp1 + fp1)
# Recall of with electricity
tp1/(tp1 + fn1)
# Precision of without electricity
tn1/(tn1 + fn1)
# Recall of without electricity
tn1/(tn1 + fp1)
# Accuracy
(tn1+tp1)/(tn1 + fn1 + tp1 + fp1)
